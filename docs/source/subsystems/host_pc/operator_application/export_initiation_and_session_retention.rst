Export Initiation and Session Retention
=======================================

The Export Initiation and Session Retention system provides comprehensive data export and persistent storage for spectrometer measurements. It implements a dual-mode retention architecture supporting lightweight in-memory CSV export for interactive analysis alongside high-speed Dense Binary Capture directly to disk for long-duration 125 Hz measurement campaigns.

.. _uuid-d6e7f8a9-b0c1-42d3-e4f5-556677889901:

Subsystem Role & Dual-Mode Architecture
---------------------------------------

UUID: :ref:`D6E7F8A9-B0C1-42D3-E4F5-556677889901 <uuid-d6e7f8a9-b0c1-42d3-e4f5-556677889901>`

At 125 Hz, streaming 3694 samples per frame produces 461,750 samples per second. Real-time ASCII CSV serialization of full frames during live acquisition causes memory exhaustion and thread backpressure. To solve this, the retention architecture provides two distinct operational paths:

1. **In-Memory Rolling Session CSV Export:** Designed for quick captures, lab inspection, and small datasets (:math:`\le 500` frames). Exports the active in-memory frame buffer directly to a 14-column CSV file upon user request.
2. **Dense Binary Capture & Offline Post-Processing:** Designed for sustained, long-duration measurement campaigns at full 125 Hz throughput:
   * **Direct Binary Recording:** Streams raw 16-bit counts and nanosecond timestamps directly to disk (using chunked binary or HDF5) on a dedicated I/O thread.
   * **Static Manifest Retention:** Saves instrument calibration state, wavelength mapping, and geometry parameters in a co-located ``manifest.json`` file at recording start.
   * **Offline CSV Conversion:** Post-processes recorded binary files into calibrated CSV datasets after acquisition is completed, avoiding real-time CPU contention.

Inputs and Outputs
------------------

.. list-table::
   :header-rows: 1

   * - Flow
     - Name
     - Structure / Type
     - Description
   * - **Input**
     - Buffered Session Frames
     - ``deque[SpectrumFrame]``
     - In-memory frames retained by ``SessionManager``.
   * - **Input**
     - Raw Binary Stream
     - Raw Packet Bytes
     - Incoming ``BinaryFramePacket`` stream during dense recording.
   * - **Output**
     - Session CSV Export
     - File (``.csv``)
     - 14-column CSV containing raw counts, calibrated intensities, wavelengths, and volts.
   * - **Output**
     - Dense Binary Recording
     - File (``.bin`` / ``.h5``)
     - High-speed raw binary recording file with nanosecond timestamps.
   * - **Output**
     - Recording Manifest
     - File (``.json``)
     - Static calibration parameters co-registered with the binary capture.

Normative Requirements
----------------------

.. _uuid-d6e7f8a9-b0c1-42d3-e4f5-556677889902:

**Requirement:** The Host PC Export Initiation and Session Retention system shall serialize in-memory session frames to CSV format containing exactly the 14 aligned data columns: ``frame_id``, ``timestamp``, ``source``, ``expected_sample_count``, ``effective_start_index``, ``effective_sample_count``, ``frame_flags``, ``sample_index``, ``wavelength_nm``, ``raw_adc_count``, ``processed_adc_count``, ``frame_dark_reference_count``, ``volts``, and ``processed_intensity``.

   **Rationale:** Standardizing the 14-column export format ensures full traceability between the original raw hardware counts and every derived physical quantity (volts, calibrated counts, wavelength).

.. _uuid-d6e7f8a9-b0c1-42d3-e4f5-556677889903:

**Requirement:** The Host PC Export Initiation and Session Retention system shall provide a Dense Binary Recorder that writes raw 16-bit sample arrays, 32-bit frame counters, and 64-bit nanosecond timestamps directly to disk on a dedicated writer thread with bounded queuing.

   **Rationale:** Direct binary disk streaming bypasses floating-point string serialization during active capture, guaranteeing sustained 125 Hz recording without queue overflows or dropped frames.

.. _uuid-d6e7f8a9-b0c1-42d3-e4f5-556677889904:

**Requirement:** The Host PC Export Initiation and Session Retention system shall write a companion ``manifest.json`` file containing active wavelength polynomial coefficients, QE reference points, intensity factors, and detector geometry at the start of every binary recording.

   **Rationale:** Co-registering static calibration state with the raw binary dataset ensures that offline processors can accurately reconstruct calibrated spectra even if application settings are later modified.

.. _uuid-d6e7f8a9-b0c1-42d3-e4f5-556677889905:

**Requirement:** The Host PC Export Initiation and Session Retention system shall provide an offline post-processor that parses recorded binary files and generates calibrated CSV datasets matching the standard data model.

   **Rationale:** Decoupling calibration math and CSV generation from the live capture loop allows high-throughput recording without sacrificing comprehensive CSV post-analysis.

Export Data Schemas
-------------------

1. **In-Memory Session CSV Schema (14 Columns):**
   * ``frame_id``, ``timestamp``, ``source``, ``expected_sample_count``, ``effective_start_index``, ``effective_sample_count``, ``frame_flags``
   * ``sample_index``, ``wavelength_nm``, ``raw_adc_count``, ``processed_adc_count``, ``frame_dark_reference_count``, ``volts``, ``processed_intensity``

2. **Dense Binary Recording Record Layout:**
   * Header: Format version string (``dense-hdf5-v1`` or chunked binary).
   * Frame Record: ``frame_id`` (uint32), ``timestamp_ns`` (int64), followed by :math:`N_{\text{samples}}` unsigned 16-bit integers (``uint16``).
   * Companion Manifest: Sample indices, wavelength array, QE factors, intensity correction factors, and device geometry.

Verification & Testing
----------------------

* **CSV Column Alignment Check:** Export 10 frames of 3694 samples; verify that the output CSV contains exactly 36,940 data rows (plus header) and that no columns contain NaN or null values.
* **Dense Binary Zero-Drop Test:** Record a continuous 125 Hz stream for 60 seconds (7,500 frames) using ``DenseBinaryRecorder``; verify that all 7,500 frames are present on disk with zero dropped sequence IDs.
* **Offline CSV Conversion Check:** Execute ``DenseFrameProcessor`` on a recorded binary file and verify that the derived CSV intensities and wavelengths match live export outputs within floating-point epsilon (:math:`10^{-6}`).
