from setuptools import setup

setup(name='google-drive-helpers',
      version='0.1',
      description='Helper functions for google drive',
      url='https://github.com/jdoepfert/google-drive-helpers',
      license='MIT',
      packages=['gdrive_helpers'],
      install_requires=[
          'google-api-python-client',
      ],
      zip_safe=False)
