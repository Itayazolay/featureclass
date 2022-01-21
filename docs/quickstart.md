# Quickstart
First let's import featureclass
```python
from featureclass import featureclass, feature
```

We'll define a a simple class with one init var called datapoint and two methods on this function.


```python
from typing import List
from statistics import var
from math import sqrt

@featureclass
class Features:
  def __init__(self, datapoint: List[float]):
    self.datapoint = datapoint
  
  @feature()
  def var(self) -> float:
    return var(self.datapoint)
   
  @feature()
  def stdev(self) -> float:
    return sqrt(self.var)
  
```
`feature` behaves like python's `property`, so when calling the function, no need to add `()`.

Now we created a `featureclass` with two features, `var` and `stdev`.
Each `feature` is cached, so it is only calculated the first time it is called.
Note that during object initialization the feature functions are NOT called. 

```python
from random import random

@featureclass
class Features:
  @feature()
  def randnum(self):
    return random()
    
inst = Features()
assert inst.randnum == inst.randnum
```

## Exception handling

Features might fail, in this case we can define either a constant value to return, or an exception handler to callback with the exception value

```python
import logging

logger = logging.getLogger()


def error_callback(instance: "Features", feature_name: str, err: Exception):
  logger.exception("Exception was raised", err, 
                   extra={"feature_name": feature_name, "instanceid": instance.instanceid})
  return None  # Can be any value, can also re-raise the exception.


@featureclass
class Features:
  def __init__(self, instanceid):
    self.instanceid = instanceid
    
  @feature()
  def err_raise(self) -> None:
    raise ValueError("This function raises a ValueError")
   
   @feature(on_error=None)
   def err_default(self) -> Optional[float]:
    raise ValueError("None should be returned and the exception will be silenced")
   
   @feature(on_error=float("inf")
   def err_default_inf(self) -> float:
    raise ValueError("float('inf') should be returned and this error is slienced")
    
   @feature(on_error=error_callback):
   def err_log_and_None(self) -> Optional[float]:
    raise ValueError("None should be returned from the on_error callback")
 
 
inst = Features("UniqueIdentifier")
try: 
  inst.err_raise
except ValueError:
  pass  # Exception raised

assert inst.err_default is None
assert inst.err_default_inf == float('inf')
assert inst.err_log_and_None == None  # and error is logged
```

## Exporting the data

We can export the featureclass values using either `asdict` as `as_dataclass`.
Note that this triggers the calculation of *all* the features that haven't been calculated yet.
`as_dataclass` can also take the class itself, and in this case return a dataclass that can be used to define all the features in the featureclass

```python
from featureclass import asdict, as_dataclass, featureclass, feature
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
        
print(asdict(MyFeatures([1,2,3,4,5]))) # {'var': 2.5, 'stdev': 1.5811388300841898}
print(as_dataclass(MyFeatures([1,2,3,4,5]))) # MyFeatures(stdev=1.5811388300841898, var=2.5)
```
