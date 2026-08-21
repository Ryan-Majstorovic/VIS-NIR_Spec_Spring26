Device Control And Acquisition Coordination
===========================================

.. note::

   Insert the user-provided I/O diagram here after the Visio source and image are available.

.. _uuid-2168f561-f3a2-4fc1-82d5-9bc67a50b01b:

System Role
-----------

UUID: :ref:`2168F561-F3A2-4FC1-82D5-9BC67A50B01B <uuid-2168f561-f3a2-4fc1-82d5-9bc67a50b01b>`

**Summary:** The Host PC device-control and acquisition-coordination system
shall coordinate connection state, acquisition start and stop actions,
complete-frame routing, integration-time requests, and command outcomes so
acquisition-control state remains available to operator and processing
workflows.

.. _uuid-3f2992ab-fc13-4f13-8bd3-089102b2636b:

System Objectives
-----------------

UUID: :ref:`3F2992AB-FC13-4F13-8BD3-089102B2636B <uuid-3f2992ab-fc13-4f13-8bd3-089102b2636b>`

**Objective 1:** The Host PC device-control and acquisition-coordination system
shall maintain Disconnected, Connecting, Ready, and Unavailable connection
states and gate acquisition and command actions until the connection is Ready.

   Rationale: Explicit readiness prevents an absent, incomplete, or unusable
   connection from authorizing control actions.

**Objective 2:** The Host PC device-control and acquisition-coordination system
shall remove readiness, gate dependent actions, and expose unavailability after
an operator disconnect or observed connection loss.

   Rationale: Removing stale readiness prevents later actions from relying on a
   device that can no longer accept them.

**Objective 3:** The Host PC device-control and acquisition-coordination system
shall accept acquisition start only while the connection is Ready and represent
acquisition as active only after an accepted start outcome.

   Rationale: Ready-state and outcome gating prevent a pending or unsuccessful
   start from appearing active.

**Objective 4:** The Host PC device-control and acquisition-coordination system
shall route complete frames only while acquisition is active, expose the stop
outcome and complete, partial, or interrupted session disposition, and prevent
unresolved post-stop data from being represented as complete.

   Rationale: Active-session routing and visible disposition keep frames
   associated with a valid session and prevent incomplete data from appearing
   complete.

The exact stop and drain boundary remains ``Not In Docs``.

**Objective 5:** The Host PC device-control and acquisition-coordination system
shall validate integration-time requests against documented constraints when
available, submit eligible requests, and distinguish accepted, rejected,
unavailable, pending, and active states.

   Rationale: Validation and state distinction prevent an invalid or
   unsuccessful request from being represented as the active measurement
   setting.

The exact integration-time application boundary remains ``Not In Docs``.

**Objective 6:** The Host PC device-control and acquisition-coordination system
shall gate commands using current preconditions, distinguish success, failure,
rejection, unavailable, and missing outcomes, and permit only dependent actions
authorized by the outcome.

   Rationale: Outcome-based gating prevents host and acquisition state from
   advancing after a failed or unresolved command.

**Objective 7:** The Host PC device-control and acquisition-coordination system
shall expose connection, acquisition-session, integration-time-request,
command-outcome, and applicable rate-profile state to operator and processing
workflows.

   Rationale: Visible state lets dependent workflows distinguish ready,
   pending, active, rejected, and unavailable conditions while keeping
   acquisition transport, display update, and the above-100-fps system design
   target separate.

.. _uuid-a75379eb-011d-4a55-a11f-f9ec8a3c480d:

System Relationship
-------------------

UUID: :ref:`A75379EB-011D-4A55-A11F-F9EC8A3C480D <uuid-a75379eb-011d-4a55-a11f-f9ec8a3c480d>`

.. list-table::
   :header-rows: 1

   * - System
     - Primary Responsibility
   * - :doc:`Connection Management <connection_management/index>`
     - Device attachment, readiness, connection loss, and action gating.
   * - :doc:`Acquisition Session Control <acquisition_session_control/index>`
     - Acquisition start and stop, complete-frame routing, and session disposition.
   * - :doc:`Integration-Time Control <integration_time_control/index>`
     - Request validation, outcome classification, and pending or active value state.
   * - :doc:`Command Status Handling <command_status_handling/index>`
     - Command-outcome normalization and dependent-action gating.

.. _uuid-960065a1-1e9d-4ddf-afc9-cb37e5c57d47:

Integration Boundary
--------------------

UUID: :ref:`960065A1-1E9D-4DDF-AFC9-CB37E5C57D47 <uuid-960065a1-1e9d-4ddf-afc9-cb37e5c57d47>`

**Summary:** The Host PC device-control and acquisition-coordination system
shall exchange supported acquisition-control requests and device outcomes at
the MCU-to-Host PC boundary defined by :doc:`Integration Interfaces
<../../integration/interfaces/system_boundaries/Integration Interfaces>`.
Integration owns wire-level command encoding, status meanings,
acknowledgments, timing, retry, recovery, and request-application details;
unresolved specifics remain ``Not In Docs``.

.. toctree::
   :maxdepth: 1
   :hidden:

   connection_management/index
   acquisition_session_control/index
   integration_time_control/index
   command_status_handling/index
