"""
Lazily evaluated annotations (PEP 649): forward references without
``from __future__ import annotations``.

``test_aod.py`` covers the same with string annotations.
"""

import aod


def test_forward_reference():
	class Person:
		employer: aod.Attr[Company | None] = aod.Attr("fetch")

	class Company:
		pass

	assert Person.employer.type == Company | None
