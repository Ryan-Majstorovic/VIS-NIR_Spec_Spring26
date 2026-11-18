"""Build the separate diagnostic image without changing CubeIDE Debug files."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIRMWARE = ROOT / "CCD-Driver-Code/STM32F411_Basic"
sys.path.insert(0, str(ROOT / "tools"))
from build_ccd_firmware import INCLUDES


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", type=Path)
    args = parser.parse_args()
    compiler = args.compiler or next(iter(sorted(Path("C:/ST").glob("STM32CubeIDE_*/STM32CubeIDE/plugins/com.st.stm32cube.ide.mcu.externaltools.gnu-tools-for-stm32.*/tools/bin/arm-none-eabi-gcc.exe"), reverse=True)), None)
    if compiler is None:
        parser.error("Use --compiler to specify arm-none-eabi-gcc.")
    output = HERE / "build"
    output.mkdir(exist_ok=True)
    flags = [str(compiler), "-mcpu=cortex-m4", "-mthumb", "-mfpu=fpv4-sp-d16", "-mfloat-abi=hard", "-std=gnu11", "-DUSE_HAL_DRIVER", "-DSTM32F411xE", "-O3", "-g3", "-ffunction-sections", "-fdata-sections", "-Wall", "--specs=nano.specs"]
    flags += ["-I" + str(FIRMWARE / directory) for directory in INCLUDES]
    objects = []
    sources = []
    log = []
    for index, line in enumerate((FIRMWARE / "Debug/objects.list").read_text().splitlines()):
        relative = Path(line.strip().strip('"').removeprefix("./"))
        source = FIRMWARE / relative.with_suffix(".c")
        if not source.exists():
            source = FIRMWARE / relative.with_suffix(".s")
        if relative.as_posix() == "Core/Src/main.o":
            source = HERE / "firmware/main.c"
        if relative.as_posix() == "Core/Src/stm32f4xx_it.o":
            source = HERE / "firmware/interrupts.c"
        obj = output / f"{index}.o"
        result = subprocess.run(flags + ["-c", str(source), "-o", str(obj)], capture_output=True, text=True)
        log.append(result.stdout + result.stderr)
        (output / "build.log").write_text("".join(log), encoding="utf-8")
        if result.returncode:
            raise RuntimeError(log[-1])
        sources.append(source)
        objects.append(str(obj))
    elf = output / "spectrometer_scope.elf"
    subprocess.run(flags + objects + ["-T" + str(FIRMWARE / "STM32F411CEUX_FLASH.ld"), "--specs=nosys.specs", "-Wl,--gc-sections", "-Wl,-Map=" + str(output / "scope.map"), "-Wl,--start-group", "-lc", "-lm", "-Wl,--end-group", "-o", str(elf)], check=True)
    for fmt, ext in [("binary", ".bin"), ("ihex", ".hex")]:
        subprocess.run([str(compiler.with_name("arm-none-eabi-objcopy.exe")), "-O", fmt, str(elf), str(elf.with_suffix(ext))], check=True)
    subprocess.run([str(compiler.with_name("arm-none-eabi-size.exe")), str(elf)], check=True)
    manifest = {"firmware": "spectrometer-scope", "abi": 2, "compiler": str(compiler), "flashed": False,
                "elf_sha256": hashlib.sha256(elf.read_bytes()).hexdigest(),
                "bin_sha256": hashlib.sha256(elf.with_suffix('.bin').read_bytes()).hexdigest(),
                "production_main_sha256": hashlib.sha256((FIRMWARE / 'Core/Src/main.c').read_bytes()).hexdigest(),
                "production_interrupts_sha256": hashlib.sha256((FIRMWARE / 'Core/Src/stm32f4xx_it.c').read_bytes()).hexdigest(),
                "timing_header_sha256": hashlib.sha256((FIRMWARE / 'Core/Inc/ccd_timing.h').read_bytes()).hexdigest(),
                "source_sha256": {str(s.relative_to(ROOT)): hashlib.sha256(s.read_bytes()).hexdigest() for s in sources}}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(elf)


if __name__ == "__main__":
    main()
