import typing, inspect


class Attr[T]:
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

	:class:`!Attr` can be used like this:

	.. sourcecode:: python

		import aod

		class Person:
			firstname: aod.Attr[str] = aod.Attr("fetch")
			lastname: aod.Attr[str] = aod.Attr("fetch")

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

	The type of the attribute can be given in the annotation (as above) or as
	a type parameter (``firstname = aod.Attr[str]("fetch")``). Both spellings
	tell type checkers that ``person.firstname`` is a ``str``. Prefer the
	annotation: it declares the attribute, so ``Person.firstname`` is an
	``Attr[str]`` for type checkers too (with the type parameter alone they
	also take the assignments in the fetch method as declarations, so
	``Person.firstname`` becomes ``Attr[str] | str``). An attribute without
	either is simply untyped. The annotation is evaluated lazily (on the first
	access to :attr:`type`), so it may refer to classes that are defined after
	the class that contains the attribute.

	:attr:`type` returns the type of the attribute, which allows code that
	derives something from the attributes of a class (e.g. serialization
	models) to find out their types.

	Compared to :class:`functools.cached_property` an :class:`!Attr` is
	declared in one line without a function body, and one fetch method can
	set any number of attributes at once (e.g. all columns of a database row),
	whereas each ``cached_property`` computes exactly one value in its own
	function.

	An attribute can also be declared without a fetch method
	(``dbid: aod.Attr[int] = aod.Attr()``). Its value is always set
	explicitly (e.g. in ``__init__``), and reading it before it has been set
	raises an :exc:`AttributeError`. For on-demand loading such an attribute
	is pointless, but it is declared like the others, so :attr:`type`,
	:meth:`known` and code that inspects the attributes of a class treat it
	the same way. The same :exc:`AttributeError` is raised when the fetch
	method didn't set the attribute.

	Note that using :class:`!Attr` descriptors only work for instances
	that have instance dictionaries.
	"""

	owner: type
	public_attr_name: str
	private_attr_name: str

	def __init__(self, fetch_method_name: str | None = None):
		self.fetch_method_name = fetch_method_name

	def __repr__(self) -> str:
		parts = [f"{self.__class__.__module__}.{self.__class__.__qualname__}"]
		if "public_attr_name" in self.__dict__: # Set by `__set_name__`
			parts.append(f"public_attr_name={self.public_attr_name!r}")
		parts.append(f"fetch_method_name={self.fetch_method_name!r}")
		parts.append(f"at {id(self):#x}")
		return f"<{' '.join(parts)}>"

	def __set_name__(self, owner: type, name: str) -> None:
		self.owner = owner
		self.public_attr_name = name
		self.private_attr_name = f"_{name}"

	@typing.overload
	def __get__(self, instance: None, type: type | None = None, /) -> Attr[T]: ...
	@typing.overload
	def __get__(self, instance: object, type: type | None = None, /) -> T: ...
	def __get__(self, instance, type=None):
		if instance is not None:
			if self.private_attr_name not in instance.__dict__:
				message = f"{instance.__class__.__qualname__!r} object has no attribute {self.public_attr_name!r}"
				if self.fetch_method_name is not None:
					getattr(instance, self.fetch_method_name)()
					message += f" after calling the method {self.fetch_method_name!r}"
				if self.private_attr_name not in instance.__dict__:
					raise AttributeError(message, name=self.public_attr_name, obj=instance)
			return instance.__dict__[self.private_attr_name]
		else:
			return self

	def __set__(self, instance: object, value: T) -> None:
		setattr(instance, self.private_attr_name, value)

	def __delete__(self, instance: object) -> None:
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

	@property
	def type(self) -> typing.Any:
		"""
		The type of the attribute.

		This is the ``T`` from the type parameter ``Attr[T](...)``, else the
		``T`` from the annotation ``name: Attr[T]`` of the owner class, else the
		annotation itself, else :data:`typing.Any` (for an unannotated
		attribute).

		The annotation is evaluated on first use (and the result cached), so
		it may refer to classes that are defined after the owner class.
		"""
		if "_type" not in self.__dict__:
			orig = getattr(self, "__orig_class__", None)
			if orig is not None:
				self._type = typing.get_args(orig)[0]
			else:
				# Evaluates lazy annotations (PEP 649) as well as string
				# annotations (``from __future__ import annotations``)
				annotations = inspect.get_annotations(self.owner, eval_str=True)
				annotation = annotations.get(self.public_attr_name, typing.Any)
				origin = typing.get_origin(annotation)
				if isinstance(origin, type) and issubclass(origin, Attr): # also subclasses of Attr
					annotation = typing.get_args(annotation)[0]
				self._type = annotation
		return self._type


# For backwards compatibility
AttrOnDemand = Attr
