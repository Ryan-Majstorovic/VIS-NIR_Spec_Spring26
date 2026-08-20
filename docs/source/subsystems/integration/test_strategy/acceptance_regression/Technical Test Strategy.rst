Technical Test Strategy
=======================

UUID: ``4D2E2C6E-7569-4558-ABEA-F4782F0C2AF3``

Integration verification shall progress from individual interface checkpoints
to the end-to-end measurement and control handoffs:

1. Confirm that Embedded forms and USB CDC transfers a complete frame preserving
   all 3648 effective samples.
2. Observe frame identity and status information and record any rejected,
   incomplete, or discontinuous observations.
3. Measure sustained accepted-frame rate.  The minimum Embedded/USB profile is
   at least 10 complete frames per second at minimum integration time.  The
   above-100-frames-per-second system design target and Host PC display-update
   profile are separate; their complete conditions and acceptance criteria
   remain ``Not In Docs``.
4. Exercise start, stop, and integration-time request round trips and observe
   the returned outcome/status.  Encoding, application timing, timeout, retry,
   and recovery details remain open.
5. Confirm that a qualified host record reaches the live display and capture
   handoff without bypassing ingress validation.
6. Confirm that the export handoff provides raw ADC counts, processed counts,
   wavelengths, volts, and processed intensity for the same measurement.
7. When independent evidence is required, use the Communications Inspector to
   observe the boundary without treating it as the normal operator application.

**Minimum evidence record:** requirement/traceability ID, hardware and
configuration revision, interface-contract revision, test conditions,
observation start and duration, accepted/rejected counts where applicable,
observed outcomes/status, evidence-artifact reference, and pass/fail or
unresolved disposition.

**Regression triggers:** Re-run the affected checkpoints after changes to frame
geometry, packet or status contract, control sequencing, integration-time
contract, connection behavior, host ingress qualification, processing order,
display/capture handoff, or CSV schema.  Optical alignment and calibration
changes may trigger system tests, but their methods are not duplicated here.

Detailed procedures, characterization categories, calculations, retention
rules, and canonical pass/fail disposition belong to :doc:`Test and
Verification <../../../test_and_verification/index>`.

**Traceability:** :ref:`191ACD4F <integration-traceability-191acd4f>` and
:ref:`6805FD49 <integration-traceability-6805fd49>`; alignment state ``Not
Started`` for the documented checkpoints and ``Not In Docs`` for unresolved
profiles.



