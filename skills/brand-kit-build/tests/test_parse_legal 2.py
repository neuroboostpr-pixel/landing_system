"""Tests for parse_legal — reading legal: section from brand-kit.md."""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

import unittest
import tempfile
import textwrap
from parse_legal import parse_legal_from_brand_kit


class TestParseLegal(unittest.TestCase):

    def _write(self, content):
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8')
        f.write(content)
        f.close()
        self.addCleanup(os.unlink, f.name)
        return f.name

    def test_parses_full_legal_section(self):
        """T1: парсит все 7 полей."""
        p = self._write(textwrap.dedent("""
            # Brand Kit

            ## Colors
            primary: #ff0000

            ## Legal
            ```yaml
            company_name: 'ООО "Ромашка"'
            entity_type: 'ООО'
            inn: '7700123456'
            ogrn: '1234567890123'
            legal_address: '123456, Москва, ул. Тверская, 1'
            contact_email: 'info@romashka.ru'
            dpo_email: 'info@romashka.ru'
            ```
        """).strip())
        result = parse_legal_from_brand_kit(p)
        self.assertEqual(result['company_name'], 'ООО "Ромашка"')
        self.assertEqual(result['inn'], '7700123456')
        self.assertEqual(result['ogrn'], '1234567890123')
        self.assertEqual(result['legal_address'], '123456, Москва, ул. Тверская, 1')
        self.assertEqual(result['contact_email'], 'info@romashka.ru')
        self.assertEqual(result['dpo_email'], 'info@romashka.ru')
        self.assertEqual(result['entity_type'], 'ООО')

    def test_returns_none_if_no_legal_section(self):
        """T2: возвращает None если секции Legal нет."""
        p = self._write("# Brand Kit\n\n## Colors\nprimary: #ff0000\n")
        result = parse_legal_from_brand_kit(p)
        self.assertIsNone(result)

    def test_returns_partial_with_todo_marker_if_placeholder_values(self):
        """T3: если есть TODO_LEGAL — помечает в result['_incomplete']=True."""
        p = self._write(textwrap.dedent("""
            ## Legal
            ```yaml
            # TODO_LEGAL: заполнить до прод-деплоя
            company_name: 'TODO_LEGAL'
            entity_type: 'TODO_LEGAL'
            inn: 'TODO_LEGAL'
            ogrn: 'TODO_LEGAL'
            legal_address: 'TODO_LEGAL'
            contact_email: 'TODO_LEGAL'
            dpo_email: 'TODO_LEGAL'
            ```
        """).strip())
        result = parse_legal_from_brand_kit(p)
        self.assertTrue(result['_incomplete'])

    def test_raises_if_file_not_found(self):
        """T4: бросает FileNotFoundError если brand-kit.md отсутствует."""
        with self.assertRaises(FileNotFoundError):
            parse_legal_from_brand_kit('/nonexistent/brand-kit.md')

    def test_returns_none_if_malformed_yaml(self):
        """T5: malformed YAML внутри Legal-блока → None + log warning."""
        p = self._write(textwrap.dedent("""
            ## Legal
            ```yaml
            company_name: [unclosed list
            ```
        """).strip())
        result = parse_legal_from_brand_kit(p)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
