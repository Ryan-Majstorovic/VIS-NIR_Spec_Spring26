Data Pipeline
=============

The Data Pipeline processes raw spectral frames from the transport layer through a series of calibration, correction, and normalization stages before display or export. This page documents the pipeline architecture, stage ordering, and data flow between subsystems.

Pipeline Stages
---------------

.. toctree::
   :maxdepth: 1

   data_reception/index
   frame_validation/index
   adc_extraction/index
   bias_dark_correction/index
   bad_pixel_masking/index
   wavelength_mapping/index
   prnu_correction/index
   qe_correction/index
   intensity_normalization/index
   hdf5_export/index

Data Flow
---------

Raw ADC frames enter via the data reception stage, pass through packet integrity validation (frame_validation), extract per-pixel ADC counts (adc_extraction), undergo bias subtraction and dark offset correction (bias_dark_correction), apply bad pixel saturation masking (bad_pixel_masking), map sample indices to wavelengths (wavelength_mapping), correct for PRNU/flat-field response (prnu_correction), divide by quantum efficiency (qe_correction), normalize to displayable intensity (intensity_normalization), and finally persist to disk via dense HDF5 recording or CSV export (hdf5_export).

Each stage consumes outputs from upstream stages and produces normalized data for downstream consumption. Calibration vectors computed at initialization (wavelengths, QE curve, flat-field) are shared across all multiplicative correction stages.