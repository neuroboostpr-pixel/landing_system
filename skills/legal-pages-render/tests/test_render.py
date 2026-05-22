"""Tests for legal-pages render — substituting brand-kit reqs into HTML templates."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

import unittest
import tempfile

from render import render_template, render_policy, render_consent


class TestRender(unittest.TestCase):

    def _legal(self, **overrides):
        base = {
            'company_name': 'ООО "Ромашка"',
            'entity_type': 'ООО',
            'inn': '7700123456',
            'ogrn': '1234567890123',
            'legal_address': '123456, Москва, ул. Тверская, 1',
            'contact_email': 'info@romashka.ru',
            'dpo_email': 'info@romashka.ru',
            'effective_date': '2026-05-21',
            'last_updated': '2026-05-21',
            '_incomplete': False,
        }
        base.update(overrides)
        return base

    def test_substitutes_all_placeholders(self):
        tpl = "Operator: {{company_name}} (ИНН {{inn}}, ОГРН {{ogrn}})\nAddr: {{legal_address}}\nContact: {{contact_email}}, DPO: {{dpo_email}}"
        result = render_template(tpl, self._legal())
        self.assertIn('ООО "Ромашка"', result)
        self.assertIn('7700123456', result)
        self.assertIn('1234567890123', result)
        self.assertIn('123456, Москва, ул. Тверская, 1', result)
        self.assertIn('info@romashka.ru', result)
        self.assertNotIn('{{', result)
        self.assertNotIn('}}', result)

    def test_raises_if_legal_incomplete(self):
        with self.assertRaises(RuntimeError):
            render_template("{{company_name}}", self._legal(_incomplete=True))

    def test_raises_if_required_field_missing(self):
        legal = self._legal()
        del legal['inn']
        with self.assertRaises(KeyError):
            render_template("ИНН: {{inn}}", legal)

    def test_render_policy_loads_template_from_disk(self):
        result = render_policy(self._legal())
        self.assertIn('Политика обработки персональных данных', result)
        self.assertIn('ООО "Ромашка"', result)
        self.assertIn('7700123456', result)
        self.assertNotIn('{{', result)

    def test_render_consent_loads_template_from_disk(self):
        result = render_consent(self._legal())
        self.assertIn('Согласие', result)
        self.assertIn('ООО "Ромашка"', result)
        self.assertIn('152-ФЗ', result)
        self.assertNotIn('{{', result)


if __name__ == '__main__':
    unittest.main()
