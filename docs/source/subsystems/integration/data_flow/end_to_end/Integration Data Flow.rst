Integration Data Flow
=====================

UUID: ``D37D1295-2B68-4EAD-A7A4-A3C29C2993C3``

Measurement-plane flow
----------------------

1. An external optical input illuminates the detector through the optical
   subsystem.  Optical behavior is upstream context for this Integration pass.
2. Embedded timing and acquisition digitize the detector output.
3. Embedded forms a complete measurement frame that preserves all 3648
   effective detector samples and associates frame identity and status.
4. USB CDC transfers the frame across the host-device boundary.
5. The Host PC reconstructs the frame, checks completeness and contract
   conformance, and preserves raw ADC counts with the frame context.
6. Host-owned processing applies approved bias/dark, bad-pixel, wavelength, and
   spectral-correction stages without redefining them here.
7. The operator application receives a qualified wavelength-and-intensity
   record for live display and capture.
8. HDF5 capture retains the measurements and the associated calibration and
   timing state during recording.
9. Session export packages raw ADC counts, processed counts, volts, and
   processed intensity in a CSV and puts wavelength mapping, calibration,
   and timing ranges in a separate JSON entry in the same ZIP.

Only complete, contract-conforming measurement content may advance from USB
ingress to host processing. The capture and archive contracts are defined in
:doc:`Host PC Session Retention <../../../host_pc/operator_application/export_initiation_and_session_retention>`.

Control-plane flow
------------------

1. The Host PC establishes and reports connection readiness.
2. The Host PC requests acquisition start, acquisition stop, or an
   integration-time change when the operator workflow permits it.
3. Embedded applies a supported request according to the approved interface
   contract.
4. Embedded returns an outcome or status, and the Host PC exposes the result to
   the dependent workflow.

Command encoding, legal state ordering, integration-time units/range/
granularity, exact application boundary, acknowledgments, retries, timeouts,
idempotency, disconnect/reconnect, and recovery are ``Not In Docs``.

Integration checkpoints occur at complete-frame formation, USB transfer, host
qualification, display/capture handoff, and session archive handoff. Detailed
procedures and pass/fail disposition belong to :doc:`Test and Verification
<../../../test_and_verification/index>`.

**Traceability:** :ref:`4000E1CA <integration-traceability-4000e1ca>`,
:ref:`F700CD12 <integration-traceability-f700cd12>`,
:ref:`A252A879 <integration-traceability-a252a879>`, and
:ref:`2BEDC9A3 <integration-traceability-2bedc9a3>`; alignment state ``Not
Started``.



