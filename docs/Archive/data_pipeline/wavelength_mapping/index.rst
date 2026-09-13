Wavelength Mapping
==================

UUID: ``C5D8F740-6A9B-4E03-B213-4H5C8E16F92G``

The wavelength mapping stage converts per-pixel array indices from the TCD1304DG linear CCD sensor into physical wavelength values in nanometers. This stage applies a calibrated polynomial transformation defined by ``CalibrationConfig.wavelength_coefficients`` that maps each pixel's position to its corresponding spectral response centre wavelength. The output is a per-pixel wavelength numpy array used by all downstream calibration and display stages.

Overview
--------

The system performs these operations on every frame after bias/dark correction:

1. **Polynomial evaluation.** Load the calibrated polynomial coefficients from ``CalibrationConfig.wavelength_coefficients`` and evaluate ``wavelengths[i] = Σ(coefficient[power] * indices^power)`` for each pixel index using numpy vectorized operations in ``backend/processing/wavelength_map.py::indices_to_wavelengths``.

2. **Coefficient fallback.** If no coefficients are configured (empty list), the function returns the raw sample indices unchanged, keeping the display in pixel-index mode.

3. **Wavelength array caching.** The wavelength array is cached by sample count and coefficient tuple in ``SpectrumBuilder._cached_wavelengths`` to avoid redundant polynomial evaluations during export or repeated processing.

4. **Per-pixel wavelength assignment.** The resulting numpy float64 array is passed to PRNU correction, QE correction, intensity normalization, display normalization, and CSV/HDF5 export stages.

Related Pages
-------------

.. toctree::
   :maxdepth: 1

   inputs_and_outputs
   procedure