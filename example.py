from random import randint
from typing import List

from featureclass import feature, feature_annotations, feature_names, featureclass


@featureclass
class MyFeatures:
    a: int

    @feature()
    def feature_1(self) -> int:
        """generate random number"""
        return randint(0, 10)

    @feature()
    def feature_2(self) -> int:
        """generate random number"""
        return randint(0, 10) + self.feature_1

    @feature()
    def feature_list(self) -> List[int]:
        """generate random of size 5"""
        return [randint(0, 10) + self.feature_1 + self.feature_2 for i in range(5)]


if __name__ == "__main__":
    myf = MyFeatures()
    print("feature_1", myf.feature_1)
    print("cached", myf.feature_1 == myf.feature_1)
    print("feature_names:", feature_names(myf))
    print("feature_annoations:", feature_annotations(myf))
    print("__annotations__:", MyFeatures.__annotations__)
