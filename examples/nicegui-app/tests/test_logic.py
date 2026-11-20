import unittest

from app.logic import make_measurement


class MeasurementLogicTests(unittest.TestCase):
    def test_inclusive_acceptance_limits(self):
        self.assertTrue(make_measurement('S-1', 0, 0, 10).accepted)
        self.assertTrue(make_measurement('S-1', 10, 0, 10).accepted)

    def test_out_of_range_is_review(self):
        self.assertFalse(make_measurement('S-2', 10.1, 0, 10).accepted)

    def test_validation_errors(self):
        for args in [('', 1, 0, 2), ('S-1', 1, 3, 2), ('S-1', float('nan'), 0, 2)]:
            with self.assertRaises(ValueError):
                make_measurement(*args)


if __name__ == '__main__':
    unittest.main()
