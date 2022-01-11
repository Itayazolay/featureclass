# featureclass
Feature engineering library that helps you keep track of feature dependencies, documentation and schema  

This library helps define a featureclass.  
featureclass is inspired by dataclass, and is meant to provide alternative way to define features engineering classes.  

I have noticed that the below code is pretty common when doing feature engineering:  

```python
from statistics import variance
from math import sqrt
class MyFeatures:
    def calc_all(self, datapoint):
        out = {}
        out['var'] = self.calc_var(datapoint),
        out['stdev'] = self.calc_std(out['var'])
        return out
        
    def calc_var(self, data) -> float:
        return variance(data)

    def calc_stdev(self, var) -> float:
        return sqrt(var)
```

Some things were missing for me from this type of implementation:  
1. Implicit dependencies between features  
2. No simple schema  
3. No documentation for features  
4. Duplicate declaration of the same feature - once as a function and one as a dict key  

This is why I created this library.  
I turned the above code into this:  
```python
from featureclass import feature, featureclass, feature_names, feature_annotations, asDict, asDataclass
from statistics import variance
from math import sqrt

@featureclass
class MyFeatures:
    def __init__(self, datapoint):
        self.datapoint = datapoint
    
    @feature()
    def var(self) -> float:
        """Calc variance"""
        return variance(self.datapoint)

    @feature()
    def stdev(self) -> float:
        """Calc stdev"""
        return sqrt(self.var)

print(feature_names(MyFeatures)) # ('var', 'stdev')
print(feature_annotations(MyFeatures)) # {'var': float, 'stdev': float}
print(asDict(MyFeatures([1,2,3,4,5]))) # {'var': 2.5, 'stdev': 1.5811388300841898}
print(asDataclass(MyFeatures([1,2,3,4,5]))) # MyFeatures(stdev=1.5811388300841898, var=2.5)

```

The feature decorator is using cached_property to cache the feature calculation,   
making sure that each feature is calculated once per datapoint
