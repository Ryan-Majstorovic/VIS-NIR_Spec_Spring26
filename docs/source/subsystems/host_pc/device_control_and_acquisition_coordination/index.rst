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

**Objective 1:** **Connection control.** Device Control and Acquisition
Coordination shall maintain the Disconnected, Connecting, Ready, and Unavailable
states and allow device-dependent actions only while the connection is Ready.

**Rationale:** Explicit readiness gating prevents commands and acquisition
requests from being sent through an unavailable connection.

**Objective 2:** **Request control.** Device Control and Acquisition
Coordination shall submit start, stop, integration-time, and operator-command
requests using the current connection and acquisition state and shall advance
state only after an accepted outcome.

**Rationale:** Outcome-driven state changes prevent rejected, failed, or missing
responses from being represented as successful device actions.

**Objective 3:** **Session reporting.** Device Control and Acquisition
Coordination shall associate complete frames with the active session and report
connection, acquisition, integration-time, command, session-disposition, and
rate information.

**Rationale:** A common session context keeps device state, received frames, and
operator-visible results synchronized.

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
