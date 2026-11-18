Export Initiation and Session Retention
=======================================

This subsystem covers the HDF5 measurement capture and the ZIP handoff for
downstream analysis.

.. _uuid-d6e7f8a9-b0c1-42d3-e4f5-556677889901:

Normative Requirements
----------------------

.. _uuid-d6e7f8a9-b0c1-42d3-e4f5-556677889903:

**Requirement:** The Host PC Export Initiation and Session Retention system
shall write accepted raw 16-bit detector samples, frame identifiers,
nanosecond timestamps, processed measurement arrays, and device-reported
timing to an HDF5 file during binary recording, using a dedicated writer
thread with bounded queuing.

**Rationale:** Binary storage avoids text serialization during acquisition,
and a bounded queue limits memory use under writer backpressure.

.. _uuid-d6e7f8a9-b0c1-42d3-e4f5-556677889904:

**Requirement:** The Host PC Export Initiation and Session Retention system
shall start each recording with the last saved calibration corrections and
shall apply newly saved corrections to subsequently accepted frames. The
system shall retain each calibration revision used by at least one recorded
frame and the revision identifier for each such frame in the
``dense-hdf5-v4`` recording.

**Rationale:** Recording the calibration used at each frame boundary lets
downstream analysis explain changes in processed data. Requiring saved
corrections isolates captured data from temporary changes to the live spectrum.

.. _uuid-7c634068-8e1e-40f6-b145-0952c4e11a8b:

**Requirement:** The Host PC Export Initiation and Session Retention system
shall use the spectrum scaling mode selected when a binary recording starts
to normalize its processed intensity values for the duration of that recording.

**Rationale:** A consistent scaling mode keeps recorded intensities comparable
across frames while the operator adjusts the live view.

.. _uuid-d6e7f8a9-b0c1-42d3-e4f5-556677889902:

**Requirement:** The Host PC Export Initiation and Session Retention system
shall stream the stored measurements from the completed HDF5 recording into
``frames.csv``, with one row per sample and the columns ``frame_index``,
``frame_id``, ``timestamp_ns``, ``sample_index``, ``raw_adc_count``,
``processed_adc_count``, ``volts``, and ``processed_intensity`` in that
order.

**Rationale:** Reading the stored measurements preserves their acquisition
and processing context, and limiting the row to sample and frame data avoids
repeating calibration arrays for each frame.

.. _uuid-d6e7f8a9-b0c1-42d3-e4f5-556677889906:

**Requirement:** The Host PC Export Initiation and Session Retention system
shall write the archive version, detector and ADC settings, sample indices,
and the saved calibration settings, wavelength mapping, and correction
vectors for each used revision to ``calibration.json``. The system shall
write separate calibration and timing ranges with zero-based inclusive start
and exclusive end frame indices. Calibration ranges shall identify the
revision and whether stored dark calibration was applied. Timing ranges
shall report the recorded integration time and timing profile identifier
and shall represent unavailable timing values as JSON ``null``.

**Rationale:** Each range can be joined to the CSV even if the device frame
counter wraps or skips values. Separate ranges keep timing changes and
calibration changes independently traceable.

.. _uuid-d6e7f8a9-b0c1-42d3-e4f5-556677889905:

**Requirement:** The Host PC Export Initiation and Session Retention system
shall create a ZIP containing exactly ``frames.csv`` and
``calibration.json`` at the path the operator confirms in the Windows Save As
dialog when exporting a completed recording. The
system shall perform conversion on a worker, accept one export at a time,
publish the archive only after both entries are complete, and report the
path or failure to the operator.

**Rationale:** Choosing a destination lets operators save each ZIP with the
related experiment files. A worker keeps the controls responsive, and
publishing only a complete archive preserves the capture and any prior
successful archive if conversion fails.

.. _uuid-d6e7f8a9-b0c1-42d3-e4f5-556677889907:

**Requirement:** The Host PC Export Initiation and Session Retention system
shall read dense HDF5 v1 through v3 recordings using the stored recording
calibration as one revision and shall expose the same frame CSV schema
through the command-line converter.

**Rationale:** A stable export schema lets downstream tools process retained
captures across HDF5 format versions.

.. _uuid-d6e7f8a9-b0c1-42d3-e4f5-556677889908:

**Requirement:** The Host PC Operator Application shall show a whole-number
export percentage in the status bar based on the frames written to the CSV
and shall reserve completion until the ZIP is published.

**Rationale:** Frame-based progress gives the operator feedback during long
exports and keeps completion tied to the availability of the ZIP.

Verification
------------

* Export a capture containing a saved calibration change and a timing change
  on different frames. Verify the ranges against the stored frame indices and
  compare CSV measurements with the HDF5 arrays.
* Export an older capture and verify that missing timing is reported as JSON
  ``null``.
* Induce an export failure and verify that the HDF5 source and any previously
  completed ZIP are preserved.
* Cancel the Save As dialog and verify that no ZIP is created. Repeat and
  confirm a different folder and filename, then verify the ZIP at that path.
* Export a multi-frame recording and verify that the percentage advances as
  frames are written and that the completion message follows publication.
