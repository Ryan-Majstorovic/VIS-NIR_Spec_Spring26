"""Build the CCD firmware outside tracked CubeIDE Debug artifacts.

Usage: python tools/build_ccd_firmware.py [--compiler /path/to/arm-none-eabi-gcc]
"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FIRMWARE = ROOT / "CCD-Driver-Code/STM32F411_Basic"
INCLUDES = (
    "Core/Inc", "Drivers/STM32F4xx_HAL_Driver/Inc",
    "Drivers/CMSIS/Device/ST/STM32F4xx/Include", "Drivers/CMSIS/Include",
    "USB_DEVICE/App", "USB_DEVICE/Target",
    "Middlewares/ST/STM32_USB_Device_Library/Core/Inc",
    "Middlewares/ST/STM32_USB_Device_Library/Class/CDC/Inc",
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", default=os.environ.get("ARM_GCC") or shutil.which("arm-none-eabi-gcc"))
    parser.add_argument("--output", type=Path, default=ROOT / ".scratch/integration-timing/build")
    args = parser.parse_args()
    compiler = args.compiler or next(Path("C:/ST").glob("**/tools/bin/arm-none-eabi-gcc.exe"), None)
    if not compiler:
        parser.error("Set ARM_GCC or --compiler to arm-none-eabi-gcc.")
    compiler = Path(compiler)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    flags = [str(compiler), "-mcpu=cortex-m4", "-mthumb", "-mfpu=fpv4-sp-d16", "-mfloat-abi=hard",
             "-std=gnu11", "-DUSE_HAL_DRIVER", "-DSTM32F411xE", "-O0", "-g3",
             "-ffunction-sections", "-fdata-sections", "-Wall", "--specs=nano.specs"]
    flags += ["-I" + str(FIRMWARE / directory) for directory in INCLUDES]
    objects = []
    for index, line in enumerate((FIRMWARE / "Debug/objects.list").read_text().splitlines()):
        relative = Path(line.strip().strip('"').removeprefix("./"))
        source = FIRMWARE / relative.with_suffix(".c")
        if not source.exists():
            source = FIRMWARE / relative.with_suffix(".s")
        obj = output / f"{index}.o"
        subprocess.run(flags + ["-c", str(source), "-o", str(obj)], check=True)
        objects.append(str(obj))
    elf = output / "STM32F411_Basic.elf"
    subprocess.run(flags + objects + ["-T" + str(FIRMWARE / "STM32F411CEUX_FLASH.ld"),
                   "--specs=nosys.specs", "-Wl,--gc-sections", "-Wl,-Map=" + str(output / "firmware.map"),
                   "-Wl,--start-group", "-lc", "-lm", "-Wl,--end-group", "-o", str(elf)], check=True)
    subprocess.run([str(compiler.with_name("arm-none-eabi-size" + compiler.suffix)), str(elf)], check=True)
    print(elf)


if __name__ == "__main__":
    main()
