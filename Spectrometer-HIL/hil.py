"""Build a standalone STM32F411 stimulus device; never modifies or flashes hardware."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import shutil
import struct
import subprocess

TOOL_DIR = Path(__file__).resolve().parent
REPO_DIR = TOOL_DIR.parent
PRODUCTION_DIR = REPO_DIR / "CCD-Driver-Code" / "STM32F411_Basic"
BUILD_DIR = TOOL_DIR / "build"
SAMPLE_COUNT = 3694
EFFECTIVE_START = 32
EFFECTIVE_COUNT = 3648
BASELINE = 3000
ADC_MAX = 4095
TABLE_FRAMES = 32
HEADER = struct.Struct("<4sBBHIHHHHI")
FLASH_BASE = 0x08000000
RATES = (1, 5, 10, 20, 25, 50, 100, 125)

# Compile the existing USB implementation and vendor support without copying or
# changing the production application, CubeIDE project, or GUI.
INCLUDES = (
    "Core/Inc", "USB_DEVICE/App", "USB_DEVICE/Target",
    "Drivers/STM32F4xx_HAL_Driver/Inc",
    "Drivers/STM32F4xx_HAL_Driver/Inc/Legacy",
    "Drivers/CMSIS/Device/ST/STM32F4xx/Include", "Drivers/CMSIS/Include",
    "Middlewares/ST/STM32_USB_Device_Library/Core/Inc",
    "Middlewares/ST/STM32_USB_Device_Library/Class/CDC/Inc",
)
HAL_MODULES = (
    "hal", "hal_cortex", "hal_rcc", "hal_rcc_ex", "hal_flash",
    "hal_flash_ex", "hal_gpio", "hal_pwr", "hal_pwr_ex", "hal_pcd",
    "hal_pcd_ex", "ll_usb",
)
SOURCES = (
    "Core/Src/system_stm32f4xx.c", "Core/Src/syscalls.c", "Core/Src/sysmem.c",
    "Core/Startup/startup_stm32f411ceux.s",
    "USB_DEVICE/App/usb_device.c", "USB_DEVICE/App/usbd_desc.c",
    "USB_DEVICE/App/usbd_cdc_if.c", "USB_DEVICE/Target/usbd_conf.c",
    "Middlewares/ST/STM32_USB_Device_Library/Core/Src/usbd_core.c",
    "Middlewares/ST/STM32_USB_Device_Library/Core/Src/usbd_ctlreq.c",
    "Middlewares/ST/STM32_USB_Device_Library/Core/Src/usbd_ioreq.c",
    "Middlewares/ST/STM32_USB_Device_Library/Class/CDC/Src/usbd_cdc.c",
)


def find_toolchain(override: str | None) -> Path:
    if override:
        directory = Path(override).resolve()
    elif executable := shutil.which("arm-none-eabi-gcc"):
        directory = Path(executable).parent
    else:
        candidates = sorted(Path("C:/ST").glob(
            "STM32CubeIDE_*/STM32CubeIDE/plugins/"
            "com.st.stm32cube.ide.mcu.externaltools.gnu-tools-for-stm32.*/tools/bin"
        ))
        if not candidates:
            raise RuntimeError("Pass --toolchain pointing to the ARM GCC bin directory.")
        directory = candidates[-1]
    if not (directory / "arm-none-eabi-gcc.exe").is_file():
        raise RuntimeError(f"ARM GCC not found in {directory}")
    return directory


def create_frames(pattern: str, noise: int, seed: int) -> list[list[int]]:
    """Generate raw detector counts, including shielded/dummy baseline samples."""
    rng = random.Random(seed)
    frames = []
    for frame_index in range(TABLE_FRAMES):
        samples = []
        for sample_index in range(SAMPLE_COUNT):
            pixel = sample_index - EFFECTIVE_START
            signal = 0.0
            if 0 <= pixel < EFFECTIVE_COUNT:
                if pattern == "peaks":
                    # Gaussian line stimuli with known centers/widths for plots.
                    for center, width, amplitude in ((700, 35, 1900), (2450, 80, 1200)):
                        signal += amplitude * math.exp(-0.5 * ((pixel - center) / width) ** 2)
                elif pattern == "sweep":
                    center = 200 + frame_index * (EFFECTIVE_COUNT - 401) / (TABLE_FRAMES - 1)
                    signal = 2000 * math.exp(-0.5 * ((pixel - center) / 45) ** 2)
                elif pattern == "saturated":
                    signal = BASELINE
            # The current GUI expects inverted CCD polarity: more light lowers
            # the raw ADC value. Dummy/shielded samples retain a dark baseline.
            count = round(BASELINE - signal) + rng.randint(-noise, noise)
            samples.append(max(0, min(ADC_MAX, count)))
        frames.append(samples)
    return frames


def write_inputs(output: Path, frames: list[list[int]], fps: int, drop_every: int) -> bytes:
    (output / "hil_config.h").write_text(
        "#ifndef HIL_CONFIG_H\n#define HIL_CONFIG_H\n"
        f"#define HIL_FRAME_COUNT {len(frames)}U\n"
        f"#define HIL_PERIOD_MS {1000 // fps}U\n"
        f"#define HIL_DROP_EVERY {drop_every}U\n#endif\n", encoding="ascii"
    )
    source = ['#include "hil_packet.h"', 'const HilPacket hil_frames[HIL_FRAME_COUNT] = {']
    wire = bytearray()
    for samples in frames:
        # All templates have ID zero. Firmware assigns scheduled frame IDs.
        source.append("  { .header = {{'C','C','D','1'}, 1, 1, 0, 0, 3694, 32, 3648, 1, 7388},")
        source.append("    .samples = {")
        for start in range(0, SAMPLE_COUNT, 24):
            source.append("      " + ",".join(map(str, samples[start:start + 24])) + ",")
        source.append("    } },")
        wire.extend(HEADER.pack(b"CCD1", 1, 1, 0, 0, SAMPLE_COUNT,
                                EFFECTIVE_START, EFFECTIVE_COUNT, 1, SAMPLE_COUNT * 2))
        wire.extend(struct.pack(f"<{SAMPLE_COUNT}H", *samples))
    source.append("};\n")
    (output / "hil_data.c").write_text("\n".join(source), encoding="ascii")
    return bytes(wire)


def build(args: argparse.Namespace) -> Path:
    toolchain = find_toolchain(args.toolchain)
    output = BUILD_DIR / f"{args.pattern}-{args.fps}fps-noise{args.noise}-seed{args.seed}-drop{args.drop_every}"
    output.mkdir(parents=True, exist_ok=True)
    frames = create_frames(args.pattern, args.noise, args.seed)
    expected_wire = write_inputs(output, frames, args.fps, args.drop_every)
    source_paths = [PRODUCTION_DIR / source for source in SOURCES]
    source_paths.extend(PRODUCTION_DIR / f"Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_{module}.c"
                        for module in HAL_MODULES)
    source_paths.extend([TOOL_DIR / "firmware/main.c", output / "hil_data.c"])
    elf = output / "spectrometer_hil.elf"
    common = ["-mcpu=cortex-m4", "-mthumb", "-mfpu=fpv4-sp-d16", "-mfloat-abi=hard"]
    command = [str(toolchain / "arm-none-eabi-gcc.exe"), *common,
               "-std=gnu11", "-Os", "-g3", "-DUSE_HAL_DRIVER", "-DSTM32F411xE",
               "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra"]
    for directory in [TOOL_DIR / "firmware", output, *(PRODUCTION_DIR / p for p in INCLUDES)]:
        command.extend(["-I", str(directory)])
    command.extend(str(p) for p in source_paths)
    command.extend(["-T", str(PRODUCTION_DIR / "STM32F411CEUX_FLASH.ld"),
                    "--specs=nosys.specs", "--specs=nano.specs", "-Wl,--gc-sections",
                    f"-Wl,-Map={output / 'spectrometer_hil.map'}", "-o", str(elf)])
    completed = subprocess.run(command, capture_output=True, text=True)
    (output / "build.log").write_text(completed.stdout + completed.stderr, encoding="utf-8")
    if completed.returncode:
        raise RuntimeError(f"Compilation failed; see {output / 'build.log'}\n{completed.stderr}")
    for format_name, extension in (("binary", "bin"), ("ihex", "hex")):
        subprocess.run([str(toolchain / "arm-none-eabi-objcopy.exe"), "-O", format_name,
                        str(elf), str(elf.with_suffix('.' + extension))], check=True)

    # Check the actual ARM-compiled table bytes, so padding/endianness mistakes
    # cannot be hidden by testing only the Python stimulus generator.
    symbols = subprocess.check_output([str(toolchain / "arm-none-eabi-nm.exe"),
                                       "-S", str(elf)], text=True)
    table_symbol = next(line.split() for line in symbols.splitlines()
                        if line.split()[-1] == "hil_frames")
    offset = int(table_symbol[0], 16) - FLASH_BASE
    size = int(table_symbol[1], 16)
    compiled_wire = elf.with_suffix(".bin").read_bytes()[offset:offset + size]
    if compiled_wire != expected_wire:
        raise RuntimeError("Compiled frame table differs from the expected CCD1 wire bytes.")
    (output / "compiled_frames.ccd1").write_bytes(compiled_wire)
    manifest = {
        "pattern": args.pattern, "fps_requested": args.fps, "noise_counts": args.noise,
        "seed": args.seed, "drop_every": args.drop_every, "table_frames": len(frames),
        "packet_bytes": 7412, "compiled_table_matches": True,
        "elf_sha256": hashlib.sha256(elf.read_bytes()).hexdigest(),
        "gui_verified": False, "hardware_verified": False,
        "toolchain": str(toolchain),
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    size_report = subprocess.check_output([str(toolchain / "arm-none-eabi-size.exe"), str(elf)], text=True)
    print(size_report.strip())
    print(f"Built {elf}\nCompiled frame table: {len(frames)} packets verified byte-for-byte.")
    print("Ready for manual flashing. USB behavior and achieved frame rate require board testing.")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pattern", choices=("dark", "peaks", "sweep", "saturated"), default="peaks")
    parser.add_argument("--fps", type=int, choices=RATES, default=10)
    parser.add_argument("--noise", type=int, default=4, help="Uniform noise amplitude in ADC counts (0..100).")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--drop-every", type=int, default=0, help="Skip each Nth scheduled frame; 0 disables.")
    parser.add_argument("--toolchain", help="Path to the ARM GCC bin directory; autodetects CubeIDE under C:/ST.")
    args = parser.parse_args()
    if not 0 <= args.noise <= 100:
        parser.error("--noise must be 0..100")
    if not 0 <= args.drop_every <= 0xFFFFFFFF or args.drop_every == 1:
        parser.error("--drop-every must be 0 (off) or 2..4294967295")
    try:
        build(args)
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
