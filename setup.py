from glob import glob
from setuptools import setup, find_packages

# def git(cmd):
#     import subprocess    
#     out = subprocess.check_output("git %s"%cmd, shell=True)
#     return out.strip()

# def current_version():
#     branch = [x[2:] for x in git("branch").split('\n') if x.startswith('* ')][0]
#     if branch.startswith("release/"):
#         return open("RELEASE-VERSION").read().strip()
#     return git("describe --dirty")

setup(name = 'lbne-build',
      version = '0.7.5',
      description = 'Worch/waf tools to build LBNE software.',
      author = 'Brett Viren',
      author_email = 'brett.viren@gmail.com',
      license = 'GPLv2',
      url = 'http://github.com/LBNE/lbne-build',
      namespace_packages = ['worch'],
      packages = ['worch','worch.lbne','worch.lbne.tbbinst','worch.lbne.pandorasrc'],
      install_requires = [l for l in open("requirements.txt").readlines() if l.strip()],
      data_files = [
          ('share/worch/config/lbne', glob('config/*.cfg')),
          ('share/worch/patches/lbne', glob('patches/lbne/*.patch')),
          ('share/worch/wscripts/lbne', ['wscript']),
      ],
)
