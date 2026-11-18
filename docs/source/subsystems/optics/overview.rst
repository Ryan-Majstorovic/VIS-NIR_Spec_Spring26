Optics System Overview
======================

This page states what the Optics system is for, why it uses a Czerny-Turner
layout, and the criteria it must meet. The hardware that carries out the
design is in :doc:`Optics Architecture
<optical_path/czerny_turner/Optics Architecture>`.

.. _uuid-48fc9581-eaff-4e34-9b0c-0d1bf006e71f:

Purpose
-------

UUID: :ref:`48FC9581-EAFF-4E34-9B0C-0D1BF006E71F <uuid-48fc9581-eaff-4e34-9b0c-0d1bf006e71f>`

**Summary:** The Optics system takes light delivered by fiber, separates it by
wavelength, and focuses the spectrum across the TCD1304DG linear CCD so that
each pixel receives a narrow, repeatable band of wavelengths. Everything
downstream depends on that mapping. If the optics place a wavelength at the
wrong pixel, spread it over too many pixels, or move it between captures, no
later processing can recover the lost information.

The optical path is a used B&W Tek compact Czerny-Turner bench provided by
the client. The original design target was 400 nm to 1000 nm with a
custom-built bench. The B&W Tek bench covers approximately 400 nm to 800 nm,
which the client accepted for this stage of the project. An order-sorting
filter, a custom enclosure, and a redesigned layout are future work.

.. _uuid-e3f10c7f-da96-4576-bbff-497412e4dddf:

Design Approach
---------------

UUID: :ref:`E3F10C7F-DA96-4576-BBFF-497412E4DDDF <uuid-e3f10c7f-da96-4576-bbff-497412e4dddf>`

**Summary:** The bench uses the two-concave-mirror geometry of a
Czerny-Turner monochromator with the exit slit replaced by the linear CCD, so
the whole dispersed band is recorded in one exposure. The arrangement was
chosen for three reasons:

* **All-reflective focusing.** Mirrors focus every wavelength at the same
  distance; a lens would leave one end of a wide band out of focus.
* **Compact, folded path.** A transmission-grating layout is simpler to align
  but needs a long straight path that did not fit the size target.
* **Available hardware.** The B&W Tek bench supplies a working housing,
  mirrors, and grating, so the project could concentrate on detection,
  calibration, and software.

The accepted cost is alignment sensitivity: slit position, mirror tilt,
grating angle, and detector placement interact, and a small error in any one
broadens lines or shifts the band off the detector.

.. _uuid-3ba60956-b9ba-4440-a771-5fd750687808:

Light Path And Focusing
-----------------------

UUID: :ref:`3BA60956-B9BA-4440-A771-5FD750687808 <uuid-3ba60956-b9ba-4440-a771-5fd750687808>`

1. **Fiber input.** A low-OH multimode fiber carries light to the entrance
   slit. Its numerical aperture sets the cone of light leaving the slit.
2. **Entrance slit.** The slit is the object the spectrometer images. A
   narrower slit gives finer resolution but passes less light.
3. **Collimating mirror.** A concave mirror one focal length from the slit
   turns the diverging cone into a parallel beam aimed at the grating.
4. **Diffraction grating.** The reflective grating sends each wavelength off
   at a different angle, spreading the spectrum along one axis.
5. **Focusing mirror and detector.** A second concave mirror focuses each
   wavelength to a different point along the TCD1304DG array. Each point is
   an image of the slit in that wavelength's light.

The Czerny-Turner focal surface is curved but the CCD is flat, so best focus
is a compromise across the band: a detector placed for the sharpest 520 nm
line can leave the 405 nm and 650 nm lines broader. Line width is therefore
measured at every calibration line, not only at the center of the array.

The fiber's light cone should fill the collimating mirror without spilling
past it; spilled light scatters inside the housing as stray light. Whether the
0.22 NA fiber matches the bench's acceptance angle depends on the mirror focal
lengths, which are ``Not In Docs``.

.. _uuid-3a113e98-e52c-4b54-8624-4939610e4ed2:

Design Criteria
---------------

UUID: :ref:`3A113E98-E52C-4B54-8624-4939610E4ED2 <uuid-3a113e98-e52c-4b54-8624-4939610e4ed2>`

**Requirement OPT-R1 (Wavelength coverage):** The Optics system shall
disperse first-order light from approximately 400 nm to 800 nm across the
3648-pixel effective array of the TCD1304DG at one fixed grating angle.

**Rationale:** One fixed geometry lets one pixel-to-wavelength map cover the
whole client-approved band. Any part of the band that falls off the array
cannot be measured at all.

**Requirement OPT-R2 (Spectral resolution):** The Optics system shall focus
narrow-line sources to a FWHM of 5 nm or less at each calibration wavelength.

**Rationale:** Line width sets how close two spectral features can be and
still be told apart. Checking at each wavelength catches focus errors that
only appear away from the center of the array.

**Requirement OPT-R3 (Fiber input):** The Optics system shall accept input
light through an SMA-terminated, 50 µm, low-OH multimode fiber.

**Rationale:** The fiber lets the same source be moved between the prototype
and the reference spectrometer without disturbing the source. Low-OH fiber
avoids the hydroxyl absorption that weakens near-infrared light, which keeps
the long-wavelength end usable and preserves the option of extending coverage
toward 1000 nm.

**Requirement OPT-R4 (Ordered, repeatable dispersion):** The Optics system
shall place wavelengths on the detector in monotonic order and return each
calibration line to the same pixel position across repeated captures, fiber
reconnection, and electronics power cycling.

**Rationale:** A pixel-to-wavelength map is only valid if pixel position
depends on wavelength alone. Drift or reordering makes the calibrated axis
wrong between calibrations. The allowed shift is ``Not In Docs``.

**Requirement OPT-R5 (Second-order overlap):** The Optics system shall allow
second-order light from short wavelengths to be identified and its height
measured before an order-sorting filter is selected.

**Rationale:** A grating sends wavelength λ in second order to the same angle
as 2λ in first order, so 405 nm light can appear near 810 nm and read as false
long-wavelength signal. Its measured height sets the attenuation the future
filter needs; choosing a filter first risks leaving false signal or blocking
real light.

**Requirement OPT-R6 (Light exclusion):** The Optics system shall keep the
housing lid closed and the detector port sealed around the driver board
during every measurement.

**Rationale:** Room light adds a time-varying background that a dark frame
taken at a different moment does not remove, which biases every intensity
measurement.

.. _uuid-081c35f5-b08b-4642-a380-db10c5000a8e:

Verification
------------

UUID: :ref:`081C35F5-B08B-4642-A380-DB10C5000A8E <uuid-081c35f5-b08b-4642-a380-db10c5000a8e>`

Each criterion is verified by tests in the :doc:`Test Plan
<../test_and_verification/test_plan>`.

.. list-table::
   :header-rows: 1
   :widths: 40 25 35

   * - Criterion
     - Tests
     - Note
   * - OPT-R1 Wavelength coverage
     - OPT-2
     - Bounded by the 405 nm and 650 nm lines.
   * - OPT-R2 Spectral resolution
     - OPT-4
     - Checked at 405 nm, 520 nm, and 650 nm.
   * - OPT-R3 Fiber input
     - FIB-1
     - Through the ADASMA sleeve and M14L01 cable.
   * - OPT-R4 Ordered, repeatable dispersion
     - OPT-1, OPT-3, OPT-6, CMP-1
     - CMP-1 checks the map on an independent source.
   * - OPT-R5 Second-order overlap
     - OPT-5
     - Observation only; the filter is future work.
   * - OPT-R6 Light exclusion
     - EMB-3
     - Dark baseline with the lid closed.

.. _uuid-14a977b2-a1cd-404e-9500-1eacbf249040:

Boundary
--------

UUID: :ref:`14A977B2-A1CD-404E-9500-1EACBF249040 <uuid-14a977b2-a1cd-404e-9500-1eacbf249040>`

**Requirement:** The Optics system shall end at the detector surface, where it
delivers wavelength-dependent illumination to the TCD1304DG; the Embedded
system shall own detector timing and digitization, and the Host PC system
shall own the pixel-to-wavelength map.

**Rationale:** If optics and software both claimed the wavelength mapping, a
peak in the wrong place could be "fixed" in either one and the real cause
would be hidden.
