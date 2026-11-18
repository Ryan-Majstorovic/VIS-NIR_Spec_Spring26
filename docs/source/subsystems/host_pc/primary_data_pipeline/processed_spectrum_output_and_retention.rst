Processed Spectrum Output and Retention
=======================================

The Processed Spectrum Output and Retention stage finalizes measurement frame transformations. It converts counts into physical voltages, generates normalized display series for the real-time line plot, compresses active pixels into fixed 256-bin spectrogram rows, and bundles derived products into an immutable ``SpectrumFrame`` for session retention and export.

.. _uuid-f1a2b3c4-d5e6-47f8-a9b0-112233445566:

Subsystem Role & Assembly
-------------------------

UUID: :ref:`F1A2B3C4-D5E6-47F8-A9B0-112233445566 <uuid-f1a2b3c4-d5e6-47f8-a9b0-112233445566>`

This stage serves as the bridge between internal numerical pipeline routines and external application consumers (the Kivy GUI, session buffers, and export serializers). It guarantees that all derived outputs (counts, volts, wavelengths, normalized curves, and spectrogram rows) are co-registered with the same source frame counter and timestamp.

Inputs and Outputs
------------------

.. list-table::
   :header-rows: 1

   * - Flow
     - Name
     - Structure / Type
     - Description
   * - **Input**
     - Raw ADC Counts
     - 1D Array (int)
     - Preserved source counts from frame ingress.
   * - **Input**
     - Corrected Light Counts
     - 1D Array (float)
     - Light counts after bias, dark, and spectral corrections.
   * - **Input**
     - Wavelengths
     - 1D Array (float)
     - Evaluated wavelength values in nanometers.
   * - **Output**
     - Voltages (:math:`\mathbf{V}`)
     - 1D Array (float)
     - Voltage equivalent of optical signal across active pixels.
   * - **Output**
     - Live Display Counts
     - 1D Array (float)
     - Normalized :math:`[0.0, 1.0]` signal for real-time line plotting.
   * - **Output**
     - Spectrogram Row
     - List of 256 floats
     - Downsampled :math:`[0.0, 1.0]` values for rolling waterfall texture.
   * - **Output**
     - Spectrum Frame
     - ``SpectrumFrame``
     - Co-registered immutable record passed to state and session managers.

Normative Requirements
----------------------

.. _uuid-a2b3c4d5-e6f7-48a9-b0c1-223344556677:

**Requirement:** The Host PC Primary Data Pipeline shall convert optical light counts to volts using the configured ADC reference voltage :math:`V_{\text{ref}}` (default 3.3 V) and bit resolution :math:`N` (default 12 bits): :math:`V[p] = S_{\text{light}}[p] \cdot (V_{\text{ref}} / (2^N - 1))`.

   **Rationale:** Converting digital counts to physical volts allows radiometric cross-comparison and hardware calibration against oscilloscope probes and analog sensor specifications.

.. _uuid-b3c4d5e6-f7a8-49b0-c1d2-334455667788:

**Requirement:** The Host PC Primary Data Pipeline shall generate normalized live display counts :math:`S_{\text{disp}}[p] \in [0.0, 1.0]` supporting both ``auto_peak`` and ``absolute_saturation`` display modes.

   **Rationale:** Real-time line plotting requires auto-peak scaling to inspect weak absorption or emission features, while absolute saturation mode allows operators to verify whether the sensor is approaching saturation clipping.

.. _uuid-c4d5e6f7-a8b9-40c1-d2e3-445566778899:

**Requirement:** The Host PC Primary Data Pipeline shall compress the 3648 effective detector samples into a fixed 256-element spectrogram row using an 85% RMS and 15% peak blend across contiguous bin segments.

   **Rationale:** Fixed-width 256-bin compression preserves high-frequency spectral emission lines without overwhelming GPU texture buffers during rolling waterfall updates.

.. _uuid-d5e6f7a8-b9c0-41d2-e3f4-556677889900:

**Requirement:** The Host PC Primary Data Pipeline shall assemble an immutable ``SpectrumFrame`` containing raw ADC counts, normalized live counts, the 256-bin spectrogram row, the frame dark baseline, hardware frame counter, and timestamp.

   **Rationale:** Bundling all raw and derived representations into an immutable data container prevents thread race conditions between background acquisition and the GUI rendering loop.

Mathematical Formulation
------------------------

1. **Voltage Conversion:**

   .. math::

      V[p] = S_{\text{light}}[p] \cdot \left(\frac{V_{\text{ref}}}{2^N - 1}\right)

2. **Live Display Normalization:**

   .. math::

      S_{\text{disp}}[p] = \text{clip}\left(\frac{S_{\text{corr}}[p]}{D_{\text{norm}}},\, 0.0,\, 1.0\right)

   where :math:`D_{\text{norm}} = \max(\max(S_{\text{corr}}),\, 10^{-9})` in auto-peak mode, and :math:`D_{\text{norm}} = \max(S_{\text{sat}}[p],\, 10^{-9})` in absolute saturation mode.

3. **256-Bin Spectrogram Compression:**
   For each bin :math:`k \in [0, 255]`:

   .. math::

      \text{RMS}_k = \sqrt{\frac{1}{N_k} \sum_{i \in \text{bin}_k} s_{\text{norm}}[i]^2}, \quad
      \text{Peak}_k = \max_{i \in \text{bin}_k} s_{\text{norm}}[i]

   .. math::

      v_{\text{row}}[k] = \text{clip}\left(0.85 \cdot \text{RMS}_k + 0.15 \cdot \text{Peak}_k,\, 0.0,\, 1.0\right)

Data Structure Specification (``SpectrumFrame``)
------------------------------------------------

.. list-table::
   :header-rows: 1

   * - Field
     - Type
     - Purpose
   * - ``frame_id``
     - ``int``
     - Hardware sequence counter for gap and drop tracking.
   * - ``timestamp``
     - ``datetime``
     - UTC acquisition timestamp.
   * - ``adc_counts``
     - ``list[int]``
     - Preserved raw 16-bit ADC counts (3694 samples).
   * - ``live_display_counts``
     - ``list[float]``
     - Normalized 0-to-1 array for live line plot rendering.
   * - ``spectrogram_row``
     - ``list[float]``
     - 256-element compressed row for waterfall display.
   * - ``dark_reference_count``
     - ``float``
     - Measured baseline :math:`\beta_f` from optical black pixels.
   * - ``volts``
     - ``list[float]`` (lazy)
     - Computed voltages across active samples (populated for export).
   * - ``wavelengths_nm``
     - ``list[float]`` (lazy)
     - Computed wavelengths across active samples (populated for export).

Verification & Testing
----------------------

* **Voltage Scaling Accuracy:** Input 4095 counts with :math:`V_{\text{ref}} = 3.3\,\text{V}, N = 12` and verify that computed voltage equals exactly :math:`3.300\,\text{V} \pm 0.001\,\text{V}`.
* **Spectrogram Row Width:** Verify that every processed frame emits a ``spectrogram_row`` of length exactly 256.
* **Auto-Peak Clamping:** Verify that normalized display values never exceed :math:`1.0` or fall below :math:`0.0`, even in the presence of noise or saturated peaks.
