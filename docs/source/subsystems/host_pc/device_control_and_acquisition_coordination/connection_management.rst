Connection Management
=====================

The Connection Management system controls the physical serial transport connection between the Host PC and the spectrometer microcontroller over USB CDC. It enumerates available COM ports, manages connection state transitions, and runs a dedicated background serial reading loop.

.. _uuid-b1c2d3e4-f5a6-47b8-c9d0-112233445501:

Subsystem Role & Architecture
-----------------------------

UUID: :ref:`B1C2D3E4-F5A6-47B8-C9D0-112233445501 <uuid-b1c2d3e4-f5a6-47b8-c9d0-112233445501>`

Connection Management decouples raw OS serial port operations from the rest of the application:
* **Abstract Transport:** Uses a ``BaseTransport`` interface implemented by ``SerialTransport`` (via ``pyserial``).
* **Threaded Reader:** Spawns a dedicated daemon thread to read incoming serial chunks without blocking the UI or processing threads.
* **Synchronized Writes:** Employs a reentrant threading lock to prevent write collisions between asynchronous UI commands.

Inputs and Outputs
------------------

.. list-table::
   :header-rows: 1

   * - Flow
     - Name
     - Type
     - Description
   * - **Input**
     - Target Port
     - String (e.g., ``"COM3"``)
     - User-selected or auto-discovered COM port.
   * - **Input**
     - Serial Configuration
     - ``SerialConfig``
     - Baud rate, read timeout (default 0.1 s), and reconnect policy.
   * - **Output**
     - Connection State
     - Enum
     - ``Disconnected``, ``Connecting``, ``Connected``, or ``Error``.
   * - **Output**
     - Raw Byte Stream
     - Byte chunks
     - Raw incoming bytes delivered to packet parsing queues.

Normative Requirements
----------------------

.. _uuid-b1c2d3e4-f5a6-47b8-c9d0-112233445502:

**Requirement:** The Host PC Connection Management system shall maintain the explicit connection states ``Disconnected``, ``Connecting``, ``Connected``, and ``Error``, and shall permit device command transmission and acquisition capture only while in the ``Connected`` state.

   **Rationale:** Restricting commands and stream operations to the ``Connected`` state prevents thread exceptions, silent data loss, and malformed writes when the USB physical cable is detached or unconfigured.

.. _uuid-b1c2d3e4-f5a6-47b8-c9d0-112233445503:

**Requirement:** The Host PC Connection Management system shall execute all incoming serial port reads on a dedicated background reader thread and push raw byte chunks into a thread-safe FIFO queue.

   **Rationale:** A dedicated serial reading thread ensures that serial driver buffers do not overflow when the UI is engaged in complex rendering or when disk writes occur.

.. _uuid-b1c2d3e4-f5a6-47b8-c9d0-112233445504:

**Requirement:** The Host PC Connection Management system shall flush the packet reader buffer and reset internal frame sequence tracking upon every new connection attempt.

   **Rationale:** Purging stale bytes during reconnection prevents truncated residual bytes from a previous session from corrupting the first packet of a new session.

State Machine
-------------

.. list-table::
   :header-rows: 1

   * - Source State
     - Target State
     - Trigger Condition
     - Action
   * - ``Disconnected``
     - ``Connecting``
     - Operator requests connect or auto-connect fires.
     - Enumerate ports, open serial handle, start reader thread.
   * - ``Connecting``
     - ``Connected``
     - Serial port opens successfully.
     - Reset parse buffers, publish status, enable streaming.
   * - ``Connecting``
     - ``Error``
     - Serial port fails to open or is locked by another process.
     - Publish error message, remain disconnected.
   * - ``Connected``
     - ``Disconnected``
     - Operator requests disconnect.
     - Signal thread stop, close COM port, flush queues.
   * - ``Connected``
     - ``Error``
     - USB cable unplugged or serial read exception occurs.
     - Mark state error, stop reader thread, alert operator.

Verification & Testing
----------------------

* **Port Discovery Check:** Verify that visible system COM ports are enumerated into a selectable list without raising exceptions.
* **Disconnection Safety Check:** Disconnect while receiving a 125 Hz stream; verify that reader threads terminate cleanly and port handles are closed within 500 ms.
