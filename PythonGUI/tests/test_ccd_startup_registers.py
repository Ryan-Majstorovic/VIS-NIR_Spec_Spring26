"""Execute production StartTiming() against mapped registers, with DMA/ADC stubs.

This verifies configuration writes and trigger routing, not peripheral timing.
"""
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
FIRMWARE = ROOT / "CCD-Driver-Code/STM32F411_Basic"


class StartupRegisterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import unicorn
            from unicorn import arm_const
        except ImportError:
            raise unittest.SkipTest("Unicorn is required for register-level startup checks.")
        cc = os.environ.get("ARM_GCC") or next(Path("C:/ST").glob("**/tools/bin/arm-none-eabi-gcc.exe"), None)
        if not cc:
            raise unittest.SkipTest("Set ARM_GCC to arm-none-eabi-gcc.")
        cc = Path(cc)
        cls.directory = tempfile.TemporaryDirectory()
        output = Path(cls.directory.name)
        source = output / "startup.c"
        source.write_text('''#define main firmware_main
#include "main.c"
#undef main
HAL_StatusTypeDef __wrap_HAL_ADC_Stop_DMA(ADC_HandleTypeDef *h) { return HAL_OK; }
HAL_StatusTypeDef __wrap_HAL_ADC_Start_DMA(ADC_HandleTypeDef *h, uint32_t *p, uint32_t n) { return HAL_OK; }
HAL_StatusTypeDef __wrap_HAL_DMA_Abort(DMA_HandleTypeDef *h) { return HAL_OK; }
HAL_StatusTypeDef __wrap_HAL_DMA_Init(DMA_HandleTypeDef *h) { return HAL_OK; }
HAL_StatusTypeDef __wrap_HAL_DMA_Start_IT(DMA_HandleTypeDef *h, uint32_t s, uint32_t d, uint32_t n) { return HAL_OK; }
void configure(uint32_t us) {
  htim1.Instance = TIM1; htim2.Instance = TIM2;
  htim3.Instance = TIM3; htim4.Instance = TIM4;
  hadc1.Instance = ADC1;
  TIM1->ARR = CCD_MASTER_PERIOD_TICKS - 1U;
  TIM1->CCR1 = CCD_MASTER_HIGH_TICKS;
  StartTiming(us);
}
''')
        includes = ("Core/Inc", "Core/Src", "Drivers/STM32F4xx_HAL_Driver/Inc",
                    "Drivers/CMSIS/Device/ST/STM32F4xx/Include", "Drivers/CMSIS/Include",
                    "USB_DEVICE/App", "USB_DEVICE/Target",
                    "Middlewares/ST/STM32_USB_Device_Library/Core/Inc",
                    "Middlewares/ST/STM32_USB_Device_Library/Class/CDC/Inc")
        elf = output / "startup.elf"
        args = [str(cc), "-O0", "-mcpu=cortex-m4", "-mthumb", "-mfpu=fpv4-sp-d16", "-mfloat-abi=hard",
                "-DUSE_HAL_DRIVER", "-DSTM32F411xE", "-ffunction-sections", "-fdata-sections", "-nostdlib",
                "-Wl,--gc-sections", "-Wl,-Ttext=0x10000", "-Wl,-Tdata=0x20000000", "-Wl,-e,configure"]
        args += ["-I" + str(FIRMWARE / p) for p in includes]
        args += ["-Wl,--wrap=" + name for name in ("HAL_ADC_Stop_DMA", "HAL_ADC_Start_DMA", "HAL_DMA_Abort",
                                                  "HAL_DMA_Init", "HAL_DMA_Start_IT")]
        args += [str(source), str(FIRMWARE / "Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_tim.c"),
                 str(FIRMWARE / "Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_cortex.c"),
                 "-lgcc", "-o", str(elf)]
        result = subprocess.run(args, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stderr)
        symbols = subprocess.check_output([str(cc.with_name("arm-none-eabi-nm" + cc.suffix)), str(elf)], text=True)
        cls.entry = int(next(s.split()[0] for s in symbols.splitlines() if s.endswith(" configure")), 16)
        cls.elf = elf.read_bytes()
        cls.unicorn, cls.reg = unicorn, arm_const

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "directory"):
            cls.directory.cleanup()

    def read(self, address):
        return struct.unpack("<I", self.uc.mem_read(address, 4))[0]

    def test_real_startup_polarity_phase_and_independent_trigger_routing(self):
        for us in (10, 8000, 8001, 32001, 5_000_000):
            with self.subTest(integration_us=us):
                u = self.unicorn
                self.uc = u.Uc(u.UC_ARCH_ARM, u.UC_MODE_THUMB | u.UC_MODE_MCLASS)
                self.uc.mem_map(0, 0x20000)
                self.uc.mem_map(0x20000000, 0x20000)
                self.uc.mem_map(0x40000000, 0x30000)
                self.uc.mem_map(0xE000E000, 0x1000)
                phoff = struct.unpack_from("<I", self.elf, 28)[0]
                phsize, phcount = struct.unpack_from("<HH", self.elf, 42)
                for i in range(phcount):
                    kind, offset, address, _, size, _, _, _ = struct.unpack_from("<8I", self.elf, phoff + i * phsize)
                    if kind == 1 and size:
                        self.uc.mem_write(address, self.elf[offset:offset + size])
                reloads = []
                def record_reload(uc, access, address, size, value, user_data):
                    if address in (0x40000414, 0x40000814):
                        timer = address - 0x14
                        reloads.append((timer, self.read(timer + 0x2C), self.read(timer + 0x34)))
                self.uc.hook_add(u.UC_HOOK_MEM_WRITE, record_reload)
                self.uc.reg_write(self.reg.UC_ARM_REG_SP, 0x2001FFF0)
                self.uc.reg_write(self.reg.UC_ARM_REG_R0, us)
                self.uc.reg_write(self.reg.UC_ARM_REG_LR, 0x1F001)
                self.uc.emu_start(self.entry | 1, 0x1F000, count=100000)
                self.assertEqual(self.uc.reg_read(self.reg.UC_ARM_REG_PC), 0x1F000)
                tim1, tim2, tim3, tim4 = 0x40010000, 0x40000000, 0x40000400, 0x40000800
                self.assertEqual(self.read(tim1 + 0x24), 36)  # Phase seed: MCU low / detector high.
                self.assertEqual(self.read(tim1 + 0x20) & 3, 1)  # PA8 non-inverted, enabled.
                for timer in (tim3, tim4):
                    self.assertEqual(self.read(timer + 0x20) & 3, 3)  # Invert to cancel board U1.
                    self.assertEqual(self.read(timer + 0x08) & 0x77, 6)  # Trigger mode, ITR0=TIM1.
                self.assertEqual(self.read(tim2 + 0x08) & 0x77, 0x36)  # ADC starts from TIM4, SH does not.
                n = (us + 31999) // 32000 if us > 8000 else 1
                initial_sh_arr = (us // n) * 2 - 1
                self.assertEqual(self.read(tim3 + 0x24), initial_sh_arr)
                self.assertEqual(self.read(tim4 + 0x24), 0)
                self.assertIn((tim3, initial_sh_arr, 0 if n > 1 else 12), reloads)
                self.assertEqual(self.read(tim1 + 0x04) & 0x70, 0x10)  # One common enable trigger.
                self.assertEqual(self.read(tim3 + 0x28), 47)
                self.assertEqual(self.read(tim4 + 0x28), 47)
                self.assertEqual(self.read(tim3 + 0x34), 12)  # Fixed detector SH-high compare.
                self.assertEqual(self.read(tim1 + 0x2C), 47)
                self.assertEqual(self.read(tim1 + 0x34), 24)


if __name__ == "__main__":
    unittest.main()
