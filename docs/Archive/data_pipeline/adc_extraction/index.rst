ADC Count Extraction
====================

UUID: ``A3B7D520-4E6F-4C81-B091-2F3A6C94D70E``

The ADC count extraction stage converts the validated binary packet payload into a one-dimensional array of per-pixel ADC counts. This stage handles endianness conversion, byte packing unpacking, and any protocol-level transformations required before calibration processing begins.

Overview
--------

The system performs these operations on every validated frame:

1. **Byte-order correction.** Convert multi-byte integer values from device-endian (little-endian) to host-native byte order.

2. **Payload unpacking.** Extract the 3648 individual ADC count values from their packed binary representation into a contiguous floating-point array for downstream processing.

3. **Scaling normalization.** Apply any protocol-level scaling factors to convert raw packet bytes into physical ADC count units.

4. **Array validation.** Verify that the extracted array contains exactly 3648 elements ready for bias/dark correction.

Related Pages
-------------

.. toctree::
   :maxdepth: 1

   inputs_and_outputs
   procedure
   calculations