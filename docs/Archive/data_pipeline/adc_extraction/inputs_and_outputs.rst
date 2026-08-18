Inputs and Outputs
==================

ADC Extraction Inputs
---------------------

.. list-table::
   :header-rows: 1

   * - Validated binary payload (memoryview)
     - Output from frame validation stage
     - Raw bytes object or memoryview containing the packet payload section. Passed directly to ``np.frombuffer(payload, dtype="<u2", count=sample_count)`` for zero-copy little-endian unsigned 16-bit integer interpretation.

   * - Sample count field (int)
     - Extracted from packet header's sample_count field via FRAME_HEADER_STRUCT.unpack_from(buffer)
     - Specifies the number of samples in the payload. Passed as the ``count`` parameter to ``np.frombuffer(payload, dtype="<u2", count=sample_count)`` to limit array length.

   * - Expected pixel count (3648)
     - Known active pixel count of the TCD1304DG sensor from DeviceConfig.sample_count
     - Used to verify that exactly 3648 ADC values are extracted: ``len(adc_counts) == int(device_config.sample_count)``.

ADC Extraction Outputs
----------------------

.. list-table::
   :header-rows: 1

   * - Extracted ADC count array (np.ndarray of uint16)
     - Passed to bias and dark correction stage as frame.adc_counts
     - Produced by ``adc_counts = np.frombuffer(payload, dtype="<u2", count=sample_count).copy()``. A contiguous numpy array of unsigned 16-bit integers with shape ``(sample_count,)``.

   * - ``extraction_complete`` flag (bool)
     - Internal pipeline state set after extraction
     - Computed as ``len(adc_counts) == int(device_config.sample_count)``. True if sample count matches; false triggers logging and frame discard.

   * - Extraction latency in microseconds (float)
     - Pipeline performance metric recorded via time.perf_counter()
     - Computed as ``(t_end - t_start) * 1_000_000`` where ``t_start = time.perf_counter()`` before frombuffer and ``t_end`` after copy completes.