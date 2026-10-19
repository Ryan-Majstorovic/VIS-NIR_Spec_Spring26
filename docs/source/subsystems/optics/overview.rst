Optics System Overview
======================

.. _B&W Tek bench listing: https://www.ebay.com/itm/144873214016
.. _Thorlabs GR25-1850: https://www.thorlabs.com/item/GR25-1850

.. _uuid-45725109-9bde-4f4d-9298-123e443f1d2a:

Test Optical Bench
------------------

UUID: :ref:`45725109-9BDE-4F4D-9298-123E443F1D2A <uuid-45725109-9bde-4f4d-9298-123e443f1d2a>`

**Summary:** We perform our optical testing on a used B&W Tek compact
Czerny-Turner optical bench, procured as a parts set that contains the
housing, its lid, a reflective diffraction grating with mount, a collimating
mirror, and a focusing mirror. We mount the entrance slit on the front face
of the housing and our TCD1304DG driver board at the housing's detector port.
:numref:`fig-optics-test-build` shows our current build.

.. figure:: /_static/images/optics/test-build-assembled.webp
   :name: fig-optics-test-build
   :width: 80%
   :alt: Black B&W Tek bench housing with a red driver board mounted at the
         detector port on one end and a slit mount on the front face.

   Our assembled test build. The entrance slit mount sits on the front face
   of the housing, and the TCD1304DG driver board is mounted at the detector
   port on the end wall. Jumper leads carry the detector interface signals
   off the board.

The seller-supplied photographs below document the bench as procured.
:numref:`fig-optics-bench-top` through :numref:`fig-optics-bench-angle-b` show the
interior with the lid removed, :numref:`fig-optics-bench-port` shows the closed
housing and its detector port, and :numref:`fig-optics-bench-scale` gives a size
reference. Source for these figures and for the grating specification:
`B&W Tek bench listing`_ (eBay item 144873214016, seller ``spectrophoton``).

.. figure:: /_static/images/optics/bench-interior-top.webp
   :name: fig-optics-bench-top
   :width: 70%
   :alt: Open bench housing viewed from above with the grating and mirrors in
         their mounts.

   Bench interior from above with the lid removed, showing the grating and
   the two mirrors in their mounts. Identification of each element in this
   view is ``Not In Docs``. Image source: `B&W Tek bench listing`_.

.. figure:: /_static/images/optics/bench-interior-angle-a.webp
   :name: fig-optics-bench-angle-a
   :width: 70%
   :alt: Open bench housing viewed at an angle from the entrance side.

   Bench interior viewed at an angle from the entrance side. Image source:
   `B&W Tek bench listing`_.

.. figure:: /_static/images/optics/bench-interior-angle-b.webp
   :name: fig-optics-bench-angle-b
   :width: 70%
   :alt: Open bench housing viewed at an angle from the opposite corner.

   Bench interior viewed at an angle from the corner opposite the entrance.
   Image source: `B&W Tek bench listing`_.

.. figure:: /_static/images/optics/bench-detector-port.webp
   :name: fig-optics-bench-port
   :width: 70%
   :alt: Closed bench housing with the rectangular detector port outlined on
         the end wall.

   Closed housing with the detector port outlined on the end wall. This is
   the aperture at which we mount the TCD1304DG driver board. Image source:
   `B&W Tek bench listing`_.

.. figure:: /_static/images/optics/bench-scale-reference.webp
   :name: fig-optics-bench-scale
   :width: 45%
   :alt: Open bench housing beside a steel ruler marked in centimeters.

   Open bench beside a centimeter ruler for size reference. Image source:
   `B&W Tek bench listing`_.

.. _uuid-a03ee92d-4bf3-4c9d-9741-2089f22204fb:

Optical Arrangement
-------------------

UUID: :ref:`A03EE92D-4BF3-4C9D-9741-2089F22204FB <uuid-a03ee92d-4bf3-4c9d-9741-2089f22204fb>`

**Summary:** Light follows the Czerny-Turner sequence defined in
:doc:`Optics Architecture <optical_path/czerny_turner/Optics Architecture>`.
The table below maps each element of that sequence to its location in our
test build.

.. list-table::
   :header-rows: 1
   :widths: 18 37 25 20

   * - Element
     - Function
     - Location In Our Build
     - Open Items
   * - Entrance slit
     - Defines the source width presented to the spectrometer.
     - Slit mount on the front face of the housing
       (:numref:`fig-optics-test-build`).
     - Slit width ``Not In Docs``.
   * - Collimating mirror
     - Collimates the light diverging from the slit and directs it to the
       grating.
     - Inside the housing (:numref:`fig-optics-bench-top`).
     - Focal length ``Not In Docs``.
   * - Diffraction grating
     - Disperses the collimated beam by wavelength. The grating is reflective,
       1800 lines/mm, blazed at 500 nm.
     - Inside the housing in its supplied mount
       (:numref:`fig-optics-bench-top`).
     - Grating angle ``Not In Docs``.
   * - Focusing mirror
     - Images the dispersed spectrum onto the detector. The supplied mount
       includes adjustment screws for alignment.
     - Inside the housing (:numref:`fig-optics-bench-top`).
     - Focal length ``Not In Docs``.
   * - TCD1304DG linear CCD
     - Converts the focused spectrum into a sequential analog signal for the
       Embedded system.
     - On our driver board at the detector port
       (:numref:`fig-optics-test-build`, :numref:`fig-optics-bench-port`).
     - Detector placement tolerance ``Not In Docs``.

.. _uuid-c5c2b38e-2dcd-462a-a93f-d10755733d3d:

Key Design Parameters
---------------------

UUID: :ref:`C5C2B38E-2DCD-462A-A93F-D10755733D3D <uuid-c5c2b38e-2dcd-462a-a93f-d10755733d3d>`

.. list-table::
   :header-rows: 1
   :widths: 28 42 30

   * - Parameter
     - Value
     - Source
   * - Optical bench
     - B&W Tek compact Czerny-Turner bench, used, with lid
     - `B&W Tek bench listing`_
   * - Grating groove density
     - 1800 lines/mm (groove spacing of approximately 555.6 nm)
     - Listing; spacing derived from groove density
   * - Grating blaze wavelength
     - 500 nm
     - `B&W Tek bench listing`_
   * - Grating blaze angle
     - 26° 44′, equal to the Littrow angle at the 500 nm blaze wavelength
     - Manufacturer data for the matching `Thorlabs GR25-1850`_ part;
       consistent with the 1800 lines/mm groove density. Not confirmed for
       our grating.
   * - Grating angular dispersion
     - 0.50 nm/mrad
     - Manufacturer data for the matching `Thorlabs GR25-1850`_ part;
       consistent with the 1800 lines/mm groove density. Not confirmed for
       our grating.
   * - Grating efficiency at blaze wavelength
     - 60% to 80%, with published efficiency curves measured in the Littrow
       mounting configuration
     - Manufacturer data for the matching `Thorlabs GR25-1850`_ part. Not
       confirmed for our grating or our non-Littrow bench geometry.
   * - First-order long-wavelength limit
     - Below approximately 1111 nm (twice the groove spacing)
     - Derived from groove density; consistent with the efficiency curve in
       :numref:`fig-optics-grating-efficiency`
   * - Expected average grating efficiency, 400 nm to 1000 nm
     - Approximately 40% to 67%, read from the supplied curve
     - :numref:`fig-optics-grating-efficiency` (supplied, not measured by us)
   * - Housing size
     - Approximately 7 cm along the long edge, estimated from the scale
       photograph; caliper measurement ``Not In Docs``
     - :numref:`fig-optics-bench-scale`
   * - Detector
     - TCD1304DG linear CCD on our driver board, mounted at the detector port
     - Our build (:numref:`fig-optics-test-build`)
   * - Slit width, mirror focal lengths, grating angle
     - ``Not In Docs``
     - To be measured on our build

.. figure:: /_static/images/optics/grating-efficiency-1800-500nm.webp
   :name: fig-optics-grating-efficiency
   :width: 70%
   :alt: Absolute efficiency versus wavelength from 200 nm to 1200 nm for
         perpendicular, parallel, and average polarization.

   Supplied absolute-efficiency curve for the 1800 lines/mm grating blazed at
   500 nm, for perpendicular, parallel, and average polarization, where
   polarization is defined with respect to the grating lines. Image source:
   `B&W Tek bench listing`_. The plot matches the format of the curve
   Thorlabs published for its `Thorlabs GR25-1850`_ (1800 lines/mm, 500 nm
   blaze, measured in the Littrow mounting), which we take as the likely
   original source. We padded the image and re-lettered the clipped y-axis
   label; the curves, axes, and legend are unaltered.

The supplied curve shows two behaviors that affect our measurements. First,
efficiency depends strongly on polarization: the parallel component falls from
approximately 67% near 390 nm to below 10% near 1000 nm, while the
perpendicular component stays between approximately 65% and 85% from 450 nm to
1000 nm. Second, every curve has a local minimum near 400 nm, at the short end
of our target range. Both effects belong in the response-correction workflow
described in :doc:`Optical Component Tradeoffs
<tradeoffs/grating_selection/Optical Component Tradeoffs>`.

Whether a single grating angle places the full 400 nm to 1000 nm first-order
band across the 3648-pixel effective array depends on the mirror focal lengths
and the grating angle, which are ``Not In Docs``. We treat full-range coverage
on this bench as unverified until we measure it as described in
:doc:`Wavelength Coverage And Resolution
<performance_characterization/wavelength_and_resolution/Wavelength Coverage And Resolution>`.

**Requirement:** The Optics system shall use the test bench described in this
section, with the TCD1304DG driver board mounted at its detector port, as the
optical configuration for all optical characterization and measurement.

**Rationale:** Holding the slit, mirrors, grating, and detector port to one
known geometry lets us attribute measured coverage, FWHM, and throughput to
that geometry rather than to differences between rebuilds.

**Requirement:** The Optics system shall record the slit, grating, mirror,
filter, and detector-port configuration of the test bench with every
characterization record to identify the optical geometry that produced each
result.

**Rationale:** A change to any bench element alters wavelength coverage,
resolution, and throughput. Without the recorded configuration, we cannot
separate a change in measured performance caused by the optics from one caused
by acquisition or host-side processing.

.. _uuid-48fc9581-eaff-4e34-9b0c-0d1bf006e71f:

System Role
-----------

UUID: :ref:`48FC9581-EAFF-4E34-9B0C-0D1BF006E71F <uuid-48fc9581-eaff-4e34-9b0c-0d1bf006e71f>`

**Summary:** The Optics system shall accept input light and coordinate
collimation, wavelength dispersion, focusing, filtering, alignment, enclosure,
and performance characterization to image a VIS-NIR spectrum onto the
TCD1304DG effective detector array.

**Expected Outcome:** The Optics system shall provide usable wavelength
coverage from 400 nm to 1000 nm and approximately 5 nm FWHM for narrow sources.

**Rationale:** Coordinating the optical path, filtering, and mechanical
alignment preserves the wavelength-dependent image needed for detector capture
and allows measured optical performance to be attributed to a repeatable
configuration.

.. _uuid-3a113e98-e52c-4b54-8624-4939610e4ed2:

System Objectives
-----------------

UUID: :ref:`3A113E98-E52C-4B54-8624-4939610E4ED2 <uuid-3a113e98-e52c-4b54-8624-4939610e4ed2>`

**Objective 1:** **Optical transformation.** The Optics system shall accept
incident light, collimate it, disperse it by wavelength, and focus the spectrum
across the detector.

**Rationale:** Preserving this sequence establishes the detector-position
relationship required for wavelength measurement.

**Objective 2:** **Component and filtering decisions.** The Optics system shall
record how the grating, slit, mirrors, and filters affect wavelength coverage,
resolution, throughput, second-order overlap, stray light, and alignment.

**Rationale:** Recording each tradeoff prevents a component choice from changing
instrument performance without reviewable evidence.

**Objective 3:** **Physical verification.** The Optics system shall provide
alignment, enclosure, and characterization evidence for wavelength coverage,
FWHM, wavelength accuracy, SNR, linearity, repeatability, stray light, and
reference comparison.

**Rationale:** Physical evidence is needed to distinguish predicted optical
performance from measured instrument performance.

.. _uuid-e19ea297-0d3d-4bb1-b420-629bde897454:

System Relationship
-------------------

UUID: :ref:`E19EA297-0D3D-4BB1-B420-629BDE897454 <uuid-e19ea297-0d3d-4bb1-b420-629bde897454>`

.. list-table::
   :header-rows: 1

   * - System
     - Primary Responsibility
     - Downstream Or Adjacent Relationship
   * - Optical Path
     - The Optics optical-path system shall define the slit, collimation, dispersion, focusing, and detector-imaging sequence.
     - The Optics optical-path system shall establish wavelength-dependent illumination on the TCD1304DG effective array.
   * - Tradeoffs
     - The Optics tradeoff system shall record component and geometry choices with their optical consequences.
     - The Optics tradeoff system shall relate each choice to alignment, throughput, coverage, and resolution.
   * - Filtering
     - The Optics filtering system shall limit second-order overlap and other unwanted wavelength content before detector capture.
     - The Optics filtering system shall control the optical content presented to the detector and downstream Host PC processing.
   * - Alignment And Enclosure
     - The Optics alignment-and-enclosure system shall establish repeatable placement, light exclusion, and mechanical stability.
     - The Optics alignment-and-enclosure system shall preserve the optical configuration used for characterization and measurement.
   * - Performance Characterization
     - The Optics performance-characterization system shall define coverage, FWHM, accuracy, SNR, linearity, repeatability, stray-light, and comparison checks.
     - The Optics performance-characterization system shall provide optical evidence to Test and Verification and Host PC calibration workflows.

.. _uuid-14a977b2-a1cd-404e-9500-1eacbf249040:

Integration Boundary
--------------------

UUID: :ref:`14A977B2-A1CD-404E-9500-1EACBF249040 <uuid-14a977b2-a1cd-404e-9500-1eacbf249040>`

**Summary:** The Optics system shall provide wavelength-dependent illumination
at the detector boundary. The Embedded system shall control detector timing and
digitization after that optical handoff. The Host PC system shall perform
pixel-to-wavelength association, correction, visualization, retention, and
export. The Test and Verification system shall provide canonical pass/fail
disposition.

Component placement tolerances, final slit width, grating angle, focus
tolerance, filter cutoff profile, enclosure limits, and most quantitative
characterization acceptance thresholds remain ``Not In Docs`` until approved
requirements and methods are available.

**Expected Outcome:** The Optics system shall remain independently reviewable
without duplicating Embedded acquisition, Host PC processing, or Integration
transport behavior.

**Rationale:** Separating optical formation, detector acquisition, host-side
processing, and pass/fail disposition prevents multiple subsystems from
defining or evaluating the same boundary behavior differently.

Related Pages
-------------

* :doc:`Optical Path <optical_path/Optical Path>`
* :doc:`Tradeoffs <tradeoffs/Tradeoffs>`
* :doc:`Filtering <filtering/Filtering>`
* :doc:`Alignment And Enclosure <alignment_enclosure/Alignment And Enclosure>`
* :doc:`Performance Characterization <performance_characterization/Performance Characterization>`
