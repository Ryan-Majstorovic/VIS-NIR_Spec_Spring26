Procedure
=========

UUID: ``Q4W5E6R7-T8Y9-0123-UION-PQ4567890123``

This page documents the step-by-step procedure for applying Quantum Efficiency correction in both live display and export workflows.

Live Display Procedure
----------------------

When a new spectrum frame arrives from the transport layer, the ``SpectrumBuilder._apply_multiplicative_corrections`` method executes the following steps:

1. **Check enable flag**: If ``calibration_config.apply_quantum_efficiency_correction`` is ``False``, skip QE correction entirely and return light counts unchanged.

2. **Build or retrieve QE curve**: Call :meth:`~backend.processing.calibration_manager.CalibrationManager.build_quantum_efficiency_curve` with the current wavelength array. This method interpolates calibration points, normalizes to the reference wavelength, and returns the per-pixel correction factor vector ``q_i``.

3. **Divide light counts by QE curve**: Each pixel's light-tracking count is divided by its corresponding QE correction factor:

   .. code-block:: python

      corrected_counts = light_counts / qe_curve

4. **Divide saturation reference by QE curve**: The saturation reference frame (computed through the same dark subtraction pipeline) is divided by the identical ``qe_curve`` to preserve normalization ratios:

   .. code-block:: python

      saturation_reference_counts = saturation_light_counts / qe_curve

5. **Clip outputs**: Corrected counts are clipped to minimum 0.0; saturation reference counts are clipped to minimum 1e-9 to prevent division by zero in the subsequent normalization stage.
