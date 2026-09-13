Procedure
=========

The system maps sample indices to wavelength values through the following procedure implemented in ``backend/processing/wavelength_map.py::indices_to_wavelengths``:

1. Convert the input sample indices to a numpy float array: ``indices = np.asarray(sample_indices, dtype=float)``.

2. Check whether coefficients are configured. If ``coefficients`` is empty (falsy), return the raw indices unchanged: ``return indices``. This keeps the display in pixel-index mode when no wavelength calibration has been saved.

3. Initialize a zero-filled output array with the same shape and dtype as indices: ``wavelengths = np.zeros_like(indices, dtype=float)``.

4. Evaluate the polynomial coefficient-by-coefficient using a for loop over enumerate(coefficients):

   For each iteration where ``power`` is the loop index (starting from 0) and ``coefficient`` is the value at that index:

   ``wavelengths += float(coefficient) * np.power(indices, power)``

   This computes: ``wavelengths[i] = Σ(coefficient[power] * indices[i]^power)`` for all pixel positions ``i`` simultaneously using numpy vectorized operations.

5. Return the computed wavelength array to the caller (typically ``SpectrumBuilder._wavelengths_for_sample_count()``).

6. In ``SpectrumBuilder._wavelengths_for_sample_count()``, check the cache key ``(sample_count, tuple(calibration_config.wavelength_coefficients))`` before calling ``indices_to_wavelengths()``. If the cached array exists, return it directly. Otherwise, compute the wavelengths, store them in ``self._cached_wavelengths[cache_key]``, and return the result.

7. Pass the resulting wavelength numpy array to downstream calibration stages: PRNU correction, QE correction (via ``build_quantum_efficiency_curve(wavelengths)``), intensity normalization, display normalization, and export pipelines.