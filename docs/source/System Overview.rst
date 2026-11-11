System Overview
===============

UUID: ``3F2D4CB8-9372-43E9-B29B-70643C4E64C5``

The VIS-NIR spectrometer converts light delivered by fiber into a calibrated
spectrum on a host computer. The client-approved operating band for this stage
is approximately 400 nm to 800 nm, set by the B&W Tek optical bench the
client provided in place of the original 400 nm to 1000 nm custom design. The
system has three subsystems and one verification activity:

* **Optics:** the B&W Tek compact Czerny-Turner bench disperses the light from
  the entrance slit and focuses it onto the TCD1304DG linear CCD.
* **Embedded:** an STM32F411CEU6 drives the CCD timing signals, samples the
  analog output with ADC1 into a DMA frame buffer, and streams ``CCD1``
  frames over USB CDC.
* **Host PC:** the Python application rebuilds frames, applies calibration,
  displays live spectra, and exports CSV sessions.
* **Test and Verification:** compares the calibrated prototype with a
  commercial reference spectrometer using the laser calibration unit and LED
  sources.

Each firmware frame carries 3694 samples: 32 leading dummy samples, 3648
effective CCD pixels, and 14 trailing dummy samples. The Host PC keeps the raw
ADC samples for export alongside the processed values.

End-to-End Measurement Chain
----------------------------

1. A source (calibration unit, LED, or sample light) feeds the SMA fiber,
   joined by an ADASMA sleeve to the M14L01 patch cable.
2. The fiber delivers light to the bench's entrance slit.
3. The Czerny-Turner bench disperses first-order light across the CCD's
   effective pixels.
4. The TCD1304DG outputs a sequential analog waveform.
5. The STM32 ADC samples the waveform on timer-triggered conversions, and DMA
   writes one frame into memory.
6. Firmware packages the frame as a ``CCD1`` binary USB CDC packet.
7. The Host PC validates the packet and applies bias and dark correction,
   the pixel-to-wavelength map, and any configured intensity corrections.
8. The application displays a line spectrum or rolling spectrogram.
9. CSV export writes raw and derived columns for analysis.
