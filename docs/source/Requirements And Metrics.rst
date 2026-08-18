Requirements And Metrics
========================

UUID: ``5E8ED5F1-69FA-4A37-89FE-71060AB22F0A``

The following requirements are limited to technical instrument behavior.

.. list-table::
   :header-rows: 1

   * - Area
     - Target
     - Current Evidence Hook
   * - Wavelength range
     - 400-1000 nm usable coverage.
     - Design document optics requirements and future wavelength-map test data.
   * - Detector geometry
     - TCD1304DG active array with 3648 effective pixels.
     - Firmware frame layout and host default device config.
   * - Spectral resolution
     - About 5 nm FWHM for narrow sources across the operating range.
     - Future optics characterization tests.
   * - Frame acquisition
     - Real-time display and capture; design target above 100 fps, minimum
       acceptance checks at lower subsystem thresholds where documented.
     - Firmware 8 ms ICG period, COM inspector 125 fps check, GUI performance
       diagnostics.
   * - USB transfer
     - Complete binary frame packets over USB CDC with frame IDs and flags.
     - ``CCD1`` protocol in firmware and Python parser.
   * - Calibration
     - Stored bias capture, frame-wise dark reference estimation, optional
       per-pixel dark offsets, pixel-to-wavelength map, flat-field or
       intensity correction, and spectral response correction.
     - Host processing modules, calibration config, and host-PC calibration
       documentation.
   * - Export
     - CSV rows include raw ADC counts, processed counts, wavelengths, volts,
       and processed intensity.
     - ``PythonGUI/backend/storage/export_csv.py``.
   * - Characterization
     - Wavelength accuracy, FWHM, SNR, linearity, repeatability, stray light,
       and reference comparison.
     - CIE 233:2019 and ASTM E275-style test plan entries.

Metrics should be updated only when the corresponding test method and evidence
artifact are available. Early prototype notes can be listed as observations, but
they should not replace measured acceptance results.



