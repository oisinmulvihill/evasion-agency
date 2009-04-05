import uuid
import time
import socket
import thread
import logging
import datetime
import xmlrpclib
import SimpleXMLRPCServer


from pydispatch import dispatcher


import messenger
from deviceaccess import device
from director import viewpointdirect
from deviceaccess.drivers import base
from messenger import xulcontrolprotocol        


class StoppableXMLRPCServer(SimpleXMLRPCServer.SimpleXMLRPCServer):
    """Handle requests but check for the exit flag setting periodically.
    
    This snippet is based example from:
    
        http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/425210
    
    """
    log = logging.getLogger('deviceaccess.base.service.StoppableXMLRPCServer')

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


class ControlFrameRequest(SocketServer.StreamRequestHandler):
    """Handle a viewpoint control frame request.
    """
    def handler(self):
        """
        self.rfile = request, self.wfile = response
        """
        

class StoppableTCPServer(SocketServer.ThreadingTCPServer):
    """Handle requests but check for the exit flag setting periodically.    
    """
    log = logging.getLogger('deviceaccess.base.service.StoppableTCPServer')

    exitTime = False
    
    allow_reuse_address = True

    def __init__(self, serveraddress):
        super(StoppableTCPServer, self).__init__(serveraddress, ControlFrameRequest)

    def stop(self):
        self.exitTime = True
        self.log.info("Stop: set exit flag and closed port.")

    def server_bind(self):
        super(StoppableTCPServer, self).server_bind(self)
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


class FakeViewpointDevice(device.Base):
    """A TCPServer interface implement the viewpoint control frame protocol.
    
    Valid example configuration for this device is:
    
        [fakeviewpoint]
        dev_class = service
        driver = <my code>.<myservice>
        alias = 2839
        interface = 127.0.0.1
        port = 7055
                    
    """
    log = logging.getLogger('deviceaccess.base.service.FakeViewpointDevice')
    
    def __init__(self):
        self.config = None


    def registerRequestHandler(self):
        """Called to register a class instances who's derived from         
        """
        raise NotImplemented("Please implement this method!")

                
    def setUp(self, config):
        """Create the XML-RPC services. It won't be started until
        the start() method is called.
        """
        self.config = config
        #self.server = xmlrpcserver.StoppableXMLRPCServer((config.get('interface'), int(config.get('port'))))


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
            d = self.config.get('description')
            self.log.info("%s XML-RPC Service URI 'http://%s:%s'" % (self.i,p))
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



class ServiceDevice(device.Base):
    """An XML-RPC interface device.
    
    Valid example configuration for this device is:
    
        [myservice_name]
        dev_class = service
        driver = <my code>.<myservice>
        alias = 1
        interface = 127.0.0.1
        port = 8810

    The interface and port are where to start the XML-RPC server on.
    Once its up and running then you can access the interface at:
    
        'http://interface:port/'
                    
    """
    log = logging.getLogger('deviceaccess.base.service.ServiceDevice')
    
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
        self.server = xmlrpcserver.StoppableXMLRPCServer((config.get('interface'), int(config.get('port'))))
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
            d = self.config.get('description')
            self.log.info("%s XML-RPC Service URI 'http://%s:%s'" % (self.i,p))
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

