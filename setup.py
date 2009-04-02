"""
Project's setuptool configuration.

This should eggify and in theory upload to pypi without problems.

Oisin Mulvihill
2008-12-23

"""
from setuptools import setup, find_packages

Name='evasion-deviceaccess'
ProjecUrl="" #""
Version='1.0.0'
Author='Oisin Mulvihill'
AuthorEmail='oisinmulvihill at gmail dot com'
Maintainer=' Oisin Mulvihill'
Summary='This provides the hardware abstraction layer communicated with via the event system'
License=''
ShortDescription=Summary

# Recover the ReStructuredText docs:
fd = file("lib/deviceaccess/docs/deviceaccess.stx")
Description=fd.read()
fd.close()

TestSuite = 'deviceaccess.tests'

needed = [
    'configobj',
    'twisted', 
    'pydispatcher',
    
    'evasion-messenger',
]

# Include everything under deviceaccess. I needed to add a __init__.py
# to each directory inside deviceaccess I did this using the following
# handy command:
#
#  find lib/deviceaccess -type d -exec touch {}//__init__.py \;
#
# If new directories are added then I'll need to rerun this command.
#
EagerResources = [
#    'deviceaccess',
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
