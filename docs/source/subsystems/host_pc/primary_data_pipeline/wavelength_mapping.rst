Wavelength Mapping
==================

The Wavelength Mapping stage establishes the mathematical relationship between physical detector pixel indices and optical wavelengths in nanometers. It encompasses runtime polynomial evaluation for active frames and the calibration solver used to fit polynomial coefficients from spectral reference lines.

.. _uuid-a7b8c9d0-e1f2-43a4-b5c6-778899001122:

Subsystem Role & Calibration
----------------------------

UUID: :ref:`A7B8C9D0-E1F2-43A4-B5C6-778899001122 <uuid-a7b8c9d0-e1f2-43a4-b5c6-778899001122>`

Diffraction gratings disperse incident light across the linear CCD array according to the grating equation. Due to geometric angles and Czerny-Turner optical geometry, the dispersion is non-linear across the 3648 effective pixels. A polynomial mapping function :math:`\lambda(p)` relates each pixel index :math:`p` to its center optical wavelength.

Inputs and Outputs
------------------

.. list-table::
   :header-rows: 1

   * - Flow
     - Name
     - Structure / Type
     - Description
   * - **Input**
     - Pixel Indices (:math:`p`)
     - 1D Array of integers
     - Effective pixel sequence :math:`[0, 1, \dots, 3647]`.
   * - **Input**
     - Calibration Coefficients (:math:`c_i`)
     - List of floats
     - Polynomial coefficients :math:`[c_0, c_1, \dots, c_n]`.
   * - **Input (Solver)**
     - Calibration Line Pairs
     - Array of :math:`(p_k, \lambda_k)`
     - Known reference emission line pairs (e.g., Hg-Ar or neon spectral lines).
   * - **Output**
     - Wavelength Array (:math:`\mathbf{\lambda}`)
     - 1D Array of floats
     - Aligned wavelength values in nanometers for each pixel.
   * - **Output (Solver)**
     - Fitted Coefficients
     - List of floats
     - Solved polynomial coefficients stored to configuration.

Normative Requirements
----------------------

.. _uuid-b8c9d0e1-f2a3-44b5-c6d7-889900112233:

**Requirement:** The Host PC Wavelength Mapping system shall calculate the optical wavelength for each pixel index :math:`p` using the active polynomial coefficient vector :math:`\mathbf{c}` (:math:`\lambda(p) = \sum_{i=0}^{n} c_i \cdot p^i = c_0 + c_1 p + c_2 p^2 + \dots + c_n p^n`).

   **Rationale:** Polynomial evaluation provides a fast, continuous, and repeatable mapping from detector array geometry to physical optical wavelength.

.. _uuid-c9d0e1f2-a3b4-45c6-d7e8-990011223344:

**Requirement:** The Host PC Wavelength Mapping system shall provide a least-squares polynomial regression solver that accepts :math:`K \ge n + 1` calibration line pairs :math:`(p_k, \lambda_k)` and determines the optimal coefficient vector :math:`\mathbf{c}` of order :math:`n` (default :math:`n=3`).

   **Rationale:** Spectral calibration requires empirical fitting against known atomic emission lines to compensate for mechanical alignment tolerances, focal distance offsets, and grating angle variations.

.. _uuid-d0e1f2a3-b4c5-46d7-e8f9-001122334455:

**Requirement:** The Host PC Wavelength Mapping system shall accept a fitted wavelength map only when the evaluated wavelengths strictly increase across every adjacent pair of active detector pixels or strictly decrease across every pair.

   **Rationale:** The detector orientation determines the direction of dispersion. A consistent direction preserves a unique wavelength ordering across the active detector.

.. _uuid-e1f2a3b4-c5d6-47e8-f9a0-112233445566:

**Requirement:** The Host PC Wavelength Mapping system shall default to pixel-index domain presentation when no valid reference calibration points or custom coefficients have been saved.

   **Rationale:** Displaying unverified or arbitrary default wavelength numbers misleads the operator; operating in raw pixel mode until calibration is confirmed ensures measurement integrity.

Mathematical Formulation
------------------------

1. **Least-Squares Solver Formulation:**
   Given :math:`K` calibration pairs :math:`(p_k, \lambda_k)`, the Vandermonde design matrix :math:`\mathbf{V}` is constructed:

   .. math::

      \mathbf{V} = \begin{bmatrix}
         1 & p_1 & p_1^2 & \dots & p_1^n \\
         1 & p_2 & p_2^2 & \dots & p_2^n \\
         \vdots & \vdots & \vdots & \ddots & \vdots \\
         1 & p_K & p_K^2 & \dots & p_K^n
      \end{bmatrix}, \quad
      \mathbf{\Lambda} = \begin{bmatrix} \lambda_1 \\ \lambda_2 \\ \vdots \\ \lambda_K \end{bmatrix}

   The coefficient vector :math:`\mathbf{c} = [c_0, c_1, \dots, c_n]^T` is solved via:

   .. math::

      \mathbf{c} = (\mathbf{V}^T \mathbf{V})^{-1} \mathbf{V}^T \mathbf{\Lambda}

2. **Residual Qualification:**
   The root-mean-square residual error of the fit is computed:

   .. math::

      \text{RMSE} = \sqrt{\frac{1}{K} \sum_{k=1}^{K} \left(\lambda_k - \lambda(p_k)\right)^2}

Diagnostics & Error Qualification
---------------------------------

* **Insufficient Points:** If the user attempts to fit an :math:`n`-th order polynomial with fewer than :math:`n+1` reference points, the fit is rejected and an error is returned.
* **Wavelength direction:** Verify that the solver accepts both increasing and decreasing maps and rejects a map with equal adjacent wavelengths or a change of direction within the active detector.

Verification & Testing
----------------------

* **Linear Mapping Check:** Verify that coefficients :math:`[400.0, 0.16447, 0.0, 0.0]` produce :math:`\lambda(0) = 400.0\,\text{nm}` and :math:`\lambda(3647) \approx 1000.0\,\text{nm}`.
* **Polynomial Recovery Check:** Supply 5 synthetic polynomial reference points generated from known coefficients and verify that the solver reconstructs the coefficients with zero residual error.
