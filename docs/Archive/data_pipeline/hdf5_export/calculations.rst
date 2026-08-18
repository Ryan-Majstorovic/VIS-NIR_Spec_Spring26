Dense HDF5 and CSV Export Calculations
======================================

UUID: ``H2D3F4G5-H6I7-8901-JKLM-NOPQRSTUVWX``

This page documents the mathematical operations used during dense HDF5 recording and CSV export. The export stage performs minimal calculations -- it primarily reads pre-computed values from upstream pipeline stages (wavelength mapping, bias/dark correction, PRNU/flat-field, QE correction, intensity normalization) and writes them to disk.

Symbols
-------

* ``N_bits``: ADC resolution in bits (e.g., 16 for a 16-bit ADC).
* ``V_ref``: ADC reference voltage (hardware-dependent).

ADC Raw to Volts Conversion
---------------------------

The only calculation performed specifically by the export stage is converting raw ADC counts to volts:

.. code-block:: text

   V = ADC_raw * (V_ref / 2^N_bits)

This linear mapping uses the hardware reference voltage and ADC resolution. The resulting ``V`` value is written to CSV as the ``volts`` column and stored in HDF5 as ``/frame/volts [P]`` during dense recording. All other export columns are passed through from upstream pipeline stages without modification.
