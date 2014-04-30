import unittest, uuid

from lib.services.service import UserService
from lib.models.model import User, Language

class TestUserService(unittest.TestCase):
    def setUp(self):
        self.userService = UserService()

    def test_can_save_user(self):
        user = User()
        user.username = str(uuid.uuid1())
        original = self.userService.save(user)      
        self.assertGreater(original.userId, 0, "UserId is >0")
    
    def test_can_get_user_by_id(self):
        user = User()
        user.username = str(uuid.uuid1())
        user = self.userService.save(user)
        saved = self.userService.findOne(user.userId)
        self.assertEqual(user.userId, saved.userId, "Saved UserId==Original UserId")
        
    def test_can_update_user(self):
        user = User()
        username = str(uuid.uuid1())
        user.username = username
        user = self.userService.save(user)
        self.assertEqual(user.username, username, "Name is UUID")
        username2 = str(uuid.uuid1())
        user.username = username2
        user = self.userService.save(user)
        saved = self.userService.findOne(user.userId)
        self.assertEqual(user.username, saved.username, "Updated username")
        
    def test_can_fetch_missing_object(self):
        user = self.userService.findOne(-1)
        self.assertIsNone(user, "User==None")
        
if __name__=='__main__':
    unittest.main()