#!/usr/bin/env python

import sys
import click
from subprocess import check_output
from collections import defaultdict

@click.group()
@click.pass_context
def cli(ctx):
    return

suite_packages = dict(
    art = 'cpp0x cetlib fhicl-cpp messagefacility art'.split(),
    lar = 'larana lardata larevt larpandora larsim larcore lareventdisplay larexamples larreco'.split(),
    lbn = ['lbnecode'],
)

def hashtags(package):
    cmd = "git --git-dir=%s/.git show-ref --tags -d" % package
    output = check_output(cmd.split()).split('\n')
    ht = defaultdict(list)
    for line in output:
        line = line.strip()
        if not line: 
            continue
        gh, label = line.split()
        if label.endswith('^{}'):
            ht[gh].append(label[:-3].split('/')[-1])
    return ht

def _package_tag_from_suite_tag(package, tag):
    ht = hashtags(package)
    for gh,tags in ht.items():
        if tag in tags:
            found = [t for t in tags if t.startswith('v')]
            assert len(found) == 1, str(found)
            return found[0]
    return


@cli.command("pkg-tag-from-suite-tag")
@click.argument("package")
@click.argument("tag")
@click.pass_context
def package_tag_from_suite_tag(ctx, package, tag):
    ptag = _package_tag_from_suite_tag(package, tag)
    if not ptag:
        click.echo("No package tag from %s %s" % (package,tag))
        sys.exit(1)
    click.echo('%s %s %s' % (package, ptag, tag))
    return
            
@cli.command("suite-releases")
@click.argument("suite")
@click.argument("version")
@click.pass_context
def suite_releases(ctx, suite, version):
    slabel = dict(art='ART', lar='LARSOFT')[suite]
    stag = '%s_SUITE_%s' % (slabel, version)
    
    pkgver = list()
    for pkg in suite_packages[suite]:
        ptag = _package_tag_from_suite_tag(pkg, stag)
        pkgver.append((pkg, ptag))
        click.echo('%s %s' % (ptag, pkg))
    return pkgver

if '__main__' == __name__:
    cli(obj=dict())
