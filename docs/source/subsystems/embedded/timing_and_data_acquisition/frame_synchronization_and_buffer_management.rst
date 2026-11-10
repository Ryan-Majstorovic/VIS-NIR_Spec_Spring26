Frame Synchronization and Buffer Management
===========================================

The Frame Synchronization and Buffer Management subsystem coordinates the memory storage, sequence tracking, and transmission readiness of digitized spectrometer frames. It decouples the real-time ADC DMA acquisition cycle from USB CDC packet transmission using a circular multi-slot buffer architecture.

.. _uuid-4b02028c-27d5-4758-bc9a-fc6d95a4d272:

Subsystem Role & Boundary
-------------------------

UUID: :ref:`4B02028C-27D5-4758-BC9A-FC6D95A4D272 <uuid-4b02028c-27d5-4758-bc9a-fc6d95a4d272>`

This subsystem manages the boundary between hardware interrupt routines and the communication dispatch loop. It ensures that incoming frames receive sequential hardware frame IDs, that memory buffers are safely rotated without race conditions, and that USB transmission latencies do not block ongoing analog conversions.

Inputs and Outputs
------------------

.. list-table::
   :header-rows: 1

   * - Flow
     - Name
     - Type / Format
     - Description
   * - **Input**
     - Frame Completion Event
     - ISR callback
     - ADC DMA transfer-complete notification from ``HAL_ADC_ConvCpltCallback``.
   * - **Input**
     - USB TX Complete Event
     - Driver callback
     - Notification indicating the previous packet has cleared the USB CDC endpoint.
   * - **Output**
     - Sealed Frame Packet
     - ``CcdUsbFramePacket``
     - Completed 7424-byte packet (32-byte header + 7388-byte payload + 4-byte CRC) ready for wire transmission.
   * - **Output**
     - Frame Dropped Counter
     - uint32 diagnostic counter
     - Total count of frames dropped due to buffer exhaustion or USB bus throttling.

Normative Requirements
----------------------

.. _uuid-bf57f934-133b-4e83-a1c8-ec0e87f2998c:

**Requirement:** The Embedded frame management system shall maintain a circular pool of at least four independent frame buffer slots in SRAM under continuous streaming to decouple ADC DMA acquisition from USB CDC transmission latency.

   **Rationale:** USB CDC packet transfers can experience transient delays due to host operating system scheduling; a 4-slot ping-pong buffer provides queue capacity that prevents DMA overruns and dropped frames during momentary USB stalls.

.. _uuid-e95ad698-a600-402e-b969-a615ca2c1e98:

**Requirement:** The Embedded frame management system shall assign a monotonically incrementing 32-bit frame counter (``frame_id``) to each captured frame header under all operational states to enable downstream detection of missed or dropped frames.

   **Rationale:** Monotonic sequence numbers allow the Host PC to detect packet loss immediately, calculate true capture rates, and maintain temporal alignment across measurement sessions.

.. _uuid-61aabab6-c64e-45b6-a3f9-817e67eb0975:

**Requirement:** The Embedded frame management system shall increment a dedicated dropped-frame counter and discard the incoming acquisition slot when no free buffer slots are available at a frame boundary to prevent memory corruption or transmission of partially written frames.

   **Rationale:** Overwriting an active buffer slot during transmission would deliver a corrupted frame containing mixed samples from two different exposures; discarding the newly completed frame preserves stream integrity and diagnostic visibility.

Multi-Slot Buffer Architecture
------------------------------

The firmware maintains a statically allocated pool of four frame buffers:

.. code-block:: c

   #define CCD_FRAME_BUFFER_COUNT 4U

   typedef struct {
     CcdUsbFramePacket packet;   /* 32-byte header + 7388-byte sample array + 4-byte CRC */
     volatile uint8_t active;   /* 1 if currently being filled by ADC DMA */
     volatile uint8_t ready;    /* 1 if acquisition complete, awaiting USB TX */
     uint16_t flags;            /* Frame diagnostic status flags */
   } CcdFrameSlot;

   static CcdFrameSlot ccd_frame_slots[CCD_FRAME_BUFFER_COUNT];

Frame Lifecycle State Machine
-----------------------------

Each slot cycles through four states during acquisition and transfer:

.. code-block:: text

   +-----------------------+     AcquireFrameSlot()     +-----------------------------+
   |       FREE SLOT       | -------------------------> |     ACTIVE ACQUISITION      |
   | (active = 0, ready = 0)|                            | (active = 1, DMA receiving) |
   +-----------------------+                            +-----------------------------+
               ^                                                       |
               | ReleaseFrameSlot()                                    | HAL_ADC_ConvCpltCallback
               | (TX finished)                                         v
   +-----------------------+   CDC_Transmit_Blocking()  +-----------------------------+
   |     TRANSMITTING      | <------------------------- |        READY FOR TX         |
   | (streaming over wire) |                            | (active = 0, ready = 1)     |
   +-----------------------+                            +-----------------------------+

1. **Slot Allocation:** Prior to the next ICG readout edge, the firmware calls ``AcquireFrameSlot()``. If a slot with ``active == 0`` and ``ready == 0`` is available, it is allocated and populated with the next ``frame_id`` and configuration metadata.
2. **DMA Arming:** ``ArmFrameCapture()`` points ``DMA2_Stream0`` to the allocated slot's ``payload`` array and prepares the peripheral for conversion.
3. **Capture Sealing:** Upon completion of all 3694 conversions, ``HAL_ADC_ConvCpltCallback`` validates completion, stamps the header status flags, and sets ``ready = 1``.
4. **Wire Transmission:** The background polling loop selects the oldest completed frame by hardware frame ID and starts its 7424-byte transfer.

**Requirement:** The Embedded buffer manager shall retain ownership of a USB
payload until the endpoint reports completion, including after a transmission
timeout, to prevent ADC reallocation from changing bytes still in flight.

**Rationale:** A timeout bounds waiting but does not terminate the USB DMA/endpoint
transfer; recycling the slot early can corrupt the remaining packet.

**Requirement:** The Embedded buffer manager shall transmit completed frames
in hardware-frame order following host backpressure to preserve monotonic frame
identity while exposing skipped acquisitions as counter gaps.

**Rationale:** Buffer-slot rotation alone does not preserve acquisition order
when some slots remain occupied longer than others.
