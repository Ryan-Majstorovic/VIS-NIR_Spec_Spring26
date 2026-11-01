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
  if (field == 4) return CCD_SH_INVERT_OUTPUT;
  if (field == 5) return CCD_ICG_INVERT_OUTPUT;
  if (field == 6) return CCD_MASTER_INVERT_OUTPUT;
  if (field == 7) return CCD_BOARD_INVERTS_CLOCKS;
  if (field == 8) return CCD_MASTER_INITIAL_COUNTER;
  if (field == 9) return CCD_MASTER_PERIOD_TICKS;
  if (field == 10) return CCD_MASTER_HIGH_TICKS;
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
        board_inversion = self.evaluate(8000, field=7)
        for counter in range(16000):
            oc_ref = int(counter >= compare)  # PWM2
            pb6 = oc_ref ^ internal_inversion
            ccd_icg = pb6 ^ board_inversion  # U1 74HC04
            ccd_high_ticks += ccd_icg
        self.assertEqual(ccd_high_ticks, 7388 * 2)

    def setUp(self):
        self.board_inversion = self.evaluate(8000, field=7)

    def detector_level(self, oc_ref, output_inversion):
        return oc_ref ^ output_inversion ^ self.board_inversion

    def test_sh_phase_and_width_at_detector_for_every_short_setting(self):
        from backend.device.integration import SHORT_SETTINGS
        inversion = self.evaluate(8000, field=4)
        self.assertEqual(inversion, 1)
        high_ticks = self.evaluate(8000, 0, 1, 3)
        self.assertEqual(high_ticks, 12)
        for us in SHORT_SETTINGS:
            with self.subTest(us=us):
                period_ticks = us * 2
                initial_counter = period_ticks - 1
                # Initial wrap at +0.5 us produces detector SH rising, not falling.
                detector = [self.detector_level(int((initial_counter + tick) % period_ticks < high_ticks), inversion)
                            for tick in range(16000 + period_ticks + 1)]
                self.assertEqual(detector[0:2], [0, 1])
                self.assertEqual(detector[12:14], [1, 0])
                self.assertEqual(sum(detector[1:period_ticks + 1]), 12)
                # At the next 8-ms ICG falling edge, the same SH phase repeats.
                self.assertEqual(detector[16000:16002], [0, 1])
                self.assertEqual(detector[16012:16014], [1, 0])

    def test_master_clock_is_high_at_ccd_icg_rising(self):
        inversion = self.evaluate(8000, field=6)
        seed = self.evaluate(8000, field=8)
        period = self.evaluate(8000, field=9)
        high_ticks = self.evaluate(8000, field=10)
        self.assertEqual((period, high_ticks), (48, 24))
        detector = [self.detector_level(int((seed + tick) % period < high_ticks), inversion)
                    for tick in range(period)]
        self.assertEqual(sum(detector), 24)  # 250 ns high and 250 ns low at 96 MHz.
        self.assertEqual(detector[0], 1)
        # All physical frame/readout boundaries use integer us, hence integer phiM cycles.
        for us in (10, 8000, 8001, 12500, 32001, 100001, 5_000_000):
            frame_us = max(8000, us)
            for frame in (0, 1, 1000):
                rising_cpu_tick = (frame * frame_us + frame_us - 7388) * 96
                counter = (seed + rising_cpu_tick) % period
                self.assertEqual(self.detector_level(int(counter < high_ticks), inversion), 1)
        # Nominal alignment is centered within high, not on a clock edge.
        for offset in range(-11, 12):
            self.assertEqual(self.detector_level(int((seed + offset) % period < high_ticks), inversion), 1)

    def test_long_segments_remain_low_at_detector_when_sh_is_suppressed(self):
        inversion = self.evaluate(8000, field=4)
        for us in (32001, 100001, 5_000_000):
            rows = self.rows(us, 1)
            for arr, ccr in rows[1:]:
                self.assertEqual(ccr, 0)
                for counter in (0, arr):
                    self.assertEqual(self.detector_level(int(counter < ccr), inversion), 0)
            self.assertEqual(rows[0][1] / 2, 6)

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
