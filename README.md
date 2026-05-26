# aod

`AttrOnDemand` — a descriptor for instance attributes whose values are
determined on demand on first access.

## Installation

```bash
pip install aod
```

Requires Python 3.12 or later (uses PEP 695 generic syntax).

## Usage

The name of the method that will set the attribute values can be passed
to the constructor. Several attributes can share the same fetch method, so
a single call can populate them all at once:

```python
from aod import AttrOnDemand

class Person:
	firstname = AttrOnDemand[str]("fetch")
	lastname = AttrOnDemand[str]("fetch")

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

Use `AttrOnDemand.known(instance)` to check whether a value has already
been computed without triggering a fetch.

Note that using `AttrOnDemand` descriptors only works for instances that
have instance dictionaries.

## License

MIT — see [LICENSE](LICENSE).
