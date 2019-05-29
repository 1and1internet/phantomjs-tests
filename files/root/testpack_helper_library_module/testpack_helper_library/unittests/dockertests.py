from testpack_helper_library.unittests.docker_image_test import DockerTest1and1Common
from testpack_helper_library.unittests.kube_image_test import KubeTest1and1Common
import os

test_platform = os.getenv("TEST_PLATFORM", "docker")

if test_platform == "docker":
    print("Using DockerTest1and1Common")
    Test1and1Common = DockerTest1and1Common
else:
    print("Using KubeTest1and1Common")
    Test1and1Common = KubeTest1and1Common
