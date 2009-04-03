"""
This module provides the device layer configuration parsing and handling. 

"""
import logging
import StringIO

import configobj

import deviceaccess
import traceback

def get_log():
    return logging.getLogger('deviceaccess.config')


class ConfigError(Exception):
    """This is raised for problems with loading and using the configuration.
    """


class Container(object):
    """This represents a configuration sections as recoverd from the 
    device configuration.    
    """
    reserved = ()
    def __init__(self):
        self.driver = None
        self.dev_class = None
        self.alias = None
        self.node = None
        self.name = None
        self.reserved = ('driver', 'dev_class', 'alias', 'reserved', 'name')
        self.config = None
        self.device = None
    
    def check(self):
        """Called to check that all the reserved fields have been provided.
        
        If one or more aren't provided then ConfigError
        will be raised to indicate so.
        
        """
        for i in self.reserved:
            if not getattr(self, i, None):
                raise ConfigError("The member '%s' must be provided in the configuration." % i)        
    
    def __str__(self):
        """Print out who were representing and some unique identifier."""
        #print "self:", self.__dict__
        return "<Device: node %s, alias %s>" % (self.node, self.alias)

    
    def __repr__(self):
        """This is a string the represents us, can be used as a dict key."""
        return self.__str__()


def load(config, check=None):
    """Called to test and then load the device configuration.
    
    config:
        This is a string representing the contents of the
        device layer's configuration file.
    
    check:
        If this is given the callback will be invoked and
        given the node and aliad of the config object. The
        callback can then check if its unique. Its up to the
        user to determine what to do if they're not.
    
    returned:
        This returns a list of config containers loaded with
        the entries recovered from the device's section.
    
    """
    cfg = configobj.ConfigObj(StringIO.StringIO(config))
    processed = {}
    
    def recover(section, key):
        value = section[key]
        c = processed.get(section.name, Container())            
        
        if not c.name:
            c.name = section.name    
        
        if not c.config:
            c.config = section
            
        if key == 'dev_class' and value not in deviceaccess.DEVICE_CLASSES:
            raise ConfigError("The class '%s' is not known. It might need adding to '%s'." % (key, deviceaccess.DEVICE_CLASSES))
            
        elif key == 'driver':
            def recover_driver():
                # default: nothing found.
                returned = None
                
                # Check I can at least import the stated module.
                try:
                    imported_driver = __import__(section[key], fromlist=section[key].split('.'))
                except ImportError, e:
                     raise ImportError("The driver '%s' was not found! %s" % (section[key], traceback.format_exc()))                        

                # Now see if it contains a Device class all driver must have to load:
                if hasattr(imported_driver, 'Device'):
                    returned = getattr(imported_driver, 'Device')
                    
                return returned

            value = recover_driver()
            if not value:
                raise ConfigError("I was unable to import '%s' from '%s'." % (item, current))
                        
        setattr(c, key, value)
        processed[section.name] = c
        
    # Process all the config sections creating config containers.
    cfg.walk(recover)
    
    # Verify we've got all the sections I require:
    alias_check = {}
    def update_and_check(c):
        c.check()
        c.node, c.alias = deviceaccess.node.add(c.dev_class, c.name, c.alias)
        if alias_check.get(c.alias, 0):
            bad = c.alias.split('/')[-1]
            raise ConfigError("A duplicate config alias '%s' has been found for configuration '%s'" % (bad, c.name))
        else:
            alias_check[c.alias] = 1
        
        return c

    returned = [update_and_check(c) for c in processed.values()]
    
    return returned
    
    
    
    
    
