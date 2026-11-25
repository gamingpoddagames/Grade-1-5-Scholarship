import unittest
from sinhala_speech import expand_currency

class CurrencyTests(unittest.TestCase):
    def test_currency(self):
        self.assertEqual(expand_currency("රු. 5,000"), "රුපියල් 5,000")
        self.assertEqual(expand_currency("රු.4500"), "රුපියල් 4500")
        self.assertEqual(expand_currency("රු. 10 සහ රු. 20"), "රුපියල් 10 සහ රුපියල් 20")
    def test_preserve(self):
        self.assertEqual(expand_currency("රුපියල් 500"), "රුපියල් 500")
        self.assertEqual(expand_currency("20%"), "20%")
