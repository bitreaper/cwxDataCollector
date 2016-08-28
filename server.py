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

# system libs
import os
import time
import random
import string
import cherrypy
from cherrypy.process.plugins import SimplePlugin

# local libs
from sqlThread import SqlThread

#############################
# config
#############################

config = {
  'global' : {
    'server.socket_host' : '0.0.0.0',
    'server.socket_port' : 8080,
    'server.thread_pool' : 10
  }
}

##############################
# Exit handler definition.  Needed because Ctrl+C would not work right otherwise.  It's also needed
# because any changes to this file would cause the server to hang instead of restart.
# A good example can be found here:
# http://stackoverflow.com/questions/29238079/why-is-ctrl-c-not-captured-and-signal-handler-called
##############################

class ExitPlugin(SimplePlugin):

    def __init__(self, threadList, bus):
        SimplePlugin.__init__(self, bus)
        self.threadList = threadList

    def start(self):
        self.bus.log('Setting up exit handler plugin')
    # Setting start()'s priority to greater than 65 so that it is fired up after the fork if daemonized
    # See this for more details: https://groups.google.com/forum/#!topic/cherrypy-users/1fmDXaeCrsA
    start.priority = 70
    
    def exit(self):
        ''' iterate over threads and call their stop methods, then iterate again for each join.'''
        for thread in self.threadList:
            thread.stop()

        for thread in self.threadList:
            thread.join()

        self.unsubscribe()


##############################
# app definition
##############################

class SensorNetCollector(object):
    def __init__(self,sql):
        self.sql = sql

    ############
    @cherrypy.expose
    def index(self,):
        return '''try "keep?sensor=sensorname&data=mydata&sensorType=type" for your request.'''

    ############
    # for testing a sensor's link without storing the information.  It will just echo back to you the data you sent.
    @cherrypy.expose
    def testlink(self,sensor,data,sensorType):
        return "OK, {}, {}, {}".format(sensor, data, sensorType)

    ############
    @cherrypy.expose
    def keep(self,sensor,data,sensorType):
        if all([sensor, data, sensorType]):
            timestamp = int(time.time())
            self.sql.queue.put((sensor,timestamp,data,sensorType))
            return 'OK'
        else:
            if sensor:
                msg = '''You forgot to add data'''
            if data:
                msg = '''You forgot to add sensor id'''
            return msg


##############################
# main
##############################

if __name__ == '__main__':

    sqlThread = SqlThread()
    sqlThread.start()

    ExitPlugin([sqlThread], cherrypy.engine).subscribe()
    cherrypy.quickstart(SensorNetCollector(sqlThread), '/', config=config)
