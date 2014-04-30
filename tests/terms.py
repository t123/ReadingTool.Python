import unittest, time, uuid, time

from lib.services.service import LanguageService, UserService, TermService
from lib.models.model import User, Language, Term, TermType
from lib.misc import Application
from lib.db import Db

class TestTermService(unittest.TestCase):
    def setUp(self):
        self.db = Db(Application.connectionString)
        self.userService = UserService()
        self.languageService = LanguageService()
        self.termService = TermService()
        self.user = User()
        self.user.username = str(uuid.uuid1())
        self.user = self.userService.save(self.user)
        self.language = Language()
        self.languageService.save(self.language)
        
        Application.user = self.user
         
    def test_can_get_term_by_id(self):
        term = Term()
        term.languageId = self.language.languageId
        original = self.termService.save(term)
        saved = self.termService.findOne(original.termId)
        self.assertEqual(original.termId, saved.termId, "Saved termId==Original termId")
        
    def test_can_update_term(self):
        term = Term()
        term.languageId = self.language.languageId
        term = self.termService.save(term)
        self.assertEqual(term.basePhrase, "", "Name is empty")
        time.sleep(0.5)
        term.basePhrase = 'Bob'
        original = self.termService.save(term)
        saved = self.termService.findOne(original.termId)
        self.assertEqual(saved.basePhrase, term.basePhrase, "Updated basePhrase")
        self.assertGreater(saved.modified, term.created, "Modified>Created")
        
    def test_can_delete_term(self):
        term = Term()
        term.languageId = self.language.languageId
        term = self.termService.save(term)
        self.assertGreater(term.termId, 0, "Term is saved")
        self.termService.delete(term.termId)
        saved = self.termService.findOne(term.termId)
        self.assertIsNone(saved, "Term is deleted")
        
    def test_can_get_term_by_phrase_and_language(self):
        term = Term()
        term.phrase = "PHRASE"
        term.languageId = self.language.languageId
        original = self.termService.save(term)
        saved = self.termService.fineOneByPhraseAndLanguage("Phrase", self.language.languageId)
        self.assertEqual(original.termId, saved.termId, "Saved termId==Original termId")
        
    def test_can_save_term(self):
        term = Term()
        term.languageId = self.language.languageId
        original = self.termService.save(term)      
        saved = self.termService.findOne(original.termId)
        
        self.assertIsNotNone(term, "term is not None")
        self.assertGreater(saved.termId, 0, "termId is >0")
        self.assertEqual(original.termId, saved.termId, "Saved PK is retrieved PK")
        self.assertEqual(saved.userId, Application.user.userId, "term has Application UserId")
        self.assertGreaterEqual(saved.created, saved.modified, "Created and modified udpated")

    def test_term_log_entry_is_added_with_create(self):
        term = Term()
        term.languageId = self.language.languageId
        term = self.termService.save(term)      
        result = self.db.scalar("SELECT COUNT(*) as count FROM termlog WHERE termId=:termId AND type=:type", termId=term.termId, type=TermType.Create)
        self.assertEqual(result, 1, "Create entry found")
        
    def test_term_log_entry_is_added_with_update(self):
        term = Term()
        term.languageId = self.language.languageId
        term = self.termService.save(term)      
        result = self.db.scalar("SELECT COUNT(*) as count FROM termlog WHERE termId=:termId AND type=:type", termId=term.termId, type=TermType.Modify)
        self.assertEqual(result, 0, "Modify entry not found")
        term = self.termService.save(term)      
        result = self.db.scalar("SELECT COUNT(*) as count FROM termlog WHERE termId=:termId AND type=:type", termId=term.termId, type=TermType.Modify)
        self.assertEqual(result, 1, "Modify entry found")      
        
    def test_term_log_entry_is_added_with_delete(self):
        term = Term()
        term.languageId = self.language.languageId
        term = self.termService.save(term)      
        result = self.db.scalar("SELECT COUNT(*) as count FROM termlog WHERE termId=:termId AND type=:type", termId=term.termId, type=TermType.Delete)
        self.assertEqual(result, 0, "Delete entry not found")
        self.termService.delete(term.termId)      
        result = self.db.scalar("SELECT COUNT(*) as count FROM termlog WHERE termId=:termId AND type=:type", termId=term.termId, type=TermType.Delete)
        self.assertEqual(result, 1, "Delete entry found")

if __name__=='__main__':
    unittest.main()