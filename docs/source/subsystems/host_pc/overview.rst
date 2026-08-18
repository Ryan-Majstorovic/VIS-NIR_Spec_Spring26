Host PC System Overview
=======================

.. _uuid-42e97793-9f90-4eb8-9757-fde4d6527dbc:

System Role
-----------

UUID: :ref:`42E97793-9F90-4EB8-9757-FDE4D6527DBC <uuid-42e97793-9f90-4eb8-9757-fde4d6527dbc>`

**Summary:** The Host PC subsystem defines the intended software behavior for
the operator-facing application, the host-side acquisition-control path, and
the primary measurement-processing pipeline that transforms device traffic into
processed spectral outputs.

**Expected Outcome:** The Host PC specification shall define how the software
coordinates acquisition, processes incoming data, presents live information to
the operator, and retains session data for later export without treating the
current code layout as the source of truth.

**Rationale:** This page exists to keep the Host PC documentation authoritative
before implementation review starts and to keep later traceability local to the
behaviors that the host software is expected to deliver.

.. _uuid-90977a32-cb75-4745-b6d0-470f1b5116be:

System Objectives
-----------------

UUID: :ref:`90977A32-CB75-4745-B6D0-470F1B5116BE <uuid-90977a32-cb75-4745-b6d0-470f1b5116be>`

**Objective 1:** The Host PC specification shall separate the primary data
pipeline, acquisition-control behavior, and operator application behavior into
distinct authoritative systems.

**Objective 2:** The primary data pipeline shall remain the most rigorous
backend path because it converts incoming device traffic into processed,
wavelength-associated, and retained spectrum outputs.

**Objective 3:** The acquisition-control section shall define what the host is
responsible for doing when it connects to the device, starts or stops
acquisition, applies integration-time requests, and handles command outcomes.

**Objective 4:** The operator application section shall define intended user
workflows for session control, visualization, calibration and user settings,
and export initiation without freezing the current UI layout into the
specification.

.. _uuid-55f3ab31-2428-4459-a33f-4cc03984fd05:

System Relationship
-------------------

UUID: :ref:`55F3AB31-2428-4459-A33F-4CC03984FD05 <uuid-55f3ab31-2428-4459-a33f-4cc03984fd05>`

+---------------------------------------------+-------------------------------------------------------------+------------------------------------------------------------+
| System                                      | Primary Responsibility                                      | Downstream Or Adjacent Relationship                        |
+=============================================+=============================================================+============================================================+
| Primary Data Pipeline                       | Convert incoming device data into validated, corrected,     | Feeds retained processed outputs into operator-facing      |
|                                             | wavelength-associated, and retained host-side spectrum data.| visualization and export workflows.                        |
+---------------------------------------------+-------------------------------------------------------------+------------------------------------------------------------+
| Device Control And Acquisition Coordination | Define the host-side behaviors for connection readiness,    | Uses the low-level host-to-MCU interface documented under  |
|                                             | acquisition control, integration-time changes, and command  | :doc:`../integration/interfaces/Interfaces` to drive       |
|                                             | outcome handling.                                           | acquisition behavior.                                      |
+---------------------------------------------+-------------------------------------------------------------+------------------------------------------------------------+
| Operator Application                        | Define the operator workflows for monitoring, settings,     | Consumes pipeline outputs and control state to present     |
|                                             | calibration selection, and export initiation.               | the intended user-facing software behavior.                |
+---------------------------------------------+-------------------------------------------------------------+------------------------------------------------------------+

.. _uuid-7e7e9cf8-7577-4dc8-97b7-6730476d1d41:

Integration Boundary
--------------------

UUID: :ref:`7E7E9CF8-7577-4DC8-97B7-6730476D1D41 <uuid-7e7e9cf8-7577-4dc8-97b7-6730476d1d41>`

**Summary:** Low-level host-to-microcontroller interaction details belong in
the Integration documentation rather than inside the Host PC subsystem pages.
The Host PC pages define what the host is expected to do; the integration pages
define how the host and embedded device communicate across that boundary.

**Expected Outcome:** Host PC control pages can reference the interface
contract without duplicating packet or command details, and standalone
validation tooling such as the COM Inspector remains supporting evidence rather
than a normal operating path.

.. note::

   Insert the user-provided Host PC architecture diagram here after the Visio
   source and image are available.

Related Pages
-------------

* :doc:`Primary Data Pipeline <primary_data_pipeline/index>`
* :doc:`Device Control And Acquisition Coordination <device_control_and_acquisition_coordination/index>`
* :doc:`Operator Application <operator_application/index>`
