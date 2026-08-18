Protocol Error Handling
=======================

UUID: ``E9H2I3J4-K5L6-7890-MNOP-QR1234567890``

This page documents the error conditions detected during CCD1 protocol frame reception and the corresponding recovery actions taken by the host PC parser.

Incomplete Header Buffer
------------------------

UUID: ``F1A2B3C4-D5E6-7890-FGHI-JK1234567890``

**Condition**: The internal byte buffer contains fewer than 29 bytes (the binary frame header size).

**Detection**: Checked at the start of binary frame parsing when magic bytes ``CCD1`` are found at the buffer start.

**Action**: Return consumed count of 0 ("need more data"). All bytes remain in the buffer. The parser waits for additional byte chunks from the serial reader before retrying frame parsing.

**Recovery**: No action required. Parsing automatically resumes when sufficient bytes arrive from subsequent serial reads.

Invalid Magic Bytes
-------------------

UUID: ``G2B3C4D5-E6F7-8901-GHIJ-KL2345678901``

**Condition**: The first 4 bytes of the buffer do not match the magic identifier ``CCD1`` (hex values 0x43, 0x43, 0x44, 0x31).

**Detection**: Checked immediately after confirming the buffer has at least 29 bytes. The magic field is unpacked using struct format offset 0 with size 4 bytes.

**Action**: Return consumed count of 1 ("skip 1 byte"). One byte is advanced from the buffer start position to resynchronize the parser.

**Recovery**: Parser continues scanning the remaining buffer for the next occurrence of valid magic bytes or a newline delimiter. Corrupted leading bytes are discarded.

Version Mismatch
----------------

UUID: ``H3C4D5E6-F7G8-9012-HIJK-LM3456789012``

**Condition**: The version field in the frame header does not equal the supported protocol version value ``1``.

**Detection**: Checked after successful magic byte validation. The version field is at header offset 4, encoded as a single unsigned byte (struct code B).

**Action**: Return consumed count of 1 ("skip 1 byte"). The entire invalid frame header is skipped by advancing one byte.

**Recovery**: Parser continues scanning for the next valid frame boundary. This error indicates the embedded device transmitted a protocol version different from what the host application supports.

Packet Type Mismatch
--------------------

UUID: ``I4D5E6F7-G8H9-0123-IJKL-MN4567890123``

**Condition**: The packet_type field in the frame header does not equal ``1`` (binary frame packet identifier).

**Detection**: Checked after magic byte and version validation. The packet_type field is at header offset 5, encoded as a single unsigned byte (struct code B).

**Action**: Return consumed count of 1 ("skip 1 byte"). One byte is advanced from the buffer start position.

**Recovery**: Parser continues scanning for the next valid frame boundary. This error may indicate a future protocol extension or corrupted header data.

Invalid Sample Count
--------------------

UUID: ``J5E6F7G8-H9I0-1234-JKLM-NO5678901234``

**Condition**: The sample_count field is zero or exceeds the maximum allowed value of 8192 (``MAX_BINARY_SAMPLE_COUNT``).

**Detection**: Checked after magic, version, and packet_type validation. The sample_count field is at header offset 12, encoded as an unsigned 32-bit integer (struct code I).

**Action**: Return consumed count of 1 ("skip 1 byte"). One byte is advanced from the buffer start position.

**Recovery**: Parser continues scanning for the next valid frame boundary. This error indicates either a zero-length payload or an implausibly large sample count, both suggesting header corruption.

Payload Length Mismatch
-----------------------

UUID: ``K6F7G8H9-I0J1-2345-KLMN-OP6789012345``

**Condition**: The payload_bytes field in the header does not equal the calculated expected value of ``sample_count * 2`` (each ADC sample is 16 bits = 2 bytes).

**Detection**: Checked after validating sample_count range. The payload_bytes field is at header offset 24, encoded as an unsigned 32-bit integer (struct code I). Expected value is computed as ``sample_count * 2``.

**Action**: Return consumed count of 1 ("skip 1 byte"). One byte is advanced from the buffer start position.

**Recovery**: Parser continues scanning for the next valid frame boundary. This error indicates a mismatch between the declared sample count and payload length, suggesting header or payload corruption during transmission.

Incomplete Payload Buffer
-------------------------

UUID: ``L7G8H9I0-J1K2-3456-LMNO-PQ7890123456``

**Condition**: The buffer contains a valid header but does not yet contain all bytes of the ADC payload (header size 29 + payload_bytes).

**Detection**: After all header validations pass, the parser checks if ``len(buffer) >= (29 + payload_bytes)``. If false, the remaining payload bytes have not arrived via the serial port.

**Action**: Return consumed count of 0 ("need more data"). All bytes in the buffer are retained for the next parsing cycle.

**Recovery**: No action required. The parser automatically processes the complete frame when all remaining payload bytes arrive through subsequent serial reads. This is normal behavior for high-speed data transmission where packets may be split across multiple TCP/serial chunks.

Buffer Overflow
---------------

UUID: ``M8H9I0J1-K2L3-4567-MNOP-QR8901234567``

**Condition**: The internal byte buffer grows beyond ``FRAME_HEADER_LIMIT`` (1024 bytes) without finding a valid packet boundary (no magic bytes or newline delimiter).

**Detection**: Checked when no newline and no magic bytes exist anywhere in the buffer during the text line search phase.

**Action**: Truncate the buffer to its last 3 bytes, preserving any potential partial magic byte sequence that might span the truncation point.

**Recovery**: Parser resumes with a reduced buffer containing only the tail end of accumulated data. This prevents unbounded memory growth while maintaining the ability to detect magic bytes that may have been split across the truncation boundary.

Text Line Errors
----------------

UUID: ``N9I0J1K2-L3M4-5678-NOPQ-RS9012345678``

**Condition**: Decoded text lines contain invalid UTF-8 sequences or are empty after stripping.

**Detection**: During text line extraction, the raw buffer bytes are decoded using ``utf-8`` encoding with ``errors="replace"`` which substitutes invalid byte sequences with the Unicode replacement character (U+FFFD). Empty strings after stripping whitespace are discarded.

**Action**: Lines containing replacement characters are classified as TextLinePacket and passed to the caller for logging or display. Empty lines are silently dropped.

**Recovery**: No buffer action required; the line bytes have already been removed during extraction. The replacement character allows diagnostic tools to identify positions where non-UTF-8 data was transmitted by the embedded device.