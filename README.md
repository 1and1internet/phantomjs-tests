# Testpack Framework

The intention of this image is to replace our previous 'rspec' test framework which was not well supported. It is intended to be used as part of a CI tool (in our case drone).

## Instructions for use

The image under test should be mounted under /mnt .

It should contain a folder structure like:
```bash
testpack/
├── requirements.txt
└── scripts
    └── myWebTests.py
```

In this case there is a requirements.txt file that contains the python module requirements of the test script 'myWebTests.py', such as 'selenium'.

## Sample
The file 'testReference.py' is provided as an example of how a test might be structured.

## PhantomJS, Selenium and Python 3

PhantomJS is a headless webkit, i.e. it can be used to open and manipulate websites without a browser. This is baked into the framework by default.

Selenium provides us with a client that gives us an easier and more powerful way of using PhantomJS. It is not part of this image but the sample reference demonstrates how tests can be written using these two in combination. It can be installed along with the tests by adding it to the requirements.txt file.

Currently, only python3 is baked into this framework. There is no reason why it could not support other scripting languages / versions as the need arises. In theory, any executable under the 'scripts' folder could be run, however, adaptations may be necessary.
