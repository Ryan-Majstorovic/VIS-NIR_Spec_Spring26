Operator Application
====================

.. note::

   Insert the user-provided I/O diagram here after the Visio source and image
   are available.

.. _uuid-71d2ed58-e8db-4e12-ba3f-d9ab7883c5e6:

System Role
-----------

UUID: :ref:`71D2ED58-E8DB-4E12-BA3F-D9AB7883C5E6 <uuid-71d2ed58-e8db-4e12-ba3f-d9ab7883c5e6>`

**Summary:** The Host PC operator-application system shall provide session
control, visualization, calibration and user settings, and export initiation
and session retention for the current acquisition session without defining a
particular user-interface layout.

.. _uuid-1a395633-071f-4ce1-944c-2b9128d28ba0:

System Objectives
-----------------

UUID: :ref:`1A395633-071F-4CE1-944C-2B9128D28BA0 <uuid-1a395633-071f-4ce1-944c-2b9128d28ba0>`

**Objective 1:** **Session workflow.** The Operator Application shall coordinate
connection, acquisition, inspection, stop, retention, and disconnect actions
using the current connection and session state.

**Rationale:** State-directed actions prevent the operator workflow from
starting or ending measurement activity in the wrong device state.

**Objective 2:** **Presentation and configuration.** The Operator Application
shall present wavelength-associated spectra and status, manage calibration and
user-setting selections, and identify missing, stale, invalid, or unavailable
information.

**Rationale:** Presenting data state with the spectrum prevents unavailable or
outdated measurements and settings from appearing current.

**Objective 3:** **Retention and export.** The Operator Application shall retain
session records, verify the five required data products, create CSV output,
report the export outcome, and preserve the session after an export failure.

**Rationale:** Retaining the source session protects review and recovery when
output creation is incomplete or unsuccessful.

.. _uuid-6036bb15-b648-4643-a82f-44bc18209cd1:

System Relationship
-------------------

UUID: :ref:`6036BB15-B648-4643-A82F-44BC18209CD1 <uuid-6036bb15-b648-4643-a82f-44bc18209cd1>`

.. list-table::
   :header-rows: 1

   * - System
     - Primary Responsibility
   * - :doc:`Session Control <session_control/index>`
     - Operator-session workflow and state.
   * - :doc:`Visualization <visualization/index>`
     - Live and rolling measurement presentation.
   * - :doc:`Calibration And User Settings <calibration_and_user_settings/index>`
     - Calibration selection and user-setting management.
   * - :doc:`Export Initiation And Session Retention <export_initiation_and_session_retention/index>`
     - Retained-session export and outcome reporting.

.. _uuid-2b60386e-37b5-481e-8406-fb94eca5a6fd:

Integration Boundary
--------------------

UUID: :ref:`2B60386E-37B5-481E-8406-FB94ECA5A6FD <uuid-2b60386e-37b5-481e-8406-fb94eca5a6fd>`

**Summary:** The Host PC operator-application system consumes connection and
acquisition state from Device Control And Acquisition Coordination and
qualified processed and retained spectrum products from the Primary Data
Pipeline. Integration owns the low-level MCU-to-Host PC contract, and the
Primary Data Pipeline owns calibration mathematics and measurement processing.

.. toctree::
   :maxdepth: 1
   :hidden:

   session_control/index
   visualization/index
   calibration_and_user_settings/index
   export_initiation_and_session_retention/index
