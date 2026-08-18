Quantum Efficiency Correction
==============================

UUID: ``Q1W2E3R4-T5Y6-7890-UION-PQ1234567890``

The Quantum Efficiency (QE) correction stage compensates for the wavelength-dependent sensitivity of the CCD sensor. After dark subtraction and bad pixel masking, each pixel's count is divided by an interpolated QE curve to produce a spectrally flat response to uniform illumination. This section documents how the QE correction factor is computed from calibration points, applied to both the live signal and its saturation reference, and stored in dense HDF5 recordings.

Related Pages
-------------

.. toctree::
   :maxdepth: 1

   calculations
   inputs_and_outputs
   procedure
   export_procedure
