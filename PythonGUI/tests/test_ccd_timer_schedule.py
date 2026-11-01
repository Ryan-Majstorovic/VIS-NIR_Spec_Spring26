"""Execute the production C schedule generator, then model timer shadow latching.

Requires arm-none-eabi-gcc (ARM_GCC or STM32CubeIDE) and the Unicorn test extra.
This checks digital schedules, not STM32 peripheral or detector propagation timing.
"""
import os
from pathlib import Path
import random
import sys
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "PythonGUI"))


class CompiledScheduleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import unicorn
            from unicorn import arm_const
        except ImportError:
            raise unittest.SkipTest("Unicorn is required to execute the compiled ARM schedule generator.")
        compiler = os.environ.get("ARM_GCC")
        if not compiler:
            compiler = next(Path("C:/ST").glob("**/tools/bin/arm-none-eabi-gcc.exe"), None)
        if not compiler:
            raise unittest.SkipTest("Set ARM_GCC to arm-none-eabi-gcc.")
        compiler = Path(compiler)
        cls.directory = tempfile.TemporaryDirectory()
        output = Path(cls.directory.name)
        source = output / "schedule.c"
        source.write_text('''#include "ccd_timing.h"
uint32_t evaluate(uint32_t us, uint32_t index, uint32_t sh, uint32_t field) {
  if (field == 0) return CcdIntegrationValid(us);
  if (field == 1) return CcdSegmentCount(us);
  if (field == 5) return CCD_ICG_INVERT_OUTPUT;
  CcdTimingSegment s = CcdSegment(us, index, sh);
  return field == 2 ? s.arr : s.ccr;
}
''')
        subprocess.run([str(compiler), "-O2", "-mcpu=cortex-m4", "-mthumb", "-nostdlib",
                        "-I" + str(ROOT / "CCD-Driver-Code/STM32F411_Basic/Core/Inc"),
                        "-Wl,-Ttext=0x10000", "-Wl,-e,evaluate", str(source), "-o", str(output / "schedule.elf")],
                       check=True, capture_output=True)
        subprocess.run([str(compiler.with_name("arm-none-eabi-objcopy" + compiler.suffix)), "-O", "binary",
                        str(output / "schedule.elf"), str(output / "schedule.bin")], check=True)
        symbols = subprocess.check_output([str(compiler.with_name("arm-none-eabi-nm" + compiler.suffix)), str(output / "schedule.elf")], text=True)
        cls.entry = int(next(line.split()[0] for line in symbols.splitlines() if line.endswith(" evaluate")), 16)
        cls.uc = unicorn.Uc(unicorn.UC_ARCH_ARM, unicorn.UC_MODE_THUMB | unicorn.UC_MODE_MCLASS)
        cls.uc.mem_map(0x10000, 0x10000)
        cls.uc.mem_write(0x10000, (output / "schedule.bin").read_bytes())
        cls.uc.mem_map(0x20000000, 0x10000)
        cls.reg = arm_const

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "directory"):
            cls.directory.cleanup()

    def evaluate(self, us, index=0, sh=0, field=0):
        for register, value in zip((self.reg.UC_ARM_REG_R0, self.reg.UC_ARM_REG_R1,
                                    self.reg.UC_ARM_REG_R2, self.reg.UC_ARM_REG_R3),
                                   (us, index, sh, field)):
            self.uc.reg_write(register, value)
        self.uc.reg_write(self.reg.UC_ARM_REG_SP, 0x2000FFF0)
        self.uc.reg_write(self.reg.UC_ARM_REG_LR, 0x18001)
        self.uc.emu_start(self.entry | 1, 0x18000, count=10000)
        self.assertEqual(self.uc.reg_read(self.reg.UC_ARM_REG_PC), 0x18000)
        return self.uc.reg_read(self.reg.UC_ARM_REG_R0)

    def rows(self, us, sh):
        n = self.evaluate(us, field=1)
        return [(self.evaluate(us, i, sh, 2), self.evaluate(us, i, sh, 3)) for i in range(n)]

    def test_c_validation_matches_host(self):
        from backend.device.integration import valid_integration
        for us in list(range(8002)) + [10000, 12500, 32001, 100001, 5_000_000, 5_000_001]:
            self.assertEqual(bool(self.evaluate(us)), valid_integration(us))

    def test_icg_preserves_high_time_after_driver_inversion(self):
        internal_inversion = self.evaluate(8000, field=5)
        self.assertEqual(internal_inversion, 1)
        compare = self.evaluate(8000, 0, 0, 3)
        ccd_high_ticks = 0
        for counter in range(16000):
            oc_ref = int(counter >= compare)  # PWM2
            pb6 = oc_ref ^ internal_inversion
            ccd_icg = pb6 ^ 1  # U1 74HC04
            ccd_high_ticks += ccd_icg
        self.assertEqual(ccd_high_ticks, 7388 * 2)

    @unittest.expectedFailure
    def test_sh_phase_at_detector_after_driver_inversion(self):
        # Remaining qualification issue: SH was specified at the MCU boundary.
        # U1 inverts PA6 too; MCU SH rising is detector SH falling.
        mcu_high_ticks = self.evaluate(8000, 0, 1, 3)
        detector_sh_rise_us = 0.5 + mcu_high_ticks / 2
        self.assertAlmostEqual(detector_sh_rise_us, 0.5)

    def test_preload_rotation_and_physical_edges(self):
        rng = random.Random(42)
        for us in [8001, 10000, 12500, 32000, 32001, 100001, 5_000_000] + [rng.randint(8001, 5_000_000) for _ in range(30)]:
            with self.subTest(us=us):
                sh, icg = self.rows(us, 1), self.rows(us, 0)
                n = len(sh)
                self.assertEqual(sum(arr + 1 for arr, _ in sh), us * 2)
                self.assertEqual([arr for arr, _ in sh], [arr for arr, _ in icg])
                # Same initial active/shadow/DMA rotations as StartTiming().
                for rows, rotation in ((sh, 1), (icg, 2)):
                    active = rows[0]
                    shadow = rows[1 % n]
                    dma = [rows[(i + rotation) % n] for i in range(n)]
                    if rotation == 1:  # Initial SH wrap first latches row 0.
                        shadow = dma[0]
                        dma = dma[1:] + dma[:1]
                    for i in range(n * 3):
                        self.assertEqual(active, rows[i % n])
                        active, shadow = shadow, dma[i % n]
                self.assertEqual([ccr for _, ccr in sh], [12] + [0] * (n - 1))
                high_ticks = sum(max(0, arr + 1 - ccr) for arr, ccr in icg)
                self.assertEqual(high_ticks, 7388 * 2)
                self.assertEqual((icg[-1][0] + 1 - icg[-1][1]) / 2, 7388)
                self.assertEqual(sh[0][1] / 2, 6)
                # Every other ICG segment is continuously low, including at overflow.
                self.assertTrue(all(ccr == arr + 1 for arr, ccr in icg[:-1]))


if __name__ == "__main__":
    unittest.main()
