import unittest, time, uuid, time

from lib.services.service import LanguageService, UserService
from lib.models.model import User, Language
from lib.misc import Application

class TestLangugeService(unittest.TestCase):
    def setUp(self):
        self.userService = UserService()
        self.languageService = LanguageService()
        self.user = User()
        self.user.username = str(uuid.uuid1())
        self.user = self.userService.save(self.user)
        Application.user = self.user
         
    def test_can_save_language(self):
        language = Language()
        original = self.languageService.save(language)      
        saved = self.languageService.findOne(original.languageId)
        
        self.assertIsNotNone(language, "Language is not None")
        self.assertGreater(saved.languageId, 0, "LanguageId is >0")
        self.assertEqual(original.languageId, saved.languageId, "Saved PK is retrieved PK")
        self.assertEqual(saved.userId, Application.user.userId, "Language has Application UserId")
        self.assertGreaterEqual(saved.created, saved.modified, "Created and modified udpated")

    def test_can_get_language_by_id(self):
        language = Language()
        original = self.languageService.save(language)
        saved = self.languageService.findOne(original.languageId)
        self.assertEqual(original.languageId, saved.languageId, "Saved LanguageId==Original LanguageId")
        
    def test_can_update_language(self):
        language = Language()
        language = self.languageService.save(language)
        self.assertEqual(language.name, '', "Name is empty")
        time.sleep(0.5)
        language.name = 'Bob'
        original = self.languageService.save(language)
        saved = self.languageService.findOne(original.languageId)
        self.assertEqual(saved.name, language.name, "Updated name")
        self.assertGreater(saved.modified, language.created, "Modified>Created")      

if __name__=='__main__':
    unittest.main()