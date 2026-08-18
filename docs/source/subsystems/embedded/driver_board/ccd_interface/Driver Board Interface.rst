Driver Board Interface
======================

UUID: ``7AB68D84-F976-4944-A5BB-3633E38F8A3B``

The custom CCD driver board connects the STM32 timing/acquisition signals to
the TCD1304DG and supports the analog signal path.

Interface checks should cover:

* CCD timing inputs: fM, SH, and ICG.
* CCD analog output path into ADC1 input PA0 / ADC1_IN0.
* Power rails and local decoupling near the CCD and analog path.
* Continuity checks for opens and shorts before powered testing.
* Oscilloscope verification of signal levels and timing at the board interface.

The design document identifies grounding, decoupling, shielding, and filtering
as important because the detector output is noise-sensitive.



