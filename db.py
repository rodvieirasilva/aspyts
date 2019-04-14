import sqlite3
from datetime import datetime

class DB(object):
    
    def __init__(self):
        self.DATA_BASE_NAME = 'aspyts.db3'
        self.STATUS_EXECUTING = "executing"
        self.STATUS_ERROR = "error"
        self.STATUS_FINISHED = "success"

        self.cursor = None
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.DATA_BASE_NAME)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, type, value, tb):
        self.conn.commit()
        self.conn.close()
    
    def execute(self, sql, args=()):
        self.cursor.execute(sql, args)
        return self.cursor

    def now(self):
        return datetime.now().isoformat(' ')

    def getIdStatus(self, name):
        self.execute("""
                INSERT OR IGNORE INTO status (name, dt_insert) VALUES (?,?)        
                """, [
                    name,
                    self.now()
                ])
        cursor = self.execute("SELECT id FROM status WHERE name = ?;" ,[
            name
        ])
        return cursor.fetchone()[0]

    def checkActive(self, id_task):
        cursor = self.execute("""
                select active from task where id = ?
                """, [
                    id_task
                ])        
        return bool(cursor.fetchone()[0])

    def create(self):        
        self.execute(
            '''CREATE TABLE IF NOT EXISTS task (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name text NOT NULL, 
                interval REAL NOT NULL,
                cmd text NOT NULL,
                dt_last_exec text,
                dt_insert text NOT NULL,
                active INTEGER,
                UNIQUE(name, interval, cmd)
            )''')
        self.execute(
            '''CREATE TABLE IF NOT EXISTS status (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name text NOT NULL,
                dt_insert TEXT NOT NULL,
                UNIQUE(name)
            )'''
        )
        self.execute(
            '''CREATE TABLE IF NOT EXISTS exec (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                id_task INTEGER NOT NULL, 
                dt_start text NOT NULL,
                dt_finish text,
                id_status INTEGER NOT NULL,
                output TEXT,
                result_code INTEGER,
                dt_insert text NOT NULL
            )'''
        )
    
    def listTask(self):
        cursor = self.execute("""
            SELECT 
                id, name, interval, cmd, dt_last_exec, dt_insert, active
            FROM task
            order by name, interval
        """)
        return cursor

    def nextTask(self):
        cursor = self.execute("""
            SELECT 
                id, name, interval, cmd, dt_last_exec, dt_insert
            FROM task
            where 
                active = 1 AND (
                    (strftime('%s','now') - strftime('%s',dt_last_exec)) >= interval OR
                    (dt_last_exec IS NULL)
                )
            order by dt_last_exec, id
            limit 1
        """)
        return cursor

    def insertTask(self, name, interval, cmd, active=True):
        cursor = self.execute('''        
            insert OR IGNORE into task (
                    name, 
                    interval,
                    cmd,
                    dt_insert,
                    active) values (
                        ?,
                        ?,
                        ?,
                        ?,
                        ?
                    )
        ''', [
            name, interval, cmd, self.now(), int(active)
        ])
        return cursor.lastrowid
    
    def updateTask(self, id, dt_last_exec=None, active=1):
        sql = 'update task set '
        args = []
        if(not dt_last_exec is None):
            sql = sql + "dt_last_exec = ?, "            
            args.append(dt_last_exec)       

        args.append(active)
        args.append(id)

        self.execute(sql + '''        
                active = ?
            where id = ?
        ''', args)

    def insertExec(self, id_task):
        now = self.now()
        cursor = self.execute('''        
            INSERT INTO exec (id_task, dt_start, id_status, dt_insert)
            values (?,?,?,?)
        ''', [
            id_task,
            now,
            self.getIdStatus(self.STATUS_EXECUTING),
            now,
        ])
        return cursor.lastrowid 

    def updateExec(self, id, status, output, dt_finish, result_code):
        self.execute('''        
            UPDATE exec SET 
                dt_finish = ?,
                id_status = ?,
                output=?,
                result_code=?
            where id = ?
        ''', [
            dt_finish,
            self.getIdStatus(status),
            output,
            result_code,
            id
        ])