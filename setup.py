import os
from setuptools import setup
import sys

# Dynamically import __version__ at execution time
temp_path = os.path.join(os.path.abspath("."), 'datautils')
sys.path.insert(0, temp_path)
from version import __version__
sys.path.pop(0)


setup(
    name="datautils",
    version=__version__,
    url='https://github.com/anuponwa/datautils',
    author='Anupong Wannakrairot',
    description='Functionalities to connect to different cloud sources and clean data',
    packages=['datautils'],
    install_requires=[
        'google==3.0.0',
        'google-api-core==2.21.0',
        'google-auth==2.35.0',
        'google-cloud==0.34.0',
        'google-cloud-bigquery==3.26.0',
        'google-cloud-core==2.4.1',
        'google-cloud-secret-manager==2.21.0',
        'google-cloud-storage==2.18.2',
        'google-crc32c==1.6.0',
        'pandas'
    ],
    extras_require={
        'azure': [
            'databricks-sdk==0.36.0'
            'databricks-sql-connector==3.6.0'
        ],
    },
)