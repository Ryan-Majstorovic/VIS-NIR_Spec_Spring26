Validation
==========

.. _trace-2ed19d37:
.. _uuid-95e711d5-fa43-48be-b294-3fdff36ffe13:

Planned Client Validation Steps
-------------------------------

UUID: :ref:`95E711D5-FA43-48BE-B294-3FDFF36FFE13 <uuid-95e711d5-fa43-48be-b294-3fdff36ffe13>`

**Local Traceability ID:** :ref:`2ED19D37 <trace-2ed19d37>`

**Alignment State:** Not Started

**Step 1:** Connect the instrument through the documented operator workflow.

   **Expected Outcome:** Connection readiness is visible and acquisition
   actions remain gated until readiness is established.

**Step 2:** Begin an acquisition session.

   **Expected Outcome:** The session state becomes visible and complete frames
   become eligible for processing and retention.

**Step 3:** Confirm live spectral presentation.

   **Expected Outcome:** A qualified intensity-versus-wavelength view is
   presented; rolling spectrogram behavior is available when selected.

**Step 4:** Request an integration-time change.

   **Expected Outcome:** The operator can distinguish a successful, rejected,
   or unavailable future command outcome and can identify when a successful
   value becomes active.

**Step 5:** Select or apply the calibration inputs required by the planned
measurement.

   **Expected Outcome:** Active bias/dark, wavelength, flat-field/PRNU, and
   spectral-response/QE selections are visible, and missing or incompatible
   inputs are not silently activated.

**Step 6:** Initiate CSV export for the retained session.

   **Expected Outcome:** The planned export contains raw ADC counts, processed
   counts, wavelength, volts, and processed intensity with row correspondence.

**Step 7:** Review the resulting spectrum and the verification evidence record.

   **Expected Outcome:** Requirement identity, setup, raw observations, derived
   metrics, criterion state, artifact location, and review state are present.

**Rationale:** The client workflow demonstrates the intended routine path from
connection through evidence review without requiring source-code or hardware
reconfiguration.

**Open Requirement:** Overall client-demonstration criterion, permitted setup
assistance, timing limit, evidence-retention rule, and reviewer authority are
``Not In Docs``.
