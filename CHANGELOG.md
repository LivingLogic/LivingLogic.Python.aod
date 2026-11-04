# ChangeLog

## 0.3.0 (2026-11-04)

The type of an attribute can now be given in an annotation
(`firstname: aod.Attr[str] = aod.Attr("fetch")`) instead of as a type
parameter. Annotations are evaluated lazily, so they may refer to classes
that are defined later in the module.

Added the property `Attr.type` that returns the type of the attribute (from
the type parameter or the annotation; `typing.Any` for an untyped attribute).

`Attr.__set_name__()` now records the owner class in `Attr.owner`.

Python 3.14 is required now.


## 0.2.0 (2026-06-01)

Renamed `AttrOnDemand` to `Attr`: Using the fully qualified name `aod.Attr` is
still shorter then using `AttrOnDemand` and sufficiently distinct.


## 0.1.1 (2026-05-26)

Fixed project URLs.


## 0.1.0 (2026-05-26)

Initial release.
