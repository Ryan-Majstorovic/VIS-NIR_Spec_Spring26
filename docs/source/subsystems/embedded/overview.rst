Embedded System Overview
========================

.. note::

   Insert the user-provided Embedded architecture diagram here after the Visio
   source and image are available.

.. _uuid-dd4f5c01-b4f1-4809-ad9e-68b3059bebeb:

System Role
-----------

UUID: :ref:`DD4F5C01-B4F1-4809-AD9E-68B3059BEBEB <uuid-dd4f5c01-b4f1-4809-ad9e-68b3059bebeb>`

**Summary:** The Embedded system shall coordinate detector control, timing,
digitization, frame formation, the driver-board interface, and USB CDC transfer
to convert the TCD1304DG analog output into complete measurement frames for the
Host PC system.

**Expected Outcome:** The Embedded system shall provide complete frames that
preserve all 3648 effective detector samples in acquisition order and include
the identity and status needed at the Integration boundary.

**Rationale:** Coordinating these functions within one subsystem preserves the
timing relationship between detector readout, sample acquisition, frame
completion, and transfer so the host does not receive data whose acquisition
state is ambiguous.

.. _uuid-b5095b6c-c6fd-4966-9685-ae6966ceda21:

System Objectives
-----------------

UUID: :ref:`B5095B6C-C6FD-4966-9685-AE6966CEDA21 <uuid-b5095b6c-c6fd-4966-9685-ae6966ceda21>`

**Objective 1:** **Timing and acquisition.** The Embedded system shall generate
the fM, SH, ICG, and ADC-trigger signals and preserve all 3648 effective
detector samples in acquisition order.

**Rationale:** Stable timing and ordered sampling preserve the relationship
between detector position and measured signal.

**Objective 2:** **Transport and control.** The Embedded system shall transfer
each complete frame with its frame identity and status over USB CDC and process
start, stop, and integration-time requests through the Integration interface.

**Rationale:** A defined transport and control boundary prevents partial frames
or unresolved commands from being treated as completed measurements.

**Objective 3:** **Verification evidence.** The Embedded system shall produce
requirements-linked test records for detector timing, frame acquisition, USB
transfer, control handling, and driver-board operation.

**Rationale:** Requirements-linked records make failures traceable to the
Embedded function that produced them.

.. _uuid-8e892af2-4ec5-40ac-922b-4e1dce44264a:

System Relationship
-------------------

UUID: :ref:`8E892AF2-4EC5-40AC-922B-4E1DCE44264A <uuid-8e892af2-4ec5-40ac-922b-4e1dce44264a>`

.. list-table::
   :header-rows: 1

   * - System
     - Primary Responsibility
     - Downstream Or Adjacent Relationship
   * - Controller
     - The Embedded controller system shall coordinate timing, acquisition, frame ownership, and supported host-control application.
     - The Embedded controller system shall keep control requests and frame ownership coordinated throughout each capture.
   * - Timers
     - The Embedded timer system shall generate the required fM, SH, ICG, and ADC-trigger timing at the detector and acquisition boundaries.
     - The Embedded timer system shall provide repeatable timing relationships for detector charge transfer and ADC sampling.
   * - Acquisition
     - The Embedded acquisition system shall digitize the detector output and form complete measurement frames containing all 3648 effective pixels.
     - The Embedded acquisition system shall preserve detector-position order for downstream spectral processing.
   * - USB CDC
     - The Embedded USB CDC system shall transfer complete measurement frames and supported control outcomes through the Integration interface contract.
     - The Embedded USB CDC system shall use the shared Integration contract so the Host PC system can distinguish measurement content from control status.
   * - Driver Board
     - The Embedded driver-board system shall preserve detector timing, power integrity, and analog-signal integrity between the controller, TCD1304DG, and acquisition input.
     - The Embedded driver-board system shall prevent electrical-interface degradation from invalidating detector timing or digitized measurements.
   * - Calibrations
     - The Embedded calibration system shall produce timing-reference and effective-frame-geometry evidence under the approved capture conditions.
     - The Embedded calibration system shall provide evidence that acquired sample positions correspond to the detector behavior used by downstream processing.
   * - Validation
     - The Embedded validation system shall record the applicable requirement, configuration, evidence artifact, and disposition for each Embedded check.
     - The Embedded validation system shall make results repeatable, comparable across revisions, and traceable to the requirement being evaluated.

.. _uuid-704ce22a-40c3-4f92-ac0a-387165454c5a:

Integration Boundary
--------------------

UUID: :ref:`704CE22A-40C3-4F92-AC0A-387165454C5A <uuid-704ce22a-40c3-4f92-ac0a-387165454c5a>`

**Summary:** The Embedded system shall provide complete measurement frames,
frame identity, status information, and supported control outcomes at the
shared host-device boundary defined by
:doc:`Integration Interfaces <../integration/interfaces/Interfaces>`. The
Integration system shall define the packet marker, header, field widths, byte
order, status meanings, acknowledgment behavior, recovery behavior,
control-application boundary, and transported geometry beyond the 3648
effective detector samples. These open interface details are ``Not In Docs``.

**Expected Outcome:** The Embedded system shall remain independently reviewable
without duplicating the Integration wire contract or the Host PC system's
correction, wavelength mapping, visualization, retention, and export behavior.

**Rationale:** A single Integration boundary definition prevents the Embedded
and Host PC systems from assigning conflicting meanings to the same exchange
and keeps host-side calibration policy out of the detector-control subsystem.

Related Pages
-------------

* :doc:`Controller <controller/Controller>`
* :doc:`Calibrations <calibrations/Calibrations>`
* :doc:`Timers <timers/Timers>`
* :doc:`Acquisition <acquisition/Acquisition>`
* :doc:`USB CDC <usb_cdc/USB CDC>`
* :doc:`Driver Board <driver_board/Driver Board>`
* :doc:`Validation <validation/Validation>`
