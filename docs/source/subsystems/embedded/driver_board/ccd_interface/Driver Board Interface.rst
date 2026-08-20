Driver Board Interface
======================

UUID: ``7AB68D84-F976-4944-A5BB-3633E38F8A3B``

The custom CCD driver board shall connect the controller timing functions to the
TCD1304DG and preserve the detector analog output path into the acquisition
input.  The board-level interface shall support:

* routing of fM, SH, and ICG to the detector;
* a continuous detector analog-output path to the ADC boundary;
* power distribution and local decoupling for the detector and analog path;
* grounding, shielding, and filtering practices appropriate for a noise-
  sensitive detector output; and
* continuity inspection for opens and shorts before powered testing.

Oscilloscope checks shall verify timing and signal behavior at the driver-board
or CCD-side interface.  Exact rail values, pin maps, logic levels, termination,
filter values, decoupling values, and acceptance limits are ``Not In Docs`` and
must be supplied by the hardware requirements before implementation review.



