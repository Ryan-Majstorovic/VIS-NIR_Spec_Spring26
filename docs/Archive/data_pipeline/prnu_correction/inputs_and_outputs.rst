Inputs and Outputs
==================

This page documents the inputs consumed and outputs produced by the PRNU
correction stage.

Inputs
------

.. list-table::
   :header-rows: 1

   * - Name
     - Type
     - Description
   * - ``values``
     - ``np.ndarray[float]``
     - Per-pixel spectral values after upstream additive correction and wavelength mapping.
   * - ``correction_factors``
     - ``Sequence[float]``
     - Per-pixel multiplicative intensity-correction factors loaded from ``CalibrationConfig.intensity_correction``.
   * - ``sample_indices``
     - ``Sequence[int] | None``
     - Optional active-pixel index mapping used when the correction array is defined in a different native coordinate system.
   * - ``qe_curve_values``
     - ``np.ndarray[float] | None``
     - Optional wavelength-dependent QE factors multiplied into the PRNU factors before application when QE correction is enabled.

Outputs
-------

.. list-table::
   :header-rows: 1

   * - Name
     - Type
     - Description
   * - ``corrected_counts``
     - ``np.ndarray[float]``
     - Per-pixel signal after multiplicative PRNU normalization.
   * - ``combined_correction_factors``
     - ``np.ndarray[float]``
     - Effective per-pixel factor vector applied to the active frame after optional sample-index lookup and QE integration.
   * - ``uncorrected_passthrough``
     - ``np.ndarray[float]``
     - Returned data path when no PRNU factors are configured, preserving pipeline continuity without altering values.
