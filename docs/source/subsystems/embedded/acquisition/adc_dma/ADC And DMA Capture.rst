ADC And DMA Capture
===================

UUID: ``8F4E69AC-05DC-4E3C-8CF5-4E84DA7BBE2A``

ADC1 samples the CCD analog output on timer-triggered conversions. DMA2 Stream0
moves samples into the active frame slot.

The current frame layout is:

* 32 leading dummy samples.
* 3648 effective light-sensitive pixels.
* 14 trailing dummy samples.
* 3694 total unsigned 16-bit little-endian samples carrying 12-bit ADC results.

The host app should not invent samples when frame size changes or a malformed
frame arrives. Current GUI behavior logs a frame-size warning and plots what was
received when the layout does not match the configured full-frame geometry.



