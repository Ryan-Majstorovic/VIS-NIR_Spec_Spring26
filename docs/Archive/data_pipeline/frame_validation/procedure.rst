Procedure
=========

The system validates each incoming frame through the following procedure:

1. Receive the raw USB packet stream from the STM32 via USB CDC.

2. Parse the ``CCD1`` packet header and extract the magic bytes, length field, payload data, frame counter, and optional checksum.

3. Verify that the magic bytes match the expected protocol signature for valid CCD packets.

4. Confirm that the decoded payload contains exactly 3648 raw ADC values (the known active pixel count of the TCD1304DG sensor).

5. Check that all ADC counts fall within the valid range defined by the configured resolution: 0 to ``2^N - 1`` where N is the ADC resolution in bits.

6. If a checksum field is present, verify it matches the computed checksum of the payload contents.

7. Compare the incoming frame counter against the expected value (last known sequence number plus one). Flag and count any gaps or duplicates.

8. Set the ``frame_valid`` flag to true if all checks pass; set to false and increment the dropped-frame counter if any check fails.

9. Pass validated frames to the ADC extraction stage for pixel value extraction.