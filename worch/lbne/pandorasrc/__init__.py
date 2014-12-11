#!/usr/bin/env python
'''A "tarball"-like feature to which pulls from a VCS instead.  It
provides the "seturl" and "unpack" steps.  There is no "download" step
like "tarball" as the checkout/clone is direct to the source
directory.

'''
import os.path as osp
from waflib.TaskGen import feature
import waflib.Logs as msg

from orch.wafutil import exec_command

import orch.features
orch.features.register_defaults(
    'pandorasrc', 
    source_urlfile = '{urlfile_dir}/{package}-{version}.url',
    source_unpacked = '{package}-{version}',
    source_unpacked_path = '{source_dir}/{source_unpacked}',
    unpacked_target = 'Makefile',
    source_unpacked_target = '{source_unpacked_path}/{unpacked_target}',

    vcs_flavor = 'svn',         # git,hg,svn,cvs 
    vcs_tag = 'v00-17',
    vcs_module = '',            # used by cvs
)

def single_cmd_rule(func):
    def rule(tgen):
        def task_func(task):
            cmd = func(tgen)
            return exec_command(task, cmd)
        tgen.step('unpack',
                  rule = task_func,
                  source = tgen.worch.source_urlfile,
                  target = tgen.worch.source_unpacked_target)
    return rule


@single_cmd_rule
def do_svn(tgen):
    tag = tgen.worch.get('vcs_tag', '')
    pat = "svn --non-interactive --trust-server-cert checkout {source_url}/PandoraPFANew/tags/{vcs_tag_opt} {source_unpacked};svn --non-interactive --trust-server-cert checkout {source_url}/PandoraSDK/tags/{vcs_tag_opt} {source_unpacked}/PandoraSDK;svn --non-interactive --trust-server-cert checkout {source_url}/PandoraMonitoring/tags/{vcs_tag_opt} {source_unpacked}/PandoraMonitoring"
    return tgen.worch.format(pat, vcs_tag_opt = tag)


@feature('pandorasrc')
def feature_pandorasrc(tgen):

    tgen.step('seturl', 
              rule = "echo '%s' > %s" % (tgen.worch.source_url, tgen.worch.source_urlfile),
              update_outputs = True,
              target = tgen.worch.source_urlfile)

    flavor = tgen.worch.vcs_flavor
    doer = eval('do_%s' % flavor)
    doer(tgen)
    return
    
    
