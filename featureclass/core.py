from __future__ import annotations

import copy
import inspect
from dataclasses import make_dataclass
from functools import update_wrapper
from typing import Any, Callable, Generic, Mapping, Optional, Tuple, Type, TypeVar, Union, cast, get_type_hints

from featureclass.cached_property import cached_property  # type: ignore[attr-defined]

T = TypeVar("T")


ON_ERROR = Union[Callable[[Exception], Any], Any]


_raise_error = object()


def featureclass(cls: Type[T]) -> Type[T]:
    """
    Returns the same class as was passed in, with dunder methods
    added based on the features defined in the class.
    This sets __features__ and __annotations__ fields in the class
    """

    def is_feature(prop: Any) -> bool:
        return isinstance(prop, Feature)

    features = tuple(f for _, f in inspect.getmembers(cls, is_feature))
    setattr(cls, "__features__", features)
    if not hasattr(cls, "__annotations__"):
        setattr(cls, "__annotations__", {})

    cls.__annotations__.update({f.name: f.type for f in features})
    return cls


def feature_annotations(cls_or_obj: Any) -> Mapping[str, Type[Any]]:
    """Return annotations for feature attributes only."""
    return {f.name: f.type for f in cls_or_obj.__features__}


def feature_names(cls_or_obj: Any) -> Tuple[str, ...]:
    """
    Return the feature names.
    This is not garanteed to be the function name that defines the feature.
    """
    return tuple(f.name for f in cls_or_obj.__features__)


def asDict(obj: Any, *, deepcopy: bool = False) -> Mapping[str, Any]:
    """
    Return the feature values of the obj as a dictionary.
    use deepcopy to deepcopy the internal values.
    """
    if deepcopy:
        cp = copy.deepcopy
        return {k: cp(getattr(obj, k)) for k in feature_names(obj)}
    return {k: getattr(obj, k) for k in feature_names(obj)}


def asDataclass(cls_or_obj: Union[Type[T], T], deepcopy: bool = False) -> Union[Type[T], T]:
    """
    Dynamically create the dataclass that defines this object.
    If an object is passed, returns an initated dataclass, otherwise return the defenition only.
    """
    if not hasattr(cls_or_obj, "__features__"):
        raise TypeError("class or object is not a featureclass")

    def _make(cls: Type[T]) -> Type[T]:
        features = cls.__features__  # type: ignore[attr-defined]
        return make_dataclass(
            cls.__name__,
            fields=[(feature.name, feature.type) for feature in features],
        )

    if inspect.isclass(cls_or_obj):
        return _make(cast(Type[T], cls_or_obj))
    else:
        cls = cast(Type[T], cls_or_obj.__class__)

        return _make(cls)(**asDict(cls_or_obj, deepcopy=deepcopy))  # type: ignore[call-arg]


class Feature(Generic[T], cached_property):  # type: ignore[misc]
    name: str

    def __init__(self, f: Callable[..., T], *, name: Optional[str] = None, on_error: ON_ERROR = _raise_error) -> None:
        super().__init__(f)
        self.f = f
        self.type = get_type_hints(f).get("return", Any)
        self.name = name or f.__name__
        self.on_error = on_error

    def __get__(self, instance, owner=None) -> T:  # type: ignore[no-untyped-def]
        try:
            return cast(T, super().__get__(instance, owner))
        except Exception as err:
            on_error = self.on_error
            if on_error is _raise_error:
                raise
            elif callable(on_error):
                res = on_error(err)
            else:
                res = on_error
            return cast(T, res)


def feature(name: Optional[str] = None, on_error: ON_ERROR = _raise_error) -> Callable[[Callable[..., T]], T]:
    """
    Marks a function as a feature, which behaves like a cached property.
    Arguments:
        name: the name of the feature, defaults to the function name.
        on_error: Callable or value.
            if Callable, call it with the exception returned - on_error(exc),
            otherwise return it 'on_error' as-is.
            if not provided, raise the exception.
    """

    def feature_wrapper(f: Callable[..., T]) -> T:
        feature = Feature(f, name=name, on_error=on_error)
        update_wrapper(feature, f)
        return cast(T, feature)

    return feature_wrapper
