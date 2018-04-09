import os
import setuptools

setuptools.setup(
  name='dataflow-snippets',
  version='0.0.1',
  install_requires=[
    'pygeoip','geoip2',],
  packages=setuptools.find_packages(),
  package_data={
   'resources': ['GeoIP.dat','GeoIP2-City.mmdb',],     # All files from folder A
   },
)