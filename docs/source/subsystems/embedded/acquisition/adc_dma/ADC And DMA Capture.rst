ADC And DMA Capture
===================

UUID: ``8F4E69AC-05DC-4E3C-8CF5-4E84DA7BBE2A``

The acquisition path shall sample the CCD analog output from timer-triggered
ADC conversions and use DMA to move samples into frame storage with bounded CPU
intervention.

**Effective detector content:** Each accepted capture shall preserve all 3648
effective detector pixels in their acquisition order.  The requirement does
not currently define the number or placement of non-effective samples, so the
total transported sample count, dummy regions, sample width, byte order, ADC
trigger frequency, sample phase, input range, clipping behavior, and buffer
ownership are ``Not In Docs`` open requirements.

**Frame completion:** A frame is eligible for transfer only after the required
effective samples have been acquired and the controller has recorded whether
the capture completed normally.  A partial or invalid capture shall be
identified as such rather than silently padded or presented as a complete
measurement.

**Requirement status:** documented intended behavior; ADC/DMA implementation
alignment is ``Not Started``.



