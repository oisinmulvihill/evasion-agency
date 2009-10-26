"""
:mod:`fake` -- This is used in testing the agents
===================================================

.. module:: fake
   :platform: Unix, MacOSX, Windows
   :synopsis: This supervises then agents under its control.
.. moduleauthor:: Oisin Mulvihill <oisin.mulvihill@gmail.com>

This agent is used to test the agent manager and has no other functional use.

.. autoclass:: agency.agents.testing.fake.Agent
   :members:
   :undoc-members:


"""
from agency import agent


class Agent(agent.Base):
    """This is a completely fake module used in unit testing to allow
    the manager to call all the methods with out starting an stopping
    physical agents.

    Valid example configuration for this fake agent is::
    
        [testswipe]
        # first card swipe
        alias = 1
        cat = 'swipe'
        agent = 'agency.testing.fake'

    If you set the parent object that implements the agent.Base
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



