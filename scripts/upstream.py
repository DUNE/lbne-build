#!/usr/bin/env python

import os
import sys
import click
from subprocess import check_output, check_call
from collections import defaultdict

@click.group()
@click.option('-C','--directory',default='.',
              help='Specify a working directory (def=".").')
@click.pass_context
def cli(ctx, directory):
    '''
    Chase upstream following the "Chasing Upstream Git" policy.

    Command-level help with "<command> --help".

    '''
    ctx.obj['workdir'] = os.path.realpath(directory)
    return

suite_packages = dict(
    art = 'cpp0x cetlib fhicl-cpp messagefacility art'.split(),
    lar = 'larana lardata larevt larpandora larsim larcore lareventdisplay larexamples larreco larsoft'.split(),
    lbn = ['lbnecode'],
)

def _hashtags(directory):
    cmd = "git show-ref --tags -d"
    output = check_output(cmd, shell=True, cwd=directory)
    ht = defaultdict(list)
    for line in output.split('\n'):
        line = line.strip()
        if not line: 
            continue
        gh, label = line.split()
        if label.endswith('^{}'):
            ht[gh].append(label[:-3].split('/')[-1])
    return ht

def _package_tag_from_suite_tag(directory, stag):
    ht = _hashtags(directory)
    for gh,tags in ht.items():
        if stag in tags:
            found = [t for t in tags if t.startswith('v')]
            assert len(found) == 1, str(found)
            return found[0]
    return


def _init_one_subdir(basedir, pkg, up_url, down_url):
    subdir = os.path.join(basedir,pkg)

    if pkg in suite_packages['art']:
        down_url = down_url % ('fnal-'+pkg,)
    else:
        down_url = down_url % pkg
    if up_url:
        up_url = up_url % pkg

    if not os.path.exists(subdir):
        os.makedirs(subdir)

    if not os.path.exists(os.path.join(subdir,'.git')):
        check_call('git init', shell=True, cwd=subdir)

    remotes  = check_output('git remote', shell=True, cwd=subdir).split('\n')
    for rname, rurl in [('upstream', up_url), ('downstream', down_url)]:
        if not rurl:
            continue
        if not rname in remotes:
            check_call('git remote add %s %s' % (rname,rurl),
                       shell=True, cwd=subdir)
        check_call('git fetch %s' % rname, 
                   shell=True, cwd=subdir)

    if not 'gitflow' in open(os.path.join(subdir,'.git/config')).read():
        check_call('git flow init -d', shell=True, cwd=subdir)

    return subdir

@cli.command("init")
@click.option('-u','--upstream-url',
              default='http://cdcvs.fnal.gov/projects/%s',
              help='Upstream git URL, add %s to be filled by package name.')
@click.option('-d','--downstream-url',
              default='git@github.com:LBNE/%s.git',
              help='Downstream git URL, add %s to be filled by package name.')
@click.pass_context
def init_workdir(ctx, upstream_url, downstream_url):
    '''Initialize a working directory.

    Initializes git repositories for all packages, adds upstream and
    downstream as remotes and fetches all commits.

    This command can be rerun to bring down fresh commits.
    '''
    workdir = ctx.obj['workdir']
    for pkg in [p for pl in suite_packages.values() for p in pl]:
        click.echo('%s' % (pkg, ))
        sd = _init_one_subdir(workdir, pkg, upstream_url, downstream_url)
        if sd:
            click.echo('\t-->%s' % (sd, ))
        else:
            raise RuntimeError('Failed to initialize for package "%s"' % pkg)

    sd = _init_one_subdir(workdir, 'FNALCore', '', downstream_url)


@cli.command("pkg-tag-from-suite-tag")
@click.argument("package")
@click.argument("suite")
@click.pass_context
def package_tag_from_suite_tag(ctx, package, suite):
    '''Display package level tag for given suite tag.'''
    workdir = ctx.obj['workdir']
    pkgdir = os.path.join(workdir, package)
    ptag = _package_tag_from_suite_tag(pkgdir, suite)
    if not ptag:
        click.echo("No package tag from %s %s" % (package,suite))
        sys.exit(1)
    click.echo('%s %s %s' % (package, ptag, suite))
    return
            
@cli.command("suite-release")
@click.argument("suite")
@click.argument("version")
@click.pass_context
def suite_release(ctx, suite, version):
    '''Print suite packages and their tags.'''
    workdir = ctx.obj['workdir']
    slabel = dict(art='ART', lar='LARSOFT')[suite]
    stag = '%s_SUITE_%s' % (slabel, version)
    
    pkgver = list()
    for pkg in suite_packages[suite]:
        pkgdir = os.path.join(workdir, pkg)
        ptag = _package_tag_from_suite_tag(pkgdir, stag)
        pkgver.append((pkg, ptag))
        click.echo('%s %s' % (ptag, pkg))
    return pkgver


if '__main__' == __name__:
    cli(obj=dict())
