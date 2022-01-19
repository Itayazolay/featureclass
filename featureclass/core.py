from __future__ import annotations

import copy
import inspect
from dataclasses import make_dataclass
from functools import update_wrapper
from typing import Any, Callable, Generic, Mapping, Optional, Tuple, Type, TypeVar, Union, cast, get_type_hints

from featureclass.cached_property import cached_property  # type: ignore[attr-defined]

T = TypeVar("T")


ON_ERROR = Union[Callable[[Any, str, Exception], Any], Any]

_FEATURES = "__featureclass_features__"


_raise_error = object()


def featureclass(cls: Type[T]) -> Type[T]:
    """
    Returns the same class as was passed in, with dunder methods
    added based on the features defined in the class.
    This sets internal featureclass attributes and update __annotations__ fields in the class
    """

    def is_feature(prop: Any) -> bool:
        return isinstance(prop, Feature)

    features = tuple(f for _, f in inspect.getmembers(cls, is_feature))
    setattr(cls, _FEATURES, features)
    if not hasattr(cls, "__annotations__"):
        setattr(cls, "__annotations__", {})

    cls.__annotations__.update({f.name: f.type for f in features})
    return cls


def feature_annotations(class_or_instance: Any) -> Mapping[str, Type[Any]]:
    """Return annotations for feature attributes only."""
    try:
        features = getattr(class_or_instance, _FEATURES)
    except AttributeError:
        raise TypeError("must be called with a featureclass or a featureclass instance")

    return {f.name: f.type for f in features}


def feature_names(class_or_instance: Any) -> Tuple[str, ...]:
    """
    Return the feature names.
    This is not garanteed to be the function name that defines the feature.
    """
    try:
        features = getattr(class_or_instance, _FEATURES)
    except AttributeError:
        raise TypeError("must be called with a featureclass or a featureclass instance")

    return tuple(f.name for f in features)


def asdict(obj: Any, *, deepcopy: bool = False) -> Mapping[str, Any]:
    """
    Return the feature values of the obj as a dictionary.
    use deepcopy to deepcopy the internal values.
    """
    if deepcopy:
        cp = copy.deepcopy
        return {k: cp(getattr(obj, k)) for k in feature_names(obj)}
    return {k: getattr(obj, k) for k in feature_names(obj)}


def as_dataclass(class_or_instance: Union[Type[T], T], deepcopy: bool = False) -> Union[Type[T], T]:
    """
    Dynamically create the dataclass that defines this object.
    If an object is passed, returns an initated dataclass, otherwise return the defenition only.
    """
    try:
        features: Tuple[Feature[Any], ...] = getattr(class_or_instance, _FEATURES)
    except AttributeError:
        raise TypeError("must be called with a featureclass or a featureclass instance")

    def _make(cls: Type[T]) -> Type[T]:
        return make_dataclass(
            cls.__name__,
            fields=[(feature.name, feature.type) for feature in features],
        )

    if inspect.isclass(class_or_instance):
        return _make(cast(Type[T], class_or_instance))
    else:
        cls = cast(Type[T], class_or_instance.__class__)

        return _make(cls)(**asdict(class_or_instance, deepcopy=deepcopy))


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
                res = on_error(instance, self.attrname, err)
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
