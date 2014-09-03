from glob import glob
from setuptools import setup, find_packages

setup(name = 'lbne-build',
      version = '0.3.1',
      description = 'Worch/waf tools to build LBNE software.',
      author = 'Brett Viren',
      author_email = 'brett.viren@gmail.com',
      license = 'GPLv2',
      url = 'http://github.com/LBNE/lbne-build',
      namespace_packages = ['worch'],
      packages = ['worch','worch.lbne','worch.lbne.tbbinst'],
      install_requires = [l for l in open("requirements.txt").readlines() if l.strip()],
      data_files = [
          ('share/worch/config/lbne', glob('config/*.cfg')),
          ('share/worch/patches/lbne', glob('patches/lbne/*.patch')),
          ('share/worch/wscripts/lbne', ['wscript']),
      ],
)
