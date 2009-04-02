"""
This implement the virtual swipe card device which is used in acceptance testing.



"""
import time
import socket
import thread
import logging
import xmlrpclib
import SimpleXMLRPCServer

from pydispatch import dispatcher

from deviceaccess.drivers import base


def get_log():
    return logging.getLogger('deviceaccess.drivers.testing.swipe')



class StoppableXMLRPCServer(SimpleXMLRPCServer.SimpleXMLRPCServer):
    """Handle requests but check for the exit flag setting periodically.
    
    This snippet is based example from:
    
        http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/425210
    
    """
    exitTime = False
    allow_reuse_address = True

    def stop(self):
        self.exitTime = True
        get_log().info("Stop: set exit flag and closed port.")

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
            

class VirtualSwipe:

    def __init__(self, device):
        self.device = device


    def cardData(self, card_data):
        """This is called to inject card data as if it had come from an 
        actual card swipe.
        
        """
        get_log().info("cardData: injecting data - %s" % card_data)

        self.device.send(card_data)

        return 0
    

class Device(base.swipe.Swipe):
    """This is a 'virtual' card swipe device. It starts a simple XML-RPC
    server and exposes a cardData(...) method. This method may be called
    acceptance/testing systems to inject raw card into the system.

    Valid example configuration for this device is:
    
        [testswipe]
        dev_class = swipe
        driver = testing.swipe
        alias = 1
        interface = 127.0.0.1
        port = 8810

    The interface and port are where to start the XML-RPC server on.
    Once its up and running then you can access the interface at:
    
        'http://interface:port/rpc2'
        
    The only method currently available it the cardData() method.
    This take the raw data that would normally come from a card
    swipe. This will then dispatch the data into the system as if
    it had come from a real swipe.
    
    """
    def __init__(self):
        self.config = None
        self.log = get_log()
        self.server = None
                
    def setUp(self, config):
        """Create the XML-RPC services. It won't be started until
        the start() method is called.
        """
        self.config = config
        self.server = StoppableXMLRPCServer((config.get('interface'), int(config.get('port'))))
        self.server.register_instance(VirtualSwipe(self))


    def tearDown(self):
        """Stop the 'vitual' swipe card interface and close the server socket.
        """
        self.stop()


    def start(self):
        """Start the 'virtual' card swipe xmlrpc interface.
        """
        def _start(data=0):
            i = self.config.get('interface')
            p = self.config.get('port')
            self.log.info("Started virtual swipe interface.")
            self.log.info("XML-RPC Service URI 'http://%s:%s/rpc2'" % (i,p))
            try:
                self.server.serve_forever()
            except TypeError,e:
                # caused by ctrl-c. Its ok
                pass                

        thread.start_new_thread(_start, (0,))
        

    def stop(self):
        """Stop the 'virtual' card swipe xmlrpc interface.
        """
        self.log.info("Stopping virtual swipe interface.")
        if self.server:
            self.server.stop()
