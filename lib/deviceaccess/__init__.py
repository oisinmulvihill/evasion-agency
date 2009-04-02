"""
This is the device layer that manages the physical hardware and 
abstracts its use from the POS, ATM and other code.

The device layer catagorises the hardware under a generic set
of classifications defined in DEVICE_CLASSES. This is then used 
to provide a generic id when the need arises to directly address 
a device. The ids follow a path type syntax. The root of all is 
the 'device' node. Devices are then hung off the root node based
on the class they belong to. For example:

  /dev/printer
  /dev/display
  /dev/swipe
  /dev/sale
  :
  etc

Once a specifc device is registered for use in the configuration
then it gets added and aliased. For example a configuration entry
for the magtek usb swipe could be:

  [magtekusb]
  # required device manager config
  alias = '1'
  dev_class = 'swipe'
  driver = 'magtek.usbcardswipe.swipe'
  # specific config
  vendor_id = 0x0801
  product_id = 0x0002

This instructs the device layer's manager to create a device

  /dev/swipe/magtekusb/1

This is assigned the alias:

  /dev/swipe/1

The device manager loads the driver 'magtek.usb.swipe' from the drivers 
directory. The device layer looks from a Device class in the module. In the 
magtek example this would be 'magtek.usb.swipe.Device'. This class 
implements the required interface the manager uses to control the device. 


Oisin Mulvihill
2007-07-23


"""
import logging

import config
import drivers
import manager
from config import ConfigError
from manager import ManagerError


def get_log():
    return logging.getLogger('manager')


# These represent the type of device a driver belongs
# to. These are the strings that are used in the class
# field in the configuration.
#
DEVICE_CLASSES = {
    'display' : 'This is the class for message output to some kind of physical display.', 
    'cashdrawer' : 'This is the class for cash drawer access.', 
    'printer' : 'This is the class for output to paper and other printed media.', 
    'sale' : 'This is the class for point of sale devices fit under to process card/chip and pin payments.', 
    'swipe' : 'This is the class for magnetic card swipe devices.',
    'websale' : 'This is the class for web-based sale devices.',
}


class Nodes(object):
    """This class manages the node and alias id string generation, based 
    on the device class currently found in deviceaccess.DEVICE_CLASSES.
    
    """
    def __init__(self):
        self.counters = {}
        self._reset()
        

    def _reset(self):
        """Used in unittesting to reset the internal counts.
        """
        for cclass in DEVICE_CLASSES:
            self.counters[cclass] = 0


    def add(self, dev_class, class_name, alias):
        """Called to generate a node_id and alias_id for the given class recovered
        from the config file.
        
        dev_class:
            This must be a string as found in deviceaccess.DEVICE_CLASSES.
            If not the ValueError will be raised.
        
        class_name:
            This is the name of the config section as recovered
            from the device configuration.
        
        alias:
            This is the user specific id recovered from the config file.
            The deviceaccess manager must make sure these are unique.
            
        returned:
            (node_id, alias_id)
            
            E.g.
                node_id = '/dev/swipe/testing/1'
                alias_id = '/dev/swipe/1'
                
            The node_id provides a specific id for addressing a particular
            driver. The alias_id is used when any instance of the driver
            maybe used.
        
        """
        if dev_class not in DEVICE_CLASSES:
            raise ValueError("Unknown device class '%s'. Is this a missing one?" % dev_class)
        
        self.counters[dev_class] += 1
        node_id = "/dev/%s/%s/%d" % (dev_class, class_name, self.counters[dev_class])
        try:
            alias = int(alias)
        except TypeError,e:
            raise ConfigError("The alias must be an integer not '%s'." % alias)

        alias_id = "/dev/%s/%d" % (dev_class, alias)
        
        return node_id, alias_id
        
        
    def get(self, dev_class):
        """Called to return the current count for the allocated node ids.
        
        dev_class:
            This must be a string as found in deviceaccess.DEVICE_CLASSES.
            If not the ValueError will be raised.

        returned:
            The amount of ids given out so far.
            
        """
        if dev_class not in DEVICE_CLASSES:
            raise ValueError("Unknown device class '%s'. Is this a missing one?" % dev_class)

        return self.counters[dev_class]
        
# Singleton instances:                
#
node = Nodes()
manager = manager.Manager()


def shutdown():
    """Shutdown the device manager, stopping and cleaning up all devices we manager.
    """
    manager.shutdown()

