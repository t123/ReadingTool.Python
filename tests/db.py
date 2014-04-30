import unittest
from lib.db import Db

class TestObject:
    def __init__(self):
        self.id = 0
        self.name = ""
        
class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Db()
        self.db.execute('CREATE TABLE testtable ( id INTEGER PRIMARY KEY, name VARCHAR ) ')
        pass
    
    def test_can_create_db_object(self):
        db = Db()
        self.assertIsNotNone(db, "Database is not None")
        
    def test_can_execute_sql(self):
        self.db.execute('SELECT * FROM "main".sqlite_master')
        self.db.commit()
        
    def test_can_execute(self):
        self.db.execute("INSERT INTO testtable ( id, name ) VALUES ( null, 'name')")
        self.db.execute("INSERT INTO testtable ( id, name ) VALUES ( null, ?)", 'name')
        self.db.execute("INSERT INTO testtable ( id, name ) VALUES ( null, :name)", name='name')
        self.db.commit()
        
    def test_can_fetch_one_object_by_id(self):
        id = self.db.execute("INSERT INTO testtable ( id, name ) VALUES ( null, 'name')")
        self.db.commit()
        obj = self.db.one(TestObject, "SELECT * from testtable WHERE id=?", id)
        
    def test_can_fetch_many_objects(self):
        for x in range(1000,1010):
            self.db.execute("INSERT INTO testtable ( id, name ) VALUES ( null, :name)", name="name"+ str(x))
        
        self.db.commit()
        objs = self.db.many(TestObject, "SELECT * FROM testtable WHERE name LIKE :name", name="name1%")
        self.assertEqual(10, len(objs), '10==len(Returned)')
        
        counter = 1000
        for obj in objs:
            self.assertEqual(obj.name, 'name%s' % counter, 'Name matches')
            counter += 1
            
    def test_can_fetch_one_by_unnamed(self):
        id = self.db.execute("INSERT INTO testtable ( id, name ) VALUES ( null, 'name')")
        self.db.commit()
        fetched = self.db.one(TestObject, "SELECT * FROM testtable WHERE id=?", id)
        self.assertIsNotNone(fetched , 'fetched is not none')
        self.assertEqual(fetched.name, 'name', 'name==name')
        
    def test_can_fetch_one_by_named(self):
        id = self.db.execute("INSERT INTO testtable ( id, name ) VALUES ( null, 'name')")
        self.db.commit()
        fetched = self.db.one(TestObject, "SELECT * FROM testtable WHERE id=:id", id=id)
        self.assertIsNotNone(fetched , 'fetched is not none')
        self.assertEqual(fetched.name, 'name', 'name==name')
        
    def test_can_fetch_scalar(self):
        self.db.execute("INSERT INTO testtable ( id, name ) VALUES ( null, 'name')")
        self.db.execute("INSERT INTO testtable ( id, name ) VALUES ( null, 'name')")
        self.db.execute("INSERT INTO testtable ( id, name ) VALUES ( null, 'name')")
        self.db.commit()
        result = self.db.scalar("SELECT COUNT(*) FROM testtable")
        self.assertIsNotNone(result, "Scalar fetched")
        self.assertEqual(result, 3, "Count==3")
        
if __name__=='__main__':
    unittest.main()