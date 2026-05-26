import typing

class AttrOnDemand[T]:
	"""
	A descriptor for an instance attribute whose value is determined on demand.

	When the attribute is first accessed a user specified "fetch" method will be
	called that should set the attribute value. This fetch method may also set
	other attribute values. After an attribute is set a second attribute
	access will not trigger the fetch method again.

	This avoids calculating expensive attribute values when they aren't needed
	(like a real attribute would) and it avoids calculating expensive attribute
	values more than once if the values is accessed more than once (like a
	`property` would).

	:class:`!AttrOnDemand` can be used like this:

	.. sourcecode:: python

		import aod

		class Person:
			firstname = aod.AttrOnDemand[str]("fetch")
			lastname = aod.AttrOnDemand[str]("fetch")

			def __init__(self, dbid):
				self.dbid = dbid

			def fetch(self):
				cursor = db.cursor()
				cursor.execute("select firstname, lastname from person where id=:id", id=self.dbid)
				row = cursor.fetchone()
				self.firstname = row.firstname
				self.lastname = row.lastname

		print(Person(42).firstname)

	Internally the value of an attribute ``foo`` will be stored in the instance
	dictionary as ``_foo``. As long as the value hasn't been set yet, ``_foo``
	will not be in the instance dictionary, and accessing the attribute will call
	the fetch method. The setter simply sets ``_foo`` in the instance dictionary,
	so the fetch method should set the attribute value via the setter.

	Note that using :class:`!AttrOnDemand` descriptors only work for instances
	that have instance dictionaries.
	"""
	def __init__(self, fetch_method_name: str):
		self.fetch_method_name = fetch_method_name
		self.public_attr_name = None
		self.private_attr_name = None

	def __repr__(self) -> str:
		return f"<{self.__class__.__module__}.{self.__class__.__qualname__} public_attr_name={self.public_attr_name!r} fetch_method_name={self.fetch_method_name!r} at {id(self):x}>"

	def __set_name__(self, owner, name):
		self.public_attr_name = name
		self.private_attr_name = f"_{name}"

	@typing.overload
	def __get__(self, instance: None, type: type | None = None, /) -> "AttrOnDemand[T]": ...
	@typing.overload
	def __get__(self, instance: object, type: type | None = None, /) -> T: ...
	def __get__(self, instance, type=None):
		if instance is not None:
			if self.private_attr_name not in instance.__dict__:
				getattr(instance, self.fetch_method_name)()
			return getattr(instance, self.private_attr_name)
		else:
			return self

	def __set__(self, instance: object, value: T):
		setattr(instance, self.private_attr_name, value)

	def __delete__(self, instance: object):
		"""
		Forget the value of the attribute.

		The next access will fetch the value again.
		"""
		instance.__dict__.pop(self.private_attr_name, None)

	def known(self, instance: object) -> bool:
		"""
		Return whether the attribute is known in the instance ``instance``.

		This returns whether the appropriate key is in the instance dict.
		"""
		return self.private_attr_name in instance.__dict__
