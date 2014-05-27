import sqlite3, uuid

#http://stackoverflow.com/a/18842491/215538
sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: memoryview(u.bytes_le))
    
class Db:
    def __init__(self, connectionString = ':memory:', isolationLevel=None):
        self.conn = sqlite3.connect(connectionString, isolation_level=isolationLevel, detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn.row_factory = sqlite3.Row
    
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
        
        if ka:
            cursor.execute(sql, ka)
        else:
            cursor.execute(sql, a)
            
        cursor.close()
    
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
        
        return [self._mapRowToObject(cls(), row) for row in result]

    def one(self, cls, sql, *a, **ka):
        result = None
        cursor = self.conn.cursor()
        
        if ka:
            result = cursor.execute(sql, ka).fetchone()
        else:
            result = cursor.execute(sql, a).fetchone()
            
        cursor.close()
        return self._mapRowToObject(cls(), result)
        
    def _mapRowToObject(self, obj, result):
        if not result:
            return None
        
        for column in result.keys():
            val = result[column]
            
            #print("Col=%s Val=%s" % (column,val))
            
            if hasattr(obj, column):
                setattr(obj, column, val)
        
        return obj