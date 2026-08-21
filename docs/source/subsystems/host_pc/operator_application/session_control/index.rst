Session Control
===============

.. note::

   Insert the user-provided I/O diagram here after the Visio source and image
   are available.

.. _uuid-902664d2-b91e-4a01-8911-a7a12c89657b:

System Role
-----------

UUID: :ref:`902664D2-B91E-4A01-8911-A7A12C89657B <uuid-902664d2-b91e-4a01-8911-a7a12c89657b>`

**Summary:** The Host PC session-control system shall establish readiness,
start acquisition, make accepted processed data available for inspection, stop
or pause according to the approved policy, retain eligible data, and disconnect
while presenting the current session state.

.. _uuid-fb55b99e-7aa5-4582-a2c5-8824ef9d8b32:

System Objectives
-----------------

UUID: :ref:`FB55B99E-7AA5-4582-A2C5-8824EF9D8B32 <uuid-fb55b99e-7aa5-4582-a2c5-8824ef9d8b32>`

**Objective 1:** The Host PC session-control system shall gate connection and
acquisition actions using current connection and acquisition status.

   Rationale: State-based gating prevents actions that are invalid for the
   current connection or acquisition condition.

**Objective 2:** The Host PC session-control system shall establish readiness
before acquisition actions become available.

   Rationale: Readiness qualification prevents acquisition from beginning
   before its required connection state is available.

**Objective 3:** The Host PC session-control system shall start an acquisition
session and present its current state.

   Rationale: Presenting session state preserves the association between
   operator actions and the acquisition they govern.

**Objective 4:** The Host PC session-control system shall make accepted
processed data available for inspection during the session.

   Rationale: Inspection access allows the operator to review qualified data in
   the context of the active session.

**Objective 5:** The Host PC session-control system shall stop or pause
according to the approved acquisition policy and retain eligible session data.

   Rationale: Controlled finalization and retention preserve eligible data when
   acquisition activity changes state.

**Objective 6:** The Host PC session-control system shall expose connection
loss and unavailable actions and disconnect safely.

   Rationale: Loss visibility and safe disconnection prevent a disconnected
   session from appearing active.

.. _uuid-d8b9bb75-d5c6-4efd-8d3b-d1668c6befb4:

System Relationship
-------------------

UUID: :ref:`D8B9BB75-D5C6-4EFD-8D3B-D1668C6BEFB4 <uuid-d8b9bb75-d5c6-4efd-8d3b-d1668c6befb4>`

.. list-table::
   :header-rows: 1

   * - Documentation
     - Responsibility
   * - :doc:`Inputs and Outputs <inputs_and_outputs>`
     - Action, connection-status, acquisition-status, and processed-readiness boundaries.
   * - :doc:`Procedure <procedure>`
     - Operator workflow, conditions, and session states.
   * - :doc:`Diagnostics <diagnostics>`
     - Invalid-action, connection-loss, and partial-session conditions.
   * - :doc:`Testing <testing>`
     - Requirements-based session-control behavior tests.
   * - :doc:`Calculations <calculations>`
     - Absence of a numeric workflow calculation and open policy requirements.
   * - :doc:`Validation <validation>`
     - Local behavior claim, traceability state, and validation method.

.. _uuid-1f508f0c-776a-4183-82dc-fab83bed83de:

Integration Boundary
--------------------

UUID: :ref:`1F508F0C-776A-4183-82DC-FAB83BED83DE <uuid-1f508f0c-776a-4183-82dc-fab83bed83de>`

**Summary:** The Host PC session-control system consumes connection and
acquisition state from Device Control And Acquisition Coordination and
processed-data readiness from the Primary Data Pipeline, and it supplies
session context to Visualization and Export Initiation And Session Retention.
Low-level device commands remain outside this system. Session identity, pause
semantics, resume behavior, disconnect recovery, and the setup-time criterion
remain ``Not In Docs``.

.. toctree::
   :maxdepth: 1
   :hidden:

   inputs_and_outputs
   procedure
   diagnostics
   testing
   calculations
   validation
