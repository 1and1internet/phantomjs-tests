import getpass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class ChromeDriver:
    def __init__(self):
        self._chrome_driver = None

    def getChromeDriver(self, no_sandbox=False):
        if self._chrome_driver is None:
            chrome_options = Options()
            chrome_options.add_argument("--headless")

            if getpass.getuser() == 'root' or no_sandbox:
                chrome_options.add_argument("--no-sandbox")
            self._chrome_driver = webdriver.Chrome(options=chrome_options)
        return self._chrome_driver
