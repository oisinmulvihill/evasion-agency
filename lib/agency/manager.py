"""
:mod:`manager` -- This supervises then agents under its control.
=================================================================

.. module:: manager
   :platform: Unix, MacOSX, Windows
   :synopsis: This supervises then agents under its control.
.. moduleauthor:: Oisin Mulvihill <oisin.mulvihill@gmail.com>

This is the manager. It is reposible for managing the physical agents the 
application is using. The agent manager takes care of the loading and 
intialisation of each agent, using the configuration provided by the user.

.. data:: TESTING

.. exception:: agency.manager.ManagerError

.. autoclass:: agency.manager.Manager
   :members:
   :undoc-members:


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
    """Raised for problems occuring in the agent manager.
    """
    

class Manager(object):
    """The agent manager takes care of the load of agents and 
    provides a central point to setUp, tearDown, start & stop
    all agent nodes under our care.
    
    """
    def __init__(self):
        self._agents = {}
        self.log = logging.getLogger('agency.manager.Manager')

    
    def getAgentCount(self):
        return len(self._agents.keys())
        
    agents = property(getAgentCount)
    
    
    def shutdown(self):
        """Used to tearDown and reset the internal state of the agent 
        manager ready for a new load command.
        
        """
        # Close and free any resources we may be using and clear out state.
        try:
            self.tearDown()
        except ManagerError,e:
            pass
        self._agents = {}

    
    def agent(self, alias, absolute=False):
        """Called to recover a specific agent node.
        
        alias:
            This is the alias for a specific agent
            node stored in the agent manager.
        
        
        If the alias is not found the ManagerError
        will be raised.
        
        """
#        print "self._agents:"
#        import pprint
#        pprint.pprint(self._agents)
#        print

        full_alias = alias
        if not absolute:
            full_alias = '/agent/%s' % alias

#        print "looking for: ", full_alias

        if not self._agents.has_key(full_alias):
            raise ManagerError("The agent node alias '%s' was not found!" % full_alias)
        
        return self._agents[full_alias]
    
    
    def load(self, config):
        """Load the agent configuration in and generate the agents based on this.
        
        Load can only be called after the first time, once
        shutdown has been called. If this has not been 
        done then ManagerError will be raised to indicate
        so.
        
        Returned:
            For testing purposes the loaded list of agents 
            config containers is returned. This shouldn't be 
            used normally.
        
        """
        if self.agents > 0:
            raise ManagerError("Load has been called already! Please call shutdown first!")
        
        loaded_agents = agency.config.load(config)
        
        for a in loaded_agents:
            a.agent = a.agent()
            self._agents[a.alias] = a
        
        return loaded_agents


    def formatError(self):
        """Return a string representing the last traceback.
        """
        exception, instance, tb = traceback.sys.exc_info()
        error = "".join(traceback.format_tb(tb))      
        return error


    def setUp(self):
        """Called to initialise all agents in our care.
        
        The load method must be called before this one.
        Otherwise ManagerError will be raised.
        
        """
        if self.agents < 1:
            self.log.warn("There are no agents to set up.")
            return
        
        for a in self._agents.values():
            if a.disabled == 'yes':
                # skip this agent.
                continue
            try:
                a.agent.setUp(a.config)
            except:
                self.log.exception("%s setUp error: " % a)
                sys.stderr.write("%s setUp error: %s" % (a, self.formatError()))
                if TESTING:
                    raise


    def tearDown(self):
        """Called to tearDown all agents in our care.
        
        Before calling a agents tearDown() its stop()
        method is called first.
        
        The load method must be called before this one.
        Otherwise ManagerError will be raised.
        
        """
        if self.agents < 1:
            self.log.warn("There are no agents to tear down.")
            return

        for a in self._agents.values():
            if a.disabled == 'yes':
                # skip this agent.
                continue
            try:
                if a.agent:
                    a.agent.tearDown()
            except:
                self.log.exception("%s tearDown error: " % a)
                sys.stderr.write("%s tearDown error: %s" % (a, self.formatError()))
                if TESTING:
                    raise


    def start(self):
        """Start all agents under our management
        
        The load method must be called before this one.
        Otherwise ManagerError will be raised.

        """
        if self.agents < 1:
            self.log.warn("There are no agents to start.")
            return

        for a in self._agents.values():
            if a.disabled == 'yes':
                # skip this agent.
                continue
            try:
                a.agent.start()
            except:
                self.log.exception("%s start error: " % a)
                sys.stderr.write("%s start error: %s" % (a, self.formatError()))
                if TESTING:
                    raise


    def stop(self):
        """Start all agents under our management
        
        The load method must be called before this one.
        Otherwise ManagerError will be raised.

        """
        if self.agents < 1:
            self.log.warn("There are no agents to stop.")
            return
        
        for a in self._agents.values():
            if a.disabled == 'yes':
                # skip this agent.
                continue
            try:
                a.agent.stop()
            except:
                self.log.exception("%s stop error: " % a)
                sys.stderr.write("%s stop error: %s" % (a, self.formatError()))
                if TESTING:
                    raise
        
    
    
