Session Control
===============

The Session Control system provides the operator-facing workflow for managing measurement sessions. It coordinates user-initiated recording boundaries, circular in-memory buffer sizing, session reset operations, and session metadata tracking.

.. _uuid-a3b4c5d6-e7f8-49a0-b1c2-334455667701:

Subsystem Scope & Workflow
--------------------------

UUID: :ref:`A3B4C5D6-E7F8-49A0-B1C2-334455667701 <uuid-a3b4c5d6-e7f8-49a0-b1c2-334455667701>`

This stage governs the **operator workflow session**, maintaining clean separation from the lower-level transport stream:
* **Workflow Boundaries:** The operator can begin a measurement run, clear active history, or freeze buffers for export analysis.
* **Bounded In-Memory Retention:** Implements a thread-safe circular buffer (default 500 frames) that retains complete ``SpectrumFrame`` objects for instant CSV export without risking system memory exhaustion.

Inputs and Outputs
------------------

.. list-table::
   :header-rows: 1

   * - Flow
     - Name
     - Structure / Type
     - Description
   * - **Input**
     - User Actions
     - UI Events
     - Reset Session, Export CSV, Start/Stop Recording button clicks.
   * - **Input**
     - UI Configuration
     - ``UIConfig``
     - Configurable buffer depth (``max_session_frames``, default 500).
   * - **Output**
     - Session Status
     - ``SessionStatus``
     - Session ID, start time, buffered frame count, and last export file path.
   * - **Output**
     - Buffered Frames
     - ``deque[SpectrumFrame]``
     - Time-ordered buffer of recent full measurement frames.

Normative Requirements
----------------------

.. _uuid-a3b4c5d6-e7f8-49a0-b1c2-334455667702:

**Requirement:** The Host PC Session Control system shall maintain a thread-safe circular buffer that retains up to ``max_session_frames`` (default 500 frames) of complete ``SpectrumFrame`` records in memory.

   **Rationale:** Retaining a bounded circular buffer in memory provides instant access to recent capture history for CSV export while preventing unbounded RAM growth during continuous streaming.

.. _uuid-a3b4c5d6-e7f8-49a0-b1c2-334455667703:

**Requirement:** The Host PC Session Control system shall generate a unique session identifier and initialize a new UTC start timestamp upon receiving a Session Reset request.

   **Rationale:** Unique session identifiers prevent data records and export files from different experimental runs from being conflated.

.. _uuid-a3b4c5d6-e7f8-49a0-b1c2-334455667704:

**Requirement:** The Host PC Session Control system shall atomically clear in-memory capture buffers, reset spectrogram history textures, and reset dropped frame counters when a Session Reset is triggered.

   **Rationale:** Atomic clearing guarantees that old measurement data does not bleed into the newly initiated acquisition run.

Session Workflow & Actions
--------------------------

* **Session Reset:** Clears in-memory frame queues, resets spectrogram textures, resets missed frame counters, and assigns a new session UUID.
* **Buffer Size Configuration:** The operator can adjust ``max_session_frames`` via user settings to allocate larger or smaller memory buffers based on available host RAM.
* **Session Status Card:** Displays active session ID, elapsed session time, total frames captured, and last exported CSV filename.

Verification & Testing
----------------------

* **Circular Buffer Cap Check:** Stream 1000 frames into a buffer configured for 500 frames; verify that exactly 500 frames are retained and that the oldest 500 frames were purged in FIFO order.
* **Reset Atomicity Check:** Trigger a reset while streaming; verify that the buffered count immediately drops to 0 and that the subsequent frame carries the new session identifier.
