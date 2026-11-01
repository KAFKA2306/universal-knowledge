import json
import pathlib
import tempfile
import unittest
import sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ukl import load_settings
from scripts.validate_project import validate


class ConfigTests(unittest.TestCase):
    def test_all_versioned_packs_and_pipeline_validate(self):
        self.assertEqual(validate(), [])
        settings = load_settings(ROOT / 'config/pipeline.json')
        self.assertEqual(settings['inference']['provider'], 'local_openai_compatible')

    def test_non_loopback_endpoint_is_rejected_before_run(self):
        settings = json.loads((ROOT / 'config/pipeline.json').read_text(encoding='utf-8'))
        settings['inference']['base_url'] = 'https://example.com/api'
        with tempfile.TemporaryDirectory() as temp:
            path = pathlib.Path(temp) / 'settings.json'
            path.write_text(json.dumps(settings), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'loopback'):
                load_settings(path)

    def test_refuse_relaxation_of_evidence_policy(self):
        settings = json.loads((ROOT / 'config/pipeline.json').read_text(encoding='utf-8'))
        settings['outputs']['source_quotes_required'] = False
        with tempfile.TemporaryDirectory() as temp:
            path = pathlib.Path(temp) / 'settings.json'
            path.write_text(json.dumps(settings), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'evidence policy'):
                load_settings(path)
