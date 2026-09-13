Testing
=======

.. _uuid-71c7dd62-9ea2-4bf0-9aae-c1470d75d33e:

Master Requirement-To-Test Matrix
---------------------------------

UUID: :ref:`71C7DD62-9EA2-4BF0-9AAE-C1470D75D33E <uuid-71c7dd62-9ea2-4bf0-9aae-c1470d75d33e>`

.. list-table::
   :header-rows: 1

   * - ID
     - Requirement
     - Planned Method
     - Criterion State
     - Local Traceability
     - UUID
   * - TV-01
     - 400-1000 nm usable coverage
     - Known references near both ends of the range
     - Documented target; source set and edge rule ``Not In Docs``
     - :ref:`CD6CB2E1 <trace-cd6cb2e1>`
     - :ref:`A51146EA-4B13-411A-9F04-8467E0F9B8FE <uuid-a51146ea-4b13-411a-9f04-8467e0f9b8fe>`
   * - TV-02
     - 3648 effective detector pixels
     - Frame-geometry and interface check
     - Documented effective count; total transported count ``Not In Docs``
     - :ref:`3B3A1204 <trace-3b3a1204>`
     - :ref:`BBA02827-681E-4BB2-97D8-81966C452482 <uuid-bba02827-681e-4bb2-97d8-81966c452482>`
   * - TV-03
     - Approximately 5 nm FWHM
     - Narrow-reference-source half-maximum width
     - Documented target; source and interpolation ``Not In Docs``
     - :ref:`B2F02404 <trace-b2f02404>`
     - :ref:`ED1C5555-98E0-46D6-B1A1-9404C1D59B59 <uuid-ed1c5555-98e0-46d6-b1a1-9404c1d59b59>`
   * - TV-04
     - Embedded minimum transfer acceptance and system acquisition target
     - Complete-frame count over elapsed time
     - At least 10 complete 3648-effective-sample frames/s at minimum integration
       time; observation duration, aggregation, display rate, and above-100-fps
       target conditions ``Not In Docs``
     - :ref:`B8214C8F <trace-b8214c8f>`
     - :ref:`25F5D9F4-F1EC-4AE7-BCB5-05F86670C539 <uuid-25f5d9f4-f1ec-4ae7-bcb5-05f86670c539>`
   * - TV-05
     - Complete USB frames with IDs and flags
     - Integration-contract conformance check
     - Interface criterion owned by Integration
     - :ref:`3B3A1204 <trace-3b3a1204>`
     - :ref:`90ED79A6-3162-4E1D-8167-1CF18B9140CD <uuid-90ed79a6-3162-4e1d-8167-1cf18b9140cd>`
   * - TV-06
     - Bias and dark correction
     - Blocked-input and stored-reference comparison
     - Improvement statistic and conditions ``Not In Docs``
     - :ref:`E277595D <trace-e277595d>`
     - :ref:`A8AA2658-18DB-4EC7-AA5E-99BF01B59BDE <uuid-a8aa2658-18db-4ec7-aa5e-99bf01b59bde>`
   * - TV-07
     - Pixel-to-wavelength mapping
     - Known-reference fit and residual evaluation
     - Fit form and residual threshold ``Not In Docs``
     - :ref:`E277595D <trace-e277595d>`
     - :ref:`34B2BE00-016D-47CB-9DD7-D01C3249248A <uuid-34b2be00-016d-47cb-9dd7-d01c3249248a>`
   * - TV-08
     - Flat-field, intensity, and response correction
     - Controlled reference-source comparison
     - Absolute/relative scope and tolerance ``Not In Docs``
     - :ref:`E277595D <trace-e277595d>`
     - :ref:`0A2465D5-396C-47B9-9880-DD65C5ACF107 <uuid-0a2465d5-396c-47b9-9880-dd65c5acf107>`
   * - TV-09
     - Required CSV products
     - Schema and row-correspondence inspection
     - Five products documented
     - :ref:`1680B586 <trace-1680b586>`
     - :ref:`F80249E3-1986-41E9-BB19-D9FFC10DAC0A <uuid-f80249e3-1986-41e9-bb19-d9ffc10dac0a>`
   * - TV-10
     - Wavelength accuracy
     - Reference-peak error calculation
     - Tolerance ``Not In Docs``
     - :ref:`3C903FDA <trace-3c903fda>`
     - :ref:`4376DD47-FE09-4EFC-A619-D08350608B7E <uuid-4376dd47-fe09-4efc-a619-d08350608b7e>`
   * - TV-11
     - SNR
     - Stable-source and dark/noise acquisitions
     - Bands, statistic, and threshold ``Not In Docs``
     - :ref:`F39143FD <trace-f39143fd>`
     - :ref:`1ED93409-3D7A-4E3D-91C0-425A9325C998 <uuid-1ed93409-3d7a-4e3d-91c0-425a9325c998>`
   * - TV-12
     - Linearity
     - Controlled input variation at fixed integration time
     - Fit model, levels, and threshold ``Not In Docs``
     - :ref:`5546B204 <trace-5546b204>`
     - :ref:`A43FC1E7-6196-4EEC-A8DE-664E022AB9D7 <uuid-a43fc1e7-6196-4eec-a8de-664e022ab9d7>`
   * - TV-13
     - Repeatability
     - Repeated acquisitions without realignment
     - Statistic, duration, and threshold ``Not In Docs``
     - :ref:`3A725623 <trace-3a725623>`
     - :ref:`57E2E443-83A8-4C39-BDE8-1724593A9344 <uuid-57e2e443-83a8-4c39-bde8-1724593a9344>`
   * - TV-14
     - Stray light and second-order behavior
     - Controlled filtered, unfiltered, or blocked-band comparison
     - Method and threshold ``Not In Docs``
     - :ref:`3E2147CE <trace-3e2147ce>`
     - :ref:`1D6E90B9-9949-4F98-8683-3EA5B2BF2A49 <uuid-1d6e90b9-9949-4f98-8683-3ea5b2bf2a49>`
   * - TV-15
     - Reference-instrument comparison
     - Same-source comparison under recorded conditions
     - Reference suitability and tolerance ``Not In Docs``
     - :ref:`2E04E226 <trace-2e04e226>`
     - :ref:`E7FCAB5B-6D00-4801-9058-42FCE17F4714 <uuid-e7fcab5b-6d00-4801-9058-42fce17f4714>`
   * - TV-16
     - Routine user workflow
     - Client demonstration without source-code or hardware reconfiguration
     - Step-level outcomes documented; overall criterion ``Not In Docs``
     - :ref:`2ED19D37 <trace-2ed19d37>`
     - :ref:`2CF48D1E-090E-4E45-A1AD-5216F93CAB11 <uuid-2cf48d1e-090e-4e45-a1ad-5216f93cab11>`

.. _trace-cd6cb2e1:
.. _uuid-a51146ea-4b13-411a-9f04-8467e0f9b8fe:

Test TV-01 - Wavelength Coverage
--------------------------------

UUID: :ref:`A51146EA-4B13-411A-9F04-8467E0F9B8FE <uuid-a51146ea-4b13-411a-9f04-8467e0f9b8fe>`

**Local Traceability ID:** :ref:`CD6CB2E1 <trace-cd6cb2e1>`

**Status:** Planned. **Method:** Observe suitable known references near the
short- and long-wavelength boundaries. **Open Requirement:** Source set and
usable-edge decision rule are ``Not In Docs``.

.. _trace-3b3a1204:
.. _uuid-bba02827-681e-4bb2-97d8-81966c452482:

Test TV-02 - Effective Detector Geometry
----------------------------------------

UUID: :ref:`BBA02827-681E-4BB2-97D8-81966C452482 <uuid-bba02827-681e-4bb2-97d8-81966c452482>`

**Local Traceability ID:** :ref:`3B3A1204 <trace-3b3a1204>`

**Status:** Planned. **Method:** Confirm 3648 effective detector positions
through the approved Integration contract. Total transported samples are
``Not In Docs``.

.. _trace-b2f02404:
.. _uuid-ed1c5555-98e0-46d6-b1a1-9404c1d59b59:

Test TV-03 - Spectral Resolution
--------------------------------

UUID: :ref:`ED1C5555-98E0-46D6-B1A1-9404C1D59B59 <uuid-ed1c5555-98e0-46d6-b1a1-9404c1d59b59>`

**Local Traceability ID:** :ref:`B2F02404 <trace-b2f02404>`

**Status:** Planned. **Method:** Measure FWHM of suitable narrow references at
multiple wavelengths and compare with the approximately 5 nm target.

.. _trace-b8214c8f:
.. _uuid-25f5d9f4-f1ec-4ae7-bcb5-05f86670c539:

Test TV-04 - Acquisition Rate
-----------------------------

UUID: :ref:`25F5D9F4-F1EC-4AE7-BCB5-05F86670C539 <uuid-25f5d9f4-f1ec-4ae7-bcb5-05f86670c539>`

**Local Traceability ID:** :ref:`B8214C8F <trace-b8214c8f>`

**Status:** Planned. **Method:** Count complete frames over a documented elapsed
interval. Keep transport and display rates separate. **Criterion:** Embedded
minimum transfer acceptance is at least 10 complete frames per second, each
containing 3648 effective detector samples, at minimum integration time.
**Open Requirements:** Observation duration, aggregation, display update rate,
and the conditions for the above-100-fps system target are ``Not In Docs``.

.. _uuid-90ed79a6-3162-4e1d-8167-1cf18b9140cd:

Test TV-05 - USB Frame Integrity
--------------------------------

UUID: :ref:`90ED79A6-3162-4E1D-8167-1CF18B9140CD <uuid-90ed79a6-3162-4e1d-8167-1cf18b9140cd>`

**Status:** Planned. **Method:** Apply the approved Integration contract to
frame completeness, identity, and status fields.

.. _trace-e277595d:
.. _uuid-a8aa2658-18db-4ec7-aa5e-99bf01b59bde:

Test TV-06 - Bias And Dark Correction
-------------------------------------

UUID: :ref:`A8AA2658-18DB-4EC7-AA5E-99BF01B59BDE <uuid-a8aa2658-18db-4ec7-aa5e-99bf01b59bde>`

**Local Traceability ID:** :ref:`E277595D <trace-e277595d>`

**Status:** Planned. **Method:** Compare blocked-input observations before and
after configured bias and dark operations over documented conditions.

.. _uuid-34b2be00-016d-47cb-9dd7-d01c3249248a:

Test TV-07 - Wavelength Map
---------------------------

UUID: :ref:`34B2BE00-016D-47CB-9DD7-D01C3249248A <uuid-34b2be00-016d-47cb-9dd7-d01c3249248a>`

**Status:** Planned. **Method:** Fit or evaluate the approved map against known
reference wavelengths and retain residuals.

.. _uuid-0a2465d5-396c-47b9-9880-dd65c5acf107:

Test TV-08 - Spectral Corrections
---------------------------------

UUID: :ref:`0A2465D5-396C-47B9-9880-DD65C5ACF107 <uuid-0a2465d5-396c-47b9-9880-dd65c5acf107>`

**Status:** Planned. **Method:** Compare configured correction outputs with
controlled reference-source observations. Mathematical convention is
``Not In Docs``.

.. _trace-1680b586:
.. _uuid-f80249e3-1986-41e9-bb19-d9ffc10dac0a:

Test TV-09 - CSV Products
-------------------------

UUID: :ref:`F80249E3-1986-41E9-BB19-D9FFC10DAC0A <uuid-f80249e3-1986-41e9-bb19-d9ffc10dac0a>`

**Local Traceability ID:** :ref:`1680B586 <trace-1680b586>`

**Status:** Planned. **Method:** Confirm row correspondence for raw ADC counts,
processed counts, wavelength, volts, and processed intensity.

.. _trace-3c903fda:
.. _uuid-4376dd47-fe09-4efc-a619-d08350608b7e:

Test TV-10 - Wavelength Accuracy
--------------------------------

UUID: :ref:`4376DD47-FE09-4EFC-A619-D08350608B7E <uuid-4376dd47-fe09-4efc-a619-d08350608b7e>`

**Local Traceability ID:** :ref:`3C903FDA <trace-3c903fda>`

**Status:** Planned. **Method:** Calculate error between observed and reference
peak wavelengths. The tolerance is ``Not In Docs``.

.. _trace-f39143fd:
.. _uuid-1ed93409-3d7a-4e3d-91c0-425a9325c998:

Test TV-11 - Signal-To-Noise Ratio
----------------------------------

UUID: :ref:`1ED93409-3D7A-4E3D-91C0-425A9325C998 <uuid-1ed93409-3d7a-4e3d-91c0-425a9325c998>`

**Local Traceability ID:** :ref:`F39143FD <trace-f39143fd>`

**Status:** Planned. **Method:** Use repeated stable-source and dark/noise
observations. Wavelength bands and statistic are ``Not In Docs``.

.. _trace-5546b204:
.. _uuid-a43fc1e7-6196-4eec-a8de-664e022ab9d7:

Test TV-12 - Linearity
----------------------

UUID: :ref:`A43FC1E7-6196-4EEC-A8DE-664E022AB9D7 <uuid-a43fc1e7-6196-4eec-a8de-664e022ab9d7>`

**Local Traceability ID:** :ref:`5546B204 <trace-5546b204>`

**Status:** Planned. **Method:** Vary controlled input at fixed integration
time and evaluate residuals from the approved fit.

.. _trace-3a725623:
.. _uuid-57e2e443-83a8-4c39-bde8-1724593a9344:

Test TV-13 - Repeatability
--------------------------

UUID: :ref:`57E2E443-83A8-4C39-BDE8-1724593A9344 <uuid-57e2e443-83a8-4c39-bde8-1724593a9344>`

**Local Traceability ID:** :ref:`3A725623 <trace-3a725623>`

**Status:** Planned. **Method:** Repeat acquisitions without realignment and
apply the approved repeatability statistic.

.. _trace-3e2147ce:
.. _uuid-1d6e90b9-9949-4f98-8683-3ea5b2bf2a49:

Test TV-14 - Stray Light And Second Order
-----------------------------------------

UUID: :ref:`1D6E90B9-9949-4F98-8683-3EA5B2BF2A49 <uuid-1d6e90b9-9949-4f98-8683-3ea5b2bf2a49>`

**Local Traceability ID:** :ref:`3E2147CE <trace-3e2147ce>`

**Status:** Planned. **Method:** Compare controlled filtered, unfiltered, or
blocked-band observations. Exact method and threshold are ``Not In Docs``.

.. _trace-2e04e226:
.. _uuid-e7fcab5b-6d00-4801-9058-42fce17f4714:

Test TV-15 - Reference-Instrument Comparison
--------------------------------------------

UUID: :ref:`E7FCAB5B-6D00-4801-9058-42FCE17F4714 <uuid-e7fcab5b-6d00-4801-9058-42fce17f4714>`

**Local Traceability ID:** :ref:`2E04E226 <trace-2e04e226>`

**Status:** Planned. **Method:** Observe the same suitable source with the
instrument and reference instrument under recorded conditions.

.. _uuid-2cf48d1e-090e-4e45-a1ad-5216f93cab11:

Test TV-16 - Routine Client Workflow
------------------------------------

UUID: :ref:`2CF48D1E-090E-4E45-A1AD-5216F93CAB11 <uuid-2cf48d1e-090e-4e45-a1ad-5216f93cab11>`

**Status:** Planned. **Method:** Demonstrate connect, acquisition, integration-
time adjustment, calibration selection, live presentation, and CSV export
without source-code or hardware reconfiguration.
