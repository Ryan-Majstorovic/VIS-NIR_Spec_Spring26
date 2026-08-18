Binary Frame I/O Structures
============================

This page documents the binary frame input/output structures and bit-level field definitions for the CCD1 communication protocol. All fields use little-endian byte ordering as defined by the struct format string ``<4sBBHIHHHHI`` in ``backend/device/protocol.py``.

Frame Header Layout (29 bytes total)
-------------------------------------

The binary frame header is packed using Python struct module with the following field layout:

.. list-table:: Binary Frame Header Field Definitions
   :header-rows: 1

   * - Offset (bytes)
     - Length (bytes)
     - Struct Code
     - Field Name
     - Bit Pattern
     - Value Range
     - Description

   * - 0
     - 4
     - 4s
     - Magic
     - Bits [0:31]
     - ``0x44434431`` (ASCII "CCD1")
     - Fixed magic identifier. Must match exactly for valid frame detection.

   * - 4
     - 1
     - B
     - Version
     - Bits [32:39]
     - ``0x01``
     - Protocol version number. Current and only supported value is ``1``.

   * - 5
     - 1
     - B
     - Packet Type
     - Bits [40:47]
     - ``0x01``
     - Packet class identifier. Value ``1`` denotes binary frame packet type.

   * - 6
     - 2
     - H
     - Reserved
     - Bits [48:63]
     - ``0x0000``
     - Reserved for future protocol extensions. Must be zero-filled on transmit, ignored on receive.

   * - 8
     - 4
     - I
     - Frame ID
     - Bits [64:95]
     - ``0x00000000`` to ``0xFFFFFFFF``
     - Unsigned 32-bit frame counter incremented per transmitted frame. Used for frame ordering and loss detection.

   * - 12
     - 4
     - I
     - Sample Count
     - Bits [96:127]
     - ``0x00000001`` to ``0x00002000`` (1 to 8192)
     - Number of ADC samples in the payload. Maximum value is ``MAX_BINARY_SAMPLE_COUNT`` (8192).

   * - 16
     - 2
     - H
     - Effective Start Index
     - Bits [128:143]
     - ``0x0000`` to ``0x1FFF``
     - Starting pixel index of the active sensor region in the raw ADC array. Excludes shielded pixels defined by the CCD hardware layout.

   * - 18
     - 2
     - H
     - Effective Count
     - Bits [144:159]
     - ``0x0000`` to ``0x1FFF``
     - Number of valid sensor samples in the active region. Typically equals sample_count minus shielded pixel count.

   * - 20
     - 4
     - I
     - Flags
     - Bits [160:191]
     - ``0x00000000`` to ``0xFFFFFFFF``
     - Per-frame status flags bitfield. Individual bit definitions are documented in the DeviceConfig specification.

   * - 24
     - 4
     - I
     - Payload Bytes
     - Bits [192:223]
     - ``0x00000002`` to ``0x00004000``
     - Expected payload byte count. Computed as ``sample_count * 2`` (each sample is 16-bit / 2 bytes).

ADC Payload Layout
------------------

The ADC payload immediately follows the 29-byte header and contains raw sensor data:

.. list-table:: ADC Payload Structure
   :header-rows: 1

   * - Field
     - Offset (bytes)
     - Length (bytes)
     - Data Type
     - Byte Order
     - Description

   * - ADC Sample [0]
     - 29
     - 2
     - uint16
     - Little-endian
     - First ADC sample from the CCD sensor. Corresponds to pixel index ``effective_start_index``.

   * - ADC Sample [1]
     - 31
     - 2
     - uint16
     - Little-endian
     - Second ADC sample. Corresponds to pixel index ``effective_start_index + 1``.

   * - ...
     - ...
     - ...
     - ...
     - ...
     - Intermediate samples.

   * - ADC Sample [sample_count-1]
     - ``(29 + (sample_count-1) * 2)``
     - 2
     - uint16
     - Little-endian
     - Last ADC sample. Corresponds to pixel index ``effective_start_index + sample_count - 1``.

Total payload size: ``sample_count * 2`` bytes. Each sample is a little-endian unsigned 16-bit integer representing raw ADC counts from the CCD sensor.

ASCII Text Line I/O
-------------------

Text lines use UTF-8 encoding with Unix newline delimiters:

.. list-table:: ASCII Text Packet Types
   :header-rows: 1

   * - Pattern Match
     - Packet Class
     - Content Description
     - Example

   * - Starts with ``USB CDC`` or contains ``TIM2_TRGO``, ``ICG-synchronous``, ``TIM4 update=``
     - BannerPacket
     - Startup identification and hardware configuration messages.
     - ``"USB CDC: TIM2_TRGO ICG-synchronous TIM4 update=1000"``

   * - All other non-empty lines
     - TextLinePacket
     - Diagnostic messages, error codes, timing information, or command responses.
     - ``"Sensor ready: 3694 samples expected"``

Validation Input/Output Contract
---------------------------------

The parser function ``try_parse_binary_frame(buffer)`` returns a tuple of ``(BinaryFramePacket | None, consumed_bytes)``:

.. list-table:: Validation Rules and Return Values
   :header-rows: 1

   * - Condition
     - Return Value
     - Action

   * - Buffer length < 29 bytes (incomplete header)
     - ``(None, 0)``
     - Keep bytes in buffer for next feed() call.

   * - Magic bytes != ``CCD1``
     - ``(None, 1)``
     - Advance one byte and resynchronize.

   * - Version != 1 or packet_type != 1
     - ``(None, 1)``
     - Reject frame, advance one byte.

   * - Sample count <= 0 or > 8192
     - ``(None, 1)``
     - Reject invalid sample count, advance one byte.

   * - Payload bytes != sample_count * 2
     - ``(None, 1)``
     - Reject payload length mismatch, advance one byte.

   * - Buffer length < total_bytes (incomplete payload)
     - ``(None, 0)``
     - Keep bytes in buffer for next feed() call.

   * - All validations pass
     - ``(BinaryFramePacket(...), total_bytes)``
     - Return parsed packet and consumed byte count. Caller removes consumed bytes from buffer.