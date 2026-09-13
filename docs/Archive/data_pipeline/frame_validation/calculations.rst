Calculations
============

The frame validation stage uses the following symbols:

* ``N``: ADC resolution in bits (configured value).
* ``M``: maximum valid ADC count, computed as ``2^N - 1``.
* ``P_expected``: expected pixel count per frame (3648 for TCD1304DG).
* ``S_{expected}``: expected sequence number (last known sequence number plus one).

Range Validation Calculation
----------------------------

UUID: ``F8A2C410-R001-4B91-A076-1E2F5C83D60A``

For each ADC count ``C_i`` in the decoded payload at index ``i``:

``valid = 0 <= C_i <= M``

where ``M = 2^N - 1``. If any ``C_i`` falls outside this range, the frame fails validation.

Payload Length Check
--------------------

UUID: ``F8A2C410-R002-4B91-A076-1E2F5C83D60A``

Let ``L_payload`` be the length of the decoded payload array. The frame passes the length check if:

``L_payload == P_expected``

where ``P_expected = 3648`` for the TCD1304DG sensor. Frames with ``L_payload != P_expected`` are flagged as malformed.

Frame Counter Continuity
------------------------

UUID: ``F8A2C410-R003-4B91-A076-1E2F5C83D60A``

Let ``S_{received}`` be the sequence number in the incoming packet header and ``S_{expected}`` be the expected value (last known valid sequence number plus one). The system computes:

``delta = S_{received} - S_{expected}``

* If ``delta == 0``, the frame is continuous and accepted.
* If ``delta > 1``, a gap of ``delta - 1`` frames is detected and counted.
* If ``delta < 0``, a duplicate or out-of-order frame is detected and counted.

Dropped Frame Count Update
--------------------------

UUID: ``F8A2C410-R004-4B91-A076-1E2F5C83D60A``

The dropped-frame counter ``C_dropped`` is incremented as follows:

``C_dropped = C_dropped + max(0, delta - 1)``

when ``delta > 1``, or:

``C_dropped = C_dropped + 1``

when any validation check fails.