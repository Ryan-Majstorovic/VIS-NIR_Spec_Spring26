Calculations
============

UUID: ``Q2W3E4R5-T6Y7-8901-UION-PQ2345678901``

This page documents the mathematical operations used to compute the QE correction curve from calibration points and apply it to spectral data.

Symbols
-------

* ``\lambda_i``: wavelength at pixel index ``i``, computed by the wavelength mapping stage.
* ``QE(\lambda)``: raw relative quantum efficiency value at wavelength ``\lambda`` from calibration points.
* ``\lambda_{norm}``: normalization wavelength from ``quantum_efficiency_normalization_wavelength_nm``.
* ``QE_{ref}``: quantum efficiency value at the normalization wavelength, or the maximum of all calibration values if no normalization wavelength is set.
* ``q_i``: final per-pixel QE correction factor applied to light counts.
* ``L_p``: light-tracking counts from dark subtraction (output of the bias/dark stage).
* ``L^{QE}_p``: light counts after QE division.

Step-by-Step Math
-----------------

1. **Sort calibration points by wavelength:**

   Calibration points are sorted ascending by wavelength before interpolation:

   ``\{(\lambda_{(j)}, QE_{(j)})\}_{j=1}^{M}`` where ``\lambda_{(1)} < \lambda_{(2)} < ... < \lambda_{(M)}``.

2. **Linear interpolation onto the pixel wavelength grid:**

   For each pixel wavelength ``\lambda_i``, the raw QE value is interpolated:

   ``QE_{raw}[i] = interp(\lambda_i, \{\lambda_{(j)}\}, \{QE_{(j)}\})``

   The :func:`numpy.interp` function is used with ``left`` and ``right`` extrapolation to cover wavelengths outside the calibration range.

3. **Normalize to the reference wavelength:**

   The reference normalization value is computed:

   * If ``\lambda_{norm}`` is set:
   
     ``QE_{ref} = interp(\lambda_{norm}, \{\lambda_{(j)}\}, \{QE_{(j)}\})``

   * Otherwise (no normalization wavelength):
   
     ``QE_{ref} = max(QE_{(j)})``  # maximum of all calibration values

4. **Clip and compute correction factor:**

   The normalized curve is clipped to avoid division by zero, then inverted:

   ``qe_{normalized}[i] = clip(QE_{raw}[i] / QE_{ref}, 1e-9, None)``
   
   ``q_i = 1.0 / qe_{normalized}[i]``

5. **Apply to light counts:**

   The correction factor multiplies the light-tracking counts from dark subtraction:

   ``L^{QE}_p = max(L_p * q_p, 0.0)``

   The same ``q_i`` vector is applied to both the live signal and the saturation reference frame to preserve consistent normalization ratios.

Important Implementation Notes
------------------------------

* The QE correction curve is computed once during recorder initialization (via :func:`_build_qe_correction`) or on-demand via :meth:`~backend.processing.calibration_manager.CalibrationManager.build_quantum_efficiency_curve`.
* In dense HDF5 recording, the static ``/correction/qe_correction [P]`` dataset stores the per-pixel correction factor with dtype float32.
* The system response correction (flat-field) and their product (``correction_factor_applied``) are also stored as static datasets for per-pixel lookup during export.