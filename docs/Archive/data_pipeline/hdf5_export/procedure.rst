Dense HDF5 and CSV Export Procedure
====================================

UUID: ``H4D5F6G7-H8I9-0123-JKLM-NOPQRSTUVWX``

This page documents the step-by-step procedure for writing spectral data to dense HDF5 files and CSV exports. It covers recorder initialization, per-frame write cycles, worker thread architecture, and CSV export workflows.

Dense Binary Recording Initialization
-------------------------------------

When ``DenseBinaryRecorder.start()`` is called from the UI or backend API:

1. **HDF5 file creation**: A new HDF5 file is created at the configured path with a timestamped filename. The root group contains metadata attributes for recording start time, sample count, and pipeline configuration snapshot.

2. **Static dataset allocation**: :class:`DenseFrameProcessor.__init__` computes all calibration vectors (wavelengths, QE curve, system response, combined correction factor) once and allocates static HDF5 datasets:
   a. ``/correction/wavelength [P]``: Per-pixel wavelength array from polynomial mapping.
   b. ``/correction/qe_correction [P]``: Per-pixel QE correction factor via :func:`_build_qe_correction`.
   c. ``/correction/correction_factor_applied [P]``: Combined flat-field × QE product.

3. **Chunked dataset creation**: Per-frame datasets are created with chunked compression for efficient append operations:
   a. ``/frame/volts [F][P]``: Per-frame voltage values (float32).
   b. ``/frame/intensity [F][P]``: Per-frame normalized intensity (float32).
   c. ``/frame/corrected [F][P]``: Per-frame corrected light counts (float32).
   d. ``/dark/frame_dark [F]``: Per-frame dark reference values (float32).

4. **Worker thread launch**: A dedicated background worker thread begins processing frames from an internal queue, ensuring HDF5 I/O does not block the transport layer's packet reception.

Per-Frame Write Cycle
---------------------

Each frame processed by :class:`DenseFrameProcessor.build_record()` executes:

1. **Volts computation**: Raw ADC counts are converted to volts using the ADC reference voltage and resolution bits (the only calculation performed by export).

2. **Data assembly**: Pre-computed values from upstream stages are assembled into the per-frame record:
   a. Wavelengths from static calibration vector.
   b. Corrected counts from QE stage output.
   c. Normalized intensity from normalization stage output.
   d. Dark reference from bias/dark correction stage output.

3. **HDF5 append**: The per-frame data chunk is appended to the corresponding HDF5 datasets during the worker thread flush cycle. Each frame's data size matches ``chunk_frames`` (default 128 frames) for optimal I/O performance.

4. **Queue acknowledgment**: The frame counter is marked as written, allowing the transport layer to discard processed packets from memory.

CSV Export via SpectrumBuilder
------------------------------

When CSV export is triggered via ``SpectrumBuilder.build_export_columns()``:

1. **Wavelength retrieval**: The wavelength array is retrieved from an internal cache keyed on sample count and coefficient tuple, or computed fresh via :func:`~backend.processing.wavelength_map.indices_to_wavelengths` if not cached.

2. **Volts conversion**: Raw ADC counts are converted to volts using the ADC reference voltage and resolution bits.

3. **Column assembly**: The method returns a tuple of ``(wavelengths, adc_counts, corrected_counts, frame_dark_level, volts, normalized_intensity)`` for CSV writing. Each row written to CSV contains per-pixel wavelength, raw ADC count, processed count, dark reference, volts, and normalized intensity.

4. **File writing**: The CSV file is written with headers: ``frame_id``, ``timestamp_ns``, ``sample_index``, ``wavelength_nm``, ``raw_adc_count``, ``processed_adc_count``, ``frame_dark_reference_count``, ``automatic_dark_bias_applied``, ``correction_factor_applied``, ``volts``, and ``processed_intensity``.

HDF5-to-CSV Export via export_hdf5_to_csv
-----------------------------------------

The :func:`export_hdf5_to_csv` function reads pre-written HDF5 datasets and writes per-pixel CSV rows:

1. **Dataset reading**: Static correction factors are read from ``/correction/correction_factor_applied [P]``. Per-frame data is read from ``/frame/intensity [P]``, ``/frame/volts [P]``, etc.

2. **Row assembly**: Each frame's data is assembled into CSV rows containing: frame_id, timestamp_ns, sample_index, wavelength_nm, raw_adc_count, processed_adc_count, frame_dark_reference_count, automatic_dark_bias_applied, correction_factor_applied, volts, and processed_intensity.

3. **File writing**: The CSV file is written with the same column structure as direct SpectrumBuilder export, enabling consistent downstream analysis regardless of recording format.