Procedure
=========

.. _uuid-4ec294ef-a537-40f6-9f63-53770c1a93f8:

Ordered Masking Behavior
------------------------

UUID: :ref:`4EC294EF-A537-40F6-9F63-53770C1A93F8 <uuid-4ec294ef-a537-40f6-9f63-53770c1a93f8>`

1. Receive corrected detector values and the applicable bad-pixel mask.
2. Confirm that the mask corresponds to the active detector geometry.
3. Qualify known-bad positions before downstream wavelength or spectral use.
4. Carry the mask identity and affected positions with the processed record.

.. _uuid-47882530-05db-4bfc-8f14-27549578f93d:

Masking Decisions
-----------------

UUID: :ref:`47882530-05DB-4BFC-8F14-27549578F93D <uuid-47882530-05db-4bfc-8f14-27549578f93d>`

The requirements do not select invalid-value representation, interpolation, replacement, or edge behavior. Those choices are Not In Docs and shall not be inferred.

.. _uuid-b580f0bb-a409-4ce8-9c66-bb9625d871e5:

Processing Conditions
---------------------

UUID: :ref:`B580F0BB-A409-4CE8-9C66-BB9625D871E5 <uuid-b580f0bb-a409-4ce8-9c66-bb9625d871e5>`

* **compatible mask applied**
* **mask unavailable**
* **mask geometry incompatible**
