Device Control And Acquisition Coordination
===========================================

The Device Control and Acquisition Coordination subsystem manages the communication lifecycle with the spectrometer hardware. It controls serial port attachment, demuxes mixed ASCII diagnostics and binary frame streams, tracks frame counter continuity at 125 Hz, and coordinates device command transactions.

.. _uuid-2168f561-f3a2-4fc1-82d5-9bc67a50b01b:

Subsystem Role & Responsibilities
---------------------------------

UUID: :ref:`2168F561-F3A2-4FC1-82D5-9BC67A50B01B <uuid-2168f561-f3a2-4fc1-82d5-9bc67a50b01b>`

This subsystem serves as the host-side counterpart to the embedded USB CDC interface:
* **Connection Lifecycle:** Manages port enumeration, connection gating, and reconnection logic.
* **Stream Synchronization:** Continuously receives 125 Hz binary frames and detects missing sequence IDs.
* **Command Dispatch:** Transmits ASCII configuration commands and handles firmware responses.
* **Integration Time Control:** Governs integration-time parameters across the host-device boundary.

.. _uuid-a75379eb-011d-4a55-a11f-f9ec8a3c480d:

Subsystem Sections
------------------

UUID: :ref:`A75379EB-011D-4A55-A11F-F9EC8A3C480D <uuid-a75379eb-011d-4a55-a11f-f9ec8a3c480d>`

.. list-table::
   :header-rows: 1

   * - System
     - Primary Responsibility
   * - :doc:`Connection Management <connection_management>`
     - Device attachment, readiness, connection loss, and action gating.
   * - :doc:`Acquisition Session Control <acquisition_session_control>`
     - Acquisition start and stop, complete-frame routing, and session disposition.
   * - :doc:`Integration-Time Control <integration_time_control>`
     - Request validation, outcome classification, and pending or active value state.
   * - :doc:`Command Status Handling <command_status_handling>`
     - Command-outcome normalization and dependent-action gating.

.. _uuid-960065a1-1e9d-4ddf-afc9-cb37e5c57d47:

Integration Boundary
--------------------

UUID: :ref:`960065A1-1E9D-4DDF-AFC9-CB37E5C57D47 <uuid-960065a1-1e9d-4ddf-afc9-cb37e5c57d47>`

The Host PC coordinates acquisition-control requests and device outcomes at
the MCU-to-Host PC boundary. The shared command and status contract is
documented in :doc:`../../embedded/system_control_and_hardware_interface/command_protocol_and_state_machine`.

.. toctree::
   :maxdepth: 1

   connection_management
   acquisition_session_control
   integration_time_control
   command_status_handling
