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
    def test_invalid_entry_does_not_discard_valid_feed_entries(self):
        xml=b'''<feed xmlns="http://www.w3.org/2005/Atom">
          <entry><title>bad URL</title><link rel="alternate" href="http://invalid.example/item"/></entry>
          <entry><title>valid release</title><link rel="alternate" href="https://github.com/ggml-org/llama.cpp/releases/tag/b101"/></entry>
        </feed>'''
        items=collect_feed(self.feed,lambda _:xml)
        self.assertEqual(len(items),1)
        self.assertEqual(items[0]['title'],'valid release')
        c=copy.deepcopy(self.catalog)
        c['candidates'] = []  # Isolate this parser regression from online intake state.
        intake(c,lambda _:xml)
        self.assertEqual(len(c['candidates']),1)
        validate(c,self.domains)

    def test_idempotence(self):
        c=copy.deepcopy(self.catalog)
        c['candidates'] = []  # Existing live proposals must not affect idempotence.
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


    def test_workflow_shell_syntax(self):
        import shutil
        import subprocess
        if shutil.which('bash') is None:
            self.skipTest('bash is unavailable')
        lines = (ROOT / '.github/workflows/source-intake.yml').read_text(encoding='utf-8').splitlines()
        section = next(i for i, line in enumerate(lines) if line.strip() == '- name: Open review PR only when metadata changed')
        run = next(i for i in range(section + 1, len(lines)) if lines[i] == '        run: |')
        body = []
        for line in lines[run + 1:]:
            if line and not line.startswith('          '):
                break
            body.append(line[10:] if line else '')
        script = '\n'.join(body) + '\n'
        self.assertEqual(script.count('git switch -c "$branch"'), 1)
        result = subprocess.run(['bash', '-n'], input=script, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

if __name__=='__main__': unittest.main()
