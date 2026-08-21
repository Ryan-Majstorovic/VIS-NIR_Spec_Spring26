Host PC System Overview
=======================

.. note::

   Insert the user-provided Host PC architecture diagram here after the Visio
   source and image are available.

.. _uuid-42e97793-9f90-4eb8-9757-fde4d6527dbc:

System Role
-----------

UUID: :ref:`42E97793-9F90-4EB8-9757-FDE4D6527DBC <uuid-42e97793-9f90-4eb8-9757-fde4d6527dbc>`

**Summary:** The Host PC system shall coordinate device connection and
acquisition control, accept and process complete measurement frames, present
processed spectra and acquisition status to the operator, and retain
session-associated outputs for export initiation.

.. _uuid-90977a32-cb75-4745-b6d0-470f1b5116be:

System Objectives
-----------------

UUID: :ref:`90977A32-CB75-4745-B6D0-470F1B5116BE <uuid-90977a32-cb75-4745-b6d0-470f1b5116be>`

**Objective 1:** The Host PC Primary Data Pipeline shall accept only complete
measurement frames from the Integration boundary and preserve all 3648
effective detector samples in acquisition order with their frame context for
processing.

   Rationale: Complete-frame qualification and ordered preservation protect
   detector position and frame identity from incomplete or reordered input.

**Objective 2:** The Host PC Primary Data Pipeline shall apply approved and
compatible processing and calibration inputs to qualified detector data to
produce corrected, wavelength-associated spectra.

   Rationale: Input approval and compatibility prevent unavailable,
   incompatible, or undefined processing inputs from silently changing
   measurement meaning.

**Objective 3:** The Host PC Primary Data Pipeline shall preserve source raw
counts and assemble aligned raw and derived measurement products into a
session-ready record for operator use.

   Rationale: Source preservation and product alignment keep every derived
   value traceable to the same measurement and usable by downstream Host PC
   workflows.

**Objective 4:** The Host PC Device Control And Acquisition Coordination system
shall establish and maintain device connection readiness and gate
device-dependent actions until the connection is usable.

   Rationale: Readiness gating prevents unavailable or incomplete connections
   from authorizing control actions.

**Objective 5:** The Host PC Device Control And Acquisition Coordination system
shall coordinate setting, acquisition-start, and acquisition-stop requests with
current connection and session state and shall advance dependent state only for
accepted outcomes.

   Rationale: Outcome-based state advancement prevents requested or failed
   device actions from being represented as active.

**Objective 6:** The Host PC Device Control And Acquisition Coordination system
shall associate complete frames with an active acquisition and expose control
and session outcomes to processing and operator workflows.

   Rationale: Preserving acquisition context and exposing outcomes make
   incomplete, interrupted, rejected, or unavailable conditions visible.

**Objective 7:** The Host PC Operator Application shall coordinate operator
session actions and accepted configuration with visible connection and
acquisition state.

   Rationale: State and configuration visibility prevent unavailable,
   out-of-sequence, or ambiguously configured actions from appearing valid.

**Objective 8:** The Host PC Operator Application shall present qualified
spectra together with device and session status and shall identify unavailable,
stale, or invalid presentation data.

   Rationale: Operating context and data qualification let the operator
   interpret measurements without mistaking invalid data for current data.

**Objective 9:** The Host PC Operator Application shall retain eligible
session-associated data, initiate the required CSV export, report its outcome,
and preserve reviewable data after an unsuccessful export.

   Rationale: Retaining the source session and reviewable data prevents failed
   or incomplete output from appearing successful.

.. _uuid-55f3ab31-2428-4459-a33f-4cc03984fd05:

System Relationship
-------------------

UUID: :ref:`55F3AB31-2428-4459-A33F-4CC03984FD05 <uuid-55f3ab31-2428-4459-a33f-4cc03984fd05>`

.. list-table::
   :header-rows: 1

   * - System
     - Primary Responsibility
   * - :doc:`Primary Data Pipeline <primary_data_pipeline/index>`
     - Frame reconstruction, spectral processing, and output retention.
   * - :doc:`Device Control And Acquisition Coordination <device_control_and_acquisition_coordination/index>`
     - Connection, acquisition, integration-time, and command coordination.
   * - :doc:`Operator Application <operator_application/index>`
     - Session control, visualization, settings, and export initiation.

.. _uuid-7e7e9cf8-7577-4dc8-97b7-6730476d1d41:

Integration Boundary
--------------------

UUID: :ref:`7E7E9CF8-7577-4DC8-97B7-6730476D1D41 <uuid-7e7e9cf8-7577-4dc8-97b7-6730476d1d41>`

**Summary:** The Host PC system shall receive measurement frames and exchange
supported control requests and command outcomes at the MCU-to-Host PC boundary
defined by
:doc:`Integration Interfaces <../integration/interfaces/system_boundaries/Integration Interfaces>`.
The Integration system shall define the optical-to-CCD, CCD-to-MCU, and
MCU-to-Host PC boundaries.
