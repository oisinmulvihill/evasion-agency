"""
This device is used to test the device manager and has no other
functional use.

Oisin Mulvihill
2007-07-23

"""
from deviceaccess import device


class Device(device.Base):
    """This is a completely fake module used in unit testing to allow
    the manager to call all the methods with out starting an stopping
    physical devices.

    Valid example configuration for this fake device is:
    
        [testswipe]
        # first card swipe
        alias = 1
        dev_class = 'swipe'
        driver = 'testing.fake'

    If you set the parent object that implments the device.Base
    methods, then you get callbacks for each time the methods
    are called.
    
    """
    def __init__(self):
        self.config = None
        self._parent = None
        
    def setParent(self, parent):
        self._parent = parent
#        print "setting parent: ", self._parent
    
    def getParent(self):
        # check its been set up before its used!
        return self._parent
    
    def setUp(self, config):
        if self._parent:
            self._parent.setUp(config)

    def tearDown(self):
        if self._parent:
            self._parent.tearDown()

    def start(self):
        if self._parent:
            self._parent.start()

    def stop(self):
        if self._parent:
            self._parent.stop()

    def query(self):
        """Returned a dictionary of events swipe users can subscribe too.
        """
        if self._parent:
            return self._parent.query()
        else:
            return {}




