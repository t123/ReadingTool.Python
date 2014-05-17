import sqlite3
    
class Db:
    def __init__(self, connectionString = ':memory:'):
        self.conn = sqlite3.connect(connectionString, isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        pass
    
    def commit(self):
        self.conn.commit()
        
    def rollback(self):
        self.conn.rollback()
        
    def script(self, sql):
        cursor = self.conn.cursor()
        cursor.executescript(sql)
        cursor.close()
        
    def execute(self, sql, *a, **ka):
        cursor = self.conn.cursor()
        ret = None
        
        if ka:
            cursor.execute(sql, ka)
        else:
            cursor.execute(sql, a)
            
        if sql.startswith("INSERT"):
            ret = self.scalar("SELECT last_insert_rowid()")
            
        cursor.close()
        return ret
    
    def list(self, sql, *a, **ka):
        result = None
        cursor = self.conn.cursor()
        
        if ka:
            result = cursor.execute(sql, ka).fetchall()
        else:
            result = cursor.execute(sql, a).fetchall()
            
        cursor.close()
        
        return [row[0] for row in result if row is not None]
    
    def scalar(self, sql, *a, **ka):
        cursor = self.conn.cursor()
        result = None
        
        if ka:
            result = cursor.execute(sql, ka).fetchone()
        else:
            result = cursor.execute(sql, a).fetchone()
            
        cursor.close()
        
        if result:
            return result[0]
        
        return None;
        
    def many(self, cls, sql, *a, **ka):
        result = None
        cursor = self.conn.cursor()
        
        if ka:
            result = cursor.execute(sql, ka).fetchall()
        else:
            result = cursor.execute(sql, a).fetchall()
            
        cursor.close()
        
        return [self._mapRowToObject2(cls(), row) for row in result]

    def one(self, cls, sql, *a, **ka):
        result = None
        cursor = self.conn.cursor()
        
        if ka:
            result = cursor.execute(sql, ka).fetchone()
        else:
            result = cursor.execute(sql, a).fetchone()
            
        cursor.close()
        return self._mapRowToObject2(cls(), result)
        
    def _mapRowToObject2(self, obj, result):
        if not result:
            return None
        
        for column in result.keys():
            val = result[column]
            
            #print("Col=%s Val=%s" % (column,val))
            
            if hasattr(obj, column):
                setattr(obj, column, val)
        
        return obj