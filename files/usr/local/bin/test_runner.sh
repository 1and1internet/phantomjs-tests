#!/usr/bin/env bash

function install_requirements
{
    if [ -f /tmp/tests/requirements.txt ]; then
        pip3 install -r /tmp/tests/requirements.txt
    fi
}

function wait_for_selenium_server
{
    count=3
    nc -z -w2 localhost 4444
    while [ 0 -ne $? ] && [ $count -gt 0 ]
    do
        count=$(expr $count - 1)
        sleep 1
        nc -z -w2 localhost 4444
    done
}

install_requirements
wait_for_selenium_server

[ -f /shared_storage/simple_service_information.json ] || \
    ln -sf /shared_storage/build-${CI_BUILD_NUMBER}-${CI_REPO/\//-}/simple_service_information.json /shared_storage/

run-parts --exit-on-error --regex "(^[a-zA-Z0-9_.]+)" /tmp/tests/selenium-tests/
exitval=$?

# kill supervisord after we exit, giving supervisord time to catch our exit
(sleep 1 && kill 1)&

echo "Test runner exiting with $exitval"
exit $exitval
