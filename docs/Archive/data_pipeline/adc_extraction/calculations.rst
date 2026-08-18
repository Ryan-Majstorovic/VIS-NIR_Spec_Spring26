Calculations
============

The ADC count extraction stage uses the following symbols:

* ``B_0, B_1``: least-significant and most-significant bytes at pixel index ``i``.
* ``P_expected``: expected pixel count per frame (3648 for TCD1304DG).
* ``C_extracted[i]``: extracted ADC count at pixel index ``i``.

Byte-Order Conversion Calculation
----------------------------------

UUID: ``A3B7D520-R001-4C81-B091-2F3A6C94D70E``

The system reads each pair of bytes directly as a little-endian unsigned 16-bit integer using the ``<u2`` numpy dtype specifier. For byte pair ``(B_0, B_1)`` at pixel index ``i`` where ``B_0`` is the least-significant byte and ``B_1`` is the most-significant byte:

``V_i = B_0 + 256 * B_1``

The device transmits values in little-endian byte order. On little-endian hosts (x86/x64), no runtime byte swap is required. On big-endian hosts, the numpy ``<u2`` dtype specifier handles endianness conversion automatically during frombuffer interpretation.

ADC Count Assignment
--------------------

UUID: ``A3B7D520-R002-4C81-B091-2F3A6C94D70E``

The protocol stores ADC counts as raw unsigned 16-bit integers. Each extracted value is the physical ADC count:

``C_extracted[i] = V_i``

where ``V_i`` is the unsigned 16-bit integer read directly from the payload via ``np.frombuffer(payload, dtype="<u2")``. The values are later cast to float64 for calibration arithmetic but carry no implicit scaling factor from the communication protocol.

Array Length Verification
-------------------------

UUID: ``A3B7D520-R003-4C81-B091-2F3A6C94D70E``

The extraction is valid only if the resulting array length matches the expected pixel count:

``len(C_extracted) == P_expected``

where ``P_expected = 3648`` for the TCD1304DG sensor. Any deviation triggers the ``extraction_complete`` flag to false.

Extraction Latency Measurement
------------------------------

UUID: ``A3B7D520-R004-4C81-B091-2F3A6C94D70E``

The extraction latency is measured as:

``latency_us = (t_end - t_start) * 1_000_000``

where ``t_start`` is the timestamp immediately before byte-order conversion begins and ``t_end`` is the timestamp after all 3648 values are extracted. The result is reported in microseconds.