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

1. **Triggering:** ``TIM2`` generates an internal TRGO event at each pixel interval. The trigger is timed to fire :math:`0.5\,\mu\text{s}` after the pixel transition, allowing the analog buffer amplifier to settle completely.
2. **Quantization:** ``ADC1`` performs a 12-bit successive-approximation conversion in approximately :math:`0.25\,\mu\text{s}`, producing an unsigned integer value from 0 to 4095.
3. **DMA Streaming:** ``DMA2_Stream0`` transfers each 16-bit halfword directly into the designated frame buffer in SRAM.
4. **Completion:** Upon reaching 3694 transfers, the DMA controller triggers ``HAL_ADC_ConvCpltCallback``, which closes the active capture slot and disables TIM2 until the next frame boundary.
