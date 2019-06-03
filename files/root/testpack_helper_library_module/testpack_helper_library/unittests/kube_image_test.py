import unittest
import os
import tarfile
from io import BytesIO
import time
import random
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
import requests


class KubeTest1and1Common(unittest.TestCase):
    container_ip = None
    platform = "kubernetes"
    namespace = None
    pod_name = None
    route_url = ""
    endpoint = ""
    chrome_driver = None

    @classmethod
    def setUpClass(cls, container_wait=5, network_mode="not_used_here", user=10000, working_dir="/var/www", ports={8080:8080}, environment={}):
        image_to_test = os.getenv("IMAGE_NAME")
        route_url = os.getenv("ROUTE_URL", "")
        KubeTest1and1Common.route_url = route_url
        namespace = os.getenv("K8S_TEST_NAMESPACE")
        KubeTest1and1Common.namespace = namespace
        KubeTest1and1Common.set_pod_name(image_name=image_to_test)
        if image_to_test == "":
            raise Exception("I don't know what image to test")
        config.load_kube_config()
        api = client.CoreV1Api()
        pod_manifest = KubeTest1and1Common.get_pod_manifest(image=image_to_test, ports=ports, envars=environment)
        api.create_namespaced_pod(namespace=namespace, body=pod_manifest)
        if route_url:
            try:
                api.create_namespaced_service(namespace=namespace, body=KubeTest1and1Common.get_service_manifest(ports=ports))
            except Exception:
                KubeTest1and1Common.cleanup_pod()
                raise
            try:
                KubeTest1and1Common.create_route(ports=ports)
                KubeTest1and1Common.wait_for_route()
            except Exception:
                KubeTest1and1Common.cleanup_pod()
                KubeTest1and1Common.cleanup_service()
                raise

        response = api.read_namespaced_pod(name=KubeTest1and1Common.pod_name, namespace=KubeTest1and1Common.namespace)
        while response.status.phase == 'Pending':
            time.sleep(1)
            response = api.read_namespaced_pod(name=KubeTest1and1Common.pod_name, namespace=KubeTest1and1Common.namespace)

        if response.status.phase != 'Running':
            raise Exception("Post is not running %s" % str(response.status))

        if route_url:
            KubeTest1and1Common.container_ip = KubeTest1and1Common.endpoint # Use route
        else:
            KubeTest1and1Common.container_ip = response.status.pod_ip
        time.sleep(container_wait)

    @classmethod
    def set_pod_name(cls, image_name):
        KubeTest1and1Common.pod_name = "tpf-" + image_name.split('/')[-1].replace('.', '') + "-" + str(random.randint(1,9999)).rjust(4,"0")
        KubeTest1and1Common.pod_name = (
            KubeTest1and1Common.pod_name
                .replace('debian-', 'd')
                .replace('ubuntu-','u')
                .replace('apache-', 'ap')
                .replace('nginx-', 'ngnx')
                .replace('wordpress-', 'wp')
                .replace('passenger', 'psngr')
        )

    @classmethod
    def get_pod_manifest(cls, image, ports, envars):
        name = KubeTest1and1Common.pod_name
        envar_list = []
        for k, v in envars.items():
            envar = client.V1EnvVar(name=k, value=v)
            envar_list.append(envar)

        port_list = []
        for k, v in ports.items():
            port = client.V1ContainerPort(
                    container_port=v,
                    protocol="TCP"
                )
            port_list.append(port)

        metadata = client.V1ObjectMeta(
            name=name,
            labels={
                "pod_name": KubeTest1and1Common.pod_name,
                "tier": "front",
            }
        )

        security_context = client.V1SecurityContext(
            run_as_user=10000
        )

        container = client.V1Container(
            name=name,
            image=image,
            env=envar_list,
            ports=port_list,
            security_context=security_context
        )
        spec = client.V1PodSpec(
            restart_policy="Never",
            dns_policy="ClusterFirst",
            containers=[container]
        )
        return client.V1Pod(
            api_version="v1",
            kind="Pod",
            metadata=metadata,
            spec=spec
        )

    @classmethod
    def get_service_manifest(cls, ports):
        metadata = client.V1ObjectMeta(name=KubeTest1and1Common.pod_name)

        port_list = []
        for k, v in ports.items():
            port = client.V1ServicePort(
                    target_port=v,
                    port=k,
                    protocol="TCP",
                    name=str(k) + '-tcp'
                )
            port_list.append(port)

        spec = client.V1ServiceSpec(
            ports=port_list,
            selector={"pod_name": KubeTest1and1Common.pod_name},
            type="ClusterIP",
            session_affinity="None"
        )

        return client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=metadata,
            spec=spec
        )

    @classmethod
    def create_route(cls, ports):
        headers, cluster_url = KubeTest1and1Common.get_kube_config_for_requests()

        hostname = KubeTest1and1Common.pod_name + KubeTest1and1Common.route_url
        KubeTest1and1Common.endpoint = "http://" + hostname

        portname="default-port"
        for port in ports.keys():
            portname = str(port) + '-tcp'

        route = {
            "apiVersion": "v1",
            "kind": "Route",
            "metadata": {
                "labels": { "pod_name": KubeTest1and1Common.pod_name },
                "name": KubeTest1and1Common.pod_name,
                "namespace": KubeTest1and1Common.namespace,
            },
            "spec": {
                "host": hostname,
                "port": {
                    "targetPort": portname
                },
                "to": {
                    "kind": "Service",
                    "name": KubeTest1and1Common.pod_name
                }
            }
        }

        response = requests.post(
            url=cluster_url + "/oapi/v1/namespaces/%s/routes" % (KubeTest1and1Common.namespace),
            headers=headers,
            json=route
        )

        if response.status_code > 299:
            raise Exception("create_route: %d : %s" % (response.status_code, response.text))

    @classmethod
    def wait_for_route(cls):
        retries = 12
        result = requests.get(KubeTest1and1Common.endpoint)
        while result.status_code != 200 and retries > 0:
            time.sleep(5)
            result = requests.get(KubeTest1and1Common.endpoint)
            retries -= 1
        if retries <= 0:
            raise Exception("Gave up waiting for route")

    @classmethod
    def get_kube_config_for_requests(cls):
        config_file = os.path.expanduser(os.environ.get('KUBECONFIG', '~/.kube/config'))
        kube_config = config.kube_config._get_kube_config_loader_for_yaml_file(config_file)
        token = kube_config._user.value['token']
        cluster_url = kube_config._cluster['server']
        headers = {
            "Authorization": "Bearer " + token,
            "Accept": "application/json",
            "Content": "application/json"
        }
        return (headers, cluster_url)

    @classmethod
    def tearDownClass(cls):
        KubeTest1and1Common.cleanup_pod()
        KubeTest1and1Common.cleanup_service()
        KubeTest1and1Common.cleanup_route()
        if KubeTest1and1Common.chrome_driver != None:
            KubeTest1and1Common.chrome_driver.close()

    @classmethod
    def cleanup_pod(cls):
        api = client.CoreV1Api()
        delete_options = client.V1DeleteOptions()
        try:
            api.delete_namespaced_pod(
                name=KubeTest1and1Common.pod_name,
                namespace=KubeTest1and1Common.namespace,
                body=delete_options
            )
        except ApiException as e:
            print("Exception deleting pod %s" % e)

    @classmethod
    def cleanup_service(cls):
        if KubeTest1and1Common.route_url:
            api = client.CoreV1Api()
            delete_options = client.V1DeleteOptions()
            try:
                api.delete_namespaced_service(
                    name=KubeTest1and1Common.pod_name,
                    namespace=KubeTest1and1Common.namespace,
                    body=delete_options
                )
            except ApiException as e:
                print("Exception deleting service %s" % e)

    @classmethod
    def cleanup_route(cls):
        if KubeTest1and1Common.route_url:
            headers, cluster_url = KubeTest1and1Common.get_kube_config_for_requests()
            route_url = cluster_url + "/oapi/v1/namespaces/%s/routes/%s"
            response = requests.delete(
                url=route_url % (KubeTest1and1Common.namespace, KubeTest1and1Common.pod_name),
                headers=headers
            )
            if response.status_code > 299:
                raise Exception("cleanup_route: %d : %s" % (response.status_code, response.text))

    @classmethod
    def copy_test_files(cls, startfolder, relative_source, dest):
        api = client.CoreV1Api()

        # Change to the start folder
        pwd = os.getcwd()
        os.chdir(startfolder)
        # Tar up the request folder
        pw_tarstream = BytesIO()
        with tarfile.open(fileobj=pw_tarstream, mode='w:') as tf:
            tf.add(relative_source)
        # Copy the archive to the correct destination

        # Copying file using interactive exec
        # This snippet adapted from https://github.com/kubernetes-client/python/issues/476
        exec_command = ['tar', 'xvf', '-', '-C', dest]
        resp = stream(
            api.connect_get_namespaced_pod_exec,
            name=KubeTest1and1Common.pod_name,
            namespace=KubeTest1and1Common.namespace,
            command=exec_command,
            stderr=True, stdin=True,
            stdout=True, tty=False,
            _preload_content=False
        )

        stdouts = []
        stderrs = []
        tarfiles = [pw_tarstream.getvalue().decode('utf-8')]
        while resp.is_open():
            resp.update(timeout=1)
            if resp.peek_stdout():
                stdouts.append(resp.read_stdout())
            if resp.peek_stderr():
                stderrs.append(resp.read_stderr())
            if tarfiles:
                c = tarfiles.pop(0)
                resp.write_stdin(c)
            else:
                break
        resp.close()

        # Change back to original folder
        os.chdir(pwd)

    def setUp(self):
        print ("\nIn method", self._testMethodName)
        self.container = self # Not a container at all, but all our tests expect this
        self._output = None
        self._exit_code = None

    def exec_run(self, command):
        # A lot of image tests expect to be able to call self.container.exec_run, which would
        # have been a direct use of the docker api before, but we are not in docker land anymore.
        return self.execRun(command=command)

    def execRun(self, command):
        result =  self.exec(command=command)
        return result + '\n'

    def exec(self, command):
        # This is not interactive, it just runs a command and passes back the result
        # See https://github.com/kubernetes-client/python/blob/master/examples/exec.py - for exec examples
        if not isinstance(command, list):
            command = ["/bin/bash", "-c", command]

        api = client.CoreV1Api()
        return stream(
            api.connect_get_namespaced_pod_exec,
            name=KubeTest1and1Common.pod_name,
            namespace=KubeTest1and1Common.namespace,
            command=command,
            stderr=True,
            stdout=True,
            stdin=False,
            tty=False
        )

    def logs(self):
        # Annoyingly, all our tests currently expect binary results from this, but want a string
        # We have a string, but need to encode it.
        return self.logstr().encode('utf-8')

    def logstr(self):
        api = client.CoreV1Api()
        return api.read_namespaced_pod_log(name=KubeTest1and1Common.pod_name, namespace=KubeTest1and1Common.namespace)

    def assertPackageIsInstalled(self, packageName):
        op = self.execRun("dpkg -l %s" % packageName)
        self.assertTrue(
            op.find(packageName) > -1,
            msg="%s package not installed" % packageName
        )

    def getChromeDriver(self):
        if KubeTest1and1Common.chrome_driver is None:
            from testpack_helper_library.unittests.chrome_driver import ChromeDriver
            KubeTest1and1Common.chrome_driver = ChromeDriver()
        return KubeTest1and1Common.chrome_driver.getChromeDriver()