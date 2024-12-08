from setuptools import setup, find_packages


setup(
    name='do-data-utils',
    version='2.3.1',
    url='https://github.com/anuponwa/do-data-utils',
    author='Anupong Wannakrairot',
    description='Functionalities to interact with Google and Azure, and clean data',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'databricks-sdk==0.36.0',
        'databricks-sql-connector==3.6.0',
        'google==3.0.0',
        'google-api-core==2.21.0',
        'google-auth==2.35.0',
        'google-cloud==0.34.0',
        'google-cloud-bigquery==3.26.0',
        'google-cloud-core==2.4.1',
        'google-cloud-secret-manager==2.21.0',
        'google-cloud-storage==2.18.2',
        'google-crc32c==1.6.0',
        'pandas',
        'openpyxl==3.1.5',
        'XlsxWriter==3.2.0',
    ],
    classifiers=[
        # Project maturity
        'Development Status :: 4 - Beta',

        # Intended audience
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Information Technology',

        # Topics (domain of your package)
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Database :: Database Engines/Servers',  # Since you mentioned working with data sources

        # License (match your chosen license)
        'License :: OSI Approved :: MIT License',

        # Supported programming languages and Python versions
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',  # General Python 3 support
        'Programming Language :: Python :: 3.12',

        # Operating systems
        'Operating System :: OS Independent',
    ]
)