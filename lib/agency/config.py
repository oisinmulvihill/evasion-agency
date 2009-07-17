"""
:mod:`config` -- This supervises then agents under its control.
=================================================================

.. module:: config
   :platform: Unix, MacOSX, Windows
   :synopsis: This supervises then agents under its control.
.. moduleauthor:: Oisin Mulvihill <oisin.mulvihill@gmail.com>

This module provides the device layer configuration parsing and handling. 

.. exception:: agency.config.ConfigError

.. autoclass:: agency.config.Container
   :members:
   :undoc-members:

.. autofunction:: agency.config.load(config, check=None)


"""
import logging
import StringIO

import configobj

import agency
import traceback

def get_log():
    return logging.getLogger('agency.config')


class ConfigError(Exception):
    """This is raised for problems with loading and using the configuration.
    """


class Container(object):
    """This represents a configuration sections as recoverd from the 
    device configuration.    
    """
    reserved = ()
    def __init__(self):
        self.agent = None
        self.cat = None
        self.alias = None
        self.node = None
        self.name = None
        self.disable = "no"
        # alias is no longer required.
        self.reserved = ('agent', 'cat', 'reserved', 'name')
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
        return "<Agent: node %s, alias %s>" % (self.node, self.alias)

    
    def __repr__(self):
        """This is a string the represents us, can be used as a dict key."""
        return self.__str__()


def load(config, check=None):
    """Called to test and then load the agent configuration.
    
    config:
        This is a string representing the contents of the
        configuration file.
    
    check:
        If this is given the callback will be invoked and
        given the node and alias of the config object. The
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
            
        if key == 'cat' and value not in agency.AGENT_CATEGORIES:
            raise ConfigError("The class '%s' is not known. It might need adding to '%s'." % (key, agency.AGENT_CATEGORIES))
            
        elif key == 'agent':
            def recover_agent():
                # default: nothing found.
                returned = None
                
                # Check I can at least import the stated module.
                try:
                    # absolute imports only:
                    imported_agent = __import__(section[key], fromlist=section[key].split('.'), level=0)
                except ImportError, e:
                     raise ImportError("The agent '%s' was not found! %s" % (section[key], traceback.format_exc()))                        

                # Now see if it contains a Agent category all agent must have to load:
                if hasattr(imported_agent, 'Agent'):
                    returned = getattr(imported_agent, 'Agent')
                    
                return returned

            value = recover_agent()
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
        c.node, c.alias = agency.node.add(c.cat, c.name, c.alias)
        if alias_check.get(c.alias, 0):
            bad = c.alias.split('/')[-1]
            raise ConfigError("A duplicate config alias '%s' has been found for configuration '%s'" % (bad, c.name))
        else:
            alias_check[c.alias] = 1
        
        return c

    returned = [update_and_check(c) for c in processed.values()]
    
    return returned
    
    
    
    
    
