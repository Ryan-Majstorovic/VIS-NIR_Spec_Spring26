Export Procedure
================

UUID: ``I5N6T7S8-N9O0-1234-FLDA-TS5678901234``

This page documents the step-by-step procedure for applying intensity normalization during export workflows. It covers normalization-specific operations only; upstream stages (bias subtraction, dark offset, wavelength mapping, PRNU/flat-field, QE correction) are documented in their respective pages.

CSV Export via SpectrumBuilder
------------------------------

When ``SpectrumBuilder.build_export_columns()`` is called, the normalization stage executes these steps:

1. **Retrieve corrected counts**: The fully corrected light counts (output of QE stage) and saturation reference frame are passed from ``_apply_multiplicative_corrections``.

2. **Select normalization mode**: Read ``display_normalization_mode`` from :class:`~backend.models.config.CalibrationConfig`:

   * ``"peak"`` mode: compute divisor as the peak value of corrected counts for this frame.
   * ``"absolute_saturation"`` mode: use the pre-computed saturation reference peak.

3. **Compute normalization divisor**:

   * Peak mode: ``divisor = max(max(corrected_counts), 1e-9)``
   * Absolute mode: ``divisor = max(max(saturation_reference), 1e-9)``

4. **Normalize and clip**: Divide each pixel's corrected count by the divisor, then clip to valid display bounds [0, 1]:

   .. code-block:: python

      normalized_intensity = np.clip(corrected_counts / divisor, 0.0, 1.0)

5. **Return columns**: The method returns ``(normalized_intensity, wavelengths, volts, corrected_counts, frame_dark_level)`` to the CSV export caller. Each row written to CSV contains the per-pixel wavelength, raw ADC count, processed count, dark reference, volts, and normalized intensity.

Dense HDF5 Recording via DenseFrameProcessor
--------------------------------------------

When dense binary recording is active, normalization-specific operations:

1. **Per-frame computation**: Each ``DenseFrameProcessor.build_record()`` call:
   a. Computes light counts from raw ADC via inverted CCD polarity logic (upstream stages handled before normalization).
   b. Multiplies by the pre-computed correction factor (flat-field * QE, already applied before normalization).
   c. Reads ``display_normalization_mode`` from config to select divisor source.
   d. Normalizes and clips to [0, 1] range.

2. **HDF5 dataset append**: The per-frame normalized intensity array is appended to ``/frame/intensity [P]`` during the worker thread flush cycle. Each frame's data chunk size matches ``chunk_frames`` (default 128 frames).

HDF5-to-CSV Export via export_hdf5_to_csv
-----------------------------------------

The :func:`export_hdf5_to_csv` function reads per-frame normalized intensity from ``/frame/intensity [P]`` and writes per-pixel CSV rows containing: frame_id, timestamp_ns, sample_index, wavelength_nm, raw_adc_count, processed_adc_count, frame_dark_reference_count, automatic_dark_bias_applied, correction_factor_applied, volts, and processed_intensity. No on-the-fly normalization is needed during export because normalized intensity values are pre-computed and stored as per-frame datasets.