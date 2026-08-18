Runtime Correction
==================

At runtime, each incoming raw ADC frame is processed through the bias and dark correction pipeline before being passed to subsequent stages (QE correction, PRNU correction, wavelength mapping, display normalization). The following describes how the host application applies corrections on every frame during live acquisition.

Frame Processing Steps
----------------------

When a new frame arrives from the STM32 over USB CDC, the Python application performs these steps in order:

1. **Load calibration config.** The active ``CalibrationConfig`` is read from disk (loaded at startup or reloaded after a user-initiated save). This provides all additive correction parameters: ``bias_counts``, ``dark_offset_counts``, and ``apply_dark_subtraction``.

2. **Remove master bias ``B_p``.** If the stored bias vector is non-empty, subtract it element-wise from the raw frame:

   ``R^B_p = R_p - B_p``

   If no stored bias exists (empty or not yet captured), skip this step and use the raw frame as-is.

3. **Estimate frame dark reference ``beta_f``.** When ``apply_dark_subtraction`` is true, compute the median of shielded pixels 16 through 28 from the bias-corrected frame:

   ``beta_f = median(R^B_p[16:29])``

4. **Remove stored dark vector ``D_p`` and apply frame dark.** If a stored per-pixel dark offset exists, subtract it after applying the frame dark reference:

   ``L_p = max(beta_f - (R^B_p - D_p), 0)``

   When no stored dark vector is present but dark subtraction is enabled, only the frame dark reference is applied:

   ``L_p = max(beta_f - R^B_p, 0)``

5. **Dark-disabled branch.** When ``apply_dark_subtraction`` is false, convert the inverted CCD readout to positive light-tracking counts using the ADC full-scale value:

   ``L_p = max(FS - R^B_p, 0)``

   where ``FS = 2^N - 1`` for ``N`` resolution bits.

6. **Pass result downstream.** The corrected array ``L_p`` is passed to the multiplicative correction stage (QE or PRNU when enabled), then to wavelength mapping and display normalization.

7. **Preserve metadata.** Raw counts, dark terms, and intermediate values are written to the live frame state, session buffers, and export files for traceability.

Key Implementation Notes
------------------------

* ``B_p`` is captured in-app from buffered covered frames. ``D_p`` is not auto-captured in the current UI and must be loaded from config or pasted into the calibration form.

* ``beta_f`` is measured after ``B_p`` is removed, not from the untouched raw frame.

* The CCD polarity is inverted in this system: larger light corresponds to a lower raw ADC code before the host converts it into positive light-tracking counts.

* Corrections are applied per-frame during live acquisition. When calibration parameters change (new bias captured, dark vector pasted, or toggle of dark subtraction), the latest frame is immediately rebuilt with updated values without requiring new hardware input.