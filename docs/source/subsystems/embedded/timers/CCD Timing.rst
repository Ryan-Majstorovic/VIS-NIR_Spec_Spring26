CCD Timing
==========

The timing contract defines electronic-shutter exposure, physical frame timing,
and the host-visible application boundary. Internal timer segments are not
measurement frames. These requirements adopt the approved integration-timing
plan; implementation evidence and physical qualification are recorded separately.

.. _uuid-0b79e0a3-6cee-4957-a820-c4b119b6ff9e:

Integration settings
--------------------

UUID: ``0B79E0A3-6CEE-4957-A820-C4B119B6FF9E``

**Requirement:** The Embedded timing system shall accept integer-microsecond integration durations from 10 us through 5 s, requiring exact divisors of 8000 us at and below 8 ms, to preserve the repeating SH-to-frame phase.

**Rationale:** Exact divisors return SH to the same phase at every 125 Hz frame boundary; exposures above 8 ms instead define their own frame period.

.. _uuid-5beb122e-3812-4344-9bfa-2a5a169db46a:

Physical waveforms
------------------

UUID: ``5BEB122E-3812-4344-9BFA-2A5A169DB46A``

**Requirement:** The Embedded timing system shall preserve a 6 us high duration for every emitted SH pulse and a 7.388 ms ICG-high readout duration under every supported integration setting to provide constant shift-gate and readout windows.

**Rationale:** Changing only the low intervals preserves charge-transfer pulse shape and the time available to acquire the complete detector line.

SH repeats continuously at the selected integration duration. The physical
frame period is ``max(8000, integration_us)`` microseconds. ICG-low is the
physical frame period minus 7388 microseconds. Below 8 ms, multiple SH pulses
occur within one frame, using the detector electronic-shutter function.

.. _uuid-16830605-1e4b-4fb2-9ba6-b7fbd7d8a739:

Common phase reference
----------------------

UUID: ``16830605-1E4B-4FB2-9BA6-B7FBD7D8A739``

**Requirement:** The Embedded timing system shall establish SH and ICG from a common hardware startup reference, with SH rising 0.5 us after ICG falling and ICG rising while the detector master clock is high, to provide repeatable detector transfer timing.

**Rationale:** Independent software starts introduce an uncontrolled initial offset even when all timer periods share a common clock.

The master-clock target remains 2 MHz +/- 0.1%. SH is independent of ICG:
ICG interrupts do not reset SH or stretch individual pulses. The detector
requires ICG-falling to SH-rising separation of 0.1--1 us, SH-high of at least
1 us, and SH-falling to ICG-rising separation of at least 1 us. Actual board
propagation and ICG-rising placement inside master-clock high remain physical
verification items.

.. _uuid-7cc8b51f-02fe-46a9-ba40-78a5910fc943:

Integration application boundary
--------------------------------

UUID: ``7CC8B51F-02FE-46A9-BA40-78A5910FC943``

**Requirement:** The Embedded acquisition system shall finish the current physical frame before reinitializing timing for an accepted integration change and shall withhold the initial incomplete-history exposure after restart to publish only complete exposures.

**Rationale:** The first transferred line after startup may contain charge accumulated under the previous timing or an unknown initial state.

.. _uuid-41efb7fe-f8c2-4d7b-b8fd-1ea65942c687:

Hardware capture start
----------------------

UUID: ``41EFB7FE-F8C2-4D7B-B8FD-1EA65942C687``

**Requirement:** The Embedded acquisition system shall arm ADC/DMA before ICG rises and start the 500 ksample/s conversion clock from that physical readout edge through hardware triggering to acquire all 3694 transported samples within the readout window.

**Rationale:** Hardware triggering removes interrupt-latency variation from sampling phase, while the final conversion must finish before the next detector transfer.

The first conversion-trigger target is 0.5 us after ICG rises; subsequent
triggers are spaced by 2 us. With the configured 24 MHz ADC clock, 15-cycle
sampling and 12-cycle conversion, the calculated final completion is
7387.625 us after ICG rises, before the 7388 us readout ends. Pixel identity
and analog settling at this phase still require OS measurement.

.. _uuid-669a8b5f-b109-43a2-916e-286fc4b58b87:

Timing commands and confirmation
--------------------------------

UUID: ``669A8B5F-B109-43A2-916E-286FC4B58B87``

**Requirement:** The Host PC integration controller shall retain a change as pending until device application confirmation and a matching complete frame are received to report only device-confirmed integration settings.

**Rationale:** Acknowledgment and matching frame metadata prevent requested settings from being substituted for settings actually used for acquisition.

The request is ``INTEG <integer_microseconds>\n``. Responses are:

* ``PENDING INTEG <microseconds>`` after request acceptance;
* ``OK INTEG <microseconds> <first_valid_frame_id>`` after a complete new exposure;
* ``ERR INTEG INVALID``, ``BUSY``, ``OVERFLOW``, or ``TIMING`` on failure.

One request may be pending. The host timeout is the old frame interval plus
twice the requested frame interval, plus one second, allowing the current old
exposure to finish, the incomplete new exposure to be discarded, and a complete
new exposure to be confirmed. A timeout does not change
frame metadata. Numeric entry rejects unsupported values and displays adjacent
supported durations; step controls traverse supported settings without rounding.

.. _uuid-a5fb7d05-c833-4808-8a1d-a59a78f471aa:

Per-frame timing metadata
-------------------------

UUID: ``A5FB7D05-C833-4808-8A1D-A59A78F471AA``

**Requirement:** The Embedded stream and Host PC recording systems shall preserve each frame's actual integration duration through processing, recording, and export to select exposure-dependent calibration using acquisition settings.

**Rationale:** A calibration captured at a different integration time cannot be treated as the matching dark reference for the current exposure.

CCD1 version 2 appends one little-endian uint32 ``integration_us`` to the
version-1 24-byte header, making a 28-byte header. The sample payload and geometry
are unchanged. Version-1 frames retain unknown integration time. Dense HDF5
version 2 stores ``/frame/integration_us`` (zero means unknown) and
``/frame/dark_calibration_applied``. Legacy recordings remain readable with
unknown timing; CSV conversion preserves the stored duration and correction state.
A stored dark vector is applied only when its explicitly saved integration
duration exactly matches the frame duration.

.. _uuid-964ee57a-1df7-4884-b73c-7c2573b23da0:

Timing fault response
---------------------

UUID: ``964EE57A-1DF7-4884-B73C-7C2573B23DA0``

**Requirement:** The Embedded timing system shall stop valid-frame publication when timer scheduling or ADC/DMA acquisition fails to prevent invalid timing from being presented as valid measurements.

**Rationale:** Continuing publication after loss of timing control can conceal a change in detector transfer or pixel sampling phase.

.. _uuid-753a0172-67b9-49f8-9542-bcf23f37b044:

Physical acceptance
-------------------

UUID: ``753A0172-67B9-49F8-9542-BCF23F37B044``

**Requirement:** The Test and Verification system shall measure master clock, SH, ICG, ADC trigger, and OS at the detector interface during startup, integration changes, and USB/DMA load to qualify physical timing.

**Rationale:** Software schedule models cannot establish output-driver propagation, analog settling, or the timing of actual detector signals.

**Implementation evidence (2026-11-01):** Firmware builds with the STM32
GNU toolchain. Automated tests execute the production C schedule generator
in an ARM emulator and model shadow/DMA sequencing, including wraparound.
These checks do not emulate STM32 peripherals.

**Qualification status:** Not physically qualified; no firmware flashing or
oscilloscope acceptance is claimed.

.. warning::

   A calculated edge conflict remains in the approved waveform constants.
   At 10 us SH repetition, SH is high from 610.5 to 616.5 us after ICG falls,
   while the fixed 612 us ICG-low window ends at 612 us. ICG therefore rises
   during SH-high. The corresponding waveform conformance test is an explicit
   expected failure. Resolution requires agreement on the ICG-high window:
   one proposed correction is 8 us ICG-low and 7992 us ICG-high at 125 Hz,
   retaining 7388 us of ADC readout inside that high window. These alternative
   constants have not been applied.


Required bench cases include every short divisor; 8 ms <-> 8001 us;
10 ms; 12.5 ms; 32 ms <-> 32001 us; 100.001 ms; and 5 s, in both transition
directions. Check 6 us emitted SH pulses, 7.388 ms ICG-high, absence of edges
at internal segment boundaries, constant pixel order, complete final conversion,
marked transition gaps, and correct first-valid-frame confirmation.

**Source evidence:** `Toshiba TCD1304DG timing requirements, page 8
<https://toshiba.semicon-storage.com/info/docget.jsp?did=13709&prodName=TCD1304DG>`_,
and `ST RM0383 timer synchronization and DMA
<https://www.st.com/resource/en/reference_manual/DM00119316.pdf>`_.
