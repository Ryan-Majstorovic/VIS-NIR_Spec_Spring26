Timing Reference Procedure
==========================

UUID: ``91D8792D-AE7E-430D-ABCD-1999DB7D404F``

1. Flash the firmware revision under test.
2. Connect the oscilloscope to the fM, SH, ICG, and ADC trigger monitor points.
3. Power the driver board and confirm startup USB CDC banner lines.
4. Measure fM continuously before capture.
5. Trigger on ICG and capture SH plus the ADC trigger monitor during one frame.
6. Compare measured periods and pulse widths with the timer reference values.
7. Save the oscilloscope captures and record the firmware revision.



