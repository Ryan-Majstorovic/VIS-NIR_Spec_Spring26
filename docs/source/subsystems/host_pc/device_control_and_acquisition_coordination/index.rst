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

   * - Section
     - Core Responsibilities
   * - :doc:`connection_management`
     - Serial port enumeration, connection state machine, threaded I/O, and reconnection gating.
   * - :doc:`acquisition_session_control`
     - 125 Hz stream synchronization, frame continuity tracking, sequence gap detection, and rate diagnostics.
   * - :doc:`integration_time_control`
     - Fixed 8 ms baseline documentation and planned ICG-synchronized dynamic integration time specification.
   * - :doc:`command_status_handling`
     - Mixed ASCII/binary stream demuxing, raw CDC command dispatch, and firmware message logging.

.. toctree::
   :maxdepth: 1

   connection_management
   acquisition_session_control
   integration_time_control
   command_status_handling
