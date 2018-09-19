import unittest
from selenium import webdriver
import os
import json
import base64
from collections import namedtuple
from testpack_helper_library.unittests.chrome_driver import ChromeDriver


HAVE_SERVICE_INFO = True
BUILD_FOLDER = os.getenv("BUILD_FOLDER")
SERVICE_INFO_FILENAME = "%s/simple_service_information.json" % BUILD_FOLDER
if not os.path.exists(SERVICE_INFO_FILENAME):
    HAVE_SERVICE_INFO = False


class TestTemplate1and1Common(unittest.TestCase):
    def setUp(self):
        print ("\nIn method", self._testMethodName)
        self._data_dict = None
        self._data_obj = None
        self._driver = None
        self._screenshot_folder = os.getenv("SCREENSHOTS")
        self.loadTemplateEndpoints()
        self._chrome_driver = ChromeDriver()

    def tearDown(self):
        if self._driver is not None:
            self._driver.quit()

    def loadTemplateEndpoints(self):
        if HAVE_SERVICE_INFO:
            with open(SERVICE_INFO_FILENAME, 'r') as fd:
                data_string = fd.read()

            self._data_dict = json.loads(data_string)
            self._data_obj = json.loads(data_string, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))

    def screenshot(self, name, driver):
        if self._screenshot_folder != "":
            filename = "%s/%s.png" % (self._screenshot_folder, name)
            print ("Writing screenshot %s" % filename)
            driver.get_screenshot_as_file(filename)

    def basicAuthCredentials(self, username, password):
        auth = "%s:%s" % (username, password)
        return base64.b64encode(auth.encode('utf-8')).decode('utf-8')

    def getDriver(self):
        self._driver = webdriver.PhantomJS()
        return self._driver

    def getDriverWithBasicAuth(self, username, password):
        basic_auth_creds = self.basicAuthCredentials(username, password)
        webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.Authorization'] = "Basic '%s'" % basic_auth_creds
        return self.getDriver()

    def getChromeDriver(self):
        return self._chrome_driver.getChromeDriver()