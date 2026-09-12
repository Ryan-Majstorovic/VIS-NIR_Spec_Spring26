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

**Objective 1:** **Connection readiness.** Session Control shall establish a
Ready connection before enabling acquisition actions.

**Rationale:** Requiring Ready prevents acquisition requests from being issued
before the device-control path is usable.

**Objective 2:** **Active session.** Session Control shall start an acquisition
session, present its current state, and make accepted processed records
available for inspection.

**Rationale:** A visible active-session boundary ties displayed measurements to
the acquisition that produced them.

**Objective 3:** **Session termination.** Session Control shall stop or pause
acquisition, retain the resulting session data, expose connection loss and
unavailable actions, and disconnect without representing an interrupted
session as complete.

**Rationale:** Explicit termination handling preserves partial data while
preventing an interrupted session from receiving a false successful
disposition.

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
