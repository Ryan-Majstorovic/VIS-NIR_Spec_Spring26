Visualization
=============

The Visualization system renders real-time graphical representations of spectrometer measurement data for the operator. It provides an interactive 2D line spectrum plot with cursor inspection and a rolling 2D waterfall spectrogram, operating at a decoupled 30 FPS display cadence.

.. _uuid-b4c5d6e7-f8a9-40b1-c2d3-445566778801:

Subsystem Role & Architecture
-----------------------------

UUID: :ref:`B4C5D6E7-F8A9-40B1-C2D3-445566778801 <uuid-b4c5d6e7-f8a9-40b1-c2d3-445566778801>`

Visualization decouples real-time user inspection from background data acquisition:
* **Decoupled Cadence:** While the hardware and serial reader stream data at 125 Hz, the graphical interface updates at a stable ~30 FPS (configurable via ``ui.refresh_interval_ms``).
* **Line Spectrum:** Displays the processed 3648-pixel curve with interactive cursor inspection and peak markers.
* **Waterfall Spectrogram:** Displays a continuous rolling time-history heatmap across 256 compressed spectral bins.
* **Configurable Display Ceiling:** Provides adjustable dynamic range scaling so low-amplitude signals (:math:`\le 5\%` of saturation) are vividly visible without per-frame noise flashing.

Inputs and Outputs
------------------

.. list-table::
   :header-rows: 1

   * - Flow
     - Name
     - Structure / Type
     - Description
   * - **Input**
     - Latest Spectrum Frame
     - ``SpectrumFrame``
     - Most recent frame delivered by the decoupled cadence filter.
   * - **Input**
     - Spectrogram History
     - Sequence of 256-float rows
     - History buffer of recent spectrogram rows.
   * - **Input**
     - Display Ceiling (:math:`\alpha_{\text{ceiling}}`)
     - Float :math:`[0.01, 1.00]`
     - Operator-configured dynamic range scaling ceiling.
   * - **Output**
     - Line Plot Canvas
     - Kivy graphics instructions
     - Rendered 2D spectral line with grid lines and cursor readout.
   * - **Output**
     - Spectrogram Texture
     - Kivy 2D Texture
     - Rendered rolling heatmap texture.

Normative Requirements
----------------------

.. _uuid-b4c5d6e7-f8a9-40b1-c2d3-445566778802:

**Requirement:** The Host PC Visualization system shall refresh live spectral plots at a decoupled rendering cadence of approximately 30 FPS (interval :math:`\approx 33.3\,\text{ms}`) while the background stream ingests at 125 Hz.

   **Rationale:** Redrawing 3648 line vertices and rolling textures 125 times per second causes GPU thread starvation and interface lag; throttling display redraws to 30 FPS ensures fluid user interaction while preserving 100% data capture in recording buffers.

.. _uuid-b4c5d6e7-f8a9-40b1-c2d3-445566778803:

**Requirement:** The Host PC Visualization system shall provide an interactive cursor overlay that tracks mouse or touch position, displays the nearest sample index, optical wavelength in nanometers, and calibrated intensity value, and snaps to the active peak.

   **Rationale:** Interactive cursor inspection enables laboratory operators to immediately identify spectral line positions and monitor peak intensity without exporting data to external spreadsheet tools.

.. _uuid-c62d9012-5f89-4490-ab32-aa9922ee3312:

**Requirement:** The Host PC Visualization system shall normalize rolling spectrogram rows using a configurable dynamic range ceiling :math:`\alpha_{\text{ceiling}} \in [0.01, 1.00]` relative to saturation (:math:`s_{\text{norm}}[p] = \text{clip}(S_{\text{proc}}[p] / \max(\alpha_{\text{ceiling}} \cdot S_{\text{sat}}[p],\, 10^{-9}),\, 0.0,\, 1.0)`).

   **Rationale:** When optical signals are weak (such as measurements peaking at :math:`\le 5\%` of saturation), rigid 100% saturation normalization compresses all spectral features into the dark background floor; providing a configurable ceiling expands low-amplitude signals across the full visible colormap while maintaining temporal color stability.

.. _uuid-b4c5d6e7-f8a9-40b1-c2d3-445566778805:

**Requirement:** The Host PC Visualization system shall render the rolling spectrogram using an in-place pre-allocated 2D GPU texture buffer corresponding to the configured time window (default 10.0 seconds).

   **Rationale:** Reusing an existing texture buffer and updating newly arrived rows incrementally eliminates memory reallocation stutter during continuous rendering.

Interactive Controls & Display Modes
------------------------------------

.. _uuid-ab706fb5-82ee-49ce-b695-055a5281ad54:

**Requirement:** The Host PC Visualization system shall provide the Spectrum scaling selector in Display & Layout under Live Graph and apply the selected mode immediately to the processed line spectrum.

**Rationale:** The operator can switch between feature contrast and saturation headroom in the same menu as the graph and data-view controls.

1. **Line Plot Normalization Modes:**
   * **Auto-Peak Mode:** Scales the y-axis dynamically to the peak value of the active frame, maximizing feature contrast.
   * **Absolute Saturation Mode:** Scales the y-axis against the full-scale ADC saturation ceiling, allowing operators to monitor headroom.
2. **Spectrogram Dynamic Range Ceiling:**
   * Configurable slider or setting from 1% to 100% full-scale deflection.
   * Allows high-contrast waterfall tracking for low-reflectance samples and weak light sources.

Verification & Testing
----------------------

* **Render Frame Rate Check:** Verify via ``performance_monitor`` that ``ui.render_fps`` remains within :math:`30.0 \pm 3.0\,\text{FPS}` during continuous 125 Hz stream ingestion.
* **Spectrogram Contrast Check:** Inject a synthetic 5% amplitude Gaussian peak; verify that setting :math:`\alpha_{\text{ceiling}} = 0.05` scales the peak to full colormap intensity (:math:`1.0`).
