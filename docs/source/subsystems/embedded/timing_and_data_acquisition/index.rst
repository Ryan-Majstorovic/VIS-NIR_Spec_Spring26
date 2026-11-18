Timing and Data Acquisition
============================

The Timing and Data Acquisition subsystem generates the precision electronic waveforms that operate the linear CCD, synchronizes the onboard ADC with detector pixel readout, and manages continuous DMA sample transfers into multi-slot memory buffers.

.. _uuid-4ec244c6-3b21-4485-8c9d-113ee3110972:

Subsystem Role & Responsibilities
---------------------------------

UUID: :ref:`4EC244C6-3B21-4485-8C9D-113EE3110972 <uuid-4ec244c6-3b21-4485-8c9d-113ee3110972>`

This subsystem acts as the real-time acquisition engine of the embedded spectrometer:

* **Waveform Synthesis:** Operates synchronized hardware timers to generate the 2.0 MHz master clock (fM), electronic shutter shift gate (SH), integration clear gate (ICG), and conversion triggers across exposures ranging from 10 us to 5 s.
* **Analog Digitization:** Triggers ADC1 at each pixel readout interval to convert conditioned analog sensor voltages into 16-bit little-endian count values with minimal jitter.
* **DMA Stream Pipelining:** Employs Direct Memory Access (DMA) to stream 3694 detector line samples per frame directly into circular multi-slot SRAM buffers without CPU polling.
* **Frame Integrity & Continuity:** Maintains strict spatial pixel order (32 leading dummy/shielded, 3648 effective active, 14 trailing dummy pixels), increments hardware frame sequence counters, and tracks overrun conditions.

.. _uuid-0d889212-8b33-414c-b44b-b168e38b66fc:

Subsystem Sections
------------------

UUID: :ref:`0D889212-8B33-414C-B44B-B168E38B66FC <uuid-0d889212-8b33-414c-b44b-b168e38b66fc>`

.. list-table::
   :header-rows: 1

   * - Section
     - Core Engineering Responsibilities
   * - :doc:`ccd_timing_and_waveform_generation`
     - Consolidated timer architecture (TIM1, TIM2, TIM3, TIM4), 10 us to 5 s exposure schedules, DMA shadow register reload, and waveform constraints.
   * - :doc:`adc_and_dma_acquisition`
     - 12-bit ADC1 conversion, TIM2 TRGO hardware triggering, DMA stream transfers, and 3694-pixel detector line geometry.
   * - :doc:`frame_synchronization_and_buffer_management`
     - Circular 4-slot ping-pong frame buffer management, monotonic frame ID generation, and drop/overrun fault monitoring.

.. toctree::
   :maxdepth: 1

   ccd_timing_and_waveform_generation
   adc_and_dma_acquisition
   frame_synchronization_and_buffer_management
