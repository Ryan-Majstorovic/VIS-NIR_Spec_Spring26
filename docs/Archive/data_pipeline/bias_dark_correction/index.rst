Bias and Dark Correction
========================

UUID: ``D29A5387-FD1F-40F8-9132-0R421ED6F4D9``

The bias and dark correction stage is the first additive stage of the host calibration pipeline. Its job is to remove fixed readout offsets before any wavelength, flat-field, or QE correction is applied. The processing is intentionally host-side so the raw USB ``CCD1`` frame remains available for debugging, recalibration, and export while the calibrated signal can be previewed and saved without changing firmware behavior.

Overview
--------

The current implementation uses two separate terms:

* ``B_p``: a stored master-bias vector captured from recent covered-sensor frames inside the desktop app.
* ``beta_f`` and ``D_p``: a frame-wise dark reference and an optional stored per-pixel dark-offset vector.

The processing order is:

1. Load the active ``CalibrationConfig`` from disk at startup.
2. Receive a raw ADC frame from the STM32 USB stream.
3. Remove the stored master bias ``B_p`` when present.
4. Estimate the current frame dark reference ``beta_f`` from shielded pixels 16 through 28 when dark subtraction is enabled.
5. Remove the stored dark vector ``D_p`` when present.
6. Convert the inverted CCD polarity into positive light-tracking counts.
7. Pass the result to multiplicative correction, wavelength mapping, and display normalization.
8. Preserve the raw counts and the dark terms in export artifacts.

Related Pages
-------------

.. toctree::
   :maxdepth: 1

   runtime_correction
   calibration/index
   calculations
   inputs_and_outputs
   validation
