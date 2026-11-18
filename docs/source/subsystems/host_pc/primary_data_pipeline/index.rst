Primary Data Pipeline
=====================

The Host PC Primary Data Pipeline receives raw binary measurement frames, validates frame integrity, executes calibration transformations in numerical order, and outputs aligned, session-ready spectrum records.

.. _uuid-2d3495cb-05f7-4990-9126-110d5070e578:

System Role & Flow
------------------

UUID: :ref:`2D3495CB-05F7-4990-9126-110D5070E578 <uuid-2d3495cb-05f7-4990-9126-110d5070e578>`

The primary data pipeline executes a linear, 5-stage transformation for every measurement frame:

1. **Ingress and ADC Reconstruction:** Unpacks 16-bit little-endian ADC counts from ``CCD1`` packets, validates payload byte length (``sample_count * 2``), and preserves raw counts and frame context.
2. **Bias and Dark Correction:** Subtracts the stored master bias vector :math:`B_p` (if loaded), calculates the frame dark baseline :math:`\beta_f` from optical black pixels ``[16:28]``, and inverts the detector drop to produce positive light counts.
3. **Spectral Corrections:** Multiplies light counts by flat-field intensity factors and interpolated quantum efficiency (QE) response factors.
4. **Wavelength Mapping:** Evaluates polynomial calibration coefficients :math:`\lambda(p) = \sum c_i p^i` across the 3648 effective pixels.
5. **Processed Spectrum Output and Retention:** Computes voltage representations, generates 0-to-1 display signals, downsamples 256-bin spectrogram rows, and bundles data into an immutable ``SpectrumFrame``.

.. _uuid-82ddd480-efc3-48b7-beb6-e3ed17755f65:

Pipeline Stages
---------------

UUID: :ref:`82DDD480-EFC3-48B7-BEB6-E3ED17755F65 <uuid-82ddd480-efc3-48b7-beb6-e3ed17755f65>`

.. list-table::
   :header-rows: 1

   * - Stage
     - Responsibilities
   * - :doc:`ingress_and_adc_reconstruction`
     - Header qualification, payload size verification, 16-bit ADC extraction, and raw data preservation.
   * - :doc:`bias_dark_correction`
     - Master bias vector subtraction, shielded pixel median dark baseline estimation, and optical inversion.
   * - :doc:`spectral_corrections`
     - Multiplicative flat-field intensity array and interpolated quantum efficiency (QE) response correction.
   * - :doc:`wavelength_mapping`
     - Runtime polynomial wavelength assignment and least-squares polynomial regression solver.
   * - :doc:`processed_spectrum_output_and_retention`
     - Voltage scaling, live display normalization, 256-bin spectrogram downsampling, and spectrum record output.

.. toctree::
   :maxdepth: 1

   ingress_and_adc_reconstruction
   bias_dark_correction
   spectral_corrections
   wavelength_mapping
   processed_spectrum_output_and_retention


