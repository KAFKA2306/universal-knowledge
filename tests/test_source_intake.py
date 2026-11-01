import copy
import hashlib
import json
import unittest
from pathlib import Path
from scripts.source_intake import collect_feed, intake, validate, ROOT

class IntakeTest(unittest.TestCase):
    def setUp(self):
        self.catalog=json.loads((ROOT/'config/source_registry.json').read_text(encoding='utf-8'))
        self.domains={x['id'] for x in json.loads((ROOT/'config/domain_registry.json').read_text(encoding='utf-8'))['domains']}
        self.feed=self.catalog['feeds'][0]
        self.xml=b'''<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>   New    release </title><link href="https://github.com/ggml-org/llama.cpp/releases/tag/b100" rel="alternate"/><updated>2026-11-01T00:00:00Z</updated><summary>not collected</summary></entry><entry><title>bad host</title><link rel="alternate" href="https://bad.example/release"/></entry></feed>'''
    def test_catalog(self):
        self.assertEqual(len(validate(self.catalog,self.domains)['sources']),12)
    def test_filter_and_no_body(self):
        items=collect_feed(self.feed,lambda _:self.xml)
        self.assertEqual(len(items),1)
        self.assertEqual(items[0]['title'],'New release')
        self.assertNotIn('summary',items[0])
    def test_idempotence(self):
        c=copy.deepcopy(self.catalog)
        intake(c,lambda _:self.xml)
        self.assertEqual(len(c['candidates']),1)
        intake(c,lambda _:self.xml)
        self.assertEqual(len(c['candidates']),1)
        validate(c,self.domains)
    def test_reject_unknown_domain(self):
        c=copy.deepcopy(self.catalog)
        c['sources'][0]['domain']='unregistered'
        with self.assertRaises(ValueError): validate(c,self.domains)
    def test_reject_malicious_url(self):
        c=copy.deepcopy(self.catalog)
        c['sources'][0]['url']='http://169.254.169.254/metadata'
        with self.assertRaises(ValueError): validate(c,self.domains)
    def test_fail_closed_if_feed_unavailable(self):
        def fail(_): raise OSError('offline')
        with self.assertRaises(RuntimeError): intake(copy.deepcopy(self.catalog),fail)

if __name__=='__main__': unittest.main()
