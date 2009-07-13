"""
This module implements the device interface that drivers must
inherit from and implement. The device manager looks for this
and if found uses it to create and run the device.

Oisin Mulvihill
2007-07-23

"""


class Base(object):
    """Base class device entry.
    """

    def setUp(self, config):
        """Called to set up the device and subscribe for any events
        it may be interested in.

        """

    
    def tearDown(self):
        """Called to cleanup and release any resources the device 
        may be using. 
        
        This is usually done by the device manager before the 
        program using it exits.

        """


    def start(self):
        """Called to start any processing the device may need to do.
        
        This function maybe used to start any threads polling a
        device for example.
        
        """
        
        
    def stop(self):
        """Called to stop any processing the device may be doing. 
        
        The start function may be called to resume operation.
        
        """



