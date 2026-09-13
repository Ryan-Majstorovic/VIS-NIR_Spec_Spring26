CCD1 Communication Protocol Overview
=====================================

UUID: ``A1B2C3D4-E5F6-7890-ABCD-EF1234567890``

The CCD1 communication protocol defines the binary frame format and ASCII text line structure used for data exchange between the embedded CCD controller MCU and the host PC application over USB CDC serial transport. This section describes the wire protocol at a high level; detailed I/O structures, bit-level field definitions, and validation rules are documented in the linked pages below.

Protocol Scope
--------------

The protocol operates over a full-duplex USB CDC serial link and supports two packet types:

* **Binary frame packets** (packet type 1): Carry ADC sample data from the CCD sensor with validated header fields and little-endian unsigned 16-bit payload samples.
* **ASCII text packets**: Carry startup banners, diagnostic messages, and command responses delimited by newline characters.

All binary frames begin with a 4-byte magic identifier ``CCD1`` followed by a fixed-size header structure and variable-length ADC payload.

Related Pages
-------------

.. toctree::
   :maxdepth: 1

   inputs_and_outputs
   procedure
   error_handling
