HDF5 and CSV Export Procedures
===============================

UUID: ``H5D6F7G8-H9I0-1234-JKLM-NOPQRSTUVWX``

This page documents the export procedures for converting processed spectral data from in-memory pipeline outputs to persistent file formats. It covers the HDF5-to-CSV conversion workflow and direct CSV export triggers.

HDF5-to-CSV Export via export_hdf5_to_csv
-----------------------------------------

The :func:`export_hdf5_to_csv` function converts dense HDF5 recordings to CSV format for spreadsheet analysis:

1. **File validation**: The function verifies the HDF5 file exists, is readable, and contains valid spectral datasets at expected paths (``/frame/intensity``, ``/correction/wavelength``, etc.).

2. **Static dataset reading**: Correction factors are read from static HDF5 datasets:
   a. ``/correction/correction_factor_applied [P]``: Combined flat-field × QE factor.
   b. ``/correction/qe_correction [P]``: Per-pixel QE correction factor.
   c. ``/correction/wavelength [P]``: Per-pixel wavelength array.

3. **Per-frame dataset reading**: Frame-level data is read from chunked HDF5 datasets:
   a. ``/frame/intensity [F][P]``: Normalized intensity values.
   b. ``/frame/volts [F][P]``: Voltage values.
   c. ``/dark/frame_dark [F]``: Frame-wise dark reference values.

4. **CSV row assembly**: Each frame's data is assembled into CSV rows containing: frame_id, timestamp_ns, sample_index, wavelength_nm, raw_adc_count, processed_adc_count, frame_dark_reference_count, automatic_dark_bias_applied, correction_factor_applied, volts, and processed_intensity.

5. **File writing**: The CSV file is written with headers matching the column names above. Each row represents one pixel in one frame.

Direct CSV Export via SpectrumBuilder
-------------------------------------

When ``SpectrumBuilder.build_export_columns()`` is called (e.g., from UI export button or backend API):

1. **Wavelength cache lookup**: The wavelength array is retrieved from an internal cache keyed on sample count and coefficient tuple. If not cached, it is computed fresh via :func:`~backend.processing.wavelength_map.indices_to_wavelengths`.

2. **Volts conversion**: Raw ADC counts are converted to volts using the ADC reference voltage and resolution bits (the only calculation performed during export).

3. **Column assembly**: The method returns a tuple of ``(wavelengths, adc_counts, corrected_counts, frame_dark_level, volts, normalized_intensity)`` for CSV writing. All values except volts are passed through from upstream pipeline stages without modification.

4. **File writing**: The CSV file is written with headers: ``frame_id``, ``timestamp_ns``, ``sample_index``, ``wavelength_nm``, ``raw_adc_count``, ``processed_adc_count``, ``frame_dark_reference_count``, ``automatic_dark_bias_applied``, ``correction_factor_applied``, ``volts``, and ``processed_intensity``.

Export Metadata
---------------

Both export paths write CSV files with consistent column structures, enabling identical downstream analysis regardless of recording format. The HDF5-to-CSV path includes all per-frame data from dense recordings; the direct SpectrumBuilder path exports only frames that were displayed or manually saved during the session.