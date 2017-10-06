from setuptools import setup, find_packages

setup(
        name='reskeeper',
        version='0.1.0',
        packages=['reskeeper'],
        install_requires=[
            'google-cloud==0.27.0',
            'PyYAML',
            'slackweb'],
        )

