"""Build the CCD firmware outside tracked CubeIDE Debug artifacts.

Usage: python tools/build_ccd_firmware.py [--compiler /path/to/arm-none-eabi-gcc]
"""
import argparse
import hashlib
import json
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
             "-std=gnu11", "-DUSE_HAL_DRIVER", "-DSTM32F411xE", "-O3", "-g3",
             "-ffunction-sections", "-fdata-sections", "-Wall", "--specs=nano.specs"]
    flags += ["-I" + str(FIRMWARE / directory) for directory in INCLUDES]
    objects = []
    source_hashes = {}
    for index, line in enumerate((FIRMWARE / "Debug/objects.list").read_text().splitlines()):
        relative = Path(line.strip().strip('"').removeprefix("./"))
        source = FIRMWARE / relative.with_suffix(".c")
        if not source.exists():
            source = FIRMWARE / relative.with_suffix(".s")
        obj = output / f"{index}.o"
        subprocess.run(flags + ["-c", str(source), "-o", str(obj)], check=True)
        objects.append(str(obj))
        source_hashes[str(source.relative_to(ROOT))] = hashlib.sha256(source.read_bytes()).hexdigest()
    elf = output / "STM32F411_Basic.elf"
    subprocess.run(flags + objects + ["-T" + str(FIRMWARE / "STM32F411CEUX_FLASH.ld"),
                   "--specs=nosys.specs", "-Wl,--gc-sections", "-Wl,-Map=" + str(output / "firmware.map"),
                   "-Wl,--start-group", "-lc", "-lm", "-Wl,--end-group", "-o", str(elf)], check=True)
    subprocess.run([str(compiler.with_name("arm-none-eabi-size" + compiler.suffix)), str(elf)], check=True)
    for fmt, ext in (("binary", ".bin"), ("ihex", ".hex")):
        subprocess.run([str(compiler.with_name("arm-none-eabi-objcopy" + compiler.suffix)),
                        "-O", fmt, str(elf), str(elf.with_suffix(ext))], check=True)
    (output / "manifest.json").write_text(json.dumps({
        "firmware": "production", "abi": 3, "timing_profile_id": 65537,
        "compiler": str(compiler), "optimization": "O3",
        "elf_sha256": hashlib.sha256(elf.read_bytes()).hexdigest(),
        "bin_sha256": hashlib.sha256(elf.with_suffix('.bin').read_bytes()).hexdigest(),
        "source_sha256": source_hashes,
        "timing_header_sha256": hashlib.sha256((FIRMWARE / 'Core/Inc/ccd_timing.h').read_bytes()).hexdigest(),
        "scope_observer_sha256": hashlib.sha256((FIRMWARE / 'Core/Src/production_scope.inc').read_bytes()).hexdigest(),
    }, indent=2))
    print(elf)


if __name__ == "__main__":
    main()
