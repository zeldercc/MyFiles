import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Overwrite/scripts'))
from generate import FILES, Invalid, load, render, routing, verify_outputs
from check_upstream import publication_problems


class GenerationTests(unittest.TestCase):
    def setUp(self):
        self.source = load((ROOT / 'Overwrite/tests/fixtures/source-baseline.yaml').read_text())
        self.base = json.loads((ROOT / 'Overwrite/tests/fixtures/base.json').read_text())

    def run_js(self, script, base):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d); (d / 'script.js').write_text(script); (d / 'base.json').write_text(json.dumps(base))
            result = subprocess.run(['node', str(ROOT / 'Overwrite/tests/run_js.cjs'), str(d / 'script.js'), str(d / 'base.json')],
                                    text=True, capture_output=True, timeout=10)
            if result.returncode: raise Invalid('JavaScript 执行失败')
            return json.loads(result.stdout)

    def test_fixed_filenames_and_roundtrip(self):
        outputs = render(self.source)
        self.assertEqual(set(outputs), set(FILES.values())); verify_outputs(self.source, outputs)

    def test_current_source_is_valid(self):
        current = load((ROOT / 'Overwrite/source/routing.yaml').read_text())
        verify_outputs(current, render(current))

    def test_deterministic(self):
        self.assertEqual(render(self.source), render(copy.deepcopy(self.source)))

    def test_migration_preserves_original_rules_and_provider_data(self):
        for platform, filename in FILES.items():
            original = (ROOT / 'Overwrite/tests/fixtures' / filename).read_text()
            if platform == 'clash':
                original = json.loads(original[original.index('var routing = ') + 14:original.index('\n  var groups')].strip().rstrip(';'))
            elif platform == 'openclash':
                original = {k.lstrip('+'): v for k, v in load(original.split('[YAML]\n', 1)[1]).items()}
            else:
                original = load(original)
            actual = routing(self.source, platform)
            self.assertEqual(actual['rules'], original['rules'])
            self.assertEqual(actual['rule-providers'], original['rule-providers'])
            self.assertEqual(actual.get('proxy-groups', []), original.get('proxy-groups', []))
            if platform != 'clash': self.assertEqual(actual.get('dns'), original.get('dns'))

    def test_add_rule_all_platforms(self):
        self.source['rules'].insert(0, {'id': 'test_added', 'type': 'DOMAIN', 'value': 'added.example', 'target': 'direct'})
        render(self.source)
        for p in FILES: self.assertEqual(routing(self.source, p)['rules'][0], 'DOMAIN,added.example,DIRECT')

    def test_delete_rule_all_platforms(self):
        removed = self.source['rules'].pop(0)
        render(self.source)
        for p in FILES: self.assertFalse(any(removed['value'] in r for r in routing(self.source, p)['rules']))

    def test_delete_service_prunes_unused_provider(self):
        self.source['rules'] = [r for r in self.source['rules'] if not (r['type'] == 'RULE-SET' and r['value'] == 'Nvidia')]
        render(self.source)
        for p in FILES: self.assertNotIn('Nvidia', routing(self.source, p)['rule-providers'])

    def test_modify_rule_removes_old_target_from_generated_and_js(self):
        self.source['rules'][0]['target'] = 'direct'
        output = render(self.source)
        actual = self.run_js(output[FILES['clash']], self.base)
        self.assertIn('DOMAIN,stun6.chat.bilibili.com,DIRECT', actual['rules'])
        self.assertNotIn('DOMAIN,stun6.chat.bilibili.com,REJECT', actual['rules'])

    def test_empty_rules_and_groups(self):
        self.source['rules'] = []; self.source['groups'] = []
        outputs = render(self.source); verify_outputs(self.source, outputs)
        result = self.run_js(outputs[FILES['clash']], self.base)
        self.assertEqual(result['rules'], self.base['rules'])
        for p in FILES: self.assertEqual(routing(self.source, p)['rule-providers'], {})

    def test_js_preserves_base_and_dns(self):
        result = self.run_js(render(self.source)[FILES['clash']], self.base)
        self.assertEqual(result['proxies'], self.base['proxies'])
        self.assertEqual(result['rules'][-2:], self.base['rules'])
        self.assertEqual(result['dns']['nameserver'], ['1.1.1.1'])
        self.assertEqual(result['dns']['enhanced-mode'], 'fake-ip')

    def test_js_same_version_idempotent(self):
        script = render(self.source)[FILES['clash']]
        once = self.run_js(script, self.base)
        self.assertEqual(self.run_js(script, once), once)

    def test_js_missing_target_rejected(self):
        self.base['proxy-groups'] = []
        with self.assertRaises(Invalid): self.run_js(render(self.source)[FILES['clash']], self.base)

    def test_new_generation_from_original_removes_deleted_rule(self):
        self.run_js(render(self.source)[FILES['clash']], self.base)
        self.source['rules'].pop(0)
        updated = self.run_js(render(self.source)[FILES['clash']], self.base)
        self.assertNotIn('DOMAIN,stun6.chat.bilibili.com,REJECT', updated['rules'])

    def test_unknown_field_rejected(self):
        self.source['rules'][0]['targte'] = 'direct'
        with self.assertRaises(Invalid): render(self.source)

    def test_duplicate_yaml_key_rejected(self):
        with self.assertRaises(Invalid): load('rules: []\nrules: []\n')

    def test_yaml_alias_rejected(self):
        with self.assertRaises(Invalid): load('a: &a []\nb: *a\n')

    def test_duplicate_id_rejected(self):
        self.source['rules'][1]['id'] = self.source['rules'][0]['id']
        with self.assertRaises(Invalid): render(self.source)

    def test_missing_provider_rejected(self):
        del self.source['providers']['Nvidia']
        with self.assertRaises(Invalid): render(self.source)

    def test_missing_group_rejected(self):
        self.source['groups'] = []
        # Known managed group remains a target alias, so removal must be detected.
        with self.assertRaises(Invalid): render(self.source)

    def test_invalid_cidr_rejected(self):
        self.source['rules'][1]['value'] = '192.168.18.1/24'
        with self.assertRaises(Invalid): render(self.source)

    def test_duplicate_rule_rejected(self):
        rule = copy.deepcopy(self.source['rules'][0]); rule['id'] = 'duplicate'; self.source['rules'].append(rule)
        with self.assertRaises(Invalid): render(self.source)

    def test_unvalidated_rule_type_rejected(self):
        self.source['rules'][0]['type'] = 'SUB-RULE'
        with self.assertRaises(Invalid): render(self.source)

    def test_provider_path_collision_rejected(self):
        self.source['providers']['Nvidia']['path'] = self.source['providers']['GoogleVoice']['path']
        with self.assertRaises(Invalid): render(self.source)

    def test_malformed_js_base_rejected(self):
        self.base['rules'] = 'not-an-array'
        with self.assertRaises(Invalid): self.run_js(render(self.source)[FILES['clash']], self.base)

    def test_publication_requires_native_acceptance(self):
        registry = json.loads((ROOT / 'Overwrite/compatibility/verified.json').read_text())
        registry['publication_policy'] = {'mode': 'native_required'}
        for item in registry['native_acceptance'].values(): item['accepted'] = False
        self.assertGreaterEqual(len(publication_problems(registry)), 4)

    def test_openclash_official_merger(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            from generate import yaml
            override = {('+' + k): v for k, v in routing(self.source, 'openclash').items()}
            (temp / 'base.json').write_text(json.dumps(self.base))
            (temp / 'override.yaml').write_text(yaml.safe_dump(override, allow_unicode=True))
            code = "require 'yaml'; require 'json'; require ARGV[0]; puts JSON.generate(YAML.overwrite(JSON.parse(File.read(ARGV[1])), YAML.load(File.read(ARGV[2]))))"
            result = subprocess.run(['ruby', '-e', code, str(ROOT / 'Overwrite/compatibility/vendor/OpenClash-YAML.rb'), str(temp / 'base.json'), str(temp / 'override.yaml')], text=True, capture_output=True, check=True, timeout=10)
            merged = json.loads(result.stdout)
            self.assertEqual(merged['rules'], routing(self.source, 'openclash')['rules'] + self.base['rules'])
            self.assertEqual(merged['proxies'], self.base['proxies'])
            names = [g['name'] for g in merged['proxy-groups']]
            self.assertEqual(len(names), len(set(names)))


if __name__ == '__main__': unittest.main()
