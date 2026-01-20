import unittest
import unittest.mock
import os
import shutil
import json
from credential_manager import CredentialManager

class TestCredentialManager(unittest.TestCase):
    def setUp(self):
        # Use a temporary directory for tests
        self.test_dir = os.path.join(os.path.dirname(__file__), "tmp_aria")
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
        # Patch CredentialManager to use test_dir
        self.patcher = unittest.mock.patch('os.path.expanduser', return_value=self.test_dir)
        self.patcher.start()
        
        # We need to re-initialize or mock the paths in CredentialManager if it's already imported
        # but since we are creating it here, it should be fine if it calls expanduser in __init__
        self.cm = CredentialManager()

    def tearDown(self):
        self.patcher.stop()
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_set_and_get_credential(self):
        self.cm.set_credential("test_key", "test_value")
        self.assertEqual(self.cm.get_credential("test_key"), "test_value")

    def test_list_keys(self):
        self.cm.set_credential("key1", "val1")
        self.cm.set_credential("key2", "val2")
        keys = self.cm.list_keys()
        self.assertIn("key1", keys)
        self.assertIn("key2", keys)
        self.assertEqual(len(keys), 2)

    def test_remove_credential(self):
        self.cm.set_credential("to_remove", "value")
        self.assertTrue(self.cm.remove_credential("to_remove"))
        self.assertIsNone(self.cm.get_credential("to_remove"))
        self.assertFalse(self.cm.remove_credential("non_existent"))

if __name__ == "__main__":
    unittest.main()
