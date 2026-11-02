Acquisition Session Control
===========================

The Acquisition Session Control system manages the continuous data stream lifecycle across the active hardware connection. It tracks frame counter continuity at 125 Hz, detects missing frame sequences, measures stream throughput and jitter, and coordinates background frame dispatch to session storage and display subsystems.

.. _uuid-c2d3e4f5-a6b7-48c9-d0e1-223344556601:

Subsystem Scope & Stream Separation
-----------------------------------

UUID: :ref:`C2D3E4F5-A6B7-48C9-D0E1-223344556601 <uuid-c2d3e4f5-a6b7-48c9-d0e1-223344556601>`

This stage governs the **transport-level stream lifecycle**, distinguishing it from the operator-level workflow session:
* **Stream Lifecycle (This Section):** Focuses on physical frame delivery, frame counter sequence monitoring, missed frame detection, and acquisition rate calculation.
* **Operator Session Workflow (:doc:`../operator_application/session_control`):** Focuses on user-initiated session recording, in-memory buffer sizing, and CSV export file generation.

Inputs and Outputs
------------------

.. list-table::
   :header-rows: 1

   * - Flow
     - Name
     - Structure / Type
     - Description
   * - **Input**
     - Parsed Frame
     - ``BinaryFramePacket``
     - Reconstructed frame from stream parser containing ``frame_id`` and counts.
   * - **Output**
     - Stream Metrics
     - ``PerformanceCounterSnapshot``
     - Rolling stream frame rate (FPS), total frames received, and missed frame counts.
   * - **Output**
     - Stream Status
     - ``DeviceStatus``
     - Current frame arrival timestamp, preview samples, and connection health flags.

Normative Requirements
----------------------

.. _uuid-c2d3e4f5-a6b7-48c9-d0e1-223344556602:

**Requirement:** The Host PC Acquisition Session Control system shall monitor the sequence continuity of incoming hardware frame counters (``frame_id``) and record a missed-frame event whenever :math:`\Delta \text{frame\_id} > 1`.

   **Rationale:** The STM32 microcontroller increments ``frame_id`` monotonically on every digitized frame; sequence gaps indicate USB bus drops, DMA transfer overruns, or host thread starvation.

.. _uuid-c2d3e4f5-a6b7-48c9-d0e1-223344556603:

**Requirement:** The Host PC Acquisition Session Control system shall compute the rolling stream acquisition frame rate using a moving time window across received frame timestamps.

   **Rationale:** Computing stream acquisition rate provides real-time verification that the hardware acquisition loop is operating at its nominal 125 Hz target.

.. _uuid-c2d3e4f5-a6b7-48c9-d0e1-223344556604:

**Requirement:** The Host PC Acquisition Session Control system shall dispatch every valid incoming frame to active background recording queues without throttling or discarding frames.

   **Rationale:** While the UI rendering loop is intentionally decoupled to 30 FPS, the acquisition stream coordination layer must preserve all 125 FPS for scientific disk recording.

Continuity & Performance Tracking
---------------------------------

1. **Missed Frame Calculation:**
   Upon arrival of frame :math:`i` with counter :math:`F_i`:

   .. math::

      \Delta F = F_i - F_{i-1}

   If :math:`\Delta F > 1`, the count of missed frames is incremented by :math:`\Delta F - 1`. If :math:`\Delta F \le 0` (excluding 32-bit counter rollover), an out-of-order counter diagnostic is flagged.

2. **Stream Rate Estimation:**
   Using the arrival timestamps :math:`t_i` of the last :math:`M` frames:

   .. math::

      \text{FPS}_{\text{stream}} = \frac{M}{t_i - t_{i-M}}

Diagnostics & Alerts
--------------------

* **Dropped Frame Alert:** If the missed-frame counter increases during an active session, an alert indicator on the diagnostics card is updated.
* **Stream Stalled Warning:** If no new binary frames arrive within 500 ms while in the ``Connected`` state, the acquisition status transitions to ``Stalled`` and the operator is notified.

Verification & Testing
----------------------

* **Sequence Gap Test:** Inject synthetic frames with sequence IDs ``[1, 2, 3, 6, 7]`` and verify that exactly 2 missed frames are reported.
* **125 Hz Rate Verification:** Verify that streaming 1000 frames at 8 ms intervals results in an estimated rate of :math:`125.0 \pm 1.0\,\text{FPS}`.
