Acquisition Session Control
===========================

.. note::

   Insert the user-provided I/O diagram here after the Visio source and image are available.

.. _uuid-c5b4956e-5695-4da3-88a6-387879cf6948:

System Role
-----------

UUID: :ref:`C5B4956E-5695-4DA3-88A6-387879CF6948 <uuid-c5b4956e-5695-4da3-88a6-387879cf6948>`

**Summary:** The Host PC acquisition-session-control system shall coordinate
measurement-session start and stop behavior after connection readiness, route
complete frames during active acquisition, and expose whether the resulting
session is complete, partial, or interrupted.

.. _uuid-529d7e4e-7178-42d1-a64a-624397fac33f:

System Objectives
-----------------

UUID: :ref:`529D7E4E-7178-42D1-A64A-624397FAC33F <uuid-529d7e4e-7178-42d1-a64a-624397fac33f>`

**Objective 1:** The Host PC acquisition-session-control system shall accept a
Start request only while the connection state is Ready.

   Rationale: Start gating prevents an acquisition from beginning without a
   usable device connection.

**Objective 2:** The Host PC acquisition-session-control system shall enter
Acquiring only after the acquisition-start outcome is accepted.

   Rationale: Waiting for acceptance prevents a pending or failed request from
   being represented as an active acquisition.

**Objective 3:** The Host PC acquisition-session-control system shall route
complete measurement frames to processing and retention while the acquisition
session remains active.

   Rationale: Routing only within the active session preserves the association
   between received frames and the session that requested them.

**Objective 4:** The Host PC acquisition-session-control system shall accept a
Stop request and prevent new frames from entering the session after the
approved stop boundary.

   Rationale: Closing frame admission at the stop boundary prevents later
   frames from being attributed to a completed session.

**Objective 5:** The Host PC acquisition-session-control system shall expose
whether a stopped session is complete, partial, or interrupted.

   Rationale: Session disposition prevents incomplete measurements from being
   treated as complete data products.

**Objective 6:** The Host PC acquisition-session-control system shall keep
acquisition transport rate, display update rate, and the above-100-fps system
design target as distinct measures.

   Rationale: Separating these measures prevents evidence for one boundary from
   being used as acceptance evidence for another.

Pause, buffering, backpressure, dropped-frame, and stop/drain behavior remain
``Not In Docs``.

.. _uuid-48b24259-048c-421d-b6f9-5a4d1ca7ebca:

System Relationship
-------------------

UUID: :ref:`48B24259-048C-421D-B6F9-5A4D1CA7EBCA <uuid-48b24259-048c-421d-b6f9-5a4d1ca7ebca>`

.. list-table::
   :header-rows: 1

   * - Page
     - Primary Responsibility
   * - :doc:`Inputs and Outputs <inputs_and_outputs>`
     - Start and stop inputs, readiness and frame inputs, and session outputs.
   * - :doc:`Procedure <procedure>`
     - Session flow, transition conditions, and acquisition states.
   * - :doc:`Diagnostics <diagnostics>`
     - Missing-frame, identity-gap, and stop-completeness conditions.
   * - :doc:`Testing <testing>`
     - Start, stop, complete-frame feed, and not-ready checks.
   * - :doc:`Calculations <calculations>`
     - Separation of acquisition, display, and system-target rates.
   * - :doc:`Validation <validation>`
     - Local behavior claim, traceability, and evidence method.

.. _uuid-e1252260-9443-43e9-a8ae-295125bdb6a3:

Integration Boundary
--------------------

UUID: :ref:`E1252260-9443-43E9-A8AE-295125BDB6A3 <uuid-e1252260-9443-43e9-a8ae-295125bdb6a3>`

**Summary:** The Host PC acquisition-session-control system shall exchange
supported Start and Stop requests, outcomes, complete frames, and status at the
MCU-to-Host PC boundary defined by :doc:`Integration Interfaces
<../../../integration/interfaces/system_boundaries/Integration Interfaces>`.
Integration owns the low-level request and frame-transfer contract; pause,
buffering, backpressure, dropped-frame response, and stop/drain policy remain
``Not In Docs``.

.. toctree::
   :maxdepth: 1
   :hidden:

   inputs_and_outputs
   procedure
   diagnostics
   testing
   calculations
   validation
