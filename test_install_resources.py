import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('installer', Path(__file__).with_name('install_resources.py'))
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class BoundaryTests(unittest.TestCase):
    def test_rejects_private_and_withheld_paths(self):
        for value in ['../android/keystore.properties', '/data/index.json', 'data/../secret.json', 'data/user_progress.json', 'data/credentials.json', 'image/XinBian1/1.png', 'data/x.apk', 'data\\words.json', 'data/.env']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                installer.safe_resource_path(value)

    def test_accepts_public_course_and_dictionary(self):
        for value in ['data/grammar_index.json', 'data/textbook/canonical_books/KotobaFlow1.bundle.json', 'data/classics_v1/ise/index.json']:
            self.assertEqual(installer.safe_resource_path(value).as_posix(), value)

    def test_does_not_follow_a_linked_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            elsewhere = root / 'elsewhere'
            elsewhere.mkdir()
            target = root / 'target'
            target.mkdir()
            try:
                (target / 'data').symlink_to(elsewhere, target_is_directory=True)
            except OSError:
                self.skipTest('Directory symlinks are unavailable')
            with self.assertRaises(ValueError):
                installer.checked_destination(target, 'data/grammar.json')


if __name__ == '__main__':
    unittest.main()
