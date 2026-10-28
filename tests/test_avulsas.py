import os
import tempfile
import unittest
from app.planilhas import ler_chaves_avulsas, valida_chave

class AvulsasTest(unittest.TestCase):
    def test_validacao_deduplicacao_e_avisos(self):
        base = '4324011234567800019065001000000001100000001'
        chave = next(base + str(n) for n in range(10) if valida_chave(base + str(n)))
        with tempfile.TemporaryDirectory() as pasta:
            with open(os.path.join(pasta, 'Maria.txt'), 'w', encoding='utf-8') as f:
                f.write(chave + '\n' + chave + '\n123\n')
            [arquivo] = ler_chaves_avulsas(pasta)
            self.assertEqual([n.chave for n in arquivo.notas], [chave])
            self.assertEqual(arquivo.notas[0].modelo, '65')
            self.assertIn('1 linha', arquivo.avisos[0])

if __name__ == '__main__':
    unittest.main()
