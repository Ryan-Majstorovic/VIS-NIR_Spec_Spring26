Integration Time Control
========================

The Integration Time Control system manages the optical integration time of the linear CCD sensor. It defines the baseline hardware timing configuration and specifies the planned command protocol and microcontroller execution boundary for runtime integration-time adjustment.

.. _uuid-d3e4f5a6-b7c8-49d0-e1f2-334455667701:

Baseline Hardware Reality & Planned Architecture
------------------------------------------------

UUID: :ref:`D3E4F5A6-B7C8-49D0-E1F2-334455667701 <uuid-d3e4f5a6-b7c8-49d0-e1f2-334455667701>`

* **Current Baseline State:** The STM32 microcontroller firmware initializes shift gate timing (TIM3 CH1 on PA6) as a fixed PWM waveform. The readout gate (TIM4 CH1 on PB6) runs on a fixed 8.000 ms frame period (125 Hz).
* **Planned Feature Specification:** Runtime electronic shutter control via host command protocol to adjust photon accumulation time independently of the frame readout period.

Inputs and Outputs
------------------

.. list-table::
   :header-rows: 1

   * - Flow
     - Name
     - Structure / Type
     - Description
   * - **Input**
     - Requested Integration Time
     - Integer (:math:`\mu\text{s}`)
     - Operator-selected exposure duration in microseconds.
   * - **Output**
     - Command String
     - ASCII string
     - Formatted wire command (e.g., ``"INTEG 2000\n"``).
   * - **Output**
     - Active Integration State
     - Enum / Status
     - ``Applied``, ``Pending``, or ``Rejected``.

Normative Requirements (Planned Specification)
----------------------------------------------

.. _uuid-d3e4f5a6-b7c8-49d0-e1f2-334455667702:

**Requirement:** The Host PC Integration Time Control system shall validate that requested integration times fall within the permissible range of :math:`10\,\mu\text{s}` to :math:`8000\,\mu\text{s}` before transmitting the command to hardware.

   **Rationale:** The lower bound of :math:`10\,\mu\text{s}` is constrained by the minimum CCD shift gate pulse width, and the upper bound of :math:`8000\,\mu\text{s}` is bounded by the fixed 8.0 ms ICG readout period.

.. _uuid-d3e4f5a6-b7c8-49d0-e1f2-334455667703:

**Requirement:** The Host PC Integration Time Control system shall format integration time requests as ASCII line commands adhering to the wire syntax `INTEG <duration_microseconds>\n`.

   **Rationale:** Plain ASCII line-terminated commands maintain protocol consistency with the USB CDC virtual COM port text interface and facilitate independent verification.

.. _uuid-d3e4f5a6-b7c8-49d0-e1f2-334455667704:

**Requirement:** The integration-time control architecture shall require the microcontroller firmware to apply shift gate timer register updates strictly at the TIM4 ICG pulse finished interrupt boundary.

   **Rationale:** Reprogramming shift gate timer registers during an active analog readout corrupts the pixel shift register transfer; latching timer updates at the ICG boundary guarantees that new exposure periods begin cleanly on the subsequent frame.

.. _uuid-d3e4f5a6-b7c8-49d0-e1f2-334455667705:

**Requirement:** The Host PC Integration Time Control system shall mark a requested integration time as ``Pending`` upon transmission and transition to ``Applied`` only upon receiving confirmation from the firmware (``OK INTEG <actual_microseconds>\\n``).

   **Rationale:** Acknowledgment-driven state gating prevents the Host PC and export records from reporting an integration time that was rejected or dropped by the microcontroller.

Planned State Machine
---------------------

.. list-table::
   :header-rows: 1

   * - Current State
     - Trigger
     - Next State
     - Action
   * - ``Applied``
     - Operator inputs new :math:`\mu\text{s}` value.
     - ``Validating``
     - Check range :math:`[10, 8000]\,\mu\text{s}`.
   * - ``Validating``
     - Value valid.
     - ``Pending``
     - Transmit ``"INTEG <val>\n"``.
   * - ``Validating``
     - Value out of bounds.
     - ``Applied``
     - Reject request, alert operator.
   * - ``Pending``
     - Receive ``"OK INTEG <val>\n"``.
     - ``Applied``
     - Update active metadata, log confirmation.
   * - ``Pending``
     - Timeout (1.0 s) or error response.
     - ``Applied`` (revert)
     - Revert active metadata to previous confirmed value.

Verification & Testing (Planned Acceptance)
-------------------------------------------

* **Range Boundary Test:** Submit :math:`5\,\mu\text{s}` and :math:`10000\,\mu\text{s}`; verify both are rejected by client-side validation.
* **Timing Latch Test:** Using an oscilloscope on PA6 (SH) and PB6 (ICG), verify that pulse width modifications take effect exactly at the falling edge of ICG.
