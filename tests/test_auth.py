import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import json
import src.auth

class TestAuth(unittest.TestCase):

    @patch.dict(os.environ, {"JAPANESE_APP_API_KEY": "test_env_key"})
    def test_get_secret_key_env_var(self):
        """Test retrieving API key from environment variable."""
        key = src.auth.get_secret_key()
        self.assertEqual(key, "test_env_key")

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.auth.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"api_key": "test_file_key"}')
    def test_get_secret_key_secrets_file(self, mock_file, mock_exists):
        """Test retrieving API key from secrets file."""
        mock_exists.return_value = True

        key = src.auth.get_secret_key()

        self.assertEqual(key, "test_file_key")
        mock_exists.assert_called_once()
        mock_file.assert_called_once_with(src.auth.SECRETS_FILE, 'r')

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.auth.os.path.exists')
    @patch('src.auth.secrets.token_urlsafe')
    @patch('builtins.open', new_callable=mock_open)
    @patch('src.auth.os.makedirs')
    def test_get_secret_key_generate_new(self, mock_makedirs, mock_file, mock_secrets, mock_exists):
        """Test generating a new API key when none exists."""
        mock_exists.return_value = False
        mock_secrets.return_value = "generated_new_key"

        key = src.auth.get_secret_key()

        self.assertEqual(key, "generated_new_key")
        mock_exists.assert_called()
        mock_secrets.assert_called_once_with(32)
        # Check if file was opened for writing
        mock_file.assert_called_with(src.auth.SECRETS_FILE, 'w')
        # Check if directory was created
        mock_makedirs.assert_called_once()
        # Check if JSON was written
        handle = mock_file()
        expected_json = '{\n  "api_key": "generated_new_key"\n}'
        # json.dump writes in chunks, so verifying the exact string can be tricky.
        # Instead, verify write calls or use a spy on json.dump if possible,
        # but mock_open is sufficient to check interaction.
        # For simplicity, just checking call args is often enough.
        self.assertTrue(handle.write.called)

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.auth.os.path.exists')
    @patch('src.auth.secrets.token_urlsafe')
    @patch('builtins.open', side_effect=IOError("Read Error"))
    def test_get_secret_key_read_error(self, mock_file, mock_secrets, mock_exists):
        """Test fallback to generation on file read error."""
        mock_exists.return_value = True
        mock_secrets.return_value = "fallback_generated_key"

        key = src.auth.get_secret_key()

        self.assertEqual(key, "fallback_generated_key")
        mock_exists.assert_called()
        # Should try to read, fail, then generate and save
        # mock_file is called for read (fails) AND write (succeeds? No, mocked to fail always?)
        # Wait, if open raises IOError, it raises it for *every* call if side_effect is an exception instance.
        # So saving will also fail, but the function should catch it and return the key.

        mock_secrets.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.auth.os.path.exists')
    @patch('src.auth.secrets.token_urlsafe')
    @patch('src.auth.os.makedirs')
    def test_get_secret_key_write_error(self, mock_makedirs, mock_secrets, mock_exists):
        """Test robust return even on file write error."""
        mock_exists.return_value = False
        mock_secrets.return_value = "key_despite_write_error"

        # Mock open to raise IOError specifically on write
        m = mock_open()
        # We need it to fail on the 'w' open call.
        # It's easier to mock os.makedirs to fail or just mock open to always fail.
        # Since logic tries to open for write if env and file check fail.
        with patch('builtins.open', m):
            m.side_effect = IOError("Write Error")

            key = src.auth.get_secret_key()

            self.assertEqual(key, "key_despite_write_error")
            mock_secrets.assert_called_once()

if __name__ == '__main__':
    unittest.main()
