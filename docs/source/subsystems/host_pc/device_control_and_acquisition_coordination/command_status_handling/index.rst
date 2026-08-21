Command Status Handling
=======================

.. note::

   Insert the user-provided I/O diagram here after the Visio source and image are available.

.. _uuid-396683d9-3a49-4762-8f58-f3cf28b4dc5b:

System Role
-----------

UUID: :ref:`396683D9-3A49-4762-8F58-F3CF28B4DC5B <uuid-396683d9-3a49-4762-8f58-f3cf28b4dc5b>`

**Summary:** The Host PC command-status-handling system shall gate operator
commands using connection and acquisition state, submit eligible requests
through Integration, classify returned outcomes, expose command status, and
permit only the dependent actions authorized by that outcome.

.. _uuid-de4415bd-a210-4d0a-ad19-9cc0555cc4da:

System Objectives
-----------------

UUID: :ref:`DE4415BD-A210-4D0A-AD19-9CC0555CC4DA <uuid-de4415bd-a210-4d0a-ad19-9cc0555cc4da>`

**Objective 1:** The Host PC command-status-handling system shall gate an
operator command using the current connection and acquisition preconditions.

   Rationale: Precondition gating prevents a command from being submitted when
   the device or acquisition state cannot support it.

**Objective 2:** The Host PC command-status-handling system shall submit an
eligible command through the Integration control interface.

   Rationale: Using the shared control interface keeps the request associated
   with the device outcome returned for it.

**Objective 3:** The Host PC command-status-handling system shall classify the
returned outcome as success, failure, rejection, or unavailable and shall not
report a missing outcome as success.

   Rationale: Complete classification prevents unsuccessful or unresolved
   commands from advancing the success path.

**Objective 4:** The Host PC command-status-handling system shall expose a
normalized command status, preserve failure context, and distinguish rejection
from transport failure.

   Rationale: Preserving the outcome class gives operator and dependent
   workflows the information needed to respond safely.

**Objective 5:** The Host PC command-status-handling system shall update only
the dependent actions permitted by the classified outcome and shall not
advance acquisition after failure, rejection, unavailability, or a missing
outcome.

   Rationale: Outcome-based gating prevents host state from representing a
   device action that did not succeed.

Command vocabulary, status vocabulary, timeout, retry, and recovery rules
remain ``Not In Docs``.

.. _uuid-420fbe4d-a7ae-40e6-bbe6-696a0fdc08e1:

System Relationship
-------------------

UUID: :ref:`420FBE4D-A7AE-40E6-BBE6-696A0FDC08E1 <uuid-420fbe4d-a7ae-40e6-bbe6-696a0fdc08e1>`

.. list-table::
   :header-rows: 1

   * - Page
     - Primary Responsibility
   * - :doc:`Inputs and Outputs <inputs_and_outputs>`
     - Operator command, readiness state, Integration outcome, and normalized status.
   * - :doc:`Procedure <procedure>`
     - Command gating, submission, classification, and dependent-action flow.
   * - :doc:`Diagnostics <diagnostics>`
     - Failure context, rejection distinction, and missing-outcome handling.
   * - :doc:`Testing <testing>`
     - Outcome-class, no-advance-on-failure, and status-visibility checks.
   * - :doc:`Calculations <calculations>`
     - Outcome classification and unresolved command policies.
   * - :doc:`Validation <validation>`
     - Local behavior claim, traceability, and evidence method.

.. _uuid-60c343d4-d0a3-4f70-ad8a-3857e1b3077b:

Integration Boundary
--------------------

UUID: :ref:`60C343D4-D0A3-4F70-AD8A-3857E1B3077B <uuid-60c343d4-d0a3-4f70-ad8a-3857e1b3077b>`

**Summary:** The Host PC command-status-handling system shall submit eligible
commands and receive command outcomes at the MCU-to-Host PC boundary defined by
:doc:`Integration Interfaces <../../../integration/interfaces/system_boundaries/Integration Interfaces>`.
Integration owns wire-level command and status definitions; command vocabulary,
status vocabulary, timeout, retry, and recovery rules remain ``Not In Docs``.

.. toctree::
   :maxdepth: 1
   :hidden:

   inputs_and_outputs
   procedure
   diagnostics
   testing
   calculations
   validation
