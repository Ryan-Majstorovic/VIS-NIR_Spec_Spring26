Host PC System Overview
=======================

.. note::

   Insert the user-provided Host PC architecture diagram here after the Visio
   source and image are available.

.. _uuid-42e97793-9f90-4eb8-9757-fde4d6527dbc:

System Role
-----------

UUID: :ref:`42E97793-9F90-4EB8-9757-FDE4D6527DBC <uuid-42e97793-9f90-4eb8-9757-fde4d6527dbc>`

**Summary:** The Host PC system shall coordinate device connection and
acquisition control, accept and process complete measurement frames, present
processed spectra and acquisition status to the operator, and retain
session-associated outputs for export initiation.

.. _uuid-90977a32-cb75-4745-b6d0-470f1b5116be:

System Objectives
-----------------

UUID: :ref:`90977A32-CB75-4745-B6D0-470F1B5116BE <uuid-90977a32-cb75-4745-b6d0-470f1b5116be>`

**Objective 1:** **Measurement processing.** The Host PC Primary Data Pipeline
shall receive complete frames, preserve the 3648 effective samples and raw
counts, perform the configured processing stages, and produce aligned spectrum
records.

**Rationale:** Ordered source preservation and aligned outputs protect the
connection between the detector measurement and every derived value.

**Objective 2:** **Device coordination.** The Host PC Device Control and
Acquisition Coordination system shall manage connection state, start and stop
acquisition, submit integration-time and command requests, and associate
received frames with the active session.

**Rationale:** Coordinating requests with connection and session state prevents
device actions or frames from being assigned to the wrong acquisition.

**Objective 3:** **Operator workflow.** The Host PC Operator Application shall
display spectra and system status, manage processing selections, retain session
data, and create CSV exports.

**Rationale:** A single operator workflow keeps presentation, configuration,
retention, and export tied to the same measurement session.

.. _uuid-55f3ab31-2428-4459-a33f-4cc03984fd05:

System Relationship
-------------------

UUID: :ref:`55F3AB31-2428-4459-A33F-4CC03984FD05 <uuid-55f3ab31-2428-4459-a33f-4cc03984fd05>`

.. list-table::
   :header-rows: 1

   * - System
     - Primary Responsibility
   * - :doc:`Primary Data Pipeline <primary_data_pipeline/index>`
     - Frame reconstruction, spectral processing, and output retention.
   * - :doc:`Device Control And Acquisition Coordination <device_control_and_acquisition_coordination/index>`
     - Connection, acquisition, integration-time, and command coordination.
   * - :doc:`Operator Application <operator_application/index>`
     - Session control, visualization, settings, and export initiation.

.. _uuid-7e7e9cf8-7577-4dc8-97b7-6730476d1d41:

Integration Boundary
--------------------

UUID: :ref:`7E7E9CF8-7577-4DC8-97B7-6730476D1D41 <uuid-7e7e9cf8-7577-4dc8-97b7-6730476d1d41>`

**Summary:** The Host PC system shall receive measurement frames and exchange
supported control requests and command outcomes at the MCU-to-Host PC boundary
defined by
:doc:`Integration Interfaces <../integration/interfaces/system_boundaries/Integration Interfaces>`.
The Integration system shall define the optical-to-CCD, CCD-to-MCU, and
MCU-to-Host PC boundaries.
