Spectrometer COM Inspector
==========================

Standalone CLI for watching the spectrometer USB CDC stream.

This folder is independent from `CCD-Driver-Code` and `PythonGUI`. It does not
import either project. It only opens the selected COM port and counts complete
`CCD1` frame packets seen on that serial stream.

Setup
-----

```powershell
python -m pip install -r Spectrometer-COM-Inspector/requirements.txt
```

Usage
-----

List visible serial ports:

```powershell
python Spectrometer-COM-Inspector/spectrometer_com_inspector.py --list
```

Inspect the spectrometer stream:

```powershell
python Spectrometer-COM-Inspector/spectrometer_com_inspector.py --port COM3
```

Run the 125 fps acceptance check:

```powershell
python Spectrometer-COM-Inspector/spectrometer_com_inspector.py --port COM3 --duration 60 --require-125fps
```

The report prints once per second:

- frames seen during the last interval
- estimated frames per second
- total frames seen
- last firmware `frame_id`
- missed frame IDs detected from gaps
- last frame flags and sample count
- parser resync error bytes

The `--require-125fps` check passes only when a duration run reaches at least
124 fps with zero missed frame IDs, zero bad sync bytes, `sample_count=3694`,
and `flags=0x0001`.

Only one program can usually own a COM port at a time. Close the GUI before
running this inspector on the same spectrometer port.
