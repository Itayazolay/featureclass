from __future__ import annotations
import inspect
from typing import Tuple, Optional, Generic, Type, TypeVar, Callable, Union, get_type_hints, cast, Mapping, Any
from functools import lru_cache, update_wrapper
from collections import Mapping
from abc import ABCMeta

_raise_error = object()
cache = lru_cache(maxsize=1)

T = TypeVar("T")

class FeatureClass(ABCMeta):
    __features__: Tuple[Feature, ...]

FC = Union[Type[FeatureClass], FeatureClass]

def featureclass(cls: type) -> Type[FeatureClass]:
    def is_feature(prop) -> bool:
        return isinstance(prop, property) and isinstance(prop.fget, Feature)
    
    setattr(cls, "__features__", tuple(f.fget for _, f in inspect.getmembers(cls, is_feature)))
    return cls

def feature_annotations(cls_or_obj) -> Mapping[str, Type[Any]]:
    return {f.name: get_type_hints(f)['return'] for f in cls_or_obj.__features__}

def feature_names(cls_or_obj) -> Tuple[str, ...]:
    return tuple(f.name for f in cls_or_obj.__features__)


class Feature(Generic[T]):
    name: str

    def __init__(self, f: Callable[..., T], *, name: Optional[str] = None, on_error=_raise_error) -> None:
        self.__wrapped__ = cache(f)
        self.type = get_type_hints(f)['return']
        self.name = name or f.__name__
        self.on_error = on_error

    def __call__(self, self_) -> T:
        try:
            res = self.__wrapped__(self_)
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
        return cast(T, property(feature))
    return feature_wrapper
