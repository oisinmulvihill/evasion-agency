"""
"""
import unittest


import deviceaccess
import deviceaccess.config as config


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


class deviceaccessTest(unittest.TestCase):

    def setUp(self):
        # unittesting reset:
        deviceaccess.node._reset()

        # unittesting reset:
        deviceaccess.manager.shutdown()

#    def testABC(self):
#        self.assertEquals(1,0,"buildbot email test")

    def testmanager(self):
        """Test the Manager class.
        """
        self.assertEquals(deviceaccess.manager.devices, 0)

        # Make sure you can't call the following without calling load:
        self.assertRaises(deviceaccess.ManagerError, deviceaccess.manager.tearDown)
        self.assertRaises(deviceaccess.ManagerError, deviceaccess.manager.setUp)
        self.assertRaises(deviceaccess.ManagerError, deviceaccess.manager.start)
        self.assertRaises(deviceaccess.ManagerError, deviceaccess.manager.stop)

        # shutdown should be ok though:
        deviceaccess.manager.shutdown()

        
        td1 = TestDevice()
        td2 = TestDevice()
        td3 = TestDevice()
        
        test_config = """
        
        [testswipe]
        # first card swipe
        alias = 1
        dev_class = 'swipe'
        driver = 'testing.fake'
        interface = 127.0.0.1
        port = 8810
        
        [magtekusbhid]
        # second card swipe
        alias = 2
        dev_class = 'swipe'
        driver = 'testing.fake'
        interface = 127.0.0.1
        port = 8810
        
        [tsp700]
        # first printer
        alias = 1
        dev_class = 'printer'
        driver = 'testing.fake'
        interface = 127.0.0.1
        port = 8810
        
        """

        devices = deviceaccess.manager.load(test_config)
        self.assertEquals(len(devices), 3)
        
        dev1 = deviceaccess.manager.dev('swipe/1')
        self.assertEquals(dev1.node, '/dev/swipe/testswipe/1')
        dev1.device.setParent(td1)

        dev2 = deviceaccess.manager.dev('swipe/2')
        self.assertEquals(dev2.node, '/dev/swipe/magtekusbhid/2')
        dev2.device.setParent(td2)

        dev3 = deviceaccess.manager.dev('printer/1')
        self.assertEquals(dev3.node, '/dev/printer/tsp700/1')
        dev3.device.setParent(td3)

        # Call all the methods and check that the individual
        # device methods have also been called:
        deviceaccess.manager.setUp()
        self.assertEquals(td1.setUpCalled, True)
        self.assertEquals(td2.setUpCalled, True)
        self.assertEquals(td3.setUpCalled, True)

        deviceaccess.manager.start()
        self.assertEquals(td1.startCalled, True)
        self.assertEquals(td2.startCalled, True)
        self.assertEquals(td3.startCalled, True)

        deviceaccess.manager.stop()
        self.assertEquals(td1.stopCalled, True)
        self.assertEquals(td2.stopCalled, True)
        self.assertEquals(td3.stopCalled, True)

        deviceaccess.manager.tearDown()
        self.assertEquals(td1.tearDownCalled, True)
        self.assertEquals(td2.tearDownCalled, True)
        self.assertEquals(td3.tearDownCalled, True)


    def testdeviceaccessNodes(self):
        """Test the device node id generation.
        """
        
        # check that all the device nodes have no entries:
        for dev_class in deviceaccess.DEVICE_CLASSES:
            count = deviceaccess.node.get(dev_class)
            self.assertEquals(count, 0)

        self.assertRaises(ValueError, deviceaccess.node.add, 'unknown dev class', 'testing' ,'1')

        # test generation of new ids
        node_id, alias_id = deviceaccess.node.add('swipe', 'testing', '12')
        self.assertEquals(node_id, '/dev/swipe/testing/1')
        self.assertEquals(alias_id, '/dev/swipe/12')

        node_id, alias_id = deviceaccess.node.add('swipe', 'testing', '23')
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
        c.driver = 'testing.swipe'
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
        driver = 'testing.swipe'
        interface = 127.0.0.1
        port = 8810
        
        """
        def check(node, alias):
            pass
         
        devices = deviceaccess.config.load(test_config, check)
        dev1 = devices[0]
        
        self.assertEquals(dev1.alias, '/dev/swipe/1')
        self.assertEquals(dev1.node, '/dev/swipe/testswipe/1')        
        self.assertEquals(dev1.name, 'testswipe')        
                
        import deviceaccess.drivers.testing.swipe as swipe
        self.assertEquals(dev1.driver, swipe.Device)

        self.assertEquals(dev1.interface, '127.0.0.1')        
        self.assertEquals(dev1.port, '8810')        


    def testBadConfigurationCatching(self):
        """Test that bad configurations are caught.
        """
        test_config = """
        [testswipe]
        alias = 1
        dev_class = 'swipe12'           # unknow dev_class
        driver = 'testing.swipe'
        interface = 127.0.0.1
        port = 8810
        
        """

        self.assertRaises(deviceaccess.ConfigError, deviceaccess.config.load, test_config)


        test_config = """
        [testswipe]
        alias = 1
        dev_class = 'swipe'           
        driver = 'testing.doesnotexits'     # unknown driver module
        interface = 127.0.0.1
        port = 8810
        
        """

        self.assertRaises(deviceaccess.ConfigError, deviceaccess.config.load, test_config)

        # test duplicated aliases i.e. the two same dev_class entries have been
        # given the same alias
        test_config = """
        [testswipe]
        alias = 1                    # first alias: OK
        dev_class = 'swipe'           
        driver = 'testing.swipe'
        interface = 127.0.0.1
        port = 8810

        [magtek]
        alias = 1                   # Duplicate alias!
        dev_class = 'swipe'           
        driver = 'testing.fake'     
        
        """

        self.assertRaises(deviceaccess.ConfigError, deviceaccess.config.load, test_config)
        
        
        
