Embedded Architecture
=====================

UUID: ``9F6C2C68-53B8-4B6B-BB9F-42068A583BF3``

The embedded subsystem is built around the STM32F411CEU6.  Its intended role is
to coordinate the TCD1304DG timing signals, digitize the CCD analog output, and
make complete measurement frames available to the host computer.

**Controller responsibilities:**

* generate the fM, SH, and ICG timing signals required by the detector;
* receive host-requested acquisition start, stop, and integration-time settings;
  the application boundary at which each request takes effect is ``Not In
  Docs`` and remains an open shared control contract;
* trigger ADC conversions and transfer the resulting samples using DMA;
* preserve the effective detector data for all 3648 active pixels; and
* hand complete frames, frame identity, and status information to the USB CDC
  transfer boundary.

The controller is responsible for acquisition coordination, not host-side
calibration, wavelength mapping, display, or CSV export.  The exact command
encoding, status encoding, integration-time units and limits, and complete
transported sample geometry are shared-contract items and remain open until
specified by the Integration section.

**Requirement status:** documented intended behavior; firmware alignment is
``Not Started``.



