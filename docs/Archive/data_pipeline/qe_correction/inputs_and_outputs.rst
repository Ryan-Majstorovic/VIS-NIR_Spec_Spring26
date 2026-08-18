Inputs and Outputs
==================

UUID: ``Q3W4E5R6-T7Y8-9012-UION-PQ3456789012``

This page documents the inputs consumed and outputs produced by the Quantum Efficiency correction stage.

Inputs
------

.. list-table::
   :header-rows: 1

   * - Name
     - Type
     - Description
   * - ``light_counts``
     - ``np.ndarray[float]``
     - Per-pixel light-tracking counts from dark subtraction (output of bias/dark correction stage).
   * - ``saturation_light_counts``
     - ``np.ndarray[float]``
     - Per-pixel saturation reference counts, processed through the same dark subtraction pipeline.
   * - ``wavelengths``
     - ``np.ndarray[float]``
     - Wavelength array in nanometers from wavelength mapping stage (same length as pixel count).
   * - ``quantum_efficiency_points``
     - ``list[QuantumEfficiencyPoint]``
     - Calibration points with ``wavelength_nm`` and ``relative_value`` fields. May be empty if QE correction is disabled.
   * - ``quantum_efficiency_normalization_wavelength_nm``
     - ``float | None``
     - Wavelength at which the QE curve is normalized to unity. If ``None``, the maximum calibration value is used as the reference.
   * - ``apply_quantum_efficiency_correction``
     - ``bool``
     - Flag from :class:`~backend.models.config.CalibrationConfig` that enables or disables the entire stage.

Outputs
-------

.. list-table::
   :header-rows: 1

   * - Name
     - Type
     - Description
   * - ``corrected_counts``
     - ``np.ndarray[float]``
     - Per-pixel light counts after QE division, clipped to minimum of 0.0.
   * - ``saturation_reference_counts``
     - ``np.ndarray[float]``
     - Per-pixel saturation reference counts after the same QE division, clipped to minimum of 1e-9.
   * - ``qe_correction_curve``
     - ``np.ndarray[float32]``
     - Static per-pixel correction factor vector (stored in HDF5 at ``/correction/qe_correction [P]``).

Data Flow Integration
---------------------

The QE-corrected counts flow into the display normalization stage, which divides by either the saturation reference or frame peak. In dense recording, both ``corrected_counts`` and ``saturation_reference_counts`` are written to HDF5 datasets for export-time lookup.
