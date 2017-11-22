#!/usr/bin/env python3

import unittest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import os
import json


class TestReference(unittest.TestCase):
    def setUp(self):
        # phantomjs as been added to PATH, so this works...
        self.driver = webdriver.PhantomJS('phantomjs')
        print ("\nIn method", self._testMethodName)
        self.screenshot_folder = os.getenv("SCREENSHOTS")
        self.build_folder = os.getenv("BUILD_FOLDER")
        self.endpoint_data = self.loadTemplateEndpoints()

    def loadTemplateEndpoints(self):
        fname = "%s/simple_service_information.json" % self.build_folder
        with open(fname, 'r') as fd:
            return json.load(fd)

    def screenshot(self, name):
        if self.screenshot_folder != "":
            filename = "%s/%s.png" % (self.screenshot_folder, name)
            print ("Writing screenshot %s" % filename)
            self.driver.get_screenshot_as_file(filename)

    # <tests to run>

    def test_ReferenceTest(self):
        # Run tests using typical selenium client commands
        pass

    # </tests to run>

    def tearDown(self):
        self.driver.quit()

if __name__ == '__main__':
    unittest.main(verbosity=1)
