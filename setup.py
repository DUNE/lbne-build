from glob import glob
from setuptools import setup, find_packages

toolname = 'lbne'
myshare = 'share/worch/' + toolname
setup(name = 'lbne-build',
      version = '0.0',
      description = 'Worch/waf tools to build LBNE software.',
      author = 'Brett Viren',
      author_email = 'brett.viren@gmail.com',
      license = 'GPLv2',
      url = 'http://github.com/LBNE/lbne-build',
      namespace_packages = ['worch'],
      packages = ['worch','worch.lbne','worch.lbne.tbbinst'],
      install_requires = [
          'worch-ups >= 0.1',
      ],
      dependency_links = [
          'https://github.com/brettviren/worch-ups/archive/0.1.tar.gz#egg=worch-ups-0.1',
      ],
      data_files = [('share/worch/config/lbne', glob('config/*.cfg')),
                    ('share/worch/patches/lbne', glob('patches/*.patch'))],
)
