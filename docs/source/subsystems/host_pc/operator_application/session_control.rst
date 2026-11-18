Session Control
===============

Session Control covers the operator's recording workflow and the rolling
buffers used by live display and bias capture.

.. _uuid-a3b4c5d6-e7f8-49a0-b1c2-334455667701:

Normative Requirements
----------------------

.. _uuid-a3b4c5d6-e7f8-49a0-b1c2-334455667702:

**Requirement:** The Host PC Session Control system shall retain up to
``max_session_frames`` complete recent frames in a thread-safe circular buffer
for bias capture and shall retain compact spectrogram rows for the rolling
display.

**Rationale:** Recent covered frames support master bias capture. Bounded
retention limits memory use during continuous streaming.

.. _uuid-a3b4c5d6-e7f8-49a0-b1c2-334455667705:

**Requirement:** The Host PC Operator Application shall expose integration time,
a recording button, and Export Session in the Integration and Recording card
and shall honor its saved visibility setting. The recording button shall show
Stop Binary Recording during an active recording and Start Binary Recording
when idle, with the button disabled during export.

**Rationale:** Keeping acquisition settings and capture actions together lets
the operator control a measurement run without losing their display layout.
The button label identifies the action available for the current recording state.

.. _uuid-a3b4c5d6-e7f8-49a0-b1c2-334455667706:

**Requirement:** The Host PC Session Control system shall finalize accepted
frames to the HDF5 file when the operator stops recording and shall enable
Export Session when the latest recording has finalized successfully and
contains at least one frame.

**Rationale:** A finalized source keeps export from reading frames that are
still being written, and the frame check ensures the archive contains
measurement data.

Verification
------------

* Check that the integration controls and recording actions fit at wide and
  narrow window sizes.
* Stream beyond the configured buffer depth and verify that the newest frames
  remain available for bias capture.
* Check Export Session before recording, during recording, after stopping an
  empty recording, and after successfully stopping a recording with frames.
