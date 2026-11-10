ADC and DMA Acquisition
========================

The ADC and DMA Acquisition subsystem manages the digitization of the analog video signal from the Toshiba TCD1304DG linear CCD sensor. It synchronizes ADC conversions with detector pixel readout and uses Direct Memory Access (DMA) to stream raw 16-bit digitized samples directly into memory buffers.

.. _uuid-9850b449-d1ec-4da6-9fc0-2b2d444c9c16:

Subsystem Role & Boundary
-------------------------

UUID: :ref:`9850B449-D1EC-4DA6-9FC0-2B2D444C9C16 <uuid-9850b449-d1ec-4da6-9fc0-2b2d444c9c16>`

This subsystem converts continuous analog sensor output voltages into discrete numerical representations. It operates as a real-time data collector, capturing the full 3694-pixel detector line geometry for every measurement frame while preserving spatial pixel sequence for subsequent baseline subtraction and wavelength mapping on the Host PC.

Inputs and Outputs
------------------

.. list-table::
   :header-rows: 1

   * - Flow
     - Name
     - Type / Format
     - Description
   * - **Input**
     - Conditioned Video Input
     - 0.0 V to 3.3 V on PA0
     - Low-impedance buffered analog video voltage from the driver board.
   * - **Input**
     - TIM2 ADC Conversion Trigger
     - Internal TRGO pulse
     - Hardware trigger initiating conversion at the settled pixel video point.
   * - **Output**
     - Digitized Frame Array
     - Array of 3694 uint16 counts
     - Contiguous 16-bit little-endian raw ADC counts stored in memory.
   * - **Output**
     - Conversion Complete Event
     - Hardware interrupt
     - DMA transfer-complete notification signaling frame availability.

Normative Requirements
----------------------

.. _uuid-d305ba7d-3dc7-44a5-8ad4-225d17863e93:

**Requirement:** The Embedded acquisition system shall sample the conditioned CCD video signal using ADC1 triggered deterministically by TIM2 TRGO pulses under continuous acquisition to eliminate sampling-point phase jitter across pixel conversions.

   **Rationale:** Jitter in the ADC sampling instant relative to the pixel clock causes conversions to land on the settling edge or reset pedestal of the CCD output waveform, injecting artificial noise into pixel counts.

.. _uuid-eb1bc617-2400-4e98-ae6f-28a2470fd8c3:

**Requirement:** The Embedded acquisition system shall transfer exactly 3694 consecutive 16-bit ADC samples per line via Direct Memory Access (DMA2_Stream0) into SRAM without CPU intervention under active capture to prevent lost samples during high-rate streaming.

   **Rationale:** Software-driven sample reading cannot sustain the microsecond pixel conversion rate; direct hardware DMA transfers guarantee zero CPU overhead and bounded acquisition timing.

.. _uuid-b6ca76bf-8875-4ff8-8077-315e8fc1a1be:

**Requirement:** The Embedded acquisition system shall preserve all 3648 effective detector pixels (elements 32 through 3679) in strict spatial acquisition sequence for every accepted capture under all operating modes to maintain geometric traceability for wavelength calibration.

   **Rationale:** Preserving the strict spatial sequence of detector samples ensures that each digitized value corresponds to its true physical detector photosite, which is critical for polynomial wavelength mapping and optical correction.

Detector Line Geometry & Spatial Layout
---------------------------------------

The TCD1304DG linear sensor produces a contiguous line of 3694 analog charge packets for each readout cycle:

.. list-table:: Sensor Line Sample Organization
   :header-rows: 1

   * - Sample Range
     - Element Count
     - Region Classification
     - Downstream Usage
   * - ``[0 : 15]``
     - 16
     - Dummy Shielded Pixels
     - Initial charge-settling elements; discarded by pipeline.
   * - ``[16 : 28]``
     - 13
     - Optical Black (Dark Reference)
     - Optically shielded pixels used by Host PC to compute frame dark baseline :math:`\beta_f`.
   * - ``[29 : 31]``
     - 3
     - Buffer Transition Pixels
     - Boundary isolation between shielded and light-sensitive areas.
   * - ``[32 : 3679]``
     - 3648
     - **Effective Active Pixels**
     - Core light-sensing photodiode array used for spectroscopy and wavelength assignment.
   * - ``[3680 : 3693]``
     - 14
     - Trailing Dummy Pixels
     - Trailing clock flush elements; discarded by pipeline.

ADC and DMA Operational Flow
----------------------------

**Requirement:** The Embedded acquisition system shall acquire one 12-bit
sample per 2 us pixel period at 500 kS/s, with a 0.5 us initial trigger delay
after ICG rise and a 15-cycle aperture at 24 MHz ADC clock, to retain one sample
per nominal detector output.

**Rationale:** The faster 1.333 MS/s diagnostic stream has multiple samples per
pixel and cannot be substituted directly into the production pixel map. The
longer production aperture provides more acquisition time for the analog source.

**Context:** The projected hold instant follows the trigger by approximately
0.719 us including internal trigger latency; analog settling remains unmeasured.

**Requirement:** The Embedded acquisition system shall stop triggering at DMA
completion IRQ entry and reject ADC overrun or DMA-error frames to prevent
conversions beyond the buffer from being accepted as valid readout.

**Rationale:** HAL dispatch latency can otherwise allow further ADC conversions
after the final sample has exhausted the DMA transfer count.

**Requirement:** The Embedded acquisition system shall arm the next frame in
the preceding idle interval and skip frames when a safe arming deadline or buffer
is unavailable to prevent a late start from shifting the pixel sequence.

**Rationale:** The corrected 8 us ICG-low interval is shorter than a full HAL
stop/start sequence, so acquisition cannot be rearmed at ICG fall.

**Requirement:** The Embedded acquisition system shall discard the first
capture following a timing reconfiguration to prevent mixed-exposure charge
from being labeled with the new integration setting.

**Rationale:** The first transferred line may contain charge accumulated under
the preceding shutter schedule.
