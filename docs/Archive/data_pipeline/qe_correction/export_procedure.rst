Export Procedure
================

UUID: ``Q5W6E7R8-T9Y0-1234-UION-PQ5678901234``

This page documents the step-by-step procedure for applying Quantum Efficiency correction during export workflows. It covers QE-specific operations only; upstream stages (bias subtraction, dark offset, wavelength mapping) are documented in their respective pages.

CSV Export via SpectrumBuilder
------------------------------

When ``SpectrumBuilder.build_export_columns()`` is called, the QE stage executes these steps:

1. **Retrieve or build QE curve**: Call :meth:`~backend.processing.calibration_manager.CalibrationManager.build_quantum_efficiency_curve` with the current wavelength array. This interpolates calibration points, normalizes to the reference wavelength, and returns the per-pixel correction factor vector ``q_i``.

2. **Divide corrected counts by QE curve**: The flat-field-corrected light counts (output of PRNU stage) are divided by the QE correction factor:

   .. code-block:: python

      corrected_counts = prnu_corrected_counts / qe_curve

3. **Divide saturation reference by QE curve**: The saturation reference frame undergoes identical QE division to preserve normalization ratios:

   .. code-block:: python

      saturation_reference = saturation_light_counts / qe_curve

4. **Clip outputs**: Corrected counts are clipped to minimum 0.0; saturation reference is clipped to minimum 1e-9 to prevent division by zero in the subsequent normalization stage.

Dense HDF5 Recording via DenseFrameProcessor
--------------------------------------------

When dense binary recording is active, QE-specific operations:

1. **Static curve computation**: Upon ``DenseBinaryRecorder.start()``, :func:`_build_qe_correction` computes the QE curve once from the calibration configuration and wavelength grid. The result is stored as a static float32 dataset at ``/correction/qe_correction [P]`` in the HDF5 file.

2. **Combined correction factor**: The QE curve is multiplied with the system response (flat-field) vector to produce ``correction_factor = system_response * qe_correction``, stored statically at ``/correction/correction_factor_applied [P]``.

3. **Per-frame application**: Each ``DenseFrameProcessor.build_record()`` call multiplies light counts by the pre-computed combined correction factor:

   .. code-block:: python

      processed_counts = light_counts * self._correction_factor
      saturation_reference = saturation_light_counts * self._correction_factor

HDF5-to-CSV Export via export_hdf5_to_csv
-----------------------------------------

The :func:`export_hdf5_to_csv` function reads the static ``/correction/correction_factor_applied`` dataset (which already includes QE multiplication) and writes per-pixel values to CSV alongside raw ADC, volts, and intensity columns. No on-the-fly QE computation is needed during export because all correction factors are pre-computed and stored as static datasets.