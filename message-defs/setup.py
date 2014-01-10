from setuptools import setup, find_packages
setup(
  name='ospecorr-messagedefs',
  version = "0.1",
  py_modules=['phy_pb2', 'linklayer_pb2', 'drm_pb2', 'radioconfig_pb2', 'application_pb2'],
  
  author='Andre Puschmann',
  author_email='andre.puschmann@tu-ilmenau.de',
  url = "https://github.com/andrepuschmann/OSPECORR",
  license = "GPL",
)
