USB CDC Stream
==============

UUID: ``A89AE97C-5C91-4E48-B052-A1DDC26781C0``

The firmware sends startup text lines and then binary ``CCD1`` frame packets.
The binary header fields are:

* ``magic``: ``CCD1``.
* ``version``: ``1``.
* ``packet_type``: ``1`` for frame packets.
* ``reserved``: currently ``0``.
* ``frame_id``: monotonically increasing ICG-cycle frame number.
* ``sample_count``: currently ``3694``.
* ``effective_start``: currently ``32``.
* ``effective_count``: currently ``3648``.
* ``flags``: ICG sync, timing fault, and USB timeout bits.
* ``payload_bytes``: ``sample_count * 2``.

The Python parser mirrors the little-endian layout ``<4sBBHIHHHHI``. Frame ID
gaps on the host indicate missed capture opportunities because IDs are assigned
from the ICG cycle counter before slot acquisition.



