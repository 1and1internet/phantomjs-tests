import unittest
import os
import docker
import tarfile
from io import BytesIO
import time


class DockerTest1and1Common(unittest.TestCase):
    docker_client = None
    container = None
    container_details = None
    container_ip = None
    platform = "docker"
    endpoint = None
    chrome_driver = None

    @classmethod
    def setUpClass(cls, container_wait=3, network_mode="bridge", user=10000, working_dir="/var/www", ports={8080:8080}, environment={}):
        image_to_test = os.getenv("IMAGE_NAME")
        if image_to_test == "":
            raise Exception("I don't know what image to test")
        DockerTest1and1Common.docker_client = docker.from_env()
        DockerTest1and1Common.container = DockerTest1and1Common.docker_client.containers.run(
            image=image_to_test,
            remove=True,
            detach=True,
            network_mode=network_mode,
            user=user,
            ports=ports,
            working_dir="/var/www",
            environment=environment
        )
        details = docker.APIClient().inspect_container(container=DockerTest1and1Common.container.id)
        DockerTest1and1Common.container_ip = details['NetworkSettings']['IPAddress']
        for port in ports.keys():
            DockerTest1and1Common.endpoint = "http://" + DockerTest1and1Common.container_ip + ":" + str(port)
            break
        DockerTest1and1Common.container_details = details
        time.sleep(container_wait) # Try not to start testing before the container is ready

    @classmethod
    def tearDownClass(cls):
        DockerTest1and1Common.container.stop()
        if DockerTest1and1Common.chrome_driver != None:
            DockerTest1and1Common.chrome_driver.close()

    @classmethod
    def copy_test_files(cls, startfolder, relative_source, dest):
        # Change to the start folder
        pwd = os.getcwd()
        os.chdir(startfolder)
        # Tar up the request folder
        pw_tarstream = BytesIO()
        with tarfile.open(fileobj=pw_tarstream, mode='w:gz') as tf:
            tf.add(relative_source)
        # Copy the archive to the correct destination
        docker.APIClient().put_archive(
            container=DockerTest1and1Common.container.id,
            path=dest,
            data=pw_tarstream.getvalue()
        )
        # Change back to original folder
        os.chdir(pwd)

    def setUp(self):
        print ("\nIn method", self._testMethodName)
        self.container = DockerTest1and1Common.container
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

    def exec(self, command):
        return self.execRun(command=command)

    def assertPackageIsInstalled(self, packageName):
        op = self.execRun("dpkg -l %s" % packageName)
        self.assertTrue(
            op.find(packageName) > -1,
            msg="%s package not installed" % packageName
        )

    def getChromeDriver(self):
        if DockerTest1and1Common.chrome_driver is None:
            from testpack_helper_library.unittests.chrome_driver import ChromeDriver
            DockerTest1and1Common.chrome_driver = ChromeDriver()
        return DockerTest1and1Common.chrome_driver.getChromeDriver()