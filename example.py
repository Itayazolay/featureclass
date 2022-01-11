from featureclass import feature, featureclass, feature_names, feature_annotations
from typing_extensions import get_type_hints
from typing import List
from random import randint


@featureclass
class MyFeatures:
    @feature()
    def feature_1(self) -> int:
        """generate random number"""
        return randint(0,10)

    @feature()
    def feature_2(self) -> int:
        """generate random number"""
        return randint(0,10) + self.feature_1
    
    @feature()
    def feature_list(self) -> List[int]:
        """generate random of size 5"""
        return [randint(0,10)+self.feature_1+self.feature_2 for i in range(5)]


if __name__ == '__main__':
    myf = MyFeatures()
    from statistics import stdev
    print("feature_1", myf.feature_1)
    print("cached", myf.feature_1 == myf.feature_1)