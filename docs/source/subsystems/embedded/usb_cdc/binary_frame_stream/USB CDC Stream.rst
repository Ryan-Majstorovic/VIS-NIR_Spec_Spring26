USB CDC Stream
==============

UUID: ``A89AE97C-5C91-4E48-B052-A1DDC26781C0``

The Embedded subsystem shall transmit each completed measurement frame over USB
CDC together with a frame identifier and status flags.  The receiver must be
able to distinguish a complete frame from a partial, malformed, or faulted
capture.

The minimum embedded transfer acceptance is complete frames containing all
3648 effective detector samples at no less than 10 frames per second at the
minimum integration time.  This lower subsystem acceptance is distinct from
the overall system design target above 100 frames per second.

The following details remain shared-contract open requirements and shall be
defined by Integration before implementation conformance is judged:

* packet marker/name and versioning;
* header fields, widths, byte order, and payload-length calculation;
* frame-identity allocation and gap semantics;
* effective-pixel and any non-effective sample representation;
* status-flag meanings, acknowledgments, and error/recovery behavior; and
* whether startup or diagnostic text shares the data stream.

The Embedded responsibility is to populate the contract from acquisition state,
not to silently fabricate samples or hide a failed capture.  Normative packet
details are ``Not In Docs`` at this boundary until the Integration contract is
approved.



