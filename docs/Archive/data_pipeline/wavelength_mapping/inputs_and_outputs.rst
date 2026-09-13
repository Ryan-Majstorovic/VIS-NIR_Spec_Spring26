Inputs and Outputs
==================

Wavelength Mapping Inputs
-------------------------

.. list-table::
   :header-rows: 1

   * - Sample indices (range or np.ndarray)
     - adc_extraction stage output frame.sample_count
     - Integer pixel positions passed as ``range(sample_count)`` to ``indices_to_wavelengths()``. Shape ``(sample_count,)`` where sample_count is typically 3648 for the active sensor region.

   * - Wavelength coefficients (list[float])
     - CalibrationConfig.wavelength_coefficients stored in calibration manager
     - Polynomial coefficients loaded via ``self._calibration_manager.config.wavelength_coefficients`` in ``SpectrumBuilder._wavelengths_for_sample_count()``. Coefficients are ordered by polynomial power: coefficient[0] is the constant term, coefficient[1] is the linear term, etc.

   * - Cached wavelength key (tuple)
     - Internal to SpectrumBuilder._cached_wavelengths
     - Composite key ``(sample_count, tuple(wavelength_coefficients))`` used for cache lookup in ``SpectrumBuilder._wavelengths_for_sample_count()``. Prevents redundant polynomial evaluation when sample count and coefficients are unchanged.

Wavelength Mapping Outputs
--------------------------

.. list-table::
   :header-rows: 1

   * - Wavelength array (np.ndarray of float64)
     - Passed to PRNU correction, QE correction, intensity normalization, display, and export stages as ``wavelengths`` parameter
     - Produced by ``indices_to_wavelengths(sample_indices, coefficients)`` in ``backend/processing/wavelength_map.py``. A numpy float64 array with shape ``(sample_count,)`` containing centre wavelength values computed via polynomial evaluation.

   * - Fallback index array (np.ndarray of int/float)
     - Returned when no coefficients are configured
     - If ``coefficients`` is empty, ``indices_to_wavelengths()`` returns the raw sample indices unchanged: ``return indices``. This keeps the display in pixel-index mode until wavelength calibration is saved.

   * - Cached wavelength array (np.ndarray reference)
     - Stored in SpectrumBuilder._cached_wavelengths cache dict
     - After first computation, the wavelength array is stored under key ``(sample_count, coefficient_key)`` for reuse by subsequent export or live-processing calls to ``_wavelengths_for_sample_count()``.