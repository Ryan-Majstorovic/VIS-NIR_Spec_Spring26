Calculations
============

.. _uuid-c9755e34-9135-4415-b7c0-c39e287a70d8:

Calculation C1 - Observed Complete-Frame Rate
---------------------------------------------

UUID: :ref:`C9755E34-9135-4415-B7C0-C39E287A70D8 <uuid-c9755e34-9135-4415-b7c0-c39e287a70d8>`

**Summary:** Calculate the average complete-frame rate over a documented
observation interval.

**Variables:** ``N_complete`` is the number of complete frames and
``delta_t`` is elapsed time.

**Calculation:** ``R_frame = N_complete / delta_t``.

**Equation Reasoning:** Counting only complete frames keeps interface
qualification separate from partial receive activity.

**Implementation Note:** Future evidence tooling and timestamp source are
``Not In Docs``.

**Acceptance Profile:** Embedded minimum transfer acceptance is
``R_frame >= 10 frames/s`` at minimum integration time, counting only complete
frames that each contain 3648 effective detector samples. This profile is
distinct from the above-100-fps system design target and from display updates.

**Open Requirement:** Observation duration, warm-up interval, aggregation
method, display update profile, and conditions for the above-100-fps system
target are ``Not In Docs``.

.. _uuid-22f91c7c-d310-486a-ac24-bdc8be1b11ac:

Calculation C2 - Wavelength Error
---------------------------------

UUID: :ref:`22F91C7C-D310-486A-AC24-BDC8BE1B11AC <uuid-22f91c7c-d310-486a-ac24-bdc8be1b11ac>`

**Summary:** Calculate signed wavelength error for each suitable reference.

**Variables:** ``lambda_observed`` is the reported peak wavelength and
``lambda_reference`` is the reference value under recorded conditions.

**Calculation:** ``e_lambda = lambda_observed - lambda_reference``.

**Equation Reasoning:** Signed error retains both magnitude and direction of
the mapping difference.

**Implementation Note:** Peak extraction and reference matching are future
verification activities.

**Rationale:** Wavelength accuracy is a required characterization metric.

**Open Requirement:** Peak window, interpolation, reference matching,
aggregation, and tolerance are ``Not In Docs``.

.. _uuid-60b5dbf0-f84f-4fef-8768-ca31ad5d905b:

Calculation C3 - Full Width At Half Maximum
-------------------------------------------

UUID: :ref:`60B5DBF0-F84F-4FEF-8768-CA31AD5D905B <uuid-60b5dbf0-f84f-4fef-8768-ca31ad5d905b>`

**Summary:** Calculate the wavelength separation between the two half-maximum
crossings of a suitable narrow spectral feature.

**Variables:** ``lambda_left`` and ``lambda_right`` are the wavelength
locations of the left and right half-maximum crossings.

**Calculation:** ``FWHM = lambda_right - lambda_left``.

**Equation Reasoning:** The crossing separation expresses spectral width in
wavelength units for comparison with the approximately 5 nm target.

**Implementation Note:** Crossing extraction is not assigned to an
implementation location in this first run.

**Rationale:** FWHM is the documented spectral-resolution measure.

**Open Requirement:** Baseline removal, peak selection, interpolation, source
linewidth treatment, and aggregation are ``Not In Docs``.

.. _uuid-cc509fbf-a260-4193-a556-5a97d39d7953:

Calculation C4 - Signal-To-Noise Ratio
--------------------------------------

UUID: :ref:`CC509FBF-A260-4193-A556-5A97D39D7953 <uuid-cc509fbf-a260-4193-a556-5a97d39d7953>`

**Summary:** Express a stable signal level relative to the selected noise
statistic.

**Variables:** ``mu_signal`` is the mean selected signal and
``sigma_noise`` is the standard deviation of the selected noise samples.

**Calculation:** ``SNR = mu_signal / sigma_noise`` when
``sigma_noise`` is nonzero.

**Equation Reasoning:** The ratio provides a repeatable comparison only when
the signal region, noise population, and preprocessing are fixed.

**Implementation Note:** Future analysis tooling and zero-noise handling are
``Not In Docs``.

**Rationale:** SNR is a required characterization metric, especially where
detector response is lower.

**Open Requirement:** Wavelength bands, sample population, dark treatment,
statistic, units, and threshold are ``Not In Docs``.

.. _uuid-501567a5-fa56-4264-91ce-91edb0486cb1:

Calculation C5 - Linearity Residual
-----------------------------------

UUID: :ref:`501567A5-FA56-4264-91CE-91EDB0486CB1 <uuid-501567a5-fa56-4264-91ce-91edb0486cb1>`

**Summary:** Calculate the deviation of each observation from an approved
linearity fit.

**Variables:** ``y_i`` is the observed response and ``y_fit_i`` is the
response predicted by the approved fit at the same controlled input.

**Calculation:** ``r_i = y_i - y_fit_i``.

**Equation Reasoning:** Residuals expose both the magnitude and pattern of
departure from the selected model.

**Implementation Note:** The fit procedure and reporting tool are future work.

**Rationale:** Linearity shall be characterized versus controlled input at
fixed integration time.

**Open Requirement:** Input levels, fit model, weighting, residual aggregation,
and threshold are ``Not In Docs``.

.. _uuid-ed22b205-1bb5-4ea3-9ac2-05890bb529b1:

Calculation C6 - Repeatability Statistic
----------------------------------------

UUID: :ref:`ED22B205-1BB5-4EA3-9AC2-05890BB529B1 <uuid-ed22b205-1bb5-4ea3-9ac2-05890bb529b1>`

**Summary:** Calculate sample standard deviation for repeated observations when
that statistic is selected by the approved method.

**Variables:** ``x_i`` are repeated values, ``x_bar`` is their mean,
and ``n`` is the number of observations.

**Calculation:** ``s = sqrt(sum((x_i - x_bar)^2) / (n - 1))`` for
``n > 1``.

**Equation Reasoning:** Sample standard deviation measures variation over a
defined repeat sequence without claiming a tolerance.

**Implementation Note:** Future analysis location is not assigned.

**Rationale:** Repeatability is required over acquisitions made without
realignment.

**Open Requirement:** Selected metric, sequence length, duration, environmental
profile, aggregation, and threshold are ``Not In Docs``.

.. _uuid-22971c51-a176-427e-9509-c552d1b1c6c3:

Calculation C7 - Dark Or Baseline Improvement
---------------------------------------------

UUID: :ref:`22971C51-A176-427E-9509-C552D1B1C6C3 <uuid-22971c51-a176-427e-9509-c552d1b1c6c3>`

**Summary:** Compare a documented baseline or noise statistic before and after
the configured bias/dark operation.

**Variables:** ``m_before`` and ``m_after`` are the same selected
statistic evaluated under matched conditions.

**Calculation:** Candidate reports are ``delta_m = m_before - m_after`` and,
when ``m_after`` is nonzero, ``ratio_m = m_before / m_after``.

**Equation Reasoning:** Reporting paired difference and ratio preserves useful
comparison options until the project selects one normative measure.

**Implementation Note:** These candidate reports are non-normative.

**Rationale:** Bias and dark correction require a controlled comparative
evaluation.

**Open Requirement:** Selected statistic, detector region, conditions,
aggregation, normative measure, and threshold are ``Not In Docs``.

.. _trace-cf2f2048:
.. _uuid-f767c5db-2f93-4e8d-97e3-eeef9f1bc530:

Calculation C8 - Uncertainty Reporting
--------------------------------------

UUID: :ref:`F767C5DB-2F93-4E8D-97E3-EEEF9F1BC530 <uuid-f767c5db-2f93-4e8d-97e3-eeef9f1bc530>`

**Local Traceability ID:** :ref:`CF2F2048 <trace-cf2f2048>`

**Summary:** Report measurement conditions, identified uncertainty
contributions, and the selected combined or expanded uncertainty.

**Variables:** ``u_i`` are standard uncertainty contributions and
``u_c`` is combined standard uncertainty.

**Calculation:** When contributions are independent and expressed as standard
uncertainties, ``u_c = sqrt(sum(u_i^2))``.

**Equation Reasoning:** Root-sum-square combination is conditional on the
independence assumption; correlated terms require a documented covariance
treatment.

**Implementation Note:** No uncertainty-analysis implementation or evidence
artifact is assigned in this first run.

**Rationale:** Reference comparisons and characterization metrics are not
interpretable without conditions and uncertainty context.

**Open Requirement:** Uncertainty budget, probability model, correlations,
coverage factor, confidence statement, significant figures, and reporting
format are ``Not In Docs``.
