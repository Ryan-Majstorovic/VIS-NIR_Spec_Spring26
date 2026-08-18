Inputs and Outputs
==================

Frame Validation Inputs
-----------------------

.. list-table::
   :header-rows: 1

   * - Raw USB packet stream
     - Incoming data from STM32 via USB CDC
     - Contains ``CCD1`` packet headers, payload data, frame counters, and optional checksums.

   * - Expected pixel count (3648)
     - Known active pixel count of the TCD1304DG sensor
     - Used to verify that each decoded payload contains exactly 3648 raw ADC values before validation proceeds.

   * - ADC resolution bits (N)
     - DeviceConfig parameter
     - Defines the valid ADC count range: 0 to ``2^N - 1``.

Frame Validation Outputs
------------------------

.. list-table::
   :header-rows: 1

   * - Validated frame payload
     - Passed to ADC extraction stage
     - A clean 3648-sample array with verified integrity and range compliance.

   * - ``frame_valid`` flag
     - Internal pipeline state
     - True if all validation checks pass; false triggers logging and frame discard.

   * - Dropped-frame count
     - Pipeline statistics counter
     - Increments when a frame fails any validation check or has a gap in the sequence number.
