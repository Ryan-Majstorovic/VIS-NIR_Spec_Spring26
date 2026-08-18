Embedded Architecture
=====================

UUID: ``9F6C2C68-53B8-4B6B-BB9F-42068A583BF3``

The embedded subsystem is built around the STM32F411CEU6. Its role is to drive
the TCD1304DG timing signals, digitize the CCD analog output, and transfer
complete line frames to the host computer.

Core responsibilities:

* Generate fM, SH, and ICG timing with hardware timers.
* Trigger ADC1 conversions at the selected readout cadence.
* Use DMA to capture a full line frame with low CPU overhead.
* Package data into the ``CCD1`` binary frame format.
* Stream frames over USB CDC with frame IDs and status flags.

The current active frame shape is 3694 total samples, composed of leading dummy
samples, 3648 effective pixels, and trailing dummy samples.



