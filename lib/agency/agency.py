"""
:mod:`agency` -- This supervises then agents under its control.
=================================================================

.. module:: agency
   :platform: Unix, MacOSX, Windows
   :synopsis: This supervises then agents under its control.
.. moduleauthor:: Oisin Mulvihill <oisin.mulvihill@gmail.com>


Agency
=========
  
This is the agency that manages the physical hardware and 
abstracts its use from the other parts of the code.

The agency catagorises the hardware under a generic set
of classifications defined in AGENT_CATEGORIES. This is then used 
to provide a generic id when the need arises to directly address 
a agent. The ids follow a path type syntax. The root of all is 
the 'agent' node. Agents are then hung off the root node based
on the class they belong to. For example::

  /agent/printer
  /agent/display
  /agent/swipe
  /agent/sale
  :
  etc

Once a specifc agent is registered for use in the configuration
then it gets added and aliased. For example a configuration entry
for the magtek usb swipe could be::

  [magtekusb]
  # required agent manager config
  alias = '1'
  cat = 'swipe'
  agent = 'magtek.usbcardswipe.swipe'
  
  # specific config
  vendor_id = 0x0801
  product_id = 0x0002

This instructs the agency's manager to create a agent::

  /agent/swipe/magtekusb/1

  /agent/swipe/1

The agent manager loads the agent package 'magtek.usb.swipe' from the
python path. The agency looks from a Base class in the module. In the 
magtek example this would be 'magtek.usb.swipe.Base'. This class 
implements the required interface the manager uses to control the agent. 


Agency API
===================

.. data:: agency.agency.AGENT_CATEGORIES

These represent the type of agent a agent belongs to. These are the strings 
that are used in the class field in the configuration.


.. autoclass:: agency.agency.Nodes
   :members:
   :undoc-members:
   
.. autofunction:: shutdown()   

"""
import logging
import itertools

import agent
import config
import agents
import manager
from config import ConfigError
from manager import ManagerError


__all__ = ['AGENT_CATEGORIES', 'Nodes', 'shutdown', 'node', 'manager']

def get_log():
    return logging.getLogger('agency.agency')


AGENT_CATEGORIES = {
    'display' : 'This is the category for message output to some kind of physical display.', 
    'cashdrawer' : 'This is the category for cash drawer access.', 
    'printer' : 'This is the category for output to paper and other printed media.', 
    'sale' : 'This is the category for point of sale agents fit under to process card/chip and pin payments.', 
    'swipe' : 'This is the category for magnetic card swipe agents.',
    'websale' : 'This is the category for web-based sale agents.',
    'service' : 'This represent some web or other type of networked service',
    'general' : 'This represents a catch all category',
}


class Nodes(object):
    """This class manages the node and alias id string generation, based 
    on the agent category currently found in agency.AGENT_CATEGORIES.
    
    """
    def __init__(self):
        self.counters = {}
        self._aliasGen = None # setup by reset.
        self._reset()
        

    def _reset(self):
        """Used in unittesting to reset the internal counts.
        """
        self._aliasGen = itertools.count(1)

        for cat in AGENT_CATEGORIES:
            self.counters[cat] = 0


    def add(self, cat, cat_name, alias=None):
        """Called to generate a node_id and alias_id for the given class recovered
        from the config file.
        
        cat:
            This must be a string as found in agency.AGENT_CATEGORIES.
            If not the ValueError will be raised.
        
        cat_name:
            This is the name of the config section as recovered
            from the agent configuration.
        
        alias:
            This is the user specific id recovered from the config file.
            The agency manager must make sure these are unique.
            
            If this is not given then an alias will be auto-generated.
            
        returned:
            (node_id, alias_id)
            
            E.g.
                node_id = '/agent/swipe/testing/1'
                alias_id = '/agent/swipe/1'
                
            The node_id provides a specific id for addressing a particular
            agent. The alias_id is used when any instance of the agent
            maybe used.
        
        """
        if cat not in AGENT_CATEGORIES:
            raise ValueError("Unknown agent class '%s'. Is this a missing one?" % cat)
        
        if not alias:
            alias = self._aliasGen.next()
        
        self.counters[cat] += 1
        node_id = "/agent/%s/%s/%d" % (cat, cat_name, self.counters[cat])
        try:
            alias = int(alias)
        except TypeError,e:
            raise ConfigError("The alias must be an integer not '%s'." % alias)

        alias_id = "/agent/%s/%d" % (cat, alias)
        
        return node_id, alias_id
        
        
    def get(self, cat):
        """Called to return the current count for the allocated node ids.
        
        cat:
            This must be a string as found in agency.AGENT_CATEGORIES.
            If not the ValueError will be raised.

        returned:
            The amount of ids given out so far.
            
        """
        if cat not in AGENT_CATEGORIES:
            raise ValueError("Unknown agent category '%s'. Is this a missing one?" % cat)

        return self.counters[cat]
        
# Singleton instances:                
#
node = Nodes()
manager = manager.Manager()


def shutdown():
    """Shutdown the agent manager, stopping and cleaning up all agents we manager.
    """
    manager.shutdown()

