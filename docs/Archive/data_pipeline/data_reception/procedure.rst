Host PC Reception Procedure
============================

This page documents the step-by-step procedure for receiving and reconstructing binary frames on the host PC side of the CCD1 communication protocol. The embedded MCU transmission details are documented in the Embedded subsystem documentation.

Serial Transport Initialization
-------------------------------

1. Open the USB CDC serial port with the configured baud rate and parameters.
2. Start a background reader thread that continuously reads byte chunks from the serial port.
3. Initialize an empty ``bytearray`` buffer for packet reconstruction.

Byte Chunk Processing Loop
--------------------------

For each byte chunk received from the serial port, perform these sub-steps in order:

Sub-step A: Append to Buffer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extend the internal ``bytearray`` buffer with the new incoming bytes, then enter the packet parsing loop.

Sub-step B: Parse Packets from Buffer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Repeat the following until no more complete packets can be extracted:

1. Check if buffer starts with magic bytes ``CCD1`` (``buffer[0:4] == b"CCD1"``).

   - If yes, attempt binary frame parsing (see Sub-step C).
   - If parsing succeeds, remove consumed bytes from buffer and repeat this step.
   - If parsing fails with consumed=1, advance one byte and repeat.
   - If parsing requires more data (consumed=0), proceed to Step 2.

2. Search for the next newline character position and magic bytes position in the buffer.

   - If a newline is found before any magic occurrence (or no magic exists), extract the text line (see Sub-step D).
   - If magic bytes are found before a newline, discard all bytes up to and including the magic prefix, then repeat Step 1.

3. Handle end-of-buffer conditions.

   - If no newline and no magic exist in the buffer, check if buffer length exceeds ``FRAME_HEADER_LIMIT`` (1024 bytes).
   - If limit exceeded, truncate buffer to last 3 bytes and break the parsing loop.
   - Otherwise, break the parsing loop and wait for more data.

Binary Frame Parsing
--------------------

When magic bytes ``CCD1`` are found at the buffer start:

1. Verify the buffer contains at least 29 bytes (the header size). If not, return "need more data" to continue buffering.

2. Unpack header fields using struct format ``<4sBBHIHHHHI`` from buffer offset 0. This extracts: magic, version, packet_type, reserved, frame_id, sample_count, effective_start_index, effective_count, flags, and payload_bytes.

3. Validate the magic field equals ``b"CCD1"``. If not, return "skip 1 byte" to resynchronize.

4. Validate version equals ``1`` and packet_type equals ``1``. If either check fails, return "skip 1 byte".

5. Validate sample_count is in the range [1, 8192]. If outside this range, return "skip 1 byte".

6. Calculate expected payload bytes as ``sample_count * 2`` (each ADC sample is 16 bits = 2 bytes).

7. Verify the payload_bytes header field equals the calculated expected value. If not, return "skip 1 byte".

8. Check if the buffer contains enough bytes for the complete frame (header size + payload_bytes). If not, return "need more data" to wait for remaining bytes.

9. Extract the payload from buffer at offset 29 through ``(29 + payload_bytes)``.

10. Convert the payload bytes to a numpy uint16 array using ``np.frombuffer(payload, dtype="<u2", count=sample_count).copy()``. This produces little-endian unsigned 16-bit ADC counts.

11. Construct a BinaryFramePacket object with all unpacked header fields and the ADC sample data.

12. Return the packet object along with the total consumed byte count ``(29 + payload_bytes)``. The caller removes these bytes from the buffer.

Text Line Extraction
--------------------

When a newline delimiter is found before any magic bytes in the buffer:

1. Extract raw bytes from the buffer start to the newline position (exclusive of the newline).

2. Remove the extracted bytes and the newline delimiter byte from the buffer.

3. Decode the extracted bytes as UTF-8 using error replacement for invalid sequences.

4. Classify the decoded line:

   - Create a BannerPacket if the line starts with "USB CDC" or contains timing keywords such as ``TIM2_TRGO``, ``ICG-synchronous``, or ``TIM4 update=``.
   - Create a TextLinePacket for all other non-empty lines (diagnostics, error codes, command responses).

5. Return the classified packet object to the caller.

Command Transmission
--------------------

Host-to-device commands use ASCII text lines sent over the same USB CDC serial link:

1. Format the command as a stripped UTF-8 string (e.g., ``"EXPOSURE 1000"``).
2. Append a newline character (``\\n``) to terminate the command.
3. Encode using ASCII encoding, discarding any non-ASCII characters.
4. Write the encoded bytes to the serial port write endpoint.

Command encoding is performed by ``encode_raw_command(command_text)`` in ``backend/device/protocol.py`` which applies the format ``f"{command_text.strip()}\\n".encode("ascii", errors="ignore")``.