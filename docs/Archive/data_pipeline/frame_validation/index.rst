Frame Validation
================

UUID: ``F8A2C410-3D5E-4B91-A076-1E2F5C83D60A``

The frame validation stage is the first step of the host calibration pipeline. It verifies that each incoming USB packet stream contains a complete, valid spectral frame before any extraction or correction is applied. This stage protects downstream processing from corrupted packets, dropped frames, or malformed payloads.

Overview
--------

The system performs these checks on every incoming frame:

1. **Packet boundary detection.** The ``CCD1`` packet header is verified against the expected magic bytes and length field.

2. **Payload length validation.** The decoded payload must contain exactly 3648 samples (the TCD1304DG active pixel count). Frames with fewer or more samples are flagged as malformed.

3. **Range checking.** All ADC counts fall within the expected range for the configured resolution: 0 to ``2^N - 1`` where N is the ADC resolution in bits.

4. **Checksum / integrity verification.** If a checksum field is present in the packet format, it is verified against the payload contents.

5. **Frame counter continuity.** The frame sequence number increments monotonically (allowing for at most one dropped frame before flagging a gap).

Frames that fail any of these checks are logged and discarded. Valid frames pass through to ADC count extraction.

Related Pages
-------------

.. toctree::
   :maxdepth: 1

   inputs_and_outputs
   procedure
   calculations