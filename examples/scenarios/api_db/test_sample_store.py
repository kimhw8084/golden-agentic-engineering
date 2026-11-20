import unittest

from sample_store import add_sample, create_store


class SampleStoreContractTests(unittest.TestCase):
    def setUp(self):
        self.db = create_store()

    def test_success_and_duplicate_contract(self):
        self.assertEqual(add_sample(self.db, 'S-1', 2.5)['status'], 201)
        self.assertEqual(add_sample(self.db, 'S-1', 3.0), {'status': 409, 'error': 'sample_id already exists'})

    def test_validation_error_contract(self):
        self.assertEqual(add_sample(self.db, ' ', 1)['status'], 400)
        self.assertEqual(add_sample(self.db, 'S-2', -1)['status'], 422)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM sample').fetchone()[0], 0)


if __name__ == '__main__':
    unittest.main()
