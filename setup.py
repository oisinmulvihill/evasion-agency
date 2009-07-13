"""
Project's setuptool configuration.

This should eggify and in theory upload to pypi without problems.

Oisin Mulvihill
2008-12-23

"""
from setuptools import setup, find_packages

Name='evasion-agency'
ProjecUrl="" #""
Version='1.0.0'
Author='Oisin Mulvihill'
AuthorEmail='oisinmulvihill at gmail dot com'
Maintainer=' Oisin Mulvihill'
Summary='This provides the hardware abstraction layer communicated with via the event system'
License=''
ShortDescription=Summary

# Recover the ReStructuredText docs:
fd = file("lib/agency/docs/agency.stx")
Description=fd.read()
fd.close()

TestSuite = 'agency.tests'

needed = [
    'Mako',
    'configobj',
    'pydispatcher',
    'evasion-messenger',
]

import sys
if not sys.platform.startswith('win'):
    needed.append('twisted')
    

# Include everything under agency. I needed to add a __init__.py
# to each directory inside agency I did this using the following
# handy command:
#
#  find lib/agency -type d -exec touch {}//__init__.py \;
#
# If new directories are added then I'll need to rerun this command.
#
EagerResources = [
#    'agency',
]

ProjectScripts = [
    'scripts/manager',
]

PackageData = {
    # Include every file type in the egg file:
    '': ['*.*'],
}

# Make exe versions of the scripts:
EntryPoints = {
}


setup(
#    url=ProjecUrl,
    zip_safe=False,
    name=Name,
    version=Version,
    author=Author,
    author_email=AuthorEmail,
    description=ShortDescription,
    long_description=Description,
    license=License,
    test_suite=TestSuite,
    scripts=ProjectScripts,
    install_requires=needed,
    packages=find_packages('lib'),
    package_data=PackageData,
    package_dir = {'': 'lib'},
    eager_resources = EagerResources,
    entry_points = EntryPoints,
)
