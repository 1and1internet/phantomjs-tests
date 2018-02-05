import unittest
import os
import docker


class Test1and1Common(unittest.TestCase):
    docker_client = None
    container = None

    @classmethod
    def setUpClass(cls):
        image_to_test = os.getenv("IMAGE_NAME")
        if image_to_test == "":
            raise Exception("I don't know what image to test")
        Test1and1Common.docker_client = docker.from_env()
        Test1and1Common.container = Test1and1Common.docker_client.containers.run(
            image=image_to_test,
            remove=True,
            detach=True
        )

    @classmethod
    def tearDownClass(cls):
        Test1and1Common.container.stop()

    def setUp(self):
        print ("\nIn method", self._testMethodName)
        self.container = Test1and1Common.container
        self._output = None
        self._exit_code = None

    def execRun(self, command):
        result = self.container.exec_run(command)
        if isinstance(result, tuple):
            self._exit_code = result[0]
            self._output = result[1].decode('utf-8')
        else:
            self._output = result.decode('utf-8')
        return self._output

    def assertPackageIsInstalled(self, packageName):
        op = self.execRun("dpkg -l %s" % packageName)
        self.assertTrue(
            op.find(packageName) > -1,
            msg="%s package not installed" % packageName
        )
