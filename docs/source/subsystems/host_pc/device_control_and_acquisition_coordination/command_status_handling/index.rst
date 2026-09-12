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

**Objective 1:** **Command entry.** Command-Status Handling shall compare each
operator command with the current connection and acquisition state before
submitting it through the Integration interface.

**Rationale:** State-based gating prevents commands from being issued when their
device or acquisition preconditions are absent.

**Objective 2:** **Outcome classification.** Command-Status Handling shall
classify the response as success, failure, rejection, unavailable, or missing
and shall preserve the returned failure information.

**Rationale:** Distinct outcomes retain the cause of an unsuccessful command
instead of reducing every failure to one ambiguous state.

**Objective 3:** **Dependent actions.** Command-Status Handling shall enable
dependent actions after success and shall prevent state advancement after
failure, rejection, unavailability, or a missing response.

**Rationale:** Outcome-controlled advancement prevents downstream workflows from
acting on a command that did not complete.

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
