#!/usr/bin/env python
'''
   cwxDataCollector - A simple python webserver set to collect sensor data.

   Copyright (C) 2016 Bitreaper <bitreaper AT n357 DOT com>
   
   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License (GPL) as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.
   
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
   
   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

import os
import time
import sqlite3
from threading import Thread
from Queue import Queue,Empty,Full

class SqlStatements( object ):
    LIST_TABLES = "select name from sqlite_master where type ='table';"    
    
class SqlThread(Thread):
    sqlfile = "sensordata.sqlite3"

    def __init__(self):
        self.running = False
        self.queue = Queue()
        super(SqlThread, self).__init__()

    def sqlInit(self):
        self.conn = sqlite3.connect( self.sqlfile )
        self.cursor = self.conn.cursor()
        # check to see that the table we need exists create it if it doesn't
        if 0 == len(self.cursor.execute(SqlStatements.LIST_TABLES).fetchall()):
            retdata = self.cursor.execute( "CREATE TABLE sensors (sensorid TEXT, timestamp NUMERIC, data TEXT, sensorType TEXT);" )
            self.conn.commit()

    def start( self ):
        self.running = True
        super(SqlThread, self).start()

    def stop( self ):
        self.running = False

    def run(self):
        self.sqlInit()
        data = None
        while self.running:
            if self.queue.qsize() > 0:
                try:
                    data = self.queue.get(False)
                    #print "Data received, would stuff {} {} {} {}".format(data[0],data[1],data[2],data[3])
                    self.cursor.execute(
                        "INSERT INTO sensors VALUES ('{}',{},'{}','{}')".format(
                            data[0],
                            data[1],
                            data[2],
                            data[3])
                        )
                    self.conn.commit()
                except Empty as e:
                    pass
            time.sleep(1)


#########################
# super simple unit test.    
if __name__ == "__main__":
    sqlThread = SqlThread()
    sqlThread.start()

    timestamp = int(time.time())
    print("pushing data for %d" % timestamp)
    sqlThread.queue.put(('outside',timestamp,'200','light'))
    time.sleep(2)

    timestamp = int(time.time())
    print("pushing data for %d" % timestamp)
    sqlThread.queue.put(('bathroom',timestamp,'2900','vcc'))
    time.sleep(2)
    
    timestamp = int(time.time())
    print("pushing data for %d" % timestamp)
    sqlThread.queue.put(('livingroom',timestamp,'25','temp'))
    time.sleep(2)

    sqlThread.stop()
    sqlThread.join()
