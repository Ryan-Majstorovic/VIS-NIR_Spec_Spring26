Host PC System Overview
=======================

.. figure:: /_static/diagrams/host_pc/system-overview.png
   :alt: High-level Host PC system architecture showing the STM32F411 microcontroller USB-C interface, decoupled 125 Hz background processing operations, and 30 FPS operator graphical user interface.
   :width: 85%
   :align: center

   High-level Host PC system architecture and decoupled execution model.

.. _uuid-42e97793-9f90-4eb8-9757-fde4d6527dbc:

System Role
-----------

UUID: :ref:`42E97793-9F90-4EB8-9757-FDE4D6527DBC <uuid-42e97793-9f90-4eb8-9757-fde4d6527dbc>`

The Host PC system manages the host-side software operations for the VIS-NIR spectrometer. It covers USB CDC stream ingestion, frame reconstruction and calibration, the operator application, and HDF5 capture and session archive export.

.. _uuid-90977a32-cb75-4745-b6d0-470f1b5116be:

System Architecture & Decoupled Execution Model
-----------------------------------------------

UUID: :ref:`90977A32-CB75-4745-B6D0-470F1B5116BE <uuid-90977a32-cb75-4745-b6d0-470f1b5116be>`

The Host PC software architecture is decoupled into asynchronous execution layers to guarantee 100% data capture fidelity at 125 Hz without starving the graphical user interface:

1. **Device Ingress & Wire Transport (125 Hz Cadence):** A background serial worker thread reads raw bytes from the USB CDC virtual COM port, separates ASCII diagnostic text from binary frames, and reconstructs 16-bit ADC count arrays from ``CCD1`` packets.
2. **Primary Data Pipeline & Calibration:** Executes master bias subtraction, frame dark baseline tracking, optical inversion to positive light counts, flat-field intensity correction, quantum efficiency (QE) response correction, polynomial wavelength mapping, and voltage scaling.
3. **Core State & Session Coordination:** Maintains thread-safe application snapshots, circular in-memory session buffers, packet sequence gap tracking (missed frame detection), and streaming performance metrics.
4. **Operator Desktop Interface (Decoupled 30 FPS Cadence):** A Kivy-based UI layer rendering real-time 3648-point line spectra, interactive cursor readouts, rolling waterfall spectrograms (compressed to 256 bins), device controls, and calibration management.
5. **Capture and Export:** Full-rate HDF5 capture and post-recording ZIP export of frame measurements and calibration and timing history.

.. _uuid-55f3ab31-2428-4459-a33f-4cc03984fd05:

Subsystem Relationships
-----------------------

UUID: :ref:`55F3AB31-2428-4459-A33F-4CC03984FD05 <uuid-55f3ab31-2428-4459-a33f-4cc03984fd05>`

.. list-table::
   :header-rows: 1

   * - Subsystem
     - Primary Engineering Responsibility
   * - :doc:`Primary Data Pipeline <primary_data_pipeline/index>`
     - Frame qualification, baseline tracking, optical inversion, calibration math, wavelength mapping, and calibrated spectrum record output.
   * - :doc:`Device Control And Acquisition Coordination <device_control_and_acquisition_coordination/index>`
     - Serial connection lifecycle, stream demuxing, sequence gap tracking, 125 Hz stream synchronization, and command protocol dispatch.
   * - :doc:`Operator Application <operator_application/index>`
     - 30 FPS line/waterfall visualization, interactive cursor analysis, user settings, in-memory session retention, and high-speed binary disk recording.

.. _uuid-7e7e9cf8-7577-4dc8-97b7-6730476d1d41:

Integration & Boundary Responsibilities
---------------------------------------

UUID: :ref:`7E7E9CF8-7577-4DC8-97B7-6730476D1D41 <uuid-7e7e9cf8-7577-4dc8-97b7-6730476d1d41>`

The Host PC system interacts with external systems across strictly defined boundaries:

* **Hardware & Sensor Geometry Boundary (Optics / Sensor Hardware):** The physical detector geometry (Toshiba TCD1304DG: 3694 total elements, 32 leading shielded/dummy pixels, 3648 effective active pixels, 14 trailing dummy pixels) is defined by hardware and optical specifications. The Host PC does not define physical sensor geometry; it consumes configured or reported geometry parameters (``effective_start_index = 32``, ``effective_sample_count = 3648``) to slice valid detector data from raw frames.
* **Wire Protocol Boundary (Integration):** The wire framing contract (packet magic ``CCD1``, header fields, payload byte count, byte endianness) is owned by Integration. The Host PC ingests conforming byte streams and validates payload lengths without redefining wire transport rules.
* **Measurement Plane Output:** The Host PC produces fully qualified, calibrated spectrum records and session export datasets for downstream analysis.

Normative System Requirements
-----------------------------

.. _uuid-a1100223-1001-4001-8001-001122334401:

**Requirement:** The Host PC system shall ingest binary measurement frames from the USB CDC transport at the nominal hardware frame rate of 125 Hz while decoupling user interface rendering to a stable cadence of approximately 30 FPS.

   **Rationale:** Decoupling serial packet ingestion from UI rendering prevents canvas redraws from throttling incoming packet processing, ensuring 100% frame capture fidelity and avoiding packet buffer overflows.

.. _uuid-a1100223-1001-4001-8001-001122334402:

**Requirement:** The Host PC system shall preserve raw 16-bit ADC sample counts in their acquired order for every accepted measurement frame, regardless of subsequent calibration, normalization, or visualization transformations.

   **Rationale:** Unaltered raw detector counts maintain traceability to physical detector voltages, enable post-acquisition recalibration, and provide the uncorrupted ground truth required for scientific export.
