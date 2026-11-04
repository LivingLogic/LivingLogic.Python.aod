# aod

`Attr` — a descriptor for instance attributes whose values are
determined on demand on first access.

## Installation

```bash
pip install aod
```

Requires Python 3.14 or later (uses lazily evaluated annotations, PEP 649).

## Usage

The name of the method that will set the attribute values can be passed
to the constructor. Several attributes can share the same fetch method, so
a single call can populate them all at once:

```python
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

p = Person(42)
print(p.firstname)   # triggers fetch, sets both firstname and lastname
print(p.lastname)    # already known, no fetch
```

Internally the value of an attribute `foo` will be stored in the instance
dictionary as `_foo`. As long as the value hasn't been set yet, `_foo` will
not be in the instance dictionary, and accessing the attribute will call the
fetch method. The setter simply sets `_foo` in the instance dictionary, so
the fetch method should set the attribute values via the setter.

Deleting an attribute forgets its cached value; the next access will fetch
it again:

```python
del p.firstname
print(p.firstname)   # fetches again (and refreshes lastname too)
```

Use `Attr.known(instance)` to check whether a value has already
been computed without triggering a fetch.

Note that using `Attr` descriptors only works for instances that
have instance dictionaries.

## Types

The type of an attribute can be given in the annotation (as above) or as a
type parameter:

```python
class Person:
	firstname: aod.Attr[str] = aod.Attr("fetch")   # annotation
	lastname = aod.Attr[str]("fetch")              # type parameter
	nickname = aod.Attr("fetch")                   # untyped
```

Both spellings tell type checkers that `p.firstname` is a `str`. Prefer the
annotation: it declares the attribute, so `Person.firstname` is an
`Attr[str]` and `Person.firstname.known(p)` type checks. With the type
parameter alone, a type checker also takes the assignments in the fetch
method as declarations of the attribute, so `Person.lastname` becomes
`Attr[str] | str` and `Person.lastname.known(p)` is an error.

`Attr.type` returns the type of the attribute (`typing.Any` for an untyped
one). The annotation is evaluated on the first access to `Attr.type`, so it
may refer to classes that are defined after the class containing the
attribute:

```python
class Person:
	employer: aod.Attr[Company | None] = aod.Attr("fetch")

class Company:
	...

print(Person.employer.type)   # Company | None
```

`Attr.type` is meant for code that derives something from the attributes
of a class, e.g. serialization models, documentation or forms.

## License

MIT — see [LICENSE](LICENSE).
