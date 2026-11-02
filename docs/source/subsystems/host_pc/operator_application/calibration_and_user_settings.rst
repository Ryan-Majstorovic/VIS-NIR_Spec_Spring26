Calibration and User Settings
=============================

The Calibration and User Settings system manages operator configuration, interactive calibration capture workflows, signal processing toggles, and persistent parameter storage for the spectrometer software.

.. _uuid-c5d6e7f8-a9b0-41c2-d3e4-556677889901:

Subsystem Scope & Management
----------------------------

UUID: :ref:`C5D6E7F8-A9B0-41C2-D3E4-556677889901 <uuid-c5d6e7f8-a9b0-41c2-d3e4-556677889901>`

This subsystem provides the user controls and storage mechanisms needed to tune and maintain instrument accuracy:
* **Live Pipeline Toggles:** Real-time enabling and disabling of dark subtraction, intensity flattening, and quantum efficiency corrections.
* **Interactive Bias Capture:** Automated multi-frame averaging under covered aperture conditions to generate master bias vectors.
* **Wavelength Fitting Interface:** Interactive editing of reference emission line pairs and execution of polynomial regression fits.
* **Configuration Persistence:** Bounded JSON serialization for user hardware preferences (``user.json``) and calibration arrays (``calibration.json``).

Inputs and Outputs
------------------

.. list-table::
   :header-rows: 1

   * - Flow
     - Name
     - Structure / Type
     - Description
   * - **Input**
     - User Selections
     - GUI Controls
     - Toggles, coefficient inputs, COM port choices, reference points.
   * - **Input**
     - Covered Raw Frames
     - Stream of ``SpectrumFrame``
     - Incoming dark frames during bias capture routine.
   * - **Output**
     - Updated Configuration
     - ``UserConfig`` / ``CalibrationConfig``
     - Validated Pydantic models dispatched to runtime services.
   * - **Output**
     - Stored JSON Files
     - File System (``.json``)
     - Serialized configuration files on disk.

Normative Requirements
----------------------

.. _uuid-c5d6e7f8-a9b0-41c2-d3e4-556677889902:

**Requirement:** The Host PC Calibration and User Settings system shall provide an automated master bias capture routine that averages a configured number of consecutive covered frames :math:`N` (default 8) to compute the master bias vector :math:`B_p` (:math:`B_p[p] = \frac{1}{N} \sum_{i=1}^{N} S_{\text{raw}, i}[p]`).

   **Rationale:** Automated averaging reduces high-frequency temporal noise on dark reference pixels and establishes a repeatable fixed pattern offset baseline.

.. _uuid-c5d6e7f8-a9b0-41c2-d3e4-556677889903:

**Requirement:** The Host PC Calibration and User Settings system shall immediately rebuild the live display spectrum using the updated calibration parameters whenever an algorithm toggle or calibration array is modified.

   **Rationale:** Immediate live frame rebuilding provides instant visual confirmation of calibration adjustments without requiring the operator to restart streaming.

.. _uuid-c5d6e7f8-a9b0-41c2-d3e4-556677889904:

**Requirement:** The Host PC Calibration and User Settings system shall persist user hardware settings to ``configs/user.json`` and calibration arrays to ``configs/calibration.json``, falling back to default configuration files if user files are absent.

   **Rationale:** Separating hardware user preferences from scientific calibration parameters allows operators to reset COM port preferences without invalidating optical calibration data.

Calibration Workflows
---------------------

1. **Master Bias Capture:**
   * Operator covers spectrometer entrance slit.
   * Clicks "Capture Bias" in the UI.
   * System collects the next 8 frames, verifies matching sample dimensions, computes the per-pixel mean, and stores the resulting vector in ``CalibrationConfig``.
2. **Wavelength Calibration Setup:**
   * Operator inputs known emission line pairs (Pixel Index, Wavelength in nm) from a spectral calibration lamp.
   * Operator clicks "Fit Wavelength Map".
   * System solves the polynomial coefficients, checks monotonicity (:math:`\frac{d\lambda}{dp} > 0`), and saves the coefficients.

Verification & Testing
----------------------

* **Bias Averaging Verification:** Feed 8 frames of identical count values ``[100, 100, ...]``; verify that the stored bias vector equals exactly 100 counts across all pixels.
* **Fallback Config Test:** Delete ``user.json`` and ``calibration.json``; verify that the application launches cleanly using default configuration values without crashing.
