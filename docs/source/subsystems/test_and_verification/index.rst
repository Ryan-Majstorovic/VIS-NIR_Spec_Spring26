Test and Verification
=====================

.. _trace-0647b389:
.. _uuid-4675cd82-c766-4d59-8aec-c8cdace41275:

Overview
--------

UUID: :ref:`4675CD82-C766-4D59-8AEC-C8CDACE41275 <uuid-4675cd82-c766-4d59-8aec-c8cdace41275>`

**Summary:** Test and Verification decides whether the prototype meets its
documented limits. The core of the plan is a side-by-side comparison with a
commercial reference spectrometer: the reference establishes the true
wavelengths of the calibration sources, the prototype is calibrated against
them, and both instruments then measure the same LED and broadband sources.

* :doc:`Test Plan <test_plan>` lists every test, its pass criterion, and the
  measurements deferred beyond this semester.
* :doc:`Comparison Procedure <procedure>` gives the run order, the
  matched-condition rules, and the contents of a test record.
* :doc:`Calculations <calculations>` defines every derived number.

**Requirement:** The Test and Verification system shall take its pass limits
only from ``Requirements And Metrics.rst`` and shall record ``Not In Docs``
where a test has no documented limit.

**Rationale:** A limit chosen while looking at the data can be set to make a
result pass. Holding limits to the documented requirements keeps each result
an honest test of the design.

.. _uuid-7c35f02d-e592-4b12-ad80-bdd5758f6876:

Status Values
-------------

UUID: :ref:`7C35F02D-E592-4B12-AD80-BDD5758F6876 <uuid-7c35f02d-e592-4b12-ad80-bdd5758f6876>`

* **Planned:** The method and criterion are documented; no result is
  claimed.
* **Pass**, **Fail**, **Inconclusive:** Assigned from a complete test record
  as described in :ref:`Result Disposition
  <uuid-bd53c5b6-b340-46b1-b46e-7458d173321b>`.

.. toctree::
   :maxdepth: 1
   :hidden:

   test_plan
   procedure
   calculations
