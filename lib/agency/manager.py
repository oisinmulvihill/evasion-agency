"""
This is the manager. It is reposible for managing the physical devices the 
application is using. The device manager takes care of the loading and 
intialisation of each device, using the configuration provided by the user.

Oisin Mulvihill
2007-07-23


"""
import sys
import logging
import traceback

import agency


def get_log():
    return logging.getLogger('agency.manager')


# Set to True to prevent the manager form catching exceptions
# in its methods.
TESTING=True


class ManagerError(Exception):
    """Raised for problems occuring in the device manager.
    """
    

class Manager(object):
    """The device manager takes care of the load of devices and 
    provides a central point to setUp, tearDown, start & stop
    all device nodes under our care.
    
    """
    def __init__(self):
        self._devices = {}
        self.log = logging.getLogger('agency.manager.Manager')

    
    def getDeviceCount(self):
        return len(self._devices.keys())
        
    devices = property(getDeviceCount)
    
    
    def shutdown(self):
        """Used to tearDown and reset the internal state of the device 
        manager ready for a new load command.
        
        """
        # Close and free any resources we may be using and clear out state.
        try:
            self.tearDown()
        except ManagerError,e:
            pass
        self._devices = {}

    
    def dev(self, alias):
        """Called to recover a specific device node.
        
        alias:
            This is the alias for a specific device
            node stored in the device manager.
        
        
        If the alias is not found the ManagerError
        will be raised.
        
        """
#        print "self._devices:"
#        import pprint
#        pprint.pprint(self._devices)
#        print
        
        full_alias = '/dev/%s' % alias

#        print "looking for: ", full_alias

        if not self._devices.has_key(full_alias):
            raise ManagerError("The device node alias '%s' was not found!" % full_alias)
        
        return self._devices[full_alias]
    
    
    def load(self, config):
        """Load the device configuration in and generate the devices based on this.
        
        Load can only be called after the first time, once
        shutdown has been called. If this has not been 
        done then ManagerError will be raised to indicate
        so.
        
        Returned:
            For testing purposes the loaded list of devices 
            config containers is returned. This shouldn't be 
            used normally.
        
        """
        if self.devices > 0:
            raise ManagerError("Load has been called already! Please call shutdown first!")
        
        loaded_devices = agency.config.load(config)
        
        for dev in loaded_devices:
            dev.device = dev.driver()
            self._devices[dev.alias] = dev
        
        return loaded_devices


    def formatError(self):
        """Return a string representing the last traceback.
        """
        exception, instance, tb = traceback.sys.exc_info()
        error = "".join(traceback.format_tb(tb))      
        return error


    def setUp(self):
        """Called to initialise all devices in our care.
        
        The load method must be called before this one.
        Otherwise ManagerError will be raised.
        
        """
        if self.devices < 1:
            raise ManagerError("Load has not been called! Please do this first!")
        
        for dev in self._devices.values():
            try:
                dev.device.setUp(dev.config)
            except:
                self.log.exception("%s setUp error: " % dev)
                sys.stderr.write("%s setUp error: %s" % (dev, self.formatError()))
                if TESTING:
                    raise


    def tearDown(self):
        """Called to tearDown all devices in our care.
        
        Before calling a devices tearDown() its stop()
        method is called first.
        
        The load method must be called before this one.
        Otherwise ManagerError will be raised.
        
        """
        if self.devices < 1:
            raise ManagerError("Load has not been called! Please do this first!")

        for dev in self._devices.values():
            try:
                dev.device.tearDown()
            except:
                self.log.exception("%s tearDown error: " % dev)
                sys.stderr.write("%s tearDown error: %s" % (dev, self.formatError()))
                if TESTING:
                    raise


    def start(self):
        """Start all devices under our management
        
        The load method must be called before this one.
        Otherwise ManagerError will be raised.

        """
        if self.devices < 1:
            raise ManagerError("Load has not been called! Please do this first!")

        for dev in self._devices.values():
            try:
                dev.device.start()
            except:
                self.log.exception("%s start error: " % dev)
                sys.stderr.write("%s start error: %s" % (dev, self.formatError()))
                if TESTING:
                    raise


    def stop(self):
        """Start all devices under our management
        
        The load method must be called before this one.
        Otherwise ManagerError will be raised.

        """
        if self.devices < 1:
            raise ManagerError("Load has not been called! Please do this first!")
        
        for dev in self._devices.values():
            try:
                dev.device.stop()
            except:
                self.log.exception("%s stop error: " % dev)
                sys.stderr.write("%s stop error: %s" % (dev, self.formatError()))
                if TESTING:
                    raise
        
    
    
