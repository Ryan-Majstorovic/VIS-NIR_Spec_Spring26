Integration Interfaces
======================

UUID: ``62A0D29F-0C9F-4B01-A8E8-31FE44B01500``

Integration separates the measurement plane from the control plane.  Optics is
upstream context; the normative cross-subsystem contract begins with the
Embedded measurement-frame responsibility and ends with the Host PC handoffs
to display, capture, retention, and export.

**Measurement plane:** Embedded shall provide complete binary measurement
frames over USB CDC with frame identity and status information.  Each accepted
frame shall preserve all 3648 effective detector samples.  The Host PC shall
reconstruct and validate the frame before correction, wavelength association,
display, capture, retention, or export.

**Control plane:** The Host PC manages connection readiness and requests
acquisition start, acquisition stop, and integration-time changes.  Embedded
applies supported requests and returns an outcome or status.  Command encoding,
legal ordering, application boundary, acknowledgment, errors, retries,
timeouts, and idempotency are ``Not In Docs``.

Responsibility and handoff table:

.. list-table::
   :header-rows: 1

   * - Component
     - Integration responsibility
     - Handoff
   * - Embedded
     - CCD timing, digitization, complete-frame formation, frame identity/status, and supported control application.
     - Measurement frames and control outcomes/status over USB CDC.
   * - Host PC
     - Connection and acquisition coordination, frame reconstruction/validation, processing, display/capture, retention, and export initiation.
     - Qualified spectrum records and export-ready session data.
   * - Communications Inspector
     - Optional independent observation of USB/frame behavior and production of verification evidence.
     - Observation records; never authoritative measurement processing.
   * - Test and Verification
     - Detailed methods, calculations, evidence requirements, and pass/fail disposition.
     - Canonical verification records in :doc:`Test and Verification <../../../test_and_verification/index>`.
   * - Optics
     - Upstream illumination and wavelength-dispersion context.
     - Detector illumination; detailed optics behavior remains outside this Integration pass.

**Physical/electrical context:** The driver-board and USB physical interfaces
must support the responsibilities above.  Connector, rail, pin, logic-level,
shielding, grounding, and electrical acceptance values are owned by the
applicable hardware requirements and are not inferred here.

**Open protocol requirements:** protocol version, packet marker and header,
checksum, field widths, byte order, status-flag meanings, text/binary
coexistence, total transported sample count beyond 3648 effective samples,
resynchronization, disconnect/reconnect behavior, partial-frame disposition,
and concurrent port access are ``Not In Docs``.

Local traceability
------------------

.. _integration-traceability-db0c2800:

``DB0C2800`` defines the Embedded, Host PC, and support-tool responsibility
boundary.

**Alignment state:** ``Not Started``

**Requirements evidence:** Requirements And Metrics; approved Embedded and Host
PC responsibility statements.

**Future implementation location:** TODO: identify the Embedded, Host PC, and
support-tool modules during the later implementation comparison.

.. _integration-traceability-4000e1ca:

``4000E1CA`` defines complete USB CDC frame-transfer responsibility with frame
identity and status.

**Alignment state:** ``Not Started``

**Requirements evidence:** Requirements And Metrics USB transfer and detector
geometry requirements; Design Document USB interface requirements.

**Future implementation location:** TODO: identify the frame producer,
transport, and host-ingress locations during the later implementation
comparison.

.. _integration-traceability-f700cd12:

``F700CD12`` defines the start, stop, integration-time, and outcome/status
boundary.

**Alignment state:** ``Not Started``

**Requirements evidence:** Design Document host-command and configurable
integration-time requirements; approved Host PC and Embedded control statements.

**Future implementation location:** TODO: identify the host control and Embedded
request-application locations during the later implementation comparison.

.. _integration-traceability-a252a879:

``A252A879`` defines the end-to-end measurement handoff through host display and
capture.

**Alignment state:** ``Not Started``

**Requirements evidence:** Requirements And Metrics real-time display and
capture requirement; approved Host PC pipeline and operator-application pages.

**Future implementation location:** TODO: identify the host ingress,
processing, display, and capture locations during the later implementation
comparison.

.. _integration-traceability-2bedc9a3:

``2BEDC9A3`` defines the required CSV data-product handoff.

**Alignment state:** ``Not Started``

**Requirements evidence:** Requirements And Metrics export fields; approved
Host PC retention and export pages.

**Future implementation location:** TODO: identify the session-retention and
CSV-export locations during the later implementation comparison.

.. _integration-traceability-7205fdb2:

``7205FDB2`` defines the Communications Inspector as independent verification
support.

**Alignment state:** ``Not Started``

**Requirements evidence:** Intended Tooling And Integration issue; Design
Document MCU-to-host interface-verification needs.

**Future implementation location:** TODO: identify the Communications Inspector
entry point and evidence-output locations during the later implementation
comparison.

.. _integration-traceability-191acd4f:

``191ACD4F`` defines integration verification sequencing and evidence fields.

**Alignment state:** ``Not Started``

**Requirements evidence:** Design Document interface, integration, regression,
and acceptance-testing sections.

**Future implementation location:** TODO: identify interface fixtures, evidence
records, and verification entry points during the later implementation
comparison.

.. _integration-traceability-6805fd49:

``6805FD49`` records unresolved transport and display acceptance profiles.

**Alignment state:** ``Not In Docs``

**Requirements evidence:** Requirements And Metrics separates the above-100-fps
design target from lower documented subsystem acceptance thresholds; approved
Embedded pages define a 10-fps minimum transport profile.

**Future implementation location:** TODO: identify transport measurement and
display-performance locations after the missing profiles are approved.

Protocol details explicitly identified as open remain ``Not In Docs`` and are
reviewed separately from the documented behaviors above.



