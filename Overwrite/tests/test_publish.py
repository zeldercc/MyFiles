import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Overwrite/scripts'))
import publish
from generate import FILES, load, render


class PublishTests(unittest.TestCase):
    def command(self, folder, *args):
        return subprocess.check_output(['git', '-C', str(folder), *args], text=True, stderr=subprocess.DEVNULL).strip()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.repo = self.folder / 'repo'; self.repo.mkdir()
        self.remote = self.folder / 'remote.git'
        subprocess.run(['git', 'init', '--bare', str(self.remote)], check=True, capture_output=True)
        self.command(self.repo, 'init', '-b', 'main')
        self.command(self.repo, 'config', 'user.name', 'Local Test')
        self.command(self.repo, 'config', 'user.email', 'local-test@example.invalid')
        self.command(self.repo, 'remote', 'add', 'origin', str(self.remote))
        source = self.repo / 'Overwrite/source/routing.yaml'; source.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / 'Overwrite/source/routing.yaml', source)
        compat = self.repo / 'Overwrite/compatibility/verified.json'; compat.parent.mkdir(parents=True)
        registry = json.loads((ROOT / 'Overwrite/compatibility/verified.json').read_text())
        registry['publication_policy'] = {'mode': 'automated_checks_only', 'native_tests_skipped_by_user': True, 'reason': 'unit test explicit opt-out'}
        compat.write_text(json.dumps(registry))
        self.outputs = render(load(source.read_text()))
        build = self.repo / '.build/Overwrite'; build.mkdir(parents=True)
        for name, content in self.outputs.items():
            (build / name).write_text(content)
            shutil.copyfile(ROOT / 'Overwrite/tests/fixtures' / name, self.repo / 'Overwrite' / name)
        (self.repo / '.gitignore').write_text('.build/\n')
        self.command(self.repo, 'add', '.')
        self.command(self.repo, 'commit', '-m', 'initial fixture')
        self.command(self.repo, 'push', 'origin', 'main')
        self.initial = self.command(self.repo, 'rev-parse', 'HEAD')

    def urlopen(self, request, **kwargs):
        name = request.full_url.rsplit('/', 1)[-1]
        return io.BytesIO(self.outputs[name].encode())

    def test_all_four_fixed_files_published_in_one_commit(self):
        with patch.object(publish, 'ROOT', self.repo), patch.dict(os.environ, {'GITHUB_REPOSITORY': 'local/test'}), patch.object(publish.urllib.request, 'urlopen', side_effect=self.urlopen):
            publish.main()
        current = self.command(self.repo, 'rev-parse', 'HEAD')
        self.assertNotEqual(current, self.initial)
        changed = self.command(self.repo, 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD').splitlines()
        self.assertEqual(set(changed), {'Overwrite/' + name for name in FILES.values()})
        remote = subprocess.check_output(['git', '--git-dir', str(self.remote), 'rev-parse', 'main'], text=True).strip()
        self.assertEqual(current, remote)

    def test_stale_run_cannot_overwrite_newer_main(self):
        newer = self.folder / 'newer'
        subprocess.run(['git', 'clone', '-b', 'main', str(self.remote), str(newer)], check=True, capture_output=True)
        self.command(newer, 'config', 'user.name', 'Local Test')
        self.command(newer, 'config', 'user.email', 'local-test@example.invalid')
        (newer / 'newer.txt').write_text('new commit')
        self.command(newer, 'add', 'newer.txt'); self.command(newer, 'commit', '-m', 'newer source state'); self.command(newer, 'push', 'origin', 'main')
        with patch.object(publish, 'ROOT', self.repo):
            with self.assertRaises(ValueError): publish.main()
        self.assertEqual(self.command(self.repo, 'rev-parse', 'HEAD'), self.initial)


if __name__ == '__main__': unittest.main()
