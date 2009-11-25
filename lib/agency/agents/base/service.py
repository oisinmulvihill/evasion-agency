"""
:mod:`agency.agents.base.service` 
==================================

.. module:: 'agency.agents.base.service'
.. moduleauthor:: Oisin Mulvihill <oisin.mulvihill@gmail.com>


.. autoclass:: agency.agents.base.service.ServiceDevice
   :members:
   :undoc-members:

.. autoclass:: agency.agents.base.service.FakeViewpointDevice
   :members:
   :undoc-members:
   
"""
import uuid
import time
import socket
import thread
import logging
import datetime
import xmlrpclib
import SocketServer
import SimpleXMLRPCServer

from pydispatch import dispatcher


import messenger
from agency import agent
from messenger import xulcontrolprotocol        



class ControlFrameRequest(SocketServer.StreamRequestHandler):
    """Handle a viewpoint control frame request.
    """
    def handler(self):
        """
        self.rfile = request, self.wfile = response
        """
        

class StoppableTCPServer(SocketServer.TCPServer):
    """Handle requests but check for the exit flag setting periodically.    
    """
    log = logging.getLogger('agency.agents.base.service.StoppableTCPServer')

    exitTime = False
    
    allow_reuse_address = True

    def __init__(self, serveraddress, ControlFrameRequest):
        SocketServer.TCPServer.__init__(self, serveraddress, ControlFrameRequest)

    def stop(self):
        self.exitTime = True
        self.log.info("Stop: set exit flag and closed port.")

    def server_bind(self):
        SocketServer.TCPServer.server_bind(self)
        self.socket.settimeout(1)
        self.run = True
        
    def get_request(self):
        """Handle a request/timeout and check the exit flag.
        """
        while not self.exitTime:
            try:
                returned = self.socket.accept()
                if len(returned) > 1:
                    conn, address = returned
                    conn.settimeout(None)
                    returned = (conn, address)
                return returned
            except socket.timeout:
                pass



class StoppableXMLRPCServer(SocketServer.ThreadingMixIn, SimpleXMLRPCServer.SimpleXMLRPCServer):
    """Handle requests but check for the exit flag setting periodically.
    
    This snippet is based example from:
    
        http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/425210
    
    """
    log = logging.getLogger('agency.base.service.StoppableXMLRPCServer')

    exitTime = False
    
    allow_reuse_address = True

    def stop(self):
        self.exitTime = True
        self.log.info("Stop: set exit flag and closed port.")

    def server_bind(self):
        SimpleXMLRPCServer.SimpleXMLRPCServer.server_bind(self)
        self.socket.settimeout(1)
        self.run = True
        
    def get_request(self):
        """Handle a request/timeout and check the exit flag.
        """
        while not self.exitTime:
            try:
                returned = self.socket.accept()
                if len(returned) > 1:
                    conn, address = returned
                    conn.settimeout(None)
                    returned = (conn, address)
                return returned
            except socket.timeout:
                pass



class ServiceDevice(agent.Base):
    """An XML-RPC interface agent.
    
    Valid example configuration for this agent is:
    
        [myservice_name]
        cat = service
        agent = <my code>.<myservice>
        interface = 127.0.0.1
        port = 8810

    The interface and port are where to start the XML-RPC server on.
    Once its up and running then you can access the interface at:
    
        'http://interface:port/'
                    
    """
    log = logging.getLogger('agency.base.service.ServiceDevice')
    
    def __init__(self):
        self.config = None


    def registerInterface(self):
        """Called to register a class instances who's members form the XML-RPC interace.

        Example Returned:

            class MyService(object):
                def ping(self):
                    return 'hello'

            return MyService()

        In this example, the ping() method will then be available when
        the service is started.
        
        """
        raise NotImplemented("Please implement this method!")

                
    def setUp(self, config):
        """Create the XML-RPC services. It won't be started until
        the start() method is called.
        """
        self.config = config
        interface = config.get('interface')
        port = int(config.get('port'))
        while True:
            try:
                self.log.info("Creating service...")
                self.server = StoppableXMLRPCServer((interface, port))
                
            except socket.error, e:
                if e[0] == 48 or e[1] == 'Address already in use':
                    self.log.error("Address (%s, %s) in use. Retrying..." % (interface, port))
                    pass
            
            except Exception, e:
                self.log.exception("Service creation failed - ")
                break
                
            else:
                self.log.info("Service created OK.")
                break
                
            time.sleep(1)
            
        self.server.register_instance(self.registerInterface())


    def tearDown(self):
        """Stop the service.
        """
        self.stop()


    def start(self):
        """Start xmlrpc interface.
        """
        def _start(data=0):
            i = self.config.get('interface')
            p = self.config.get('port')
            self.log.info("XML-RPC Service URI 'http://%s:%s'" % (i,p))
            try:
                self.server.serve_forever()
            except TypeError,e:
                # caused by ctrl-c. Its ok
                pass                

        thread.start_new_thread(_start, (0,))
        

    def stop(self):
        """Stop xmlrpc interface.
        """
        if self.server:
            self.server.stop()

