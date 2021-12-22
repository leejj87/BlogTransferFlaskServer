import sqlite3
import os
import datetime
from .__init__ import BASEFILE_LOCATION,LOGDIRECTORY

class DB_Managements(object):
    def __init__(self):
        self.con = sqlite3.connect(os.path.join(LOGDIRECTORY,'log.db'),check_same_thread=False)
        self.cursor_obj=None
    def cursor(self):
        self.cursor_obj=self.con.cursor()
    def execute_sql(self,sql):
        if self.cursor_obj is not None:
            return self.cursor_obj.execute(sql)
        else:
            raise Exception("Cursor Required")
    def commit(self):
        self.con.commit()
    def rollback(self):
        self.con.rollback()
    def close(self):
        self.cursor_obj.close()
        self.con.close()
class SelectStatement(DB_Managements):
    def __init__(self):
        super().__init__()
        self.cursor()
    def getSelectResults(self,query):

        self.execute_sql(query)
        while True:
            row = self.cursor_obj.fetchone()
            if row == None:
                break
            else: yield  row
class DDLStatement(DB_Managements):
    def __init__(self):
        super().__init__()
        self.cursor()
    def insert(self,query):
        try:
            self.execute_sql(query)
        except Exception as err:
            print(err)
            self.rollback()
            return False
        else:
            self.commit()
            return True

def max_idx():
    select_instance=SelectStatement()
    query="""select MAX(IDX) as max_index from MAIN_LOG"""
    for i in select_instance.getSelectResults(query):
        print(i)

def addToMainLogs(blogurl,status,script,msg):
    date_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    insert_instance=DDLStatement()
    query="""insert into MAIN_LOG (BLOG_URL,STATUS,SCRIPT,MESSAGES,DATETIME)values('{blog_url}','{status}','{script}','{message}','{datetime}')""".format(blog_url=blogurl,status=status,script=script,message=msg,datetime=date_time)
    result=insert_instance.insert(query)
    insert_instance.close()
    return result
def addToSystemLogs(status,msg):
    date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    insert_instance = DDLStatement()
    query="""insert into SYSTEM_LOG (STATUS,MESSAGES,DATETIME)values('{status}','{message}','{datetime}')""".format(status=status,message=msg,datetime=date_time)
    result=insert_instance.insert(query)
    insert_instance.close()
    return result
def getSystemLogs():
    sql="""select * from SYSTEM_LOG"""
    instance_select = SelectStatement()
    list_result = []
    for i in instance_select.getSelectResults(sql):
        list_result.append(list(i))
    instance_select.close()
    return list_result
def getLogs(idx=None):
    if idx is None:
        sql="""select * from MAIN_LOG"""
    else:
        sql="""select * from MAIN_LOG where IDX={}""".format(idx)
    instance_select=SelectStatement()
    list_result=[]
    for i in instance_select.getSelectResults(sql):
        list_result.append(list(i))
    instance_select.close()
    return list_result
#addLogs("test","test","test","test")