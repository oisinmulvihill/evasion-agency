"""
This is the base class for the swipe card device. It is used
by the magtek and testing swipe devices.

Oisin Mulvihill
2007-08-02

"""
import logging

from pydispatch import dispatcher

import messenger
from deviceaccess import device


def get_log():
    return logging.getLogger("deviceaccess.drivers.base.swipe")


class Swipe(device.Base):
    """This is the base class for swipe devices, it implements
    the message dispatch so the driver only has to call send
    with the card data.
    
    """
    def send(self, card_data):
        """Send out the SWIPE_CARD_DATA event with the named 'card'
        argument, containing the raw card data.
        """
        get_log().debug("Sending SWIPE_CARD_DATA event.")
        
        dispatcher.send(
            signal=messenger.EVT('SWIPE_CARD_DATA'),
            card=card_data
        )






