PRNU Correction (Intensity/Gain Normalization)
===============================================

UUID: ``D6E9F850-7B0C-4F14-C324-5I6D9F27G03H``

The PRNU (Photo-Response Non-Uniformity) correction stage applies per-pixel multiplicative gain factors to compensate for pixel-to-pixel sensitivity variations across the TCD1304DG linear CCD sensor. This stage consumes the ``CalibrationConfig.intensity_correction`` calibration curve and applies it element-wise or via sample-index lookup using ``backend/processing/intensity_correction.py::apply_intensity_correction``.

Overview
--------

The system performs these operations on every frame after wavelength mapping:

1. **Gain factor loading.** Load the per-pixel intensity correction factors from ``CalibrationConfig.intensity_correction`` stored in the calibration manager. These factors are typically derived from PRNU calibration measurements or QE-corrected reference spectra.

2. **Index-based lookup.** When ``sample_indices`` are provided, construct a lookup array via list comprehension: ``[factors[index] if 0 <= index < len(factors) else 1.0 for index in sample_indices]``, mapping potentially sparse calibration indices to the active pixel positions.

3. **Direct element-wise multiplication.** When no sample indices are provided, apply factors directly: ``corrected[:limit] *= factors[:limit]`` where ``limit = min(len(data), len(factors))``.

4. **QE curve integration.** If ``CalibrationConfig.apply_quantum_efficiency_correction`` is enabled, the QE correction curve is computed from wavelength values via ``build_quantum_efficiency_curve(wavelengths)`` and multiplied into the intensity correction factors before application.

Related Pages
-------------

.. toctree::
   :maxdepth: 1

   inputs_and_outputs
   procedure