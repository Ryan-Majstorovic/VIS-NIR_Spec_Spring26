Calculations
============

The bad-pixel masking stage uses the following symbols:

* ``M``: per-pixel validity mask with shape ``(sample_count,)``, dtype bool.
* ``W``: sliding window buffer with shape ``(dead_pixel_window_size, sample_count)``.
* ``B``: calibration-defined bad pixel indices from ``CalibrationConfig.bad_pixel_indices``.
* ``p``: individual pixel index in range ``[0, sample_count)``.

Calibration-Defined Bad Pixel Masking
--------------------------------------

UUID: ``B9C4E630-R001-4D92-A102-3G4B7D05E81F``

For each index ``b`` in the calibration-defined bad pixel list ``B``:

``M[b] = False``

where ``b`` is an integer pixel index from ``CalibrationConfig.bad_pixel_indices``. This operation uses numpy advanced indexing: ``M[np.array(B)] = False``.

Dead Pixel Detection Calculation
---------------------------------

UUID: ``B9C4E630-R002-4D92-A102-3G4B7D05E81F``

For each pixel index ``p``, the peak-to-peak variation across the sliding window is computed as:

``range_p = np.ptp(W[:, p])``

where ``np.ptp`` computes the difference between maximum and minimum values along the frame axis. The pixel is classified as dead when:

``if range_p <= dead_pixel_threshold: M[p] = False``

Stuck Pixel Detection Calculation
----------------------------------

UUID: ``B9C4E630-R003-4D92-A102-3G4B7D05E81F``

For each pixel index ``p``, the absolute inter-frame differences are computed as:

``deltas_p = np.abs(np.diff(W[:, p]))``

where ``np.diff`` computes consecutive frame differences along the frame axis. The pixel is classified as stuck or noisy when any delta exceeds the threshold:

``if np.any(deltas_p > stuck_pixel_delta_threshold): M[p] = False``

Saturation Masking Calculation
-------------------------------

UUID: ``B9C4E630-R004-4D92-A102-3G4B7D05E81F``

For the current frame array ``F`` with shape ``(sample_count,)``, saturation is detected element-wise:

``saturation_mask = F >= saturation_adc_count``

The validity mask is updated:

``M[saturation_mask] = False``

Note: The saturation threshold ``saturation_adc_count`` may be wavelength-dependent in later implementations. The current placeholder uses a single global ADC count threshold.

Mask Statistics Calculation
----------------------------

UUID: ``B9C4E630-R005-4D92-A102-3G4B7D05E81F``

The mask statistics dictionary is computed as follows:

* ``total_pixels = sample_count``
* ``valid_pixels = int(np.sum(M))``
* ``dead_pixel_count = number of pixels where M[p] was set False by dead pixel detection``
* ``stuck_pixel_count = number of pixels where M[p] was set False by stuck pixel detection``
* ``saturation_pixel_count = int(np.sum(saturation_mask))``
* ``bad_pixel_count = len(B)``

These statistics are recorded in the pipeline telemetry output.