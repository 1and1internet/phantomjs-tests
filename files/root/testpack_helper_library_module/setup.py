from distutils.core import setup

setup(
    name='testpack_helper_library',
    version='1.0',
    packages=[
        'testpack_helper_library',
        'testpack_helper_library.unittests',
    ],
    package_dir={'': '.'},
    url='http://py.glo.gb/pkg/testpack_helper_library/',
    license='',
    author='Brian Wilkinson',
    author_email='brian.wilkinson@fasthosts.com',
    description='',
    install_requires=[
        "docker>=3.0.0,<4.0.0"
    ],
)
