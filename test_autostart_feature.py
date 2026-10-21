import sys
import unittest
from autostart import (
    is_auto_start_supported,
    get_launch_command,
    is_auto_start_enabled,
    set_auto_start,
    sync_auto_start_path,
)

class TestAutoStart(unittest.TestCase):
    def setUp(self):
        # Save initial auto start state
        self.initial_state = is_auto_start_enabled()

    def tearDown(self):
        # Restore initial state
        set_auto_start(self.initial_state)

    def test_support(self):
        if sys.platform == "win32":
            self.assertTrue(is_auto_start_supported())
        else:
            self.assertFalse(is_auto_start_supported())

    def test_launch_command(self):
        cmd = get_launch_command()
        self.assertIsInstance(cmd, str)
        self.assertTrue(cmd.startswith('"'))
        self.assertTrue(len(cmd) > 5)

    def test_enable_and_disable(self):
        if not is_auto_start_supported():
            return

        # Enable
        ok, msg = set_auto_start(True)
        self.assertTrue(ok)
        self.assertTrue(is_auto_start_enabled())

        # Test sync does not break enabled state
        sync_auto_start_path()
        self.assertTrue(is_auto_start_enabled())

        # Disable
        ok, msg = set_auto_start(False)
        self.assertTrue(ok)
        self.assertFalse(is_auto_start_enabled())

if __name__ == "__main__":
    unittest.main()
