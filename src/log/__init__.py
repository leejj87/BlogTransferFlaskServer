import os
import sqlite3
from pathlib import Path
BASEFILE_LOCATION=os.path.dirname(os.path.abspath(__file__))
LOGDIRECTORY=os.path.join(Path(BASEFILE_LOCATION).parent.parent,'logs')
if not os.path.exists(LOGDIRECTORY):
    os.makedirs(LOGDIRECTORY)
if not os.path.exists(os.path.join(LOGDIRECTORY,'log.db')):
    con = sqlite3.connect(os.path.join(LOGDIRECTORY, 'log.db'))
    cursorObj = con.cursor()
    try:
        cursorObj.execute("CREATE TABLE MAIN_LOG(IDX integer PRIMARY KEY, BLOG_URL text, STATUS text, SCRIPT text, MESSAGES text, DATETIME text)")
        con.commit()
    except:
        pass
    try:
        cursorObj.execute("CREATE TABLE SYSTEM_LOG(IDX integer PRIMARY KEY, STATUS text, MESSAGES text, DATETIME text)")
        con.commit()
    except:
        pass
    con.close()

