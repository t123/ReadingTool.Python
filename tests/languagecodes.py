import unittest
import time

from lib.services.service import LanguageCodeService
from lib.models.model import LanguageCode

class TestLangugeCodeService(unittest.TestCase):
    def setUp(self):
        self.languageCodeService = LanguageCodeService()
        pass
        
    def test_can_fetch_all_language_codes(self):
        lc = self.languageCodeService.findAll()
        self.assertIsInstance(lc, list, 'List returned')
    
    def test_can_fetch_language_code_by_code(self):
        lc = self.languageCodeService.findOne('--')
        self.assertEqual(lc.code, '--', 'Code is --')
        self.assertEqual(lc.name, 'Not Set', 'Name is Not Set')
        
if __name__=='__main__':
    unittest.main()