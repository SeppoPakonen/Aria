import unittest
import os
import shutil
import tempfile
import zipfile
from unittest.mock import MagicMock, patch
import sys

class TestArtifactExport(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.aria_home = os.path.join(self.test_dir, ".aria")
        os.makedirs(self.aria_home)
        os.makedirs(os.path.join(self.aria_home, "reports"))
        os.makedirs(os.path.join(self.aria_home, "scripts"))
        
        # Create some dummy files
        with open(os.path.join(self.aria_home, "aria.log"), "w") as f:
            f.write("test log")
        with open(os.path.join(self.aria_home, "reports", "report1.md"), "w") as f:
            f.write("test report")
        with open(os.path.join(self.aria_home, "credentials.json"), "w") as f:
            f.write('{"secret": "val"}')
            
        self.patcher = patch('os.path.expanduser', return_value=self.test_dir)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        shutil.rmtree(self.test_dir)

    def test_export_artifacts(self):
        from aria import main
        import sys
        
        output_zip = os.path.join(self.test_dir, "test_out.zip")
        
        # Mock sys.argv
        with patch.object(sys, 'argv', ['aria', 'settings', 'export-artifacts', '--path', output_zip]):
            # Mock PluginManager to avoid loading real plugins
            with patch('aria.PluginManager') as mock_pm_class:
                mock_pm = mock_pm_class.return_value
                mock_pm.get_plugin_commands.return_value = []
                mock_pm.get_navigator.return_value = None
                mock_pm.context = {}
                
                main()
        
        self.assertTrue(os.path.exists(output_zip))
        
        # Verify zip contents
        with zipfile.ZipFile(output_zip, 'r') as zip_ref:
            filenames = zip_ref.namelist()
            self.assertIn('aria.log', filenames)
            self.assertIn('reports/report1.md', filenames)
            self.assertNotIn('credentials.json', filenames)

if __name__ == "__main__":
    unittest.main()
