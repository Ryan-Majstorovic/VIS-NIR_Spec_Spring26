Embedded Validation
===================

UUID: ``542C4175-30A6-4498-8BE9-2DDDE4A65002``

Embedded validation should include:

* Oscilloscope timing checks for fM, SH, and ICG.
* ADC/DMA single-frame capture checks for full sample count and waveform shape.
* USB CDC packet checks for header fields, payload length, flags, and frame ID
  continuity.
* Stress checks for USB timeout behavior and dropped-frame counters.
* Regression checks after changing timer, ADC, DMA, USB, or frame-buffer code.

The COM inspector can validate the host-visible stream independently from the
full GUI.



