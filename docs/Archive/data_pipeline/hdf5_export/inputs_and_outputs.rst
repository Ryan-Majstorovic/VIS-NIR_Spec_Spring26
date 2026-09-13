Dense HDF5 and CSV Export Inputs and Outputs
============================================

UUID: ``H3D4F5G6-H7I8-9012-JKLM-NOPQRSTUVWX``

This page documents the inputs consumed and outputs produced by the dense HDF5
recording and CSV export stages. The export stage primarily passes through
pre-computed values from upstream pipeline stages.

Inputs
------

.. list-table::
   :header-rows: 1

   * - Name
     - Type
     - Description
   * - ``adc_counts``
     - ``np.ndarray[int16]``
     - Raw ADC counts per pixel (from transport layer).
   * - ``wavelengths``
     - ``np.ndarray[float32]``
     - Per-pixel wavelength array from wavelength mapping stage.
   * - ``corrected_counts``
     - ``np.ndarray[float32]``
     - Per-pixel light counts after all multiplicative corrections (output of QE stage).
   * - ``normalized_intensity``
     - ``np.ndarray[float32]``
     - Per-pixel normalized intensity in range [0, 1] (output of normalization stage).
   * - ``frame_dark_reference``
     - ``float``
     - Frame-wise dark reference value :math:`\beta_f` from bias/dark correction stage.
   * - ``correction_factor_applied``
     - ``np.ndarray[float32]``
     - Combined flat-field x QE correction factor (static, computed at recorder init).
   * - ``display_normalization_mode``
     - ``str``
     - Normalization mode string from calibration config (``"peak"`` or ``"absolute_saturation"``).

Outputs
-------

.. list-table::
   :header-rows: 1

   * - Name
     - Type
     - Description
   * - ``volts``
     - ``np.ndarray[float32]``
     - Per-pixel voltage values computed from raw ADC counts via ADC reference and resolution.
   * - ``csv_columns``
     - ``tuple[np.ndarray, ...]``
     - Tuple of (wavelengths, adc_counts, corrected_counts, dark_reference, volts, normalized_intensity) for CSV writing.
   * - ``hdf5_datasets``
     - ``dict[str, np.ndarray]``
     - Dictionary mapping HDF5 dataset paths to data arrays for dense binary recording.

HDF5 Dataset Layout
-------------------

Dense recording writes the following datasets:

* ``/frame/volts [F][P]``: Per-frame per-pixel voltage values (float32).
* ``/frame/intensity [F][P]``: Per-frame normalized intensity values (float32).
* ``/frame/corrected [F][P]``: Per-frame corrected light counts (float32).
* ``/dark/frame_dark [F]``: Per-frame dark reference values (float32).
* ``/correction/wavelength [P]``: Static per-pixel wavelength array (float32).
* ``/correction/qe_correction [P]``: Static per-pixel QE correction factor (float32).
* ``/correction/correction_factor_applied [P]``: Static combined correction factor (float32).

Where ``F`` is the frame dimension and ``P`` is the pixel/sample dimension.
Static datasets have no frame dimension.
