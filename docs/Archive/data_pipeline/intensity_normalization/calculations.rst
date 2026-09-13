Calculations
============

UUID: ``I2N3T4S5-N6O7-8901-FLDA-TS2345678901``

This page documents the mathematical operations used for intensity normalization in both live display and export workflows.

Symbols
-------

* ``L^{QE}_p``: light-tracking counts at pixel ``p`` after QE correction (output of QE stage).
* ``q_p``: per-pixel QE correction factor from calibration.
* ``S_p``: saturation reference count at pixel ``p`` (light counts when detector is fully saturated).
* ``I_p``: normalized intensity value at pixel ``p``, range [0, 1].
* ``\max(L^{QE})``: peak corrected light count in the current frame.
* ``\max(S)``: global saturation reference peak from calibration configuration.

Normalization Modes
-------------------

The system supports two normalization modes controlled by ``display_normalization_mode`` in :class:`~backend.models.config.CalibrationConfig`:

Mode 1: Peak Normalization (``"peak"`` or default)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each frame is normalized to its own peak value. This mode maximizes visual contrast for weak signals but prevents direct cross-frame intensity comparisons:

.. code-block:: text

   I_p = L^{QE}_p / max(\max(L^{QE}), 1e-9)

Mode 2: Absolute Saturation Normalization (``"absolute_saturation"``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each frame is normalized to the absolute saturation reference, preserving cross-frame intensity ratios for quantitative analysis:

.. code-block:: text

   I_p = L^{QE}_p / max(\max(S), 1e-9)

Clipping and Bounds
-------------------

All normalized intensities are clipped to the valid display range:

.. code-block:: text

   I_p = clip(I_p, LIVE_DISPLAY_CLIP_MIN, NORMALIZED_SIGNAL_MAX)

Where ``LIVE_DISPLAY_CLIP_MIN`` is typically 0.0 and ``NORMALIZED_SIGNAL_MAX`` is typically 1.0. The minimum clipping prevents negative intensities from noise; the maximum clipping ensures values remain within displayable bounds.

Dense Recording Intensity Storage
---------------------------------

In dense HDF5 recording, per-frame normalized intensity arrays are stored at ``/frame/intensity [P]`` with dtype float32. Each frame's intensity dataset is appended sequentially during the worker thread flush cycle. The correction factor applied (including QE multiplication) is stored statically at ``/correction/correction_factor_applied [P]`` for export-time lookup.