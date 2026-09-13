System Overview
===============

UUID: ``3F2D4CB8-9372-43E9-B29B-70643C4E64C5``

The VIS-NIR spectrometer converts incident light over the target 400-1000 nm
range into calibrated data on a host computer. The technical system is divided
into four coupled areas:

* The optical path accepts light through a slit, collimates it, disperses it
  with a reflective grating, focuses the spectrum, and images it onto the
  TCD1304DG linear CCD.
* The embedded acquisition system drives the CCD timing signals with an
  STM32F411CEU6, samples the analog output with ADC1, fills a DMA frame buffer,
  and streams frames over USB CDC.
* The host-PC application receives mixed text and binary USB CDC data, rebuilds
  ``CCD1`` frame packets, applies calibration, displays live spectra, and
  exports measurement sessions.
* Integration and characterization connect the optical alignment, embedded
  timing, USB transfer, and host-side calibration into one measurement chain.

The current firmware packet geometry is 3694 total samples per frame: 32 leading
dummy samples, 3648 effective CCD pixels, and 14 trailing dummy samples. The
host app preserves raw ADC samples for export and produces processed display
values through the calibration pipeline.

End-to-End Measurement Chain
----------------------------

1. Light enters the slit or fiber-coupled input.
2. The Czerny-Turner optical path disperses first-order wavelengths across the
   CCD active region.
3. The TCD1304DG outputs a sequential analog waveform.
4. The STM32 ADC samples the waveform on timer-triggered conversions.
5. DMA writes one frame into memory.
6. Firmware packages the samples into a ``CCD1`` binary USB CDC frame.
7. The host parser validates the frame header and payload.
8. The host processing path applies dark/bias, wavelength, flat-field, and
   response corrections when configured.
9. The UI displays a line spectrum or rolling spectrogram.
10. CSV export writes raw and derived columns for downstream analysis.



