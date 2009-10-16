import logging

import agent
import agency
import config
import agents
import manager
from agency import *
from config import ConfigError
from manager import ManagerError


def get_log():
    return logging.getLogger('manager')
