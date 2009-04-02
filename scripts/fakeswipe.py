"""
Send whatever is typed after the command invokation out as a card swipe event.

This sends directly to the fake swipe device listening on "localhost:8810". 
This injects the card data event as a real card swipes would normal do.

Example:

    python scripts/fakeswipe.py hello there


Oisin Mulvihill
2009-04-01

"""
import sys
from xmlrpclib import Server

data = " ".join(sys.argv[1:])

s = Server('http://localhost:8810')
s.cardData(data)
