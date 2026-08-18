Inputs and Outputs
==================

This page defines the transport-stream elements consumed by ingress and ADC
reconstruction and the structured host-side outputs produced once the incoming
stream has been reconstructed, checked, and converted into ordered measurement
data.

.. _uuid-a21fdaa0-9bcf-4fa5-bff4-bb0bb98c3419:

Inputs
------

UUID: :ref:`A21FDAA0-9BCF-4FA5-BFF4-BB0BB98C3419 <uuid-a21fdaa0-9bcf-4fa5-bff4-bb0bb98c3419>`

.. list-table::
   :header-rows: 1

   * - Item
     - Expected Values
     - Structure
     - Purpose
   * - USB CDC read chunk
     - Any non-empty byte sequence returned by the active transport read loop
     - ``bytes``
     - Carry newly arrived device-stream data into the Host PC receive path.
   * - Buffered partial stream
     - Zero or more retained bytes from earlier incomplete reads
     - ``bytearray``
     - Preserve incomplete frame headers, incomplete payloads, or incomplete
       text lines until enough bytes arrive to classify and reconstruct them.
   * - Binary frame sync marker
     - Leading bytes equal to ``b"CCD1"``
     - 4-byte magic identifier
     - Signal that the current buffer head should be interpreted as a binary
       ``CCD1`` frame candidate.
   * - ASCII line delimiter
     - Newline byte ``0x0A`` with optional preceding carriage return
     - Byte terminator inside the buffered stream
     - Mark the end of one text line for host-side classification.

.. _uuid-782b5cbe-1220-4f95-add4-4ed377911e35:

Outputs
-------

UUID: :ref:`782B5CBE-1220-4F95-ADD4-4ED377911E35 <uuid-782b5cbe-1220-4f95-add4-4ed377911e35>`

.. list-table::
   :header-rows: 1

   * - Item
     - Expected Values
     - Structure
     - Purpose
   * - Reconstructed frame metadata
     - Valid header fields plus a payload length consistent with the declared
       sample count
     - Structured frame record
     - Preserve frame identity, geometry, and status fields for downstream
       pipeline processing.
   * - Ordered ADC sample sequence
     - ``sample_count`` little-endian unsigned 16-bit samples in acquisition
       order
     - ADC-domain array or equivalent ordered sample container
     - Provide the raw detector readout that later correction stages consume.
   * - Banner packet
     - Non-empty ASCII line matching the banner keyword rules
     - ``BannerPacket`` or equivalent banner record
     - Preserve startup and timing-related firmware text as structured banner
       messages.
   * - Text line packet
     - Any other non-empty ASCII line
     - ``TextLinePacket`` or equivalent text record
     - Preserve generic firmware diagnostics, command responses, and other
       text output without treating it as measurement data.
   * - Residual parser buffer
     - Incomplete header bytes, incomplete payload bytes, or incomplete text
       bytes
     - Internal ``bytearray`` state
     - Carry unresolved stream fragments into the next receive iteration.

.. _uuid-56aa8564-f48c-49db-b2f2-a98be7bcd7cf:

Binary Frame Header Layout
--------------------------

UUID: :ref:`56AA8564-F48C-49DB-B2F2-A98BE7BCD7CF <uuid-56aa8564-f48c-49db-b2f2-a98be7bcd7cf>`

The binary header uses the layout ``<4sBBHIHHHHI``. The header is 24 bytes
long.

.. list-table::
   :header-rows: 1

   * - Offset
     - Length
     - Struct Code
     - Field
     - Current Host Expectation
     - Purpose
   * - 0
     - 4
     - ``4s``
     - ``magic``
     - ``b"CCD1"``
     - Distinguish binary frame candidates from other buffered bytes.
   * - 4
     - 1
     - ``B``
     - ``version``
     - ``1``
     - Reject unsupported protocol revisions on the host side.
   * - 5
     - 1
     - ``B``
     - ``packet_type``
     - ``1``
     - Restrict the current parser path to binary frame packets only.
   * - 6
     - 2
     - ``H``
     - ``reserved``
     - Parsed but not used later
     - Preserve the current wire layout without assigning host behavior to this
       field.
   * - 8
     - 4
     - ``I``
     - ``frame_id``
     - Unsigned 32-bit counter
     - Carry frame ordering metadata into later host stages.
   * - 12
     - 2
     - ``H``
     - ``sample_count``
     - ``1`` to ``8192``
     - Define how many ADC samples are expected in the payload.
   * - 14
     - 2
     - ``H``
     - ``effective_start``
     - Host stores the received value directly
     - Describe where the active spectral region begins inside the raw frame.
   * - 16
     - 2
     - ``H``
     - ``effective_count``
     - Host stores the received value directly
     - Describe how many samples belong to the active spectral region.
   * - 18
     - 2
     - ``H``
     - ``flags``
     - Host stores the received value directly
     - Carry per-frame status bits alongside the ADC payload.
   * - 20
     - 4
     - ``I``
     - ``payload_bytes``
     - Must equal ``sample_count * 2``
     - Confirm that the declared ADC payload length matches the header.

.. _uuid-50f12fd8-8d81-4cd7-87a7-f23a3c315f39:

ADC Payload Layout
------------------

UUID: :ref:`50F12FD8-8D81-4CD7-87A7-F23A3C315F39 <uuid-50f12fd8-8d81-4cd7-87a7-f23a3c315f39>`

The ADC payload immediately follows the 24-byte header and contains the full
raw CCD readout for one frame. Each sample is stored as a little-endian
unsigned 16-bit value.

.. list-table::
   :header-rows: 1

   * - Field
     - Offset (bytes)
     - Length (bytes)
     - Data Type
     - Byte Order
     - Description
   * - ADC Sample [0]
     - ``24``
     - 2
     - ``uint16``
     - Little-endian
     - First raw ADC sample in the frame payload.
   * - ADC Sample [1]
     - ``26``
     - 2
     - ``uint16``
     - Little-endian
     - Second raw ADC sample in the frame payload.
   * - ...
     - ...
     - ...
     - ...
     - ...
     - Intermediate raw ADC samples from the same frame-wide CCD readout.
   * - ADC Sample [sample_count-1]
     - ``24 + ((sample_count - 1) * 2)``
     - 2
     - ``uint16``
     - Little-endian
     - Final raw ADC sample in the frame payload.

Total payload size is ``sample_count * 2`` bytes. In the current default Host
PC geometry this corresponds to a full-frame payload of ``3694`` samples, with
the active spectral region later described by ``effective_start`` and
``effective_count`` rather than by shortening the receive payload itself.

.. _uuid-b0ba5251-52af-4f84-a378-0634d7b76da3:

ASCII Line Classification
-------------------------

UUID: :ref:`B0BA5251-52AF-4F84-A378-0634D7B76DA3 <uuid-b0ba5251-52af-4f84-a378-0634d7b76da3>`

The Host PC parser treats non-empty newline-delimited text as one of two packet
classes:

.. list-table::
   :header-rows: 1

   * - Match Rule
     - Expected Values
     - Structure
     - Purpose
   * - Banner line
     - Starts with ``USB CDC`` or contains ``TIM2_TRGO``,
       ``ICG-synchronous``, or ``TIM4 update=``
     - ``BannerPacket``
     - Separate startup and timing-identification text from generic log lines.
   * - Generic text line
     - Any other non-empty decoded line
     - ``TextLinePacket``
     - Preserve diagnostics and command responses without treating them as
       binary frame data.
   * - Empty or whitespace-only line
     - No packet created
     - No output object
     - Avoid producing meaningless host log packets for blank lines.
