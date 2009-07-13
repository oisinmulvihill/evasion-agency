"""
"""
import unittest


import agency
import agency.config as config


class TestDevice(object):
    """Used to check the device manager is calling the correct methods.
    """
    def __init__(self):
        self.setUpCalled = False
        self.tearDownCalled = False
        self.startCalled = False
        self.stopCalled = False
        self.queryCalled = False

    def setUp(self, config):
        self.setUpCalled = True
    
    def tearDown(self):
        self.tearDownCalled = True

    def start(self):
        self.startCalled = True
        
    def stop(self):
        self.stopCalled = True

    def query(self):
        self.queryCalled = True


class agencyTest(unittest.TestCase):

    def setUp(self):
        # unittesting reset:
        agency.node._reset()

        # unittesting reset:
        agency.manager.shutdown()

#    def testABC(self):
#        self.assertEquals(1,0,"buildbot email test")

    def testmanager(self):
        """Test the Manager class.
        """
        self.assertEquals(agency.manager.devices, 0)

        # Make sure you can't call the following without calling load:
        self.assertRaises(agency.ManagerError, agency.manager.tearDown)
        self.assertRaises(agency.ManagerError, agency.manager.setUp)
        self.assertRaises(agency.ManagerError, agency.manager.start)
        self.assertRaises(agency.ManagerError, agency.manager.stop)

        # shutdown should be ok though:
        agency.manager.shutdown()

        
        td1 = TestDevice()
        td2 = TestDevice()
        td3 = TestDevice()
        
        test_config = """
        
        [testswipe]
        # first card swipe
        alias = 1
        dev_class = 'swipe'
        driver = 'agency.drivers.testing.fake'
        interface = 127.0.0.1
        port = 8810
        
        [magtekusbhid]
        # second card swipe
        alias = 2
        dev_class = 'swipe'
        driver = 'agency.drivers.testing.fake'
        interface = 127.0.0.1
        port = 8810
        
        [tsp700]
        # first printer
        alias = 1
        dev_class = 'printer'
        driver = 'agency.drivers.testing.fake'
        interface = 127.0.0.1
        port = 8810
        
        """

        devices = agency.manager.load(test_config)
        self.assertEquals(len(devices), 3)
        
        dev1 = agency.manager.dev('swipe/1')
        self.assertEquals(dev1.node, '/dev/swipe/testswipe/1')
        dev1.device.setParent(td1)

        dev2 = agency.manager.dev('swipe/2')
        self.assertEquals(dev2.node, '/dev/swipe/magtekusbhid/2')
        dev2.device.setParent(td2)

        dev3 = agency.manager.dev('printer/1')
        self.assertEquals(dev3.node, '/dev/printer/tsp700/1')
        dev3.device.setParent(td3)

        # Call all the methods and check that the individual
        # device methods have also been called:
        agency.manager.setUp()
        self.assertEquals(td1.setUpCalled, True)
        self.assertEquals(td2.setUpCalled, True)
        self.assertEquals(td3.setUpCalled, True)

        agency.manager.start()
        self.assertEquals(td1.startCalled, True)
        self.assertEquals(td2.startCalled, True)
        self.assertEquals(td3.startCalled, True)

        agency.manager.stop()
        self.assertEquals(td1.stopCalled, True)
        self.assertEquals(td2.stopCalled, True)
        self.assertEquals(td3.stopCalled, True)

        agency.manager.tearDown()
        self.assertEquals(td1.tearDownCalled, True)
        self.assertEquals(td2.tearDownCalled, True)
        self.assertEquals(td3.tearDownCalled, True)


    def testagencyNodes(self):
        """Test the device node id generation.
        """
        
        # check that all the device nodes have no entries:
        for dev_class in agency.DEVICE_CLASSES:
            count = agency.node.get(dev_class)
            self.assertEquals(count, 0)

        self.assertRaises(ValueError, agency.node.add, 'unknown dev class', 'testing' ,'1')

        # test generation of new ids
        node_id, alias_id = agency.node.add('swipe', 'testing', '12')
        self.assertEquals(node_id, '/dev/swipe/testing/1')
        self.assertEquals(alias_id, '/dev/swipe/12')

        node_id, alias_id = agency.node.add('swipe', 'testing', '23')
        self.assertEquals(node_id, '/dev/swipe/testing/2')
        self.assertEquals(alias_id, '/dev/swipe/23')

    
    def testConfigContainer(self):
        """Verify the behaviour of the test container.
        """
        c = config.Container()
        
        # Check it catches that I haven't provided the required fields:
        self.assertRaises(config.ConfigError, c.check)
        
        c.node = '/dev/swipe/testing/1'
        c.alias = '/dev/swipe/1'
        c.dev_class = 'swipe'
        c.driver = 'devicaccess.drivers.testing.swipe'
        c.name = 'testingswipe'
        
        # This should not now raise ConfigError.
        c.check()
    
    
    def testConfiguration(self):
        """Test the configuration catches the required fields.
        """
        test_config = """
        
        [testswipe]
        alias = 1
        dev_class = 'swipe'
        driver = 'agency.drivers.testing.swipe'
        interface = 127.0.0.1
        port = 8810
        
        """
        def check(node, alias):
            pass
         
        devices = agency.config.load(test_config, check)
        dev1 = devices[0]
        
        self.assertEquals(dev1.alias, '/dev/swipe/1')
        self.assertEquals(dev1.node, '/dev/swipe/testswipe/1')        
        self.assertEquals(dev1.name, 'testswipe')        
                
        self.assertEquals(dev1.interface, '127.0.0.1')        
        self.assertEquals(dev1.port, '8810')        


    def testBadConfigurationCatching(self):
        """Test that bad configurations are caught.
        """
        test_config = """
        [testswipe]
        alias = 1
        dev_class = 'swipe12'           # unknow dev_class
        driver = 'agency.drivers.testing.swipe'
        interface = 127.0.0.1
        port = 8810
        
        """

        self.assertRaises(agency.ConfigError, agency.config.load, test_config)


        test_config = """
        [testswipe]
        alias = 1
        dev_class = 'swipe'           
        driver = 'agency.drivers.testing.doesnotexits'     # unknown driver module
        interface = 127.0.0.1
        port = 8810
        
        """
        self.assertRaises(ImportError, agency.config.load, test_config)

        # test duplicated aliases i.e. the two same dev_class entries have been
        # given the same alias
        test_config = """
        [testswipe]
        alias = 1                    # first alias: OK
        dev_class = 'swipe'           
        driver = 'agency.drivers.testing.swipe'
        interface = 127.0.0.1
        port = 8810

        [magtek]
        alias = 1                   # Duplicate alias!
        dev_class = 'swipe'           
        driver = 'agency.drivers.testing.fake'     
        
        """

        self.assertRaises(agency.ConfigError, agency.config.load, test_config)
        
        
        
