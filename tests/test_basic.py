from featureclass import featureclass, feature_names, feature, feature_annotations
import unittest
import time

class TestBasic(unittest.TestCase):
    def setUp(self) -> None:
        @featureclass
        class MyFeatures:
            def __init__(self):
                self.a = 0

            @feature()
            def feature_1(self) -> int:
                return 2**2

            @feature()
            def feature_2(self) -> int:
                return self.feature_1**2
            
            @feature()
            def now(self) -> float:
                return time.time()

            @feature()
            def inc(self) -> int:
                self.a+=1
                return self.a


        self.feature_cls = MyFeatures

        return super().setUp()

    def test_feature_names(self):
        self.assertSetEqual(set(feature_names(self.feature_cls)), {'feature_1', 'feature_2', 'now', 'inc'})

    def test_annotations(self):
        self.assertDictEqual(feature_annotations(self.feature_cls), {'feature_1': int, 'feature_2': int, 'now': float, 'inc': int})

    def test_cache_not_shared(self):
        a = self.feature_cls()
        b = self.feature_cls()
        self.assertEqual(a.now, a.now)
        self.assertNotEqual(b.now, a.now)
        self.assertEqual(b.now, b.now)

    def test_cache(self):
        a = self.feature_cls()
        b = self.feature_cls()
        self.assertEqual(a.inc, 1)
        self.assertEqual(b.inc, 1)
        self.assertEqual(a.inc, 1)
        self.assertEqual(b.inc, 1)


if __name__ == "__main__":
    unittest.main()