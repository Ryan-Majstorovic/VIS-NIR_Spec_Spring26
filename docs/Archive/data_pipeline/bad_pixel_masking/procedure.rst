Procedure
=========

The system applies bad-pixel and saturation masking through the following procedure:

1. Load ``CalibrationConfig.bad_pixel_indices`` from the active calibration configuration. Initialize a boolean validity mask of shape ``(sample_count,)`` with all values set to True.

2. Set masked pixels for calibration-defined bad indices: ``validity_mask[bad_pixel_indices] = False``.

3. Update the sliding window buffer by appending the current frame at the last row index and evicting the oldest row if the buffer is full.

4. **Dead pixel detection.** For each pixel index ``p``, compute the range of values across all frames in the sliding window: ``np.ptp(window[:, p])``. If the peak-to-peak variation is less than or equal to ``dead_pixel_threshold``, set ``validity_mask[p] = False``.

5. **Stuck pixel detection.** For each pixel index ``p``, compute the absolute difference between consecutive frames in the sliding window: ``np.abs(np.diff(window[:, p]))``. If any inter-frame delta exceeds ``stuck_pixel_delta_threshold``, set ``validity_mask[p] = False``.

6. **Saturation masking.** Pixels whose ADC counts exceed ``saturation_adc_count`` are masked: ``validity_mask[current_frame >= saturation_adc_count] = False``. The saturation threshold is determined by the sensor's linear full-well capacity and may be refined in later stages based on wavelength-dependent response characteristics.

7. **Mask composition.** Steps 2 through 6 apply cumulative logical AND to the validity mask, producing a single per-pixel boolean array.

8. Record mask statistics: total pixel count, valid pixel count, dead pixel count, stuck pixel count, saturation pixel count, and calibration-defined bad pixel count.

9. Pass the validity mask downstream to wavelength mapping, PRNU correction, QE correction, and display normalization stages.