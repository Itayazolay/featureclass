from __future__ import annotations
import inspect
from typing import Tuple, Optional, Generic, Type, TypeVar, Callable, Union, get_type_hints, cast, Mapping, Any
from typing_extensions import Protocol
from functools import lru_cache, update_wrapper
from collections import Mapping
from featureclass.cached_property import cached_property


_raise_error = object()
cache = lru_cache(maxsize=1)


T = TypeVar("T")


class FeatureClass(Protocol):
    __features__: Tuple[Feature, ...]


def featureclass(cls: Type[T]) -> Type[T]:
    def is_feature(prop) -> bool:
        return isinstance(prop, Feature)

    setattr(cls, "__features__", tuple(f for _, f in inspect.getmembers(cls, is_feature)))
    return cls


def feature_annotations(cls_or_obj) -> Mapping[str, Type[Any]]:
    return {f.name: f.type for f in cls_or_obj.__features__}


def feature_names(cls_or_obj) -> Tuple[str, ...]:
    return tuple(f.name for f in cls_or_obj.__features__)


class Feature(Generic[T], cached_property):
    name: str

    def __init__(self, f: Callable[..., T], *, name: Optional[str] = None, on_error=_raise_error) -> None:
        super().__init__(f)
        self.f = f
        self.type = get_type_hints(f).get('return', Any)
        self.name = name or f.__name__
        self.on_error = on_error
    

    def __get__(self ,instance, owner=None) -> T:  # type: ignore
        try:
            return super().__get__(instance, owner)
        except Exception as err:
            on_error = self.on_error
            if on_error is _raise_error:
                raise
            elif callable(on_error):
                res = on_error(err)
            else:    
                res = on_error
            return res


def feature(name: str = None, on_error=_raise_error) -> Callable[[Callable[..., T]], T]:
    def feature_wrapper(f: Callable[..., T]) -> T:
        feature = Feature(f, name=name, on_error=on_error)
        update_wrapper(feature, f)
        return cast(T, feature)

    return feature_wrapper
