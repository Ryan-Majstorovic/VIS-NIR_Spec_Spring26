Procedure
=========

The system applies PRNU (intensity/gain) correction through the following procedure implemented in ``backend/processing/intensity_correction.py::apply_intensity_correction``:

1. Convert input values to a numpy float array: ``data = np.asarray(values, dtype=float)``.

2. Check whether correction factors are configured. If ``correction_factors`` is empty (falsy), return ``data.copy()`` unchanged. This preserves pipeline continuity when PRNU calibration has not been applied.

3. Convert correction factors to a numpy float array: ``factors = np.asarray(correction_factors, dtype=float)``.

4. Evaluate the sample_indices branch:

   **Branch A -- Index-based lookup mode (sample_indices is provided):**
   
   Construct a per-pixel lookup array via list comprehension over sample indices:
   
   ``lookup = np.array([factors[index] if 0 <= index < len(factors) else 1.0 for index in sample_indices], dtype=float)``
   
   This maps calibration factors from their native indices to the active pixel positions, defaulting to a multiplicative factor of 1.0 (no correction) when an index falls outside the calibration range. The corrected output is then ``data * lookup``.

   **Branch B -- Direct element-wise mode (sample_indices is None):**
   
   Compute ``limit = min(len(data), len(factors))``. Copy data into a corrected array and apply factors in-place for the overlapping region:
   
   ``corrected = data.copy()``
   
   ``corrected[:limit] *= factors[:limit]``
   
   Return ``corrected``.

5. In ``SpectrumBuilder._build_processed_columns()``, if ``CalibrationConfig.apply_quantum_efficiency_correction`` is enabled, compute the QE curve via ``self._calibration_manager.build_quantum_efficiency_curve(wavelengths)`` before calling intensity correction. The QE curve values are multiplied into the correction factors: combined factors = intensity_correction_factors * qe_curve_values.

6. Return the corrected numpy array to the caller. In ``SpectrumBuilder``, this is returned as part of the tuple ``(corrected_counts, saturation_reference_counts, wavelengths, volts, normalized_counts, frame_dark_level)`` from ``_build_processed_columns()``.