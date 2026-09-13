Validation
==========

Use the following checks to verify that bias and dark correction parameters are correct:

1. **Dark-frame subtraction check.** Cover the sensor, acquire a session, and confirm that ``processed_adc_count`` is near zero across all pixels after calibration. The uncorrected frame should show elevated baseline counts; corrected values should be close to zero.

2. **Bias vector stability.** Capture bias twice with identical settings and compare the two vectors. They should match within expected noise (standard deviation of pixel-wise differences below a few ADC counts).

3. **Frame dark reference consistency.** With the sensor covered, inspect ``frame_dark_reference_count`` across consecutive frames. Values should be stable and consistent with the measured noise floor.

4. **Light-frame sanity check.** Expose the sensor to a uniform light source and confirm that ``processed_adc_count`` increases monotonically with integration time or source intensity after bias/dark correction.

5. **Export traceability.** Open an exported session file (CSV or HDF5) and verify that ``raw_adc_count``, ``processed_adc_count``, and ``frame_dark_reference_count`` are present and consistent with the live display values.