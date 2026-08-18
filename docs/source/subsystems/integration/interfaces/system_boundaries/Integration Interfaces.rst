Integration Interfaces
======================

UUID: ``62A0D29F-0C9F-4B01-A8E8-31FE44B01500``

Important interfaces are:

.. list-table::
   :header-rows: 1

   * - Interface
     - Data / Signal
     - Validation
   * - Optical input to CCD
     - Focused wavelength-dispersed spectrum.
     - Wavelength coverage, FWHM, and stray-light tests.
   * - CCD to driver board
     - fM, SH, ICG, analog CCD output, power.
     - Continuity, oscilloscope timing, output waveform.
   * - Driver board to STM32
     - ADC input and generated timing signals.
     - Signal-level checks and ADC capture validation.
   * - STM32 to host
     - USB CDC text and ``CCD1`` binary frames.
     - Parser tests, COM inspector, GUI connection tests.
   * - Calibration software
     - Raw samples, correction configs, derived wavelengths and intensities.
     - Known pattern tests and reference-source calibration data.



