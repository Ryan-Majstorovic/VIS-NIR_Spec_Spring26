Ingress and ADC Reconstruction
==============================

The Ingress and ADC Reconstruction stage is the entry point of the Host PC primary data pipeline. It ingests raw device packets from the transport layer, qualifies frame header integrity, validates payload dimensions, and unpacks ordered raw 16-bit ADC counts without modifying the source data.

.. _uuid-7f8ac58c-1708-486c-af4f-2d690f3ce607:

Subsystem Role & Boundary
-------------------------

UUID: :ref:`7F8AC58C-1708-486C-AF4F-2D690F3CE607 <uuid-7f8ac58c-1708-486c-af4f-2d690f3ce607>`

Ingress operates strictly as a consumer of the Integration-defined wire contract. It does not define packet encodings, serial framing, or sensor physical geometry. It reads the incoming byte buffer, matches the ``CCD1`` protocol format, and makes complete, validated measurement frames available to subsequent pipeline stages.

Inputs and Outputs
------------------

.. list-table::
   :header-rows: 1

   * - Flow
     - Name
     - Structure / Type
     - Description
   * - **Input**
     - Binary Stream Buffer
     - ``bytes`` / byte stream
     - Raw contiguous bytes delivered over USB CDC by the device transport.
   * - **Input**
     - Device Configuration
     - ``DeviceConfig``
     - Expected sample counts (default 3694) and effective pixel ranges (start 32, count 3648).
   * - **Output**
     - Binary Frame Packet
     - ``BinaryFramePacket``
     - Validated packet with frame counter, flags, timestamps, and raw 16-bit ADC count array.
   * - **Output**
     - Ingress Diagnostic
     - Error flag / log event
     - Indication of magic mismatch, size discrepancy, or stream desynchronization.

Normative Requirements
----------------------

.. _uuid-8a67f948-8087-42d0-a37d-1aa34db6d15b:

**Requirement:** The Host PC Ingress and ADC Reconstruction system shall validate that every incoming binary frame packet begins with magic bytes ``b"CCD1"``, protocol version 1, and packet type 1 before parsing payload samples.

   **Rationale:** Protocol header validation prevents unaligned text messages, garbage serial noise, or obsolete protocol versions from being interpreted as valid measurement frames.

.. _uuid-24659d9a-0778-4e53-9580-c80921452d60:

**Requirement:** The Host PC Ingress and ADC Reconstruction system shall verify that the packet payload byte length exactly equals ``sample_count * 2`` and that ``sample_count`` does not exceed 8192 samples before releasing the frame to processing.

   **Rationale:** Enforcing exact 16-bit sample payload sizing prevents memory out-of-bounds indexing, truncated frame processing, and buffer corruption.

.. _uuid-782b5cbe-1220-4f95-add4-4ed377911e35:

**Requirement:** The Host PC Ingress and ADC Reconstruction system shall unpack payload bytes into little-endian unsigned 16-bit integers (``<u2``) and preserve the complete sample array in original acquisition sequence.

   **Rationale:** The STM32 microcontroller transmits ADC counts in 16-bit little-endian format; preserving full acquisition order ensures spatial pixel correlation is maintained for dark baseline and wavelength mapping.

.. _uuid-56aa8564-f48c-49db-b2f2-a98be7bcd7cf:

**Requirement:** The Host PC Ingress and ADC Reconstruction system shall associate each reconstructed frame with a 64-bit nanosecond capture timestamp, the firmware frame counter, and received status flags.

   **Rationale:** Capturing timestamps and hardware frame counters enables missed-frame detection, stream rate calculation, and unambiguous temporal tracking across recording sessions.

Binary Header Layout
--------------------

The incoming binary frame follows the 22-byte little-endian header struct (``<4sBBHIHHHHI``):

.. list-table::
   :header-rows: 1

   * - Field
     - Format
     - Size (Bytes)
     - Meaning
   * - ``magic``
     - ``4s``
     - 4
     - Magic identifier (``b"CCD1"``).
   * - ``version``
     - ``B`` (uint8)
     - 1
     - Protocol version (must be 1).
   * - ``packet_type``
     - ``B`` (uint8)
     - 1
     - Packet type (1 = measurement frame).
   * - ``_reserved``
     - ``H`` (uint16)
     - 2
     - Alignment padding.
   * - ``frame_id``
     - ``I`` (uint32)
     - 4
     - Sequential hardware frame counter.
   * - ``sample_count``
     - ``H`` (uint16)
     - 2
     - Total ADC samples in payload (nominal 3694).
   * - ``effective_start``
     - ``H`` (uint16)
     - 2
     - Index of first active detector pixel (nominal 32).
   * - ``effective_count``
     - ``H`` (uint16)
     - 2
     - Total active detector pixels (nominal 3648).
   * - ``flags``
     - ``H`` (uint16)
     - 2
     - Hardware and acquisition status flags.
   * - ``payload_bytes``
     - ``I`` (uint32)
     - 4
     - Length of following ADC sample payload (must equal ``sample_count * 2``).

Diagnostics & Qualification
---------------------------

* **Header Desynchronization:** If the parse buffer does not match ``CCD1``, the parser skips bytes incrementally until the next valid header magic is detected.
* **Payload Length Mismatch:** If ``payload_bytes != sample_count * 2``, the packet is rejected and a qualification error is logged.
* **Frame Gap Detection:** The difference between consecutive ``frame_id`` values is monitored; gaps :math:`\Delta \text{frame\_id} > 1` are recorded as dropped frames by the performance monitor.

Verification & Testing
----------------------

* **Nominal Parse Check:** Confirm that synthetic 3694-sample ``CCD1`` packets unpack correctly into 3694 raw 16-bit integer values.
* **Truncated Packet Check:** Verify that buffers smaller than 22 bytes + payload remain buffered until complete data arrives.
* **Corrupt Magic Check:** Verify that random byte sequences do not trigger false frame emissions.
