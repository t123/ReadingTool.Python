import unittest, uuid

from lib.services.service import LanguageService, UserService, TermService, ItemService
from lib.models.model import User, Language, Term, Item, ItemType
from lib.misc import Application
from lib.db import Db

class TestIteService(unittest.TestCase):
    def setUp(self):
        self.db = Db(Application.connectionString)
        self.userService = UserService()
        self.languageService = LanguageService()
        self.termService = TermService()
        self.itemService = ItemService()
        self.user = User()
        self.user.username = str(uuid.uuid1())
        self.user = self.userService.save(self.user)
        self.language = Language()
        self.languageService.save(self.language)
        
        Application.user = self.user
        
    def test_can_save_item(self):
        language = Language()
        language = self.languageService.save(language)
        item = Item()
        item.l1LanguageId = language.languageId
        item = self.itemService.save(item)
        self.assertGreaterEqual(item.itemId, 1, "item.itemId>=1")

    def test_can_get_item_by_id(self):
        language = Language()
        language = self.languageService.save(language)
        item = Item()
        item.l1LanguageId = language.languageId
        item = self.itemService.save(item)
        self.assertGreaterEqual(item.itemId, 1, "item.itemId>=1")
        fetched = self.itemService.findOne(item.itemId)
        self.assertEqual(item.itemId, fetched.itemId, "item.itemId==fetched.itemId")

    def test_can_fetch_result_columns(self):
        l1 = Language()
        l2 = Language()
        l1.name = "language1"
        l2.name = "language2"
        l1 = self.languageService.save(l1)
        l2 = self.languageService.save(l2)
        
        item = Item()
        item.l1LanguageId = l1.languageId
        item.l2LanguageId = l2.languageId
        item = self.itemService.save(item)
        
        fetched = self.itemService.findOne(item.itemId)
        self.assertEqual(fetched.l1Language, "language1", "item.Language1==language1")
        self.assertEqual(fetched.l2Language, "language2", "item.Language2==language2")
        
if __name__ == '__main__':
    unittest.main()
