Inputs and Outputs
==================

Inputs
------

.. list-table::
   :header-rows: 1

   * - Raw ADC frame ``R_p``
     - USB ``CCD1`` payload decoded by the host
     - One raw count per sample is kept unchanged for state, CSV, and HDF5.

   * - ``bias_capture_frame_count``
     - Calibration Manager UI and ``CalibrationConfig``
     - Sets how many recent buffered covered frames are averaged when capturing ``B_p``.

   * - ``bias_counts``
     - ``CalibrationConfig``
     - Stored master-bias vector ``B_p``. If empty, no stored bias vector is removed.

   * - ``apply_dark_subtraction``
     - Calibration Manager UI and ``CalibrationConfig``
     - Enables frame-dark estimation and optional stored dark-vector use.

   * - ``dark_offset_counts``
     - ``CalibrationConfig``
     - Stored per-pixel dark vector ``D_p``. If empty, only ``beta_f`` is applied when dark subtraction is enabled.

   * - ``adc_resolution_bits`` and ``adc_reference_volts``
     - ``DeviceConfig``
     - Provide full-scale count and volts conversion after additive correction.

Outputs
-------

.. list-table::
   :header-rows: 1

   * - ``processed_adc_count``
     - Live frame state, CSV, dense HDF5
     - Light-tracking counts after additive and multiplicative correction.

   * - ``frame_dark_reference_count``
     - Live frame state, CSV, dense HDF5
     - The scalar ``beta_f`` estimated for that frame.

   * - ``automatic_dark_bias_applied``
     - Dense HDF5 only
     - The stored additive vector ``B_p + D_p`` recorded per pixel for export traceability.

   * - ``volts``
     - CSV and dense HDF5
     - Light-tracking counts converted with the configured ADC reference.

   * - ``processed_intensity``
     - Live display, CSV, dense HDF5
     - Final normalized display/export intensity after all later stages.