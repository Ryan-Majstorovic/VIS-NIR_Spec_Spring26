Bias and Dark Correction
========================

The Bias and Dark Correction stage removes systematic electronic offset (master bias) and dynamic thermal baseline drift (frame dark reference) from raw detector samples, and inverts the negative-going sensor signal to produce positive optical light counts.

.. _uuid-ca52e4d1-8178-433b-8ea9-42b6a22f3d10:

Subsystem Role & Physics
------------------------

UUID: :ref:`CA52E4D1-8178-433B-8EA9-42B6A22F3D10 <uuid-ca52e4d1-8178-433b-8ea9-42b6a22f3d10>`

The Toshiba TCD1304 linear CCD operates in an **inverted readout mode**:
* In darkness, the sensor output voltage is near its high baseline (high ADC counts).
* Under optical illumination, accumulated photoelectrons discharge the sense nodes, driving the output voltage downward toward zero (low ADC counts).

To restore physical proportionality where higher optical intensity yields higher numerical values, the processing pipeline measures downward deflection from the instantaneous dark baseline.

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
     - 1D Array (float / int)
     - Preserved raw 16-bit ADC counts from frame ingress.
   * - **Input**
     - Master Bias Vector (:math:`B_p`)
     - 1D Array (optional)
     - Stored fixed pattern offset vector captured under covered conditions.
   * - **Input**
     - Dark Offset Vector
     - 1D Array (optional)
     - Per-pixel additive dark offsets.
   * - **Output**
     - Corrected Light Counts
     - 1D Array (float)
     - Non-negative optical counts directly proportional to incident photon flux.
   * - **Output**
     - Frame Dark Level (:math:`\beta_f`)
     - Float scalar
     - Instantaneous median dark baseline measured from optical black pixels.

Normative Requirements
----------------------

.. _uuid-f09b1834-8f12-4217-91ac-7319ad0419e5:

**Requirement:** The Host PC Bias and Dark Correction system shall subtract the stored master bias vector :math:`B_p` from raw ADC counts on every accepted frame when master bias correction is configured (:math:`S_{\text{bias\_corr}}[p] = S_{\text{raw}}[p] - B_p[p]`).

   **Rationale:** Master bias subtraction removes fixed pattern electronic offsets introduced by the analog readout circuitry and ADC sample-and-hold stages.

.. _uuid-a1b2c3d4-e5f6-47a8-b9c0-112233445566:

**Requirement:** The Host PC Bias and Dark Correction system shall calculate the frame dark baseline :math:`\beta_f` as the median value of shielded optical black pixel indices 16 through 28 (:math:`\beta_f = \text{median}(S_{\text{bias\_corr}}[16:28])`).

   **Rationale:** The TCD1304 contains 16 optically shielded pixels that track thermal baseline drift and temperature variation on every frame without requiring a mechanical optical shutter.

.. _uuid-b2c3d4e5-f6a7-48b9-c0d1-223344556677:

**Requirement:** The Host PC Bias and Dark Correction system shall calculate positive light counts by subtracting the dark-corrected samples from the frame dark baseline (:math:`S_{\text{light}}[p] = \max(\beta_f - S_{\text{bias\_corr}}[p] - S_{\text{dark\_offset}}[p],\, 0.0)`).

   **Rationale:** Computing downward deflection from the dark baseline inverts the negative-going CCD voltage response into a physically meaningful positive optical signal and prevents negative intensity values.

Mathematical Formulation
------------------------

1. **Master Bias Capture Routine:**
   Captured by averaging :math:`N` frames (default 8) while the spectrometer entrance aperture is completely covered:

   .. math::

      B_p[p] = \frac{1}{N} \sum_{i=1}^{N} S_{\text{raw}, i}[p]

2. **Frame-Wise Light Calculation:**
   For each sample index :math:`p`:

   .. math::

      S_{\text{light}}[p] = \begin{cases}
         \max\left(\beta_f - (S_{\text{raw}}[p] - B_p[p]) - S_{\text{offset}}[p],\, 0.0\right) & \text{if dark subtraction enabled} \\
         \max\left(S_{\text{raw}}[p] - B_p[p],\, 0.0\right) & \text{if dark subtraction disabled}
      \end{cases}

Diagnostics & Error Qualification
---------------------------------

* **Abnormal Dark Baseline:** If :math:`\beta_f` deviates beyond acceptable baseline limits (e.g., drops below 100 counts or exceeds 4050 counts on a 12-bit scale), a baseline fault diagnostic is recorded.
* **Master Bias Dimension Check:** If the loaded master bias vector length does not match the incoming frame sample count, master bias subtraction is bypassed and a configuration mismatch error is logged.

Verification & Testing
----------------------

* **Inversion Verification:** Verify that decreasing raw ADC counts (simulating higher optical illumination) produces monotonically increasing :math:`S_{\text{light}}` counts.
* **Zero Light Floor:** Verify that raw counts equal to or exceeding :math:`\beta_f` produce exactly :math:`0.0` light counts.
* **Baseline Tracking:** Apply synthetic baseline shifts of :math:`+50` and :math:`-50` counts to raw data and verify that computed :math:`S_{\text{light}}` remains constant.
