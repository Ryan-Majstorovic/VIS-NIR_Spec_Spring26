Command Status Handling
=======================

The Command Status Handling system manages the bidirectional exchange of non-measurement data over the USB CDC virtual COM port. It demuxes mixed ASCII text lines from binary frame packets, processes microcontroller startup banners and diagnostic messages, and handles the transmission of operator commands.

.. _uuid-e4f5a6b7-c8d9-40e1-f2a3-445566778801:

Subsystem Role & Stream Demuxing
--------------------------------

UUID: :ref:`E4F5A6B7-C8D9-40E1-F2A3-445566778801 <uuid-e4f5a6b7-c8d9-40e1-f2a3-445566778801>`

The spectrometer firmware shares a single USB CDC endpoint for both high-rate binary measurement frames and ASCII text lines (startup banners, peripheral clocks, timer IRQ frequencies, and command responses). The Command Status Handling stage separates these interleaved data streams without corrupting binary frames or dropping text messages.

Inputs and Outputs
------------------

.. list-table::
   :header-rows: 1

   * - Flow
     - Name
     - Structure / Type
     - Description
   * - **Input**
     - Raw Byte Stream
     - Byte chunks
     - Incoming serial bytes from connection transport.
   * - **Input**
     - Raw Command String
     - String
     - Operator text command entered in the GUI.
   * - **Output**
     - Text Packet
     - ``BannerPacket`` / ``TextLinePacket``
     - Decoded ASCII string dispatched to logs or UI banner.
   * - **Output**
     - Wire Command Bytes
     - ``bytes``
     - ASCII string terminated with ``\n`` sent to device.

Normative Requirements
----------------------

.. _uuid-e4f5a6b7-c8d9-40e1-f2a3-445566778802:

**Requirement:** The Host PC Command Status Handling system shall parse incoming serial bytes into text lines whenever a newline character (``\n``) is encountered prior to or outside a binary ``CCD1`` frame header.

   **Rationale:** The firmware emits boot banners, timer configuration logs, and command responses as plain ASCII lines; parsing text lines immediately outside frame headers preserves diagnostics without misinterpreting text as ADC samples.

.. _uuid-e4f5a6b7-c8d9-40e1-f2a3-445566778803:

**Requirement:** The Host PC Command Status Handling system shall classify incoming text lines containing peripheral clock configurations or startup banners as ``BannerPacket`` objects and display them in the operator diagnostics card.

   **Rationale:** Exposing firmware initialization details (e.g., TIM2 TRGO rate, TIM4 ICG frequency) allows the operator to verify that the microcontroller initialized with correct clock prescalers.

.. _uuid-e4f5a6b7-c8d9-40e1-f2a3-445566778804:

**Requirement:** The Host PC Command Status Handling system shall encode operator command strings into ASCII bytes terminated with a newline (``\n``) and transmit them using a synchronized transport lock.

   **Rationale:** Line-terminated ASCII encoding conforms to the firmware's virtual COM port command parser, while a transport write lock prevents command packets from fragmenting when multiple threads submit requests.

Stream Demuxing Architecture
----------------------------

1. **Byte Scan:** The incoming buffer is scanned for ``PACKET_MAGIC`` (``b"CCD1"``).
2. **Text Extraction:** Any bytes preceding the magic token are checked for newline delimiters (``\n``). Complete lines are extracted and decoded as UTF-8 (ignoring errors).
3. **Binary Header Parse:** If ``b"CCD1"`` is at the buffer head, the 22-byte header is unpacked. If valid and the full payload is present, a ``BinaryFramePacket`` is emitted and the entire packet slice is consumed.
4. **Buffer Trimming:** If invalid or corrupt data is detected, the buffer is shifted forward by 1 byte to regain synchronization.

Diagnostics & Performance Monitoring
------------------------------------

* **Firmware Banner Capture:** Captures and displays banners such as:
  ```text
  USB CDC binary frame streaming: CCD1 (3694 samples/frame)
  TIM2_TRGO: 462.5 kHz (PA1 ADC trigger)
  ICG-synchronous capture on TIM4 update=8.000 ms
  ```
* **Queue Latency Tracking:** Monitors the queue depth of pending byte chunks to detect when background processing falls behind incoming serial traffic.

Verification & Testing
----------------------

* **Interleaved Stream Test:** Stream 50 binary frames interspersed with 5 ASCII text lines; verify that exactly 50 ``BinaryFramePacket`` objects and 5 ``TextLinePacket`` objects are emitted without parse errors.
* **Command Echo Test:** Send ``"PING\n"`` and verify that the exact byte sequence is written to the serial transport.
