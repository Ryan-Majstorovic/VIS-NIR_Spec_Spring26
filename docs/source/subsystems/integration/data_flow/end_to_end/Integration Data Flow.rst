Integration Data Flow
=====================

UUID: ``D37D1295-2B68-4EAD-A7A4-A3C29C2993C3``

The integrated data path is:

1. Light enters the slit.
2. Optics disperse and focus the spectrum onto the CCD.
3. CCD analog output is generated during readout.
4. The driver board carries timing, power, and analog signals.
5. STM32 timers drive fM, SH, and ICG.
6. ADC/DMA captures the analog waveform into a frame buffer.
7. Firmware sends ``CCD1`` packets over USB CDC.
8. Host parser reconstructs and validates frames.
9. Processing builds calibrated display/export values.
10. UI displays live data and stores session buffers.
11. Export writes CSV or dense binary artifacts.

Each stage should have at least one interface test before full-system
acceptance testing.



