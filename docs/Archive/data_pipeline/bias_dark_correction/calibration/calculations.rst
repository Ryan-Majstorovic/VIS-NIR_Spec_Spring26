Calculations
============

The calibration process uses the following symbols:

* ``R_p``: raw ADC count at pixel or sample ``p`` from a light-blocked frame.
* ``B_p``: computed master bias vector for pixel ``p``.
* ``D_p``: optional per-pixel dark offset vector.
* ``N``: number of buffered covered frames used in the capture.

Bias Capture Calculation
------------------------

When **Capture B_p** is run, the app computes the element-wise mean across all buffered covered frames:

``B_p = (1/N) * Σ_{k=1}^{N} R_{p,k}``

where ``R_{p,k}`` is the raw ADC count at pixel ``p`` in the ``k``-th buffered covered frame. The result replaces any previously stored bias vector in ``bias_counts``.

Dark Offset Calculation
-----------------------

If a dark reference measurement is captured separately (not yet auto-captured in the current UI), the per-pixel dark offset would be computed as:

``D_p = R_{dark,p} - B_p``

where ``R_{dark,p}`` is the raw count at pixel ``p`` from a longer-exposure dark frame. In the current implementation, ``D_p`` must be loaded from config or pasted manually into the calibration form.

Storage
-------

The computed values are written to:

* ``bias_counts`` in ``CalibrationConfig`` for ``B_p``.
* ``dark_offset_counts`` in ``CalibrationConfig`` for ``D_p`` (if available).