Bad-Pixel / Saturation Masking
===============================

UUID: ``B9C4E630-5F7A-4D92-A102-3G4B7D05E81F``

The bad-pixel and saturation masking stage identifies unreliable sensor outputs and flags them for downstream processing. This stage produces a per-pixel validity mask that is consumed by wavelength mapping, PRNU correction, QE correction, and display normalization stages. The mask allows downstream components to optionally interpolate, hold-last, or zero-out flagged pixel values.

Overview
--------

The system applies the following masking rules to every calibration frame:

1. **Dead pixel detection.** Pixels whose ADC counts remain constant (within ``dead_pixel_threshold`` ADC counts) across a sliding window of ``dead_pixel_window_size`` frames are classified as dead.

2. **Stuck pixel detection.** Pixels whose ADC counts jump by more than ``stuck_pixel_delta_threshold`` between consecutive frames are flagged as stuck or noisy.

3. **Saturation masking.** Pixels whose ADC counts exceed ``saturation_adc_count`` (the linear full-well capacity threshold) are masked to prevent incorrect spectral interpretation.

4. **Calibration-defined bad pixels.** Per-pixel bad-pixel indices stored in ``CalibrationConfig.bad_pixel_indices`` are unconditionally masked.

5. **Mask composition.** The individual masks are combined via logical OR into a single validity mask passed downstream.

Status
------

This stage is not yet implemented in the current desktop application. The calibration configuration schema reserves space for bad-pixel parameters:

* ``bad_pixel_indices`` (list[int]): pre-calibrated known-defect pixel indices.
* ``saturation_adc_count`` (int): ADC count threshold above which pixels are saturated.
* ``dead_pixel_threshold`` (int): maximum allowable variation for dead-pixel classification.
* ``dead_pixel_window_size`` (int): frame window size for dead-pixel detection.
* ``stuck_pixel_delta_threshold`` (int): minimum ADC jump to classify a stuck pixel.

These parameters are consumed by downstream stages once implemented.

Related Pages
-------------

.. toctree::
   :maxdepth: 1

   inputs_and_outputs
   procedure
   calculations