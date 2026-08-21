Connection Management
=====================

.. note::

   Insert the user-provided I/O diagram here after the Visio source and image are available.

.. _uuid-97aa0e47-6d1e-460d-850d-41a5c58e3c25:

System Role
-----------

UUID: :ref:`97AA0E47-6D1E-460D-850D-41A5C58E3C25 <uuid-97aa0e47-6d1e-460d-850d-41a5c58e3c25>`

**Summary:** The Host PC connection-management system shall respond to operator
connect and disconnect requests, maintain device connection and readiness
state, gate acquisition and command actions until readiness is confirmed, and
expose connection loss or unavailability.

.. _uuid-317c53b9-ca4e-4dd3-baef-9afcec4d5ca2:

System Objectives
-----------------

UUID: :ref:`317C53B9-CA4E-4DD3-BAEF-9AFCEC4D5CA2 <uuid-317c53b9-ca4e-4dd3-baef-9afcec4d5ca2>`

**Objective 1:** The Host PC connection-management system shall maintain the
Disconnected, Connecting, Ready, and Unavailable connection states.

   Rationale: Distinct states prevent a connection attempt or failed connection
   from being represented as ready.

**Objective 2:** The Host PC connection-management system shall enter
Connecting from Disconnected only in response to an operator connection request
and shall evaluate device availability and interface readiness.

   Rationale: Requiring an explicit request and readiness evaluation prevents
   unintended attachment and premature control access.

**Objective 3:** The Host PC connection-management system shall enter Ready
only after the connection is confirmed usable for host control.

   Rationale: Confirmed readiness protects acquisition and command workflows
   from using an incomplete connection.

**Objective 4:** The Host PC connection-management system shall gate
acquisition and command actions while the connection is Disconnected,
Connecting, or Unavailable.

   Rationale: Gating dependent actions prevents requests from being applied
   when no usable device connection exists.

**Objective 5:** The Host PC connection-management system shall transition out
of Ready, gate dependent actions, and expose the unavailable condition after an
operator disconnect or observed connection loss.

   Rationale: Immediate loss handling prevents stale readiness from allowing
   further control actions.

Discovery, port selection, automatic reconnect, timeout, and retry policy
remain ``Not In Docs``.

.. _uuid-17dd02f7-f14c-49fc-a508-a8356a3e0ebc:

System Relationship
-------------------

UUID: :ref:`17DD02F7-F14C-49FC-A508-A8356A3E0EBC <uuid-17dd02f7-f14c-49fc-a508-a8356a3e0ebc>`

.. list-table::
   :header-rows: 1

   * - Page
     - Primary Responsibility
   * - :doc:`Inputs and Outputs <inputs_and_outputs>`
     - Connection requests and availability inputs; visible state and readiness outputs.
   * - :doc:`Procedure <procedure>`
     - Connection flow, allowed transitions, and lifecycle states.
   * - :doc:`Diagnostics <diagnostics>`
     - Unavailable-device, connection-loss, and incomplete-readiness conditions.
   * - :doc:`Testing <testing>`
     - Attach, detach, readiness-gating, and device-loss checks.
   * - :doc:`Calculations <calculations>`
     - Readiness evaluation and open connection-policy decisions.
   * - :doc:`Validation <validation>`
     - Local behavior claim, traceability, and evidence method.

.. _uuid-6c564b0a-52af-463e-aa6a-246b9b60c66f:

Integration Boundary
--------------------

UUID: :ref:`6C564B0A-52AF-463E-AA6A-246B9B60C66F <uuid-6c564b0a-52af-463e-aa6a-246b9b60c66f>`

**Summary:** The Host PC connection-management system shall determine
availability and readiness at the MCU-to-Host PC boundary defined by
:doc:`Integration Interfaces <../../../integration/interfaces/system_boundaries/Integration Interfaces>`.
Integration owns the low-level attachment and transport boundary; device
discovery, port selection, automatic reconnect, timeout, and retry policy
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
