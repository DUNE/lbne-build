#!/usr/bin/env python
'''
A script to help chase upstream releases and make downstream ones.
'''
import os
import sys
import click
from subprocess import check_output, check_call
from collections import defaultdict, namedtuple


# data
suite_packages = dict(
    art = 'cpp0x cetlib fhicl-cpp messagefacility art'.split(),
    lar = 'larana lardata larevt larpandora larsim larcore lareventdisplay larexamples larreco larsoft'.split(),
    lbn = ['lbnecode'],
)
all_suite_packages = [p for pl in suite_packages.values() for p in pl]

def redmine_url(self, name):
    return 'https://cdcvs.fnal.gov/projects/%s' % name
def github_url(self, name):
    if name in suite_packages['art']:
        name = 'fnal-' + name
    return 'git@github.com:LBNE/%s.git' % name



class UpDownRepo(object):
    '''
    Forge a connection between upstream and downstream repositories.
    '''

    upstream_url_maker = redmine_url
    downstream_url_maker = github_url

    def __init__(self, name, basedir = '.'):
        '''
        Create an repo with upstream and downstream remotes.
        '''
        self.name = name
        self.repodir = os.path.join(basedir, name)
        self.init()


    def remotes(self):
        return [x.strip() for x in self.git('remote').split('\n')]

    def init_remotes(self):
        remotes = self.remotes()

        if 'upstream' not in remotes:
            url = self.upstream_url_maker(self.name)
            self.git('remote add upstream %s' % url)
        self.git('fetch upstream')

        if 'downstream' not in remotes:
            url = self.downstream_url_maker(self.name)
            self.git('remote add downstream %s' % url)
        self.git('fetch downstream')


    def init_local(self):
        'Initialize empty repostory if not already done.'
        if not os.path.exists(self.repodir):
            os.makedirs(self.repodir)
        if not os.path.exists(os.path.join(self.repodir, '.git')):
            self.git('init')
        try: 
            self.git('config --get-regexp gitflow.prefix.*')
        except: 
            self.git('flow init -d')

    def init(self):
        self.init_local()
        self.init_remotes()

    def git(self, cmd):
        'Run a git command, return output.'
        return check_output('git '+ cmd, shell=True, cwd=self.repodir)

    def hashtags(self):
        'Return dictionary maping a git hash to a git tag'
        ht = defaultdict(list)
        for line in self.git('show-ref --tags -d'):
            line = line.strip()
            if not line: 
                continue
            gh, label = line.split()
            if label.endswith('^{}'):
                ht[gh].append(label[:-3].split('/')[-1])
        return ht


    def tag_for_suite(self, suite_tag):
        ht = self.hashtags()
        for gh,tags in ht.items():
            if suite_tag in tags:
                found = [t for t in tags if t.startswith('v')]
                assert len(found) == 1, str(found)
                return found[0]
        return

    def start_release(self, release, tag = None):
        '''
        Start a <release> merging in downstream master and upstream <tag> if given.
        '''
        self.git("flow release start %s" % release)
        self.git("merge downstream/master")
        if tag:
            self.git("merge %s" % tag)
        self.git("push downstream release/%s" % release)
    pass


class FNALCore(UpDownRepo):
    'FNALCore repo only has downstream'

    def __init__(self, basedir = '.'):
        '''
        Create an repo with upstream and downstream remotes.
        '''
        super(FNALCore,self).__init__('FNALCore', basedir)

    def init_remotes(self):
        if 'downstream' not in self.remotes():
            url = self.downstream_url_maker(self.name)
            self.git('remote add downstream %s' % url)
        self.git('fetch downstream')




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

@cli.command("init")
@click.argument("packages", nargs=-1)
@click.pass_context
def init_workdir(ctx, packages):
    '''Initialize a working directory.

    Initializes git repositories for all packages, adds upstream and
    downstream as remotes and fetches all commits.

    This command can be rerun to fetch fresh commits.
    '''
    workdir = ctx.obj['workdir']
    
    todo = set()
    for pkg in packages:
        if pkg in suite_packages.keys():
            todo.update(suite_packages[pkg])
            continue
        todo.add(pkg)

    if not todo:
        todo.update(all_suite_packages)
        todo.add('fnalcore')

    if 'fnalcore' in todo:
        todo.remove('fnalcore')
        FNALCore(basedir=workdir)

    for pkg in todo:
        click.echo('%s' % (pkg, ))
        UpDownRepo(pkg, workdir)



@cli.command("release-start")
@click.argument("package")
@click.argument("release")
@click.option('-t','--tag',default=None,
              help='Specify an optional upstream tag to merge.')
@click.pass_context
def release_start(ctx, package, release, tag):
    workdir = ctx.obj['workdir']
    if package.lower() == 'fnalcore': # assymetry is the devil's creation!
        p = FNALCore(workdir)
    else:
        p = UpDownRepo(package, workdir)
    p.start_release(release,tag)


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
