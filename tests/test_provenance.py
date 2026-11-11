"""Trace emitted records to the exact inputs and preserve honest legacy states."""
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ukl import read_output, to_graph


class ProvenanceTests(unittest.TestCase):
    def test_offline_run_records_exact_evidence_without_claiming_a_model(self):
        source = ROOT / 'examples/domain_samples/manufacturing_process.txt'
        pack = ROOT / 'domain_packs/manufacturing_process.json'
        fixture = ROOT / 'examples/domain_samples/manufacturing_process.model.json'
        with tempfile.TemporaryDirectory() as work:
            output = pathlib.Path(work) / 'result.json'
            subprocess.run([
                sys.executable, str(ROOT / 'ukl.py'),
                '--domain', 'manufacturing_process', '--input', str(source),
                '--fixture', str(fixture), '--output', str(output),
            ], check=True, capture_output=True, text=True)
            result = read_output(output)
        provenance = result['provenance']
        self.assertEqual(provenance['source_sha256'], hashlib.sha256(source.read_text(encoding='utf-8').encode('utf-8')).hexdigest())
        self.assertEqual(provenance['domain_pack_sha256'], hashlib.sha256(pack.read_bytes()).hexdigest())
        self.assertEqual(provenance['execution_mode'], 'fixture')
        self.assertFalse(provenance['prompt_executed'])
        self.assertEqual(provenance['status'], 'FIXTURE_NOT_MODEL')
        self.assertIsNone(provenance['model_id'])
        self.assertIsNone(provenance['model_revision'])
        self.assertEqual(len(provenance['prompt_sha256']), 64)
        self.assertEqual(len(provenance['runtime_config_sha256']), 64)
        self.assertTrue(result['records'])
        for record in result['records']:
            self.assertEqual(record['provenance'], provenance)
            self.assertEqual(record['source']['sha256'], provenance['source_sha256'])
        graph = to_graph(result)
        self.assertTrue(any(node.get('provenance') == provenance for node in graph['nodes'] if node['type'] == 'record'))

    def test_legacy_output_is_read_without_inventing_missing_model_evidence(self):
        legacy = {'version': '0.1.0', 'source_id': 'legacy',
                  'records': [{'id': 'legacy:0', 'source': {'sha256': 'existing'}}]}
        with tempfile.TemporaryDirectory() as work:
            path = pathlib.Path(work) / 'old.json'
            path.write_text(json.dumps(legacy), encoding='utf-8')
            migrated = read_output(path)
        self.assertEqual(migrated['provenance'], {'status': 'LEGACY_UNVERIFIED'})
        self.assertEqual(migrated['records'][0]['provenance'], {'status': 'LEGACY_UNVERIFIED'})
        self.assertEqual(migrated['records'][0]['source']['sha256'], 'existing')
        self.assertNotIn('model_id', migrated['records'][0]['provenance'])


if __name__ == '__main__':
    unittest.main()
