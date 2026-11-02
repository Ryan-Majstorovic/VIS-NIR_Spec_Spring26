Command Protocol and State Machine
===================================

The Command Protocol and State Machine subsystem governs host-command ingestion, parameter validation, and acquisition operational states on the embedded microcontroller. It guarantees that acquisition state transitions occur synchronously at physical frame boundaries without generating truncated frames or corrupted sensor timing.

.. _uuid-27aaae0d-d4cd-4ad2-afa9-bda4cf5169ae:

Subsystem Role & Boundary
-------------------------

UUID: :ref:`27AAAE0D-D4CD-4AD2-AFA9-BDA4CF5169AE <uuid-27aaae0d-d4cd-4ad2-afa9-bda4cf5169ae>`

This subsystem resides at the boundary between the USB CDC receiver callback and the real-time acquisition engine. It parses ASCII-encoded command lines received from the Host PC, validates numeric parameters against hardware timing capabilities, drives the internal state machine, and returns deterministic textual status responses.

Inputs and Outputs
------------------

.. list-table::
   :header-rows: 1

   * - Flow
     - Name
     - Type / Format
     - Description
   * - **Input**
     - Command Byte Stream
     - ASCII string over USB CDC
     - Line-delimited command strings (e.g., ``START\n``, ``SET_INT:1000\n``).
   * - **Input**
     - Frame Boundary Signal
     - Internal interrupt flag
     - Hardware notification from TIM4 indicating completion of an optical frame.
   * - **Output**
     - Status Line Response
     - ASCII string over USB CDC
     - Deterministic transaction outcomes (e.g., ``OK\n``, ``ERR INVALID_INT\n``).
   * - **Output**
     - Active Acquisition State
     - State variable enum
     - Internal operational state driving timer gating and DMA arming.

Normative Requirements
----------------------

.. _uuid-55b050ce-51de-43f6-8d3b-14c55b84a56c:

**Requirement:** The Embedded command processing system shall validate incoming integration time requests against the allowable range of 10 us to 5,000,000 us and verify that requests at or below 8,000 us are exact integer divisors of 8,000 us under all configuration requests to reject unsynchronized exposure parameters.

   **Rationale:** Integration times below 8 ms that are not exact divisors of 8,000 us would cause shift-gate (SH) pulses to drift across subsequent frame cycles, destroying the stable 125 Hz frame cadence and introducing variable readout artifacts.

.. _uuid-df5d194e-c5ac-4de3-9d86-009e7d1a4864:

**Requirement:** The Embedded command processing system shall apply accepted integration time changes only at the physical completion of the active frame boundary under continuous acquisition to prevent truncated exposure frames or distorted pixel charge transfers.

   **Rationale:** Altering timer registers mid-readout would corrupt the ongoing ADC DMA sequence, scramble pixel ordering, and risk driving the detector control pins with illegal pulse widths.

.. _uuid-3d8bc45f-d537-43b1-baaa-da4b2cb81839:

**Requirement:** The Embedded command processing system shall discard the first acquired physical frame following any integration time reconfiguration or acquisition restart under normal operation before releasing frames to the USB transfer queue.

   **Rationale:** The initial frame following an exposure change contains integrated charge accumulated under the previous timing regime, rendering its optical content non-representative of the newly requested integration time.

Command Protocol Reference
--------------------------

Commands are transmitted from the Host PC as ASCII strings terminated by a newline character (``\n`` or ``\r\n``):

.. list-table:: Embedded Command Set
   :header-rows: 1

   * - Command
     - Arguments
     - Successful Response
     - Error Response
     - Operational Meaning
   * - ``START``
     - None
     - ``OK``
     - ``ERR ALREADY_RUNNING``
     - Starts continuous waveform timers and arms ADC DMA acquisition.
   * - ``STOP``
     - None
     - ``OK``
     - ``ERR NOT_RUNNING``
     - Safely halts active timers and disables DMA after the current frame completes.
   * - ``SET_INT:<us>``
     - Integer microsecond duration
     - ``OK INT_APPLIED <us>``
     - ``ERR INVALID_INT``
     - Validates and schedules a new electronic shutter integration duration.
   * - ``PING``
     - None
     - ``PONG``
     - None
     - Heartbeat query to verify USB communication link integrity.
   * - ``STATUS``
     - None
     - ``STATUS <state> <int_us> <dropped>``
     - None
     - Queries current operational state, active integration time, and drop count.

State Machine Architecture
--------------------------

The firmware operational state machine transitions between four distinct operating modes:

.. code-block:: text

       +-----------+          START           +-----------+
       |  STOPPED  | -----------------------> |  RUNNING  | <-----+
       +-----------+                          +-----------+       |
             ^                                  |       ^         |
             | STOP /                          SET_INT  | Swapped |
             | Timers halted                    |       | at end  |
             |                                  v       | of frame|
             |                             +-----------------+    |
             |                             |  RECONFIGURING  | ---+
             |                             +-----------------+
             |                                  |
             |                                  | Hardware
             |                                  | Fault
             |                                  v
             | RESET / Clear Error        +-----------+
             +--------------------------- |   FAULT   |
                                          +-----------+

1. **STOPPED:** Timers TIM1, TIM2, TIM3, and TIM4 are halted. ADC DMA is unassigned. The instrument responds to configuration commands and heartbeats without emitting binary frames.
2. **RUNNING:** Waveform timers continuously generate fM, SH, ICG, and ADC triggers. ADC DMA actively populates multi-slot frame buffers, and completed frames stream over USB CDC at the nominal cadence.
3. **RECONFIGURING:** An accepted integration time change is staged in shadow memory. Waveforms continue in their existing mode until the TIM4 frame boundary interrupt triggers a synchronous register reload, discards the transition frame, and returns to ``RUNNING``.
4. **FAULT:** A hardware failure (e.g., DMA buffer overrun, timer update missing deadline) forces an emergency shutdown of the timing generators. Binary streaming halts, and a diagnostic status error is transmitted over USB.
