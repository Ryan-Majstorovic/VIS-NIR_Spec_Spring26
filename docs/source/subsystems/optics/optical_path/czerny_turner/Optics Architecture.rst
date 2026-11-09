Optics Architecture
===================

UUID: ``0F0D41FE-6F7B-4A3E-A8DD-3C1F7DCE2481``

.. _B&W Tek bench listing: https://www.ebay.com/itm/144873214016
.. _Thorlabs GR25-1850: https://www.thorlabs.com/item/GR25-1850
.. _Thorlabs M14L01: https://www.thorlabs.com/item/M14L01
.. _Thorlabs ADASMA: https://www.thorlabs.com/item/ADASMA

This page describes the hardware that carries out the design approach in the
:doc:`Optics System Overview <../../overview>`: our test bench, its optical
elements and their parameters, the grating's measured behavior, the component
tradeoffs behind the design, second-order control, and alignment.

The optical subsystem separates incident light by wavelength and images the
resulting spectrum onto the TCD1304DG linear CCD through a reflective
Czerny-Turner path:

1. A slit defines the source width presented to the spectrometer.
2. A collimating mirror forms a collimated beam.
3. A reflective diffraction grating disperses the beam by wavelength.
4. A focusing mirror images the dispersed spectrum onto the CCD.
5. The TCD1304DG converts the focused spectrum into a sequential analog signal.

Slit width, mirror placement, grating angle, and CCD position must be tuned
together because they determine throughput, resolution, wavelength coverage,
and alignment sensitivity.

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
   :width: 40%
   :align: center
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
   :width: 35%
   :align: center
   :alt: Open bench housing viewed from above with the grating and mirrors in
         their mounts.

   Bench interior from above with the lid removed, showing the grating and
   the two mirrors in their mounts. Identification of each element in this
   view is ``Not In Docs``. Image source: `B&W Tek bench listing`_.

.. figure:: /_static/images/optics/bench-interior-angle-a.webp
   :name: fig-optics-bench-angle-a
   :width: 35%
   :align: center
   :alt: Open bench housing viewed at an angle from the entrance side.

   Bench interior viewed at an angle from the entrance side. Image source:
   `B&W Tek bench listing`_.

.. figure:: /_static/images/optics/bench-interior-angle-b.webp
   :name: fig-optics-bench-angle-b
   :width: 35%
   :align: center
   :alt: Open bench housing viewed at an angle from the opposite corner.

   Bench interior viewed at an angle from the corner opposite the entrance.
   Image source: `B&W Tek bench listing`_.

.. figure:: /_static/images/optics/bench-detector-port.webp
   :name: fig-optics-bench-port
   :width: 35%
   :align: center
   :alt: Closed bench housing with the rectangular detector port outlined on
         the end wall.

   Closed housing with the detector port outlined on the end wall. This is
   the aperture at which we mount the TCD1304DG driver board. Image source:
   `B&W Tek bench listing`_.

.. figure:: /_static/images/optics/bench-scale-reference.webp
   :name: fig-optics-bench-scale
   :width: 23%
   :align: center
   :alt: Open bench housing beside a steel ruler marked in centimeters.

   Open bench beside a centimeter ruler for size reference. Image source:
   `B&W Tek bench listing`_.

**Requirement:** The Optics system shall use the test bench described in this
section, with the TCD1304DG driver board mounted at its detector port, as the
optical configuration for all optical characterization and measurement.

**Rationale:** Holding the slit, mirrors, grating, and detector port to one
known geometry lets us attribute measured coverage, FWHM, and throughput to
that geometry rather than to differences between rebuilds.

.. _uuid-a03ee92d-4bf3-4c9d-9741-2089f22204fb:

Optical Arrangement
-------------------

UUID: :ref:`A03EE92D-4BF3-4C9D-9741-2089F22204FB <uuid-a03ee92d-4bf3-4c9d-9741-2089f22204fb>`

**Summary:** The table below maps each element of the Czerny-Turner sequence
to its location in our test build.

.. list-table::
   :header-rows: 1
   :widths: 18 37 25 20

   * - Element
     - Function
     - Location In Our Build
     - Open Items
   * - Input fiber
     - Delivers light from the source under test or the calibration source
       to the entrance slit.
     - `Thorlabs M14L01`_ patch cable (Ø50 µm core, 0.22 NA, low OH,
       SMA-SMA, 1 m). A `Thorlabs ADASMA`_ mating sleeve joins the
       calibration unit's fiber output to the patch cable.
     - Fiber-to-slit mounting ``Not In Docs``.
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
   * - Input fiber
     - Multimode step-index patch cable, Ø50 µm core, 0.22 NA, low OH,
       SMA-to-SMA, 1 m long (Thorlabs M14L01)
     - `Thorlabs M14L01`_
   * - Fiber mating sleeve
     - SMA-to-SMA mating sleeve (Thorlabs ADASMA) joining the calibration
       unit's fiber output to the input patch cable
     - `Thorlabs ADASMA`_
   * - Fiber NA match to the bench acceptance angle
     - ``Not In Docs``
     - To be determined once the mirror focal lengths are measured
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
   :align: center
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
described in :ref:`Optical Component Tradeoffs
<uuid-d5cfd390-4e80-489e-87b7-ce1fc5e2e11d>`.

Whether a single grating angle places the full 400 nm to 1000 nm first-order
band across the 3648-pixel effective array depends on the mirror focal lengths
and the grating angle, which are ``Not In Docs``. We treat full-range coverage
on this bench as unverified until test OPT-3 measures it, as described in
:doc:`Optics Verification <../../verification/Optics Verification>`.

.. _uuid-d5cfd390-4e80-489e-87b7-ce1fc5e2e11d:

Optical Component Tradeoffs
---------------------------

UUID: :ref:`D5CFD390-4E80-489E-87B7-CE1FC5E2E11D <uuid-d5cfd390-4e80-489e-87b7-ce1fc5e2e11d>`

**Summary:** The main grating tradeoff is between simple alignment and compact
packaging.

.. list-table::
   :header-rows: 1
   :widths: 22 39 39

   * - Option
     - Advantage
     - Reason Not Selected, Or Accepted Cost
   * - Transmission grating
     - Mechanically simpler layout and easier alignment.
     - Not selected. The required straight optical path did not fit the
       target enclosure footprint.
   * - Reflective blazed grating, Czerny-Turner geometry (selected)
     - Compact folded path; follows common spectrometer practice; all-mirror
       focusing avoids chromatic focus shift.
     - Accepted cost: higher alignment sensitivity.
   * - Volume phase holographic (VPH) grating
     - High efficiency and low stray light.
     - Not selected. Cost and bandwidth constraints make it a poor fit for
       this prototype.

Mirror coating, grating efficiency, slit width, and filter transmission all
affect the measured intensity response.

**Requirement:** The Optics system shall provide the grating efficiency curve,
mirror coating, slit width, and filter transmission of the measurement
configuration to the response-correction workflow to correct the
wavelength-dependent optical throughput of the measured spectrum.

**Rationale:** Grating efficiency alone varies by more than a factor of six
across the band for parallel polarization. Without these inputs, the response
correction would attribute optical throughput losses to the source being
measured.

.. _uuid-406d13b5-12f2-4144-9f1e-c36e6d515fa0:

Second-Order Diffraction And Filtering
--------------------------------------

UUID: :ref:`406D13B5-12F2-4144-9F1E-C36E6D515FA0 <uuid-406d13b5-12f2-4144-9f1e-c36e6d515fa0>`

**Summary:** A grating diffracts wavelength λ in second order at the same
angle as wavelength 2λ in first order, so short-wavelength light also lands on
the long-wavelength part of the detector. In our 400 nm to 1000 nm band, any
light from 400 nm to 500 nm can appear in second order at 800 nm to 1000 nm.
With the calibration unit, the 405 nm laser is expected to produce a
second-order peak near 810 nm.

Software-only correction is not sufficient as the primary mitigation because
it requires knowing the original short-wavelength contribution and optical
throughput accurately. Overlap should be reduced physically before any
post-processing correction is applied. The planned physical mitigation is an
order-sorting filter in front of the long-wavelength part of the detector:

* A long-pass filter or a custom thin-film linear variable filter.
* A cutoff matched to the detector position where second-order light begins.
* Validation against the calibration lasers and a broadband source.

**Requirement:** The Optics system shall measure the relative height of the
second-order 405 nm peak near 810 nm before an order-sorting filter is
selected, to set the filter's required attenuation.

**Rationale:** The measured second-order height tells us how much the filter
must suppress. Selecting a filter before this measurement risks either
leaving false near-infrared signal or blocking real light without need.

For the current scope, second-order behavior is observed only (test OPT-6).
Filter selection and installation are future work.

.. _uuid-c84aa8d3-91d6-42cf-a6e7-28e7edcf87ae:

Alignment And Enclosure
-----------------------

UUID: :ref:`C84AA8D3-91D6-42CF-A6E7-28E7EDCF87AE <uuid-c84aa8d3-91d6-42cf-a6e7-28e7edcf87ae>`

**Summary:** The B&W Tek housing holds the mirrors and grating in fixed
mounts and serves as the current enclosure. Alignment is done by adjusting
the focusing-mirror screws and the detector position at the detector port.

Alignment priorities are:

* Place the first-order spectrum across the useful CCD width.
* Minimize defocus and tilt that broaden narrow spectral lines.
* Preserve the selected slit-width tradeoff between throughput and resolution.
* Record grating, mirror, and CCD positions once a repeatable setup is found.

**Requirement:** The Optics system shall keep the housing lid closed and the
detector port sealed around the driver board during every measurement to
block ambient light from reaching the detector.

**Rationale:** Ambient light adds a time-varying background that a dark frame
taken at a different moment does not remove, which biases every intensity
measurement.

A custom enclosure is future work. Its constraints should be introduced only
after the current bench meets the wavelength coverage and FWHM targets, so
that the enclosure preserves a geometry already known to work.
