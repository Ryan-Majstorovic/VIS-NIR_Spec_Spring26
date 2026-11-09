Optics System Overview
======================

This page states what the Optics system is for, the optical design approach we
chose, and the design criteria the optics must meet. Hardware details of our
build are in :doc:`Optics Architecture
<optical_path/czerny_turner/Optics Architecture>`, and the tests that check
each criterion are in :doc:`Optics Verification <verification/Optics Verification>`.

.. _uuid-48fc9581-eaff-4e34-9b0c-0d1bf006e71f:

Purpose
-------

UUID: :ref:`48FC9581-EAFF-4E34-9B0C-0D1BF006E71F <uuid-48fc9581-eaff-4e34-9b0c-0d1bf006e71f>`

**Summary:** The Optics system takes light delivered by fiber, separates it by
wavelength, and focuses the resulting spectrum across the TCD1304DG linear CCD
so that each detector pixel receives a narrow, repeatable band of wavelengths.
Everything downstream depends on that mapping: the Embedded system digitizes
the pixel intensities, and the Host PC converts pixel position into
wavelength. If the optics place a wavelength at the wrong pixel, spread it over
too many pixels, or move it between captures, no later processing can recover
the lost information.

**Expected Outcome:** The Optics system shall provide usable first-order
coverage from 400 nm to 1000 nm and approximately 5 nm FWHM for narrow
sources, with peak positions stable enough to support a pixel-to-wavelength
calibration.

For the current project scope, the optics are exercised with the laser
calibration unit (405 nm, 520 nm, 650 nm, and 980 nm lines) as described in the
:doc:`Demonstration Test Plan
<../test_and_verification/demo_test_plan>`. Order-sorting filters, a
custom-built enclosure, and a redesigned optical layout are future work.

.. _uuid-e3f10c7f-da96-4576-bbff-497412e4dddf:

Design Approach
---------------

UUID: :ref:`E3F10C7F-DA96-4576-BBFF-497412E4DDDF <uuid-e3f10c7f-da96-4576-bbff-497412e4dddf>`

**Summary:** The optics use a Czerny-Turner mirror arrangement, the
two-concave-mirror geometry of a Czerny-Turner monochromator. A monochromator
passes one wavelength at a time through an exit slit. We replace the exit slit
with the TCD1304DG linear CCD, so the instrument records the whole dispersed
band in a single exposure (strictly, it operates as a Czerny-Turner
spectrograph).

We chose this arrangement for three reasons:

* **All-reflective focusing.** Mirrors focus every wavelength at the same
  distance, while a lens focuses blue and near-infrared light at different
  distances. Over a 400 nm to 1000 nm band, a lens-based design would leave one
  end of the spectrum out of focus.
* **Compact, folded path.** The two mirrors fold the beam back on itself, so
  the path fits a small housing. A transmission-grating layout is mechanically
  simpler but needs a long straight path that did not fit our size target.
* **Available hardware.** A used B&W Tek compact Czerny-Turner bench gives us
  a working housing, mirrors, and a reflective grating, so the project can
  focus on detection, calibration, and software rather than building a bench
  from scratch.

The accepted cost is alignment sensitivity: slit position, mirror tilt,
grating angle, and detector placement all interact, and a small error in any
one broadens lines or shifts the band off the detector. The full comparison
of grating options is in :ref:`Optical Component Tradeoffs
<uuid-d5cfd390-4e80-489e-87b7-ce1fc5e2e11d>`.

.. _uuid-3ba60956-b9ba-4440-a771-5fd750687808:

Light Path And Focusing
-----------------------

UUID: :ref:`3BA60956-B9BA-4440-A771-5FD750687808 <uuid-3ba60956-b9ba-4440-a771-5fd750687808>`

**Summary:** Light travels through five stages. Each stage either shapes the
beam or sets where a wavelength lands on the detector.

1. **Fiber input.** A low-OH multimode fiber carries light from the source to
   the entrance slit. The fiber's numerical aperture sets the cone of light
   that leaves the slit.
2. **Entrance slit.** The slit is the object the spectrometer images. A
   narrower slit gives a narrower line image and finer resolution but passes
   less light.
3. **Collimating mirror.** A concave mirror placed one focal length from the
   slit turns the diverging cone into a parallel beam and directs it onto the
   grating.
4. **Diffraction grating.** The reflective grating sends each wavelength off
   at a different angle. Longer wavelengths leave at larger angles, which
   spreads the spectrum across one axis.
5. **Focusing mirror and detector.** A second concave mirror brings each
   wavelength's parallel beam to a focus at a different point along the
   TCD1304DG array. Each point is an image of the entrance slit in that
   wavelength's light.

Focus is set by the focusing-mirror adjustment screws and the detector
position. The Czerny-Turner focal surface is not perfectly flat, but the CCD
is, so best focus is a compromise across the band: a detector placed for the
sharpest 520 nm line can leave the 405 nm and 980 nm lines slightly broader.
For this reason, line width is checked at every reference wavelength rather
than only at the center of the array.

The fiber's light cone should fill the collimating mirror without spilling
past it. Light that misses the mirror scatters inside the housing as stray
light. Whether the 0.22 NA fiber matches the bench's acceptance angle depends
on the mirror focal lengths, which are ``Not In Docs``.

.. _uuid-3a113e98-e52c-4b54-8624-4939610e4ed2:

Design Criteria And Requirements
--------------------------------

UUID: :ref:`3A113E98-E52C-4B54-8624-4939610E4ED2 <uuid-3a113e98-e52c-4b54-8624-4939610e4ed2>`

**Requirement OPT-R1 (Wavelength coverage):** The Optics system shall
disperse first-order light from 400 nm to 1000 nm across the 3648-pixel
effective array of the TCD1304DG at one fixed grating angle.

**Rationale:** A single fixed geometry lets one pixel-to-wavelength map cover
the full target band. If either end of the band falls off the array, that
part of the spectrum cannot be measured at all.

**Requirement OPT-R2 (Spectral resolution):** The Optics system shall focus
narrow-line sources to a FWHM of approximately 5 nm at each reference
wavelength across the operating band.

**Rationale:** Line width sets how close two spectral features can be and
still be told apart. Checking at each wavelength catches focus and aberration
errors that only appear away from the center of the array.

**Requirement OPT-R3 (Reflective imaging):** The Optics system shall use
concave mirrors, not lenses, for collimation and focusing to keep 400 nm to
1000 nm light in focus at a single detector position.

**Rationale:** Lenses focus different wavelengths at different distances, so
a refractive design would blur one end of the band for any one detector
position.

**Requirement OPT-R4 (Fiber input):** The Optics system shall accept input
light through an SMA-terminated low-OH multimode fiber to deliver 400 nm to
1000 nm light to the entrance slit without OH absorption loss in the 800 nm to
1000 nm band.

**Rationale:** Standard silica fiber absorbs light in the 800 nm to 1000 nm
band, which would weaken the long-wavelength end of the spectrum, where the
detector and grating response are already low.

**Requirement OPT-R5 (Ordered, repeatable dispersion):** The Optics system
shall place wavelengths on the detector in monotonic order and return each
reference line to the same pixel position across repeated captures, fiber
reconnection, and electronics power cycling.

**Rationale:** A pixel-to-wavelength map is only valid if pixel position
depends on wavelength alone. Drift or reordering would make the calibrated
wavelength axis wrong between calibrations. The allowed repeatability limit
is ``Not In Docs``.

**Requirement OPT-R6 (Second-order overlap):** The Optics system shall allow
second-order diffraction of short-wavelength light into the long-wavelength
region of the detector to be identified and measured before an order-sorting
filter is selected.

**Rationale:** Second-order 405 nm light lands near 810 nm, inside our
operating band, where it would read as false near-infrared signal. Measuring
its size first tells us what filter cutoff and attenuation the future
order-sorting filter needs.

**Requirement OPT-R7 (Light exclusion):** The Optics system shall block
ambient light from reaching the detector during measurement.

**Rationale:** Room light adds a background that varies with time and is not
removed by a dark frame captured at a different moment, which biases every
intensity measurement.

.. _uuid-081c35f5-b08b-4642-a380-db10c5000a8e:

Verification Summary
--------------------

UUID: :ref:`081C35F5-B08B-4642-A380-DB10C5000A8E <uuid-081c35f5-b08b-4642-a380-db10c5000a8e>`

**Summary:** Each criterion above is checked by one or more tests in the
:doc:`Demonstration Test Plan <../test_and_verification/demo_test_plan>`. The
optics-specific view of those tests is in :doc:`Optics Verification
<verification/Optics Verification>`.

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Criterion
     - Tests
     - Current Scope
   * - OPT-R1 Wavelength coverage
     - OPT-2, OPT-3
     - Checked with the 405 nm and 980 nm lines.
   * - OPT-R2 Spectral resolution
     - OPT-5
     - Checked at all four laser lines.
   * - OPT-R3 Reflective imaging
     - Inspection, OPT-5
     - Met by the bench design; OPT-5 confirms focus across the band.
   * - OPT-R4 Fiber input
     - FIB-1
     - Checked through the ADASMA sleeve and M14L01 cable.
   * - OPT-R5 Ordered, repeatable dispersion
     - OPT-1, OPT-2, OPT-4, OPT-7, OPT-8
     - Checked; repeatability limit ``Not In Docs``.
   * - OPT-R6 Second-order overlap
     - OPT-6
     - Observation only; filter mitigation is future work.
   * - OPT-R7 Light exclusion
     - EMB-3
     - Covered by the dark-baseline check with the bench lid closed.

.. _uuid-14a977b2-a1cd-404e-9500-1eacbf249040:

Integration Boundary
--------------------

UUID: :ref:`14A977B2-A1CD-404E-9500-1EACBF249040 <uuid-14a977b2-a1cd-404e-9500-1eacbf249040>`

**Summary:** The Optics system ends at the detector surface, where it
delivers wavelength-dependent illumination to the TCD1304DG. The Embedded
system controls detector timing and digitization after that handoff. The Host
PC system performs pixel-to-wavelength association, correction, display, and
export. The Test and Verification system assigns pass/fail disposition.

**Rationale:** Separating optical formation, detector acquisition, host-side
processing, and pass/fail disposition prevents multiple subsystems from
defining or evaluating the same boundary behavior differently.

Optics Pages
------------

* :doc:`Optics Architecture <optical_path/czerny_turner/Optics Architecture>`:
  our test bench, its components and parameters, grating behavior, component
  tradeoffs, second-order control, and alignment.
* :doc:`Optics Verification <verification/Optics Verification>`: how each
  design criterion is tested and what each test record must contain.
