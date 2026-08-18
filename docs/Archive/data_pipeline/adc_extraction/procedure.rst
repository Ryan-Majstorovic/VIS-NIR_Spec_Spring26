Procedure
=========

The system extracts per-pixel ADC counts through the following procedure:

1. Receive the validated binary payload (memoryview of bytes) from the frame validation stage.

2. Read the sample count field from the packet header via ``FRAME_HEADER_STRUCT.unpack_from(buffer)``, extracting the ``sample_count`` value.

3. Call ``adc_counts = np.frombuffer(payload, dtype="<u2", count=sample_count).copy()`` to interpret the payload bytes as a contiguous numpy array of unsigned 16-bit little-endian integers and create a writable copy.

4. Verify that exactly ``int(device_config.sample_count)`` values were extracted: ``len(adc_counts) == int(device_config.sample_count)`` where device_config.sample_count is typically 3648 for the TCD1304DG sensor.

5. Set the ``extraction_complete`` flag to True if the array length matches; set to False and log an error if the count differs.

6. Record the extraction latency: ``latency_us = (t_end - t_start) * 1_000_000`` where ``t_start = time.perf_counter()`` before step 3 and ``t_end = time.perf_counter()`` after step 3 completes.

7. Attach the numpy array to the frame object as ``frame.adc_counts`` for downstream consumption by the bias and dark correction stage.