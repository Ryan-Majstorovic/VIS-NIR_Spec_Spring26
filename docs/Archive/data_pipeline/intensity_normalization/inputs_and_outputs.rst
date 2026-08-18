Inputs and Outputs
==================

UUID: ``I3N4T5S6-N7O8-9012-FLDA-TS3456789012``

This page documents the inputs consumed and outputs produced by the intensity normalization stage.

Inputs
------

.. list-table::
   :header-rows: 1

   * - Name
     - Type
     - Description
   * - ``corrected_counts``
     - ``np.ndarray[float]``
     - Per-pixel light counts after QE correction (output of QE stage).
   * - ``saturation_reference_counts``
     - ``np.ndarray[float]``
     - Per-pixel saturation reference counts, pre-normalized.
   * - ``display_normalization_mode``
     - ``str``
     - Normalization mode string from :class:`~backend.models.config.CalibrationConfig` (``"peak"`` or ``"absolute_saturation"``).

Outputs
-------

.. list-table::
   :header-rows: 1

   * - Name
     - Type
     - Description
   * - ``normalized_intensity``
     - ``np.ndarray[float32]``
     - Per-pixel normalized intensity values in range [0, 1], clipped to valid display bounds.
   * - ``normalization_mode_used``
     - ``str``
     - The normalization mode actually applied (useful for export metadata).

Data Flow Integration
---------------------

The normalized intensity array is written to the :class:`~backend.models.frames.SpectrumFrame.processed_intensity` field and displayed in real-time spectrum plots. In dense HDF5 recording, it is stored as a per-frame dataset at ``/frame/intensity [P]`` with dtype float32 for export-time lookup.
