from featureclass import featureclass, feature_names, feature, feature_annotations
import unittest


class TestBasic(unittest.TestCase):
    def setUp(self) -> None:
        @featureclass
        class MyFeatures:
            @feature()
            def feature_1(self) -> int:
                return 2**2

            @feature()
            def feature_2(self) -> int:
                return self.feature_1**2

        self.feature_cls = MyFeatures

        return super().setUp()

    def test_feature_names(self):
        self.assertEqual(feature_names(self.feature_cls), ('feature_1', 'feature_2'))

    def test_annotations(self):
        self.assertEqual(feature_annotations(self.feature_cls), {'feature_1': int, 'feature_2': int})

if __name__ == "__main__":
    unittest.main()