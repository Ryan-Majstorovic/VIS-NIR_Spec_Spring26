Inputs and Outputs
==================

Bad-Pixel Masking Inputs
------------------------

.. list-table::
   :header-rows: 1

   * - Bias/dark-corrected ADC count array
     - Output from adc_extraction stage (or bad_pixel_masking of previous frame for temporal detection)
     - numpy array of per-pixel values with shape ``(sample_count,)``. Used as input for dead/stuck/saturation classification.

   * - ``CalibrationConfig.bad_pixel_indices``
     - Stored calibration parameter
     - List of integer pixel indices that are unconditionally masked due to factory-calibrated defects.

   * - Sliding window buffer (np.ndarray)
     - Rolling frame history maintained in pipeline state
     - Shape ``(dead_pixel_window_size, sample_count)``. Holds recent frames for temporal dead-pixel and stuck-pixel detection.

Bad-Pixel Masking Outputs
-------------------------

.. list-table::
   :header-rows: 1

   * - Per-pixel validity mask (np.ndarray of bool)
     - Passed to wavelength mapping, PRNU correction, QE correction, and display stages
     - Boolean array with shape ``(sample_count,)``. True indicates a valid pixel; False indicates a masked (bad/saturated/dead/stuck) pixel.

   * - ``mask_statistics`` dict
     - Pipeline telemetry output
     - Contains counts of total pixels, valid pixels, dead pixels detected, stuck pixels detected, saturation pixels detected, and calibration-defined bad pixel count.

   * - Updated sliding window buffer
     - Internal pipeline state update
     - New frame appended; oldest row evicted to maintain ``dead_pixel_window_size`` depth.