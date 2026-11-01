"""Behavioral checks for evidence preservation and the personalized domain boundaries."""
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ukl import load_domain, normalize, build_prompt

REGISTRY = json.loads((ROOT / 'config' / 'domain_registry.json').read_text(encoding='utf-8'))


class DomainProfileTests(unittest.TestCase):
    def test_every_domain_has_a_grounded_synthetic_example(self):
        for entry in REGISTRY['domains']:
            domain_id = entry['id']
            with self.subTest(domain=domain_id):
                source = (ROOT / 'examples' / 'domain_samples' / (domain_id + '.txt')).read_text(encoding='utf-8')
                model = json.loads((ROOT / 'examples' / 'domain_samples' / (domain_id + '.model.json')).read_text(encoding='utf-8'))
                pack = load_domain(domain_id)
                result = normalize(model, source, pack, 'synthetic:' + domain_id)
                self.assertEqual(len(result['records']), 1)
                self.assertFalse(result['rejected'])
                item = result['records'][0]
                self.assertEqual(source[item['source']['start']:item['source']['end']], item['source']['quote'])
                self.assertEqual(item['label'], model['records'][0]['label'])
                self.assertEqual(result['review_required'], pack['requires_review'])

    def test_semiconductor_capex_is_not_earnings(self):
        doc = '架空の企業Aは設備投資計画を公表した。'
        action = {'kind':'action','label':'announce_capex','quote':'設備投資計画を公表した',
                  'subject':'架空の企業A','object':None,'status':'performed','parameters':{}}
        a = normalize({'records':[action]},doc,load_domain('semiconductor_capex'),'s')
        b = normalize({'records':[action]},doc,load_domain('equity_research'),'s')
        self.assertEqual(len(a['records']),1)
        self.assertEqual(b['rejected'][0]['reasons'], ['unregistered_action'])

    def test_uncertainty_and_rejection_stay_separate(self):
        text = '新しい工程の原因は不明であり、来週試作する予定だ。'
        model = {'records':[{'kind':'action','label':'run_trial','quote':'来週試作する予定だ',
                             'subject':None,'object':None,'status':'planned','parameters':{}},
                            {'kind':'action','label':'run_trial','quote':'原因が判明した',
                             'subject':None,'object':None,'status':'performed','parameters':{}}]}
        result=normalize(model,text,load_domain('manufacturing_process'),'s')
        self.assertEqual(result['records'][0]['status'],'planned')
        self.assertIn('quote_not_in_source', result['rejected'][0]['reasons'])

    def test_prompts_use_domain_pack_not_shared_action_union(self):
        prompt=build_prompt('テキスト',load_domain('game_systems'))
        self.assertIn('test_late_join',prompt[0]['content'])
        self.assertNotIn('report_earnings',prompt[0]['content'])

if __name__ == '__main__':
    unittest.main()
