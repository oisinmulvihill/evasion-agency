#!/usr/bin/env python
#
# Oisin Mulvihill
# 2008-12-23
#
import os
import sys
import nose
import os.path
import logging


current = os.path.abspath(os.path.curdir)

package_paths = [
    './lib',
]
sys.path.extend(package_paths)

# Let nosetest run free for the moment.
#
# Only bother looking for tests in these locations:
# (Note: these need to be absolute paths)
#test_paths = [
#    os.path.join(current, 'tests'),
#]
#env = os.environ
#env['NOSE_WHERE'] = ','.join(test_paths)

# Set up logging so we don't get any logger not found messages:
import deviceaccess.utils
#deviceaccess.utils.log_init(logging.DEBUG)
deviceaccess.utils.log_init(logging.CRITICAL)

result = nose.core.TestProgram().success
nose.result.end_capture()


