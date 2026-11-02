USB Transport and Verification
==============================

The USB Transport and Verification subsystem defines the wire protocol serialization, USB Virtual COM Port (CDC) transmission pipeline, timing reference calibrations, and requirements traceability matrix for the embedded spectrometer.

.. _uuid-b3a974be-b4e0-4d51-9a8c-77075869dbdd:

Subsystem Role & Responsibilities
---------------------------------

UUID: :ref:`B3A974BE-B4E0-4D51-9A8C-77075869DBDD <uuid-b3a974be-b4e0-4d51-9a8c-77075869dbdd>`

This subsystem guarantees robust, high-bandwidth data delivery and rigorous quality verification:

* **USB Packet Serialization:** Encapsulates 16-bit raw ADC count arrays into binary frame packets with a standardized 28-byte little-endian header (magic ``CCD1``, protocol version 2).
* **High-Rate Transport Delivery:** Streams 7416-byte frames over USB Full-Speed CDC at rates up to 125 Hz (7.42 Mbps) with timeout protection and non-blocking endpoint management.
* **Timing & Geometry Calibration:** Validates hardware driving clock tolerances and pixel boundary alignment using laboratory oscilloscope probing and dark-baseline qualification.
* **Traceability & Test Verification:** Provides an exhaustive traceability matrix linking embedded engineering requirements to firmware implementations and automated regression suites.

.. _uuid-d67a3431-793f-41df-bb60-64376a6ea735:

Subsystem Sections
------------------

UUID: :ref:`D67A3431-793F-41DF-BB60-64376A6EA735 <uuid-d67a3431-793f-41df-bb60-64376a6ea735>`

.. list-table::
   :header-rows: 1

   * - Section
     - Core Engineering Responsibilities
   * - :doc:`usb_cdc_stream_and_packetization`
     - USB CDC ACM endpoint configuration, 28-byte binary frame packet structure, throughput budgeting, and ASCII telemetry interleaving.
   * - :doc:`timing_and_frame_calibration`
     - Hardware oscilloscope timing checks (fM, SH, ICG) and optical black pixel geometry verification.
   * - :doc:`firmware_validation_and_traceability`
     - Automated ARM schedule emulator tests, bench inspector tooling, and full embedded requirements traceability matrix.

.. toctree::
   :maxdepth: 1

   usb_cdc_stream_and_packetization
   timing_and_frame_calibration
   firmware_validation_and_traceability
