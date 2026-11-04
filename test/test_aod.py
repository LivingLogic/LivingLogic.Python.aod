from __future__ import annotations

import typing

import aod


class Person:
	# All spellings of the type are tested: annotation, type parameter, none,
	# and a plain annotation. For a type checker only the first one works
	# cleanly (see the README), so the others are marked.
	firstname: aod.Attr[str] = aod.Attr("fetch")
	lastname = aod.Attr[str]("fetch")
	nickname = aod.Attr("fetch")
	plain: str = aod.Attr("fetch") # type: ignore
	employer: aod.Attr[Company | None] = aod.Attr("fetch")
	fetches = 0

	def __init__(self, dbid):
		self.dbid = dbid

	def fetch(self):
		self.fetches += 1
		self.firstname = "Walter"
		self.lastname = "Dörwald"
		self.nickname = None
		self.plain = "plain"
		self.employer = None


class Company:
	pass


# A subclass of `Attr` must work in annotations too (`test_type_attr_subclass`).
# Both classes are at module level because string annotations (we have
# `from __future__ import annotations`) are evaluated in the module namespace
# and can't see classes that are local to a test function.
class Field[T](aod.Attr[T]):
	pass


class Thing:
	name: Field[int] = Field("fetch")


def test_fetch_on_first_access():
	p = Person(42)
	assert not Person.firstname.known(p)
	assert p.firstname == "Walter"
	assert p.fetches == 1
	assert Person.lastname.known(p) # type: ignore
	assert p.lastname == "Dörwald"
	assert p.fetches == 1


def test_set_and_delete():
	p = Person(42)
	p.firstname = "W."
	assert p.firstname == "W."
	assert p.fetches == 0
	del p.firstname
	assert not Person.firstname.known(p)
	assert p.firstname == "Walter"
	assert p.fetches == 1
	del p.lastname # Deleting an unknown attribute is fine
	assert p.lastname == "Dörwald"
	assert p.fetches == 2


def test_class_access():
	assert isinstance(Person.firstname, aod.Attr)
	assert Person.firstname.owner is Person
	assert Person.firstname.public_attr_name == "firstname"
	assert Person.firstname.private_attr_name == "_firstname"
	assert Person.firstname.fetch_method_name == "fetch"
	assert "public_attr_name='firstname'" in repr(Person.firstname)
	assert "public_attr_name" not in repr(aod.Attr("fetch")) # Not in a class yet


def test_type():
	assert Person.firstname.type is str
	assert Person.lastname.type is str # type: ignore
	assert Person.nickname.type is typing.Any # type: ignore
	assert Person.plain.type is str # type: ignore
	assert Person.employer.type == Company | None # Forward reference, evaluated lazily


def test_type_attr_subclass():
	assert Thing.name.type is int


def test_backwards_compatibility():
	assert aod.AttrOnDemand is aod.Attr
