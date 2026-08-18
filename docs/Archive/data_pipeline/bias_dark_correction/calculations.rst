Calculations
============

The host software uses the following symbols for bias and dark correction:

* ``R_p``: raw ADC count at sample or pixel ``p``.
* ``B_p``: stored master bias from covered-frame averaging.
* ``beta_f``: frame-wise dark reference from shielded pixels 16 through 28.
* ``D_p``: stored per-pixel dark-offset vector.
* ``FS``: ADC full-scale count ``2^N - 1`` for ``N`` resolution bits.
* ``L_p``: positive light-tracking counts used by the rest of the pipeline.

Step-by-Step Math
-----------------

1. **Bias capture:**

   ``B_p = mean(covered_frame_k[p])`` over the last ``N`` buffered covered frames selected by ``bias_capture_frame_count``.

2. **Bias-correct the incoming frame:**

   ``R^B_p = R_p - B_p``

3. **Estimate the frame dark reference** when ``apply_dark_subtraction`` is true:

   ``beta_f = median(R^B_p)`` for pixel indices ``16 <= p <= 28``

4. **Convert the inverted CCD readout into light-tracking counts:**

   * Dark-enabled branch:

     ``L_p = max(beta_f - (R^B_p - D_p), 0)``

     This is equivalent to ``max(beta_f - (R_p - B_p - D_p), 0)``.

   * Dark-disabled branch:

     ``L_p = max(FS - R^B_p, 0)``

5. **Apply later multiplicative stages:**

   * Flat-field or PRNU correction multiplies ``L_p`` by the configured correction vector when enabled.
   * QE or response correction divides by the interpolated normalized response curve when enabled.
   * Display normalization then scales the corrected signal by either an absolute saturation reference or the frame peak.

Important Implementation Notes
------------------------------

* ``B_p`` is captured in-app today. ``D_p`` is not auto-captured in the current UI and is instead loaded from config or pasted into the calibration form.
* ``beta_f`` is measured after ``B_p`` is removed, not from the untouched raw frame.
* The CCD polarity is inverted in this system, so larger light corresponds to a lower raw ADC code before the host converts it into positive light-tracking counts.