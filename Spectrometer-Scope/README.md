# CCD Scope

A separate STM32F411 diagnostic firmware and desktop scope for the TCD1304DG.
It displays uncorrected video, measured MCU GPIO clocks, and timing checks.
It also supports scope snapshots from the production firmware without replacing it.
Builds leave tracked CubeIDE Debug output untouched.

## Production firmware validation

Use `--mode production` for a resolved timing zoom or `--mode productionoverview`
for the full readout. These commands observe the running production PWM clocks
and its actual 3694-sample ADC frame at 500 kS/s. They retain exposure settings.
The zoom briefly defers interrupts during GPIO observation while hardware timers,
ADC and DMA continue. The scope response temporarily interrupts normal USB frame
delivery; validate uninterrupted throughput in a separate run.

```powershell
.\PythonGUI\.venv\Scripts\python.exe tools\build_ccd_firmware.py --output .scratch\production-timing\build
.\PythonGUI\.venv\Scripts\python.exe Spectrometer-Scope\flash.py flash --serial YOUR_STLINK_SERIAL --image .scratch\production-timing\build\STM32F411_Basic.elf
.\PythonGUI\.venv\Scripts\python.exe Spectrometer-Scope\production_check.py --output .scratch\production-validation
.\PythonGUI\.venv\Scripts\python.exe Spectrometer-Scope\scope.py gui --port COM3 --mode production
```

Only one application can own COM3 at a time. Disconnect the desktop app before
using scope capture. The production image uses corrected 8 us ICG-low timing,
100 us startup integration, and CCD1 v3 CRC-protected packets with timing profile
`0x00010001`. The `production_check.py` sweep ends at 100 us. Older diagnostic
profiles below are separate comparisons and require the diagnostic image.

## What is observed

The firmware reads GPIO input registers for PA8 (master clock), PA6 (SH),
PB6 (ICG), and PA5 (ADC timer output), and timestamps observations with the
Cortex-M4 cycle counter. These are MCU pad observations before the driver board.
The optional **Detector inferred** view applies the configured inverter model;
it does not turn those observations into sensor-pin measurements.

The default analog trace contains **12,000 real 12-bit ADC samples at 1.333333
MS/s**, one every **0.75 us**, covering 9 ms. Acquisition starts 199.5 us before
the observed ICG falling edge. An internal TIM4 channel-2 compare starts TIM2;
it does not require another wire or change an output pin. The slow comparison
captures 4500 samples at 0.5 MS/s over the same 9 ms. Legacy 4000-sample modes
remain available, and saved CSCP v1 captures remain readable.

The CCD master remains 2 MHz, giving one CCD pixel period every 2 us. Fast
mode therefore has 2.667 ADC samples per pixel; ADC indices are not pixel
indices. The chart uses the estimated end of the ADC sampling aperture, including
ST's trigger latency. CSV exports include both projected trigger and hold times.
Neither analog settling nor the physical sampling aperture is measured directly.

The image reuses the production timing generator but deliberately changes the
capture procedure: TIM4 acquisition interrupts are suppressed, ADC DMA is
extended, and digital polling adds CPU/bus load. It is a diagnostic acquisition,
not a certification of normal continuous-stream throughput. The master/SH/ICG
outputs continue running between captures. Most modes restart at 10 us
integration; **trial 100 us exposure** uses 100 us. Original ICG timing is retained
by default. The separately labeled
**trial ICG 8 us** modes shorten the ICG-low pulse from 612 us to 8 us, giving a
nominal 1.5 us between SH falling and ICG rising. The 7992 us high interval covers
the 7388 us detector line. This is an experimental timing comparison, not a
proof of correct sensor-pin signals. The corrected timing is now also implemented
in the separately built production image.

`exposed` / `exposedoverview` combine the 8 us ICG pulse with 100 us integration.
They are useful for comparing optical contrast at reduced illumination. In the
2026-11-05 measurements, the 100 us trial recovered a distinct leading optical
transition while the corrected 10 us response was close to the dark baseline.
See the local measurement report at `../.scratch/ccd-fast/findings.md`.

At the current 96 MHz system clock, ADC1 runs at 24 MHz. Fast capture uses a
3-cycle (125 ns) sample time and a 72-CPU-cycle trigger interval. The 12-bit
conversion plus trigger-latency budget is 69 CPU cycles. This respects the
external-trigger timing in [ST DS10314 Rev 8, table 65](https://www.st.com/resource/en/datasheet/stm32f411ce.pdf).
The headline 2.4 MS/s ADC rating is not an achievable timer-triggered 12-bit
rate with this clock tree. Fast sampling needs a sufficiently low-impedance
analog source; it is a diagnostic timing view, not automatically better amplitude
accuracy. The slow mode retains the longer 15-cycle aperture for comparison.

DMA completion stops ADC triggering at IRQ entry. ADC overrun interrupts and DMA
errors invalidate a capture. DWT completion time is compared with the expected
trigger count to catch gross missing-trigger errors. A bounded ISR allowance
does not establish that every individual sampling aperture occurred as projected.

## Reference and validation

The reference is [Toshiba TCD1304DG datasheet, Rev. 1.5, 2026-05-20](https://toshiba.semicon-storage.com/info/docget.jsp?did=13709&prodName=TCD1304DG),
especially the clock characteristics and timing charts on printed pages 5-8.
`scope_validate.py` identifies the reference and basis beside each result.

- t1: SH falling edge to ICG rising edge, minimum 1 us (typical 5 us).
- t2: ICG falling edge to SH rising edge, 0.1-1 us.
- t3: SH high width, minimum 1 us; electronic-shutter width remains constant.
- t4: master-clock phase at ICG rising edge; sensor-pin confirmation remains
  **UNVERIFIED** because driver propagation and voltage thresholds are absent.
- The 3648 effective samples follow 32 leading samples and precede 14 trailing
  samples. The overlay uses that nominal geometry; it does not identify physical
  photosites from arbitrary illumination.

**PASS** applies to the stated observation and uncertainty. **FAIL** indicates
an observed condition outside the check. **UNVERIFIED** means the capture lacks
the resolution, edges, or physical observation needed for a conclusion. A
minimum-width measurement at the exact limit can therefore remain unverified.
The aggregate sensor result remains unverified without sensor-pin measurements.

Zoom sampling records 6144 actual timestamped GPIO observations (about 198 ns on
the tested board); overview sampling targets 1.75 us and permits interrupt-induced gaps.
Overview cannot measure a 2 MHz clock without aliasing. Clock frequency is fit
over many edges to avoid a bias from quantized individual periods. All times
share the MCU clock reference; external clock accuracy is not independently tested.

## Build, flash, recover

Use Python 3.12+ with `requirements.txt`. The existing `PythonGUI/.venv` contains
the needed packages on this workstation. ARM GCC and STM32CubeProgrammer are
autodetected from installed CubeIDE tools under `C:/ST`.

From the repository root:

```powershell
.\PythonGUI\.venv\Scripts\python.exe Spectrometer-Scope\build.py
.\PythonGUI\.venv\Scripts\python.exe Spectrometer-Scope\test_scope.py -v
.\PythonGUI\.venv\Scripts\python.exe Spectrometer-Scope\flash.py flash --serial YOUR_STLINK_SERIAL
```

`flash.py` checks the target device ID, saves a full 512 KB recovery image with a
SHA-256 record, and then downloads and verifies the scope image. A new backup
has a unique filename for each flash. Restore a previous image with:

```powershell
.\PythonGUI\.venv\Scripts\python.exe Spectrometer-Scope\flash.py restore --serial YOUR_STLINK_SERIAL --backup PATH_TO_ORIGINAL_BACKUP.bin
```

The firmware identity and dependencies are recorded in `build/manifest.json`.
No mass erase or option-byte writes are used by the diagnostic flash command.
The production GUI expects CCD1 packets and cannot acquire while CSCP scope
firmware is installed. Restore the original image before returning to that GUI.

## Desktop scope

Close/disconnect any other program using the COM port, then run:

```powershell
Spectrometer-Scope\run_scope.bat --port COM3
```

Choose the acquisition mode, then **Capture**. Fast modes record the entire analog
frame while observing a short logic window around ICG. Overview modes observe a
complete logic cycle at lower digital resolution. The trial ICG profile is clearly
separate from the original timing. The view buttons select frame start, ICG rising
edge, frame end, master clock, or a detected raw-video step.
**Leading pixels** isolates the nominal leading regions; **Auto video** scales
only the visible time window. Local leading half-drop and trailing half-return
markers locate voltage features without assigning them a physical pixel ID.
Click a plot to inspect a time and nearest ADC sample. **Repeat** repeats the selected
acquisition; the mouse wheel zooms the time axis around the pointer, and
**Auto video** expands small analog variations. **Save PNG** exports the current view. Each real acquisition also
saves a `.cscp` packet, JSON findings, and raw ADC CSV in `captures/`.

In Full view, a clock trace ends where observation ends; the remaining interval
is blank. It is never extended with an idealized timer waveform. The nominal
pixel overlay and ADC time axis are projections, explicitly labeled in the view.
The nominal 16 dummy / 13 shielded / 3 buffer regions are referenced to ICG rise;
this reference is an unverified hypothesis, not a detected pixel boundary. A
large ICG-correlated voltage step alone is insufficient to identify dummy pixels.

For an offline capture or clearly marked simulation preview:

```powershell
Spectrometer-Scope\run_scope.bat --open PATH_TO_CAPTURE.cscp
Spectrometer-Scope\run_scope.bat --demo
```

## Command-line operation

```powershell
.\PythonGUI\.venv\Scripts\python.exe Spectrometer-Scope\scope.py capture --port COM3 --mode fast
.\PythonGUI\.venv\Scripts\python.exe Spectrometer-Scope\scope.py capture --port COM3 --mode corrected
.\PythonGUI\.venv\Scripts\python.exe Spectrometer-Scope\scope.py capture --port COM3 --mode exposed
.\PythonGUI\.venv\Scripts\python.exe Spectrometer-Scope\scope.py capture --port COM3 --mode slow
.\PythonGUI\.venv\Scripts\python.exe Spectrometer-Scope\scope.py capture --port COM3 --mode fastoverview
.\PythonGUI\.venv\Scripts\python.exe Spectrometer-Scope\scope.py inspect PATH_TO_CAPTURE.cscp --plot trace.png
```

Acquisition/inspection exits 1 when timing checks fail, while preserving the
capture and report. A capture passes USB integrity only after bounded header,
payload-length, CRC32, and timestamp checks succeed. The CRC covers the header
and both payloads. CSCP v2 adds bounded ADC settings, signed start offset, timer
readback and DMA completion timestamps. Capture IDs count requested acquisitions,
not 125 Hz frame IDs. `hardware_check.py` exercises all primary comparison modes.

## Sensor-pin verification boundary

Toshiba's top-view pinout identifies ICG at pin 3, master clock at pin 4, SH at
pin 5, OS at pin 21, and ground at pin 22. Verify the package orientation against
the manufacturer's diagram before probing. Some older repository prose uses a
different pin table and must not be used to identify these sensor pins.

This version does not configure spare pins as sensor-loopback inputs. A genuine
sensor-side timing measurement requires an external scope/logic analyzer or a
separately implemented, voltage-compatible input adapter. Do not connect a
driver-board signal above the MCU input rating directly to a spare pin. The
software cannot measure detector-pin voltage, edge slew, driver delays, or t4
phase margin from the current connections.
