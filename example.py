from featureclass import feature, featureclass, feature_names, feature_annotations
from typing_extensions import get_type_hints
from typing import List



@featureclass
class MyFeatures:
    def __init__(self, a: int, b: int) -> None:
        self.a = a
        self.b = b
    
    @feature()
    def feature_1(self) -> int:
        """This does shit"""
        return self.a**2

    @feature()
    def feature_2(self) -> int:
        return self.b**3 + self.feature_1
    
    @feature()
    def feature_list(self) -> List[int]:
        return list(range(5))

myf = MyFeatures(a=2, b=3)
print(feature_names(MyFeatures))
print(feature_names(myf))

# print(MyFeatures.feature_annotations())
# print(MyFeatures.to_model().schema_json(indent=2))
# print(myf.as_model())
# print(myf.data())