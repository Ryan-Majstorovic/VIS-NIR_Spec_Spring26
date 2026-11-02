Spectral Corrections
====================

The Spectral Corrections stage applies multiplicative correction factors to light counts to compensate for non-uniform detector response (flat-field correction) and wavelength-dependent instrument throughput (quantum efficiency and optical response).

.. _uuid-c3d4e5f6-a7b8-49c0-d1e2-334455667788:

Subsystem Role & Scope
----------------------

UUID: :ref:`C3D4E5F6-A7B8-49C0-D1E2-334455667788 <uuid-c3d4e5f6-a7b8-49c0-d1e2-334455667788>`

After additive electronic and thermal baselines are removed, true photon flux estimation requires multiplicative scaling. This stage supports:
* **Flat-Field Intensity Correction:** Adjusts for pixel-to-pixel gain variations and grating illumination gradients.
* **Quantum Efficiency (QE) & System Response:** Corrects for detector silicon absorption efficiency and optical component transmission curves across the VIS-NIR wavelength band.

Inputs and Outputs
------------------

.. list-table::
   :header-rows: 1

   * - Flow
     - Name
     - Structure / Type
     - Description
   * - **Input**
     - Light Counts (:math:`S_{\text{light}}`)
     - 1D Array (float)
     - Non-negative optical counts from bias and dark correction.
   * - **Input**
     - Wavelengths (:math:`\mathbf{\lambda}`)
     - 1D Array (float)
     - Sample-aligned wavelength values in nanometers.
   * - **Input**
     - Intensity Factors (:math:`I_{\text{corr}}`)
     - 1D Array (optional)
     - Pixel-indexed multiplicative correction factors.
   * - **Input**
     - QE Reference Points
     - Array of :math:`(\lambda_k, R_k)`
     - Wavelength-to-relative-response reference curve.
   * - **Output**
     - Corrected Intensity (:math:`S_{\text{corr}}`)
     - 1D Array (float)
     - Multiplicatively corrected optical intensity values.

Normative Requirements
----------------------

.. _uuid-d4e5f6a7-b8c9-40d1-e2f3-445566778899:

**Requirement:** The Host PC Spectral Corrections system shall multiply light counts by the pixel-aligned flat-field intensity vector :math:`I_{\text{corr}}[p]` when intensity correction is enabled (:math:`S_{\text{int\_corr}}[p] = S_{\text{light}}[p] \cdot I_{\text{corr}}[p]`).

   **Rationale:** Pixel-to-pixel gain variations in the linear CCD array cause systematic sensitivity discrepancies that must be equalized using flat-field calibration data.

.. _uuid-e5f6a7b8-c9d0-41e2-f3a4-556677889900:

**Requirement:** The Host PC Spectral Corrections system shall interpolate the relative quantum efficiency curve across active sample wavelengths and scale by the normalized response curve :math:`R_{\text{norm}}[p]` when QE correction is enabled.

   **Rationale:** Silicon detectors exhibit pronounced wavelength-dependent sensitivity variations, peaking in the 500–600 nm range and rolling off toward 1000 nm; dividing by normalized response reconstructs true relative spectral irradiance.

.. _uuid-f6a7b8c9-d0e1-42f3-a4b5-667788990011:

**Requirement:** The Host PC Spectral Corrections system shall enforce a minimum response denominator bound of :math:`10^{-4}` during spectral response division.

   **Rationale:** Bounding the minimum denominator prevents division-by-zero errors and avoids extreme noise amplification in wavelength regions where detector sensitivity approaches zero.

Mathematical Formulation
------------------------

1. **Composite Correction Factor:**
   When both intensity and QE response corrections are enabled:

   .. math::

      R_{\text{norm}}[p] = \frac{R(\lambda[p])}{R(\lambda_{\text{ref}})}

   .. math::

      C_{\text{mult}}[p] = I_{\text{corr}}[p] \cdot \left(\frac{1}{\max\left(R_{\text{norm}}[p],\, 10^{-4}\right)}\right)

2. **Final Corrected Counts:**

   .. math::

      S_{\text{corr}}[p] = \max\left(S_{\text{light}}[p] \cdot C_{\text{mult}}[p],\, 0.0\right)

Diagnostics & Error Handling
----------------------------

* **Curve Dimension Mismatch:** If flat-field intensity factors do not match the active sample count, the correction is bypassed and a configuration alert is displayed.
* **Out-of-Range Wavelength Extrapolation:** If sample wavelengths extend outside the calibrated QE reference curve bounds, values are clamped to the nearest edge reference point to prevent wild polynomial divergence.

Verification & Testing
----------------------

* **Unity Flat-Field Check:** Verify that configuring an array of :math:`1.0` produces identical input and output counts.
* **Response Scaling Check:** Verify that applying a :math:`0.5` response factor at a given wavelength exactly doubles the output light intensity for that pixel.
