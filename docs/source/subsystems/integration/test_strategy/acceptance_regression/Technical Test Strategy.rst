Technical Test Strategy
=======================

UUID: ``4D2E2C6E-7569-4558-ABEA-F4782F0C2AF3``

Testing should progress from isolated checks to full instrument
characterization:

* Unit tests for host parser, calibration math, export columns, and config
  defaults.
* Firmware checks for timer configuration, ADC/DMA capture, frame buffering, and
  USB packet generation.
* Interface tests for CCD-driver, driver-MCU, MCU-host, and calibration-output
  boundaries.
* Integration tests using known byte streams and known optical inputs.
* System tests for wavelength coverage, FWHM, SNR, linearity, repeatability,
  stray light, and reference comparison.
* Regression tests whenever frame geometry, packet format, calibration ordering,
  or optical alignment changes.

Acceptance evidence should cite the UUIDs in ``traceability.rst`` and include
raw data paths, config versions, test conditions, and result summaries.



