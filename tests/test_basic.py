import time
import unittest
from dataclasses import fields

from featureclass import asDataclass, asDict, feature, feature_annotations, feature_names, featureclass


@featureclass
class MyFeatures:
    a: int

    def __init__(self) -> None:
        self.a = 0

    @feature()
    def feature_1(self) -> int:
        return 2 ** 2

    @feature()
    def feature_2(self) -> int:
        return self.feature_1 ** 2

    @feature()
    def now(self) -> float:

        return time.time()

    @feature()
    def inc(self) -> int:
        self.a += 1
        return self.a


class TestBasic(unittest.TestCase):
    def setUp(self) -> None:
        self.cls = MyFeatures

        self.inst = MyFeatures()

        return super().setUp()

    def test_feature_names(self) -> None:
        self.assertSetEqual(
            set(feature_names(self.cls)),
            {"feature_1", "feature_2", "now", "inc"},
        )
        self.assertSetEqual(
            set(feature_names(self.inst)),
            {"feature_1", "feature_2", "now", "inc"},
        )

    def test_annotations(self) -> None:
        self.assertDictEqual(
            feature_annotations(self.cls),
            {"feature_1": int, "feature_2": int, "now": float, "inc": int},
        )
        self.assertDictEqual(
            feature_annotations(self.inst),
            {"feature_1": int, "feature_2": int, "now": float, "inc": int},
        )
        self.assertDictEqual(
            {"feature_1": int, "feature_2": int, "now": float, "inc": int, "a": int}, self.inst.__annotations__
        )

        self.assertDictEqual(
            {"feature_1": int, "feature_2": int, "now": float, "inc": int, "a": int}, self.cls.__annotations__
        )

    def test_cache_not_shared(self) -> None:
        a = self.cls()
        b = self.cls()
        self.assertEqual(a.now, a.now)
        self.assertNotEqual(b.now, a.now)
        self.assertEqual(b.now, b.now)

    def test_cache(self) -> None:
        a = self.cls()
        b = self.cls()
        self.assertEqual(a.inc, 1)
        self.assertEqual(b.inc, 1)
        self.assertEqual(a.inc, 1)
        self.assertEqual(b.inc, 1)

    def test_asDict(self) -> None:
        a = self.inst
        d = asDict(a)
        self.assertSetEqual(set(feature_names(a)), set(d.keys()))
        self.assertEqual(d["inc"], 1)

    def test_asDataclass(self) -> None:
        a = self.inst
        dc = asDataclass(a)
        self.assertSetEqual(set(f.name for f in fields(dc)), set(feature_names(a)))
        self.assertDictEqual({f.name: f.type for f in fields(dc)}, feature_annotations(a))

        b = self.cls
        dc = asDataclass(b)

        self.assertSetEqual(set(f.name for f in fields(dc)), set(feature_names(b)))
        self.assertDictEqual({f.name: f.type for f in fields(dc)}, feature_annotations(b))


if __name__ == "__main__":
    unittest.main()
