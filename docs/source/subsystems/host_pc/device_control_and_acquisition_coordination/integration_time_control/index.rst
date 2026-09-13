Integration-Time Control
========================

.. note::

   Insert the user-provided I/O diagram here after the Visio source and image are available.

.. _uuid-9d1ae020-fa76-4bd5-9c9f-98924be201c2:

System Role
-----------

UUID: :ref:`9D1AE020-FA76-4BD5-9C9F-98924BE201C2 <uuid-9d1ae020-fa76-4bd5-9c9f-98924be201c2>`

**Summary:** The Host PC integration-time-control system shall receive an
operator-requested integration time, validate it against approved constraints
when available, submit it through the Integration control interface, expose
its outcome, and distinguish pending from active values.

.. _uuid-9be2b69a-07fa-42e3-8e83-7fde0675f396:

System Objectives
-----------------

UUID: :ref:`9BE2B69A-07FA-42E3-8E83-7FDE0675F396 <uuid-9be2b69a-07fa-42e3-8e83-7fde0675f396>`

**Objective 1:** **Request entry.** Integration-Time Control shall capture the
requested integration-time value with the current connection and acquisition
state and shall submit the request only while device control is available.

**Rationale:** Retaining the request context prevents a value from being applied
through a stale or unavailable connection.

**Objective 2:** **Device outcome.** Integration-Time Control shall report the
request as accepted, rejected, or unavailable without treating a missing
response as acceptance.

**Rationale:** Explicit outcome classification prevents an unconfirmed setting
from being presented as active.

**Objective 3:** **Value activation.** Integration-Time Control shall
distinguish requested, pending, and active values, apply an accepted value at
the defined acquisition boundary, and preserve the current active value after
rejection.

**Rationale:** Separating requested and active values prevents the operator from
mistaking an unapplied setting for current device behavior.

.. _uuid-b88e3829-f9d3-492a-b983-187076e993f8:

System Relationship
-------------------

UUID: :ref:`B88E3829-F9D3-492A-B983-187076E993F8 <uuid-b88e3829-f9d3-492a-b983-187076e993f8>`

.. list-table::
   :header-rows: 1

   * - Page
     - Primary Responsibility
   * - :doc:`Inputs and Outputs <inputs_and_outputs>`
     - Requested value, operating state, device outcome, and pending or active status.
   * - :doc:`Procedure <procedure>`
     - Request validation, submission, classification, and application flow.
   * - :doc:`Diagnostics <diagnostics>`
     - Invalid-request, rejection, and undefined-boundary conditions.
   * - :doc:`Testing <testing>`
     - Accepted, rejected, unavailable, unchanged-frame, and state-visibility checks.
   * - :doc:`Calculations <calculations>`
     - Constraint validation and unresolved value definitions.
   * - :doc:`Validation <validation>`
     - Local behavior claim, traceability, and evidence method.

.. _uuid-42d4406f-361a-43a5-b55e-64705add0752:

Integration Boundary
--------------------

UUID: :ref:`42D4406F-361A-43A5-B55E-64705ADD0752 <uuid-42d4406f-361a-43a5-b55e-64705add0752>`

**Summary:** The Host PC integration-time-control system shall submit supported
integration-time requests and receive their outcomes at the MCU-to-Host PC
boundary defined by :doc:`Integration Interfaces
<../../../integration/interfaces/system_boundaries/Integration Interfaces>`.
Integration owns wire-level request encoding, acknowledgment, and
device-application semantics; units, range, quantization, default,
acknowledgment behavior, and the exact application boundary remain ``Not In
Docs``.

.. toctree::
   :maxdepth: 1
   :hidden:

   inputs_and_outputs
   procedure
   diagnostics
   testing
   calculations
   validation
