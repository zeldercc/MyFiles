import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Overwrite/scripts'))
import check_upstream


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads((ROOT / 'Overwrite/compatibility/verified.json').read_text())

    def test_new_upstream_version_blocks(self):
        with patch.object(check_upstream, 'latest', return_value='unreviewed-version'):
            with self.assertRaises(ValueError): check_upstream.check(self.registry)

    def test_upstream_network_failure_blocks(self):
        with patch.object(check_upstream, 'fetch', side_effect=RuntimeError('network unavailable')):
            with self.assertRaises(RuntimeError): check_upstream.check(self.registry)

    def test_normative_change_blocks(self):
        self.registry['versions'] = {}
        with patch.object(check_upstream, 'fetch', return_value=b'changed upstream content'):
            with self.assertRaises(ValueError): check_upstream.check(self.registry)

    def test_unrecorded_native_evidence_blocks(self):
        for item in self.registry['native_acceptance'].values():
            item.update(accepted=True, app_version='test', evidence_file='Overwrite/compatibility/evidence/nonexistent.json')
        self.assertTrue(check_upstream.publication_problems(self.registry))

    def test_native_evidence_path_traversal_blocks(self):
        for item in self.registry['native_acceptance'].values():
            item.update(accepted=True, app_version='test', evidence_file='../../outside.json')
        self.assertTrue(check_upstream.publication_problems(self.registry))

    def test_invalid_source_does_not_overwrite_existing_candidates(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp); out = temp / 'out'; out.mkdir()
            previous = out / 'clashmi-routing-overwrite.yaml'; previous.write_text('previous valid output')
            source = temp / 'invalid.yaml'; source.write_text('schema_version: 99\n')
            result = subprocess.run([sys.executable, str(ROOT / 'Overwrite/scripts/generate.py'), '--source', str(source), '--out', str(out)], text=True, capture_output=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(previous.read_text(), 'previous valid output')
            self.assertEqual(len(list(out.iterdir())), 1)


if __name__ == '__main__': unittest.main()
