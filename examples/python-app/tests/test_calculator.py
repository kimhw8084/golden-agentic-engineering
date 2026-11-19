import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from calculator import difference

class CalculatorTests(unittest.TestCase):
    def test_difference(self):
        self.assertEqual(difference(7, 3), 4)
