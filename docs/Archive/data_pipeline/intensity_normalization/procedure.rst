Procedure
=========

UUID: ``I4N5T6S7-N8O9-0123-FLDA-TS4567890123``

This page documents the step-by-step procedure for applying intensity normalization in both live display and export workflows.

Live Display Procedure
----------------------

When a new spectrum frame arrives from the transport layer, the ``SpectrumBuilder._normalize_intensity`` method executes the following steps:

1. **Check enable flag**: If no multiplicative corrections were applied (all disabled), skip normalization and return light counts as-is.

2. **Select normalization mode**: Read ``display_normalization_mode`` from :class:`~backend.models.config.CalibrationConfig`:

   * ``"peak"`` mode: compute frame peak from corrected counts.
   * ``"absolute_saturation"`` mode: use the pre-computed saturation reference peak.

3. **Compute normalization divisor**:

   * Peak mode: ``divisor = max(max(corrected_counts), 1e-9)``
   * Absolute mode: ``divisor = max(max(saturation_reference), 1e-9)``

4. **Normalize and clip**: Divide each pixel's corrected count by the divisor, then clip to valid display bounds:

   .. code-block:: python

      normalized_intensity = np.clip(corrected_counts / divisor, 0.0, 1.0)

5. **Store in frame**: Write ``normalized_intensity`` to :class:`~backend.models.frames.SpectrumFrame.processed_intensity` for plot rendering.

