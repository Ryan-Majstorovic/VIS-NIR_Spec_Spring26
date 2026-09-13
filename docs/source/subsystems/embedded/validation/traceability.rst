Embedded Traceability
=====================

This local traceability register connects the Embedded intended-behavior pages
to the requirements baseline.  Entries are deliberately medium-granularity so
that each behavior can be reviewed against firmware later without treating
implementation as the source of truth.

.. _embedded-traceability-e1000001:

E1000001
--------

Controller coordination claim in the table below.

.. _embedded-traceability-e1000002:

E1000002
--------

Detector timing claim in the table below.

.. _embedded-traceability-e1000003:

E1000003
--------

Effective-pixel acquisition claim in the table below.

.. _embedded-traceability-e1000004:

E1000004
--------

USB frame-completeness claim in the table below.

.. _embedded-traceability-e1000005:

E1000005
--------

Driver-board interface claim in the table below.

.. _embedded-traceability-e1000006:

E1000006
--------

Calibration and evidence claim in the table below.

.. list-table:: Embedded behavior traceability
   :header-rows: 1

   * - ID
     - Behavior claim
     - Defining pages
     - Alignment state
     - Future evidence location
     - Requirements evidence
   * - ``E1000001``
     - The STM32F411CEU6 coordinates detector timing, acquisition, frame ownership, and USB handoff.
     - ``controller/system_controller/Embedded Architecture``
     - Not Started
     - Firmware review and controller verification
     - Requirements And Metrics; Design Document functional and resource requirements
   * - ``E1000002``
     - The controller generates fM near 2 MHz, ICG with an 8 ms period and 7.388 ms pulse target, and SH with a 10 microsecond pulse target.
     - ``timers/CCD Timing``; timer detail pages
     - Not Started
     - Timing-reference captures
     - Requirements And Metrics; Design Document CCD timing requirements
   * - ``E1000003``
     - Acquisition preserves all 3648 effective detector pixels in order.
     - ``acquisition/adc_dma/ADC And DMA Capture``
     - Not Started
     - ADC/DMA capture evidence and frame-geometry check
     - Requirements And Metrics detector geometry
   * - ``E1000004``
     - A transferred frame is complete and carries frame identity and status information.
     - ``usb_cdc/binary_frame_stream/USB CDC Stream``
     - Not Started
     - Integration contract and USB stream verification
     - Requirements And Metrics USB transfer
   * - ``E1000005``
     - The driver-board interface routes timing and analog signals while supporting power integrity and pre-power continuity checks.
     - ``driver_board/ccd_interface/Driver Board Interface``
     - Not Started
     - Board inspection and interface verification
     - Design Document embedded and EMC design requirements
   * - ``E1000006``
     - Timing-reference and frame-geometry checks produce linked evidence and an explicit unresolved disposition when requirements are missing.
     - ``calibrations/timing_reference``; ``calibrations/frame_geometry``
     - Not Started
     - Test and Verification evidence register
     - Requirements And Metrics; calibration and characterization guidance

Open contract items include total transported sample geometry, packet encoding,
integration-time semantics, ADC trigger details, exact signal ownership,
hardware electrical limits, and evidence retention rules.  These remain
``Not In Docs`` until the responsible section defines them.
