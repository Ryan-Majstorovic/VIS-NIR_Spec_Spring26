Inputs and Outputs
==================

Calibration Inputs
------------------

.. list-table::
   :header-rows: 1

   * - Light blocked raw ADC frame ``R_p``
     - Buffered CCD frames with sensor blocked from light
     - Used to compute the master bias vector ``B_p``.

   * - ``bias_capture_frame_count``
     - User-set parameter in Calibration Manager UI
     - Determines how many recent covered frames are averaged for ``B_p`` capture.

   * - Dark reference source (optional)
     - Known dark condition or shielded measurement
     - Used to estimate per-pixel dark offsets ``D_p`` if captured separately.

Calibration Outputs
-------------------

.. list-table::
   :header-rows: 1

   * - Master bias vector ``B_p``
     - Written to ``bias_counts`` in ``CalibrationConfig``
     - Per-pixel average of covered-frame measurements; applied at runtime by the correction pipeline.

   * - Per-pixel dark offsets ``D_p``
     - Written to ``dark_offset_counts`` in ``CalibrationConfig``
     - Optional stored dark vector; loaded from config or pasted into calibration form.
