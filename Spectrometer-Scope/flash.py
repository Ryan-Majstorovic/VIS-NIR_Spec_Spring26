"""Explicit diagnostic flashing and full-flash recovery through a named ST-Link."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent


def programmer():
    matches = sorted(Path("C:/ST").glob("STM32CubeIDE_*/STM32CubeIDE/plugins/com.st.stm32cube.ide.mcu.externaltools.cubeprogrammer.*/tools/bin/STM32_Programmer_CLI.exe"))
    if not matches:
        raise RuntimeError("STM32CubeProgrammer CLI not found under C:/ST.")
    return matches[-1]


def run(cli, serial, *arguments):
    command = [str(cli), "-c", "port=SWD", f"sn={serial}", "mode=UR", "freq=1000", *map(str, arguments)]
    result = subprocess.run(command, capture_output=True, text=True, errors="replace")
    print(result.stdout)
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("flash", "restore"))
    parser.add_argument("--serial", required=True, help="Exact ST-Link serial number.")
    parser.add_argument("--backup", type=Path, help="Full 512 KB recovery image for restore.")
    parser.add_argument("--image", type=Path, help="Built ELF with sibling bin and manifest.json (production or diagnostic).")
    args = parser.parse_args()
    cli = programmer()
    # Identify the target before any flash erase/write.
    identity = run(cli, args.serial)
    if not re.search(r"Device ID\s*:\s*0x431\b", identity):
        raise RuntimeError("Target is not the expected STM32F411 (device ID 0x431).")
    if args.action == "restore":
        if args.backup is None or args.backup.stat().st_size != 524288:
            parser.error("Restore requires a complete 512 KB --backup image.")
        run(cli, args.serial, "-d", args.backup.resolve(), "0x08000000", "-v", "-rst")
        return
    image = args.image.resolve() if args.image else HERE / "build/spectrometer_scope.elf"
    binary = image.with_suffix(".bin")
    manifest = json.loads((image.parent / "manifest.json").read_text())
    if hashlib.sha256(binary.read_bytes()).hexdigest() != manifest["bin_sha256"]:
        raise RuntimeError("Build manifest does not match diagnostic image.")
    if hashlib.sha256(image.read_bytes()).hexdigest() != manifest.get("elf_sha256"):
        raise RuntimeError("Build manifest does not match ELF; rebuild before flashing.")
    directory = HERE / "captures/backups"
    directory.mkdir(parents=True, exist_ok=True)
    backup = directory / f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{args.serial}.bin"
    run(cli, args.serial, "-u", "0x08000000", "0x80000", backup)
    if backup.stat().st_size != 524288:
        raise RuntimeError("Flash backup is incomplete; diagnostic flash cancelled.")
    metadata = {"utc": datetime.now(timezone.utc).isoformat(), "probe_serial": args.serial,
                "backup_sha256": hashlib.sha256(backup.read_bytes()).hexdigest(),
                "diagnostic_bin_sha256": manifest["bin_sha256"]}
    backup.with_suffix(".json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    run(cli, args.serial, "-d", image, "-v", "-rst")
    print(f"Recovery image: {backup}")


if __name__ == "__main__":
    main()
