% LBNE Plan for Software Installation of LArSoft-based code
% Ben Morgan; Brett Viren

Introduction
============

LBNE must be able to install its required software from source code on
all major collaboration platforms. Whilst binary deployment systems such as
`cvmfs` or `rpm/deb` are useful, a simple and standard from-source build must
be provided in order to easily create these binary packages and to ease
code development tasks. The single largest hindrance in
satisfying this requirement is the design and implementation of the low-level
CMake-based build system of the `LArSoft` and `art` packages which provide
the major components for the detector simulation portion of the LBNE software
stack.

The main element of the `LArSoft/art` build system that is problematic
is the tight entanglement it has with the high-level `UPS` end-user
environment/package management system (`UPS`). Rather than the management
system giving configuration to the build system, as the case in all industry
standard systems such as `rpm`/`deb`/ports/Homebrew, the `LArSoft/art` build
system *takes* configuration from `UPS`. This inversion of the usual
configuration-build hierarchy makes it impossible to build/run
the O(2000/10) C++11 sources/applications of `LArSoft/art`
without replicating the entire `UPS`-based software stack, down to the compiler
level. Though possible, this replication is difficult due the installation
process being driven by a highly complex system of undocumented scripts, both
generated and hand coded in various languages (shell, Perl and Python).
It has been found that these factors essentially prevent porting `LArSoft/art`
to different systems, even those that provide compatible C++11/14 compilers
and the required third party software "out of the box".

The heart of the problem, this inverted-dependency between the CMake build
and `UPS` configuration, was pointed out to the `art` development team in
April 2013, and in subsequent meetings both informal and official.
No acknowledge of this as an actual problem has ever been made, nor have they
supported LBNE in trying to address it. It should also be noted that LBNE's
criticisms are not unique, with other potential users of `art` (including
the CAPTAIN and SuperNEMO experiments) having rejected it due to the complexity
of the installation proceedure despite its apparently small source footprint.
Given this lack of support and that LBNE must continue to rely on `LArSoft`
and `art` in the near term, LBNE has embarked on solving the problem without
upstream Fermilab support.

The strategy is in two parts: The first part is to replace the `UPS`-entangled
CMake files with ones written to use pure-CMake functionality and thus
increase the portability of 'LArSoft/art'. The second part is to remove the
configuration management logic and data that resided in the
UPS-entanglement and move it into a higher-level layer in the form of a
Worch configuration. This strategy has already been proven to work in an
initial conversion of the `art` packages. The rest of this document
describes more about the current status of this effort, a plan for
carrying forward this strategy and a rough time-line.

The FNAL `art/LArSoft` Software Stack
=====================================
Source and Dependency Footprints of `art/LArSoft`
-------------------------------------------------
Both packages contain small amounts of C++11/14 source code (including all
unit testing code):

- FNAL foundation libraries contain in total O(200/200) C++ header/source files
- `Art` contains O(400/400) C++ header/source files
- `LArSoft` packages contain in total O(500/600) C++ header/source files

These in turn use the following standard and widely available third party
packages:

- Boost
- SQLite3
- ROOT
- CLHEP
- TBB

and only in LArSoft:

- Geant4
- GENIE

These source/dependency footprints should be contrasted with core HEP
packages such as:

- ROOT O(10000) sources, >10 external/optional dependencies
- Geant4 O(7000) sources, O(10) external/optional dependencies

These numbers are given to demonstrate the `art/LArSoft` are very simple and
lightweight packages by modern standards. It should also be noted that
neither `art` nor `LArSoft` have a large technical footprint. That is,
they only use C++11/14, and thus should not be tied to specific
architectures nor compilers.

These features should make them easy to build and install on any system that
provides a C++11/14 compliant compiler plus the requisite packages.
LBNE's experience has been that this is not the case due to the coupling
of the build system to the `UPS` configuration management system, yet there
is no technical reason for this coupling to exist.
Neither ROOT nor Geant4 require a specific configuration management
implementation to locate their required packages, making them highly portable
and easy to install despite their significantly larger source/dependency
footprint.

This is not to say that a configuration management system shouldn't be used.
Rather, the build system should not rely on one being present and in use.

The `UPS` Environment Management System
---------------------------------------
Why the stack is difficult to install

Though documentation exists for `UPS`, it is out of date and poorly broken
down into sections for beginner and experienced users.

`UPS` itself is not a blocker for LBNE, rather, it is the way that a hard
reliance on `UPS` has been built into the tools used to build `art`, `LArSoft`
and their client packages.

Note that `cvmfs` is a *deployment* system, *not* a package manager. It is
highly useful for distributing software efficiently, but it provides no
utility for building nor packaging that software easily and cleanly (and nor
should it).

The `cetbuildtools` CMake Add-ons
---------------------------------
`LArSoft/art` use the CMake build tool to configure, build and install
their runtime/development products. Many large software projects such as
ROOT, Geant4, LLVM and KDE (among others) have adopted CMake due to its
ease of use and portability, to quote from CMake's website:

> CMake is a family of tools designed to build, test and package software.
> CMake is used to control the software compilation process using simple
> platform and compiler independent configuration files. CMake generates
> native makefiles and workspaces that can be used in the compiler
> environment of your choice.

To build a package, such as ROOT, using CMake and Makefiles, all one does is

    $ cmake <args> /path/to/sourcedir
    $ make -j4
    $ make install

Custom options and configuration information, e.g. paths to needed packages,
can be passed through the command line arguments `<args>`. The `art/LArSoft`
packages should be similarly easy to build/install, but they are not for one
key reason: they require use of FNAL's `cetbuildtools` add-ons for CMake.
As an additional build-time dependency, `cetbuildtools` breaks the build
and use of `art/LArSoft` because of its design and implementation:

- `cetbuildtools` is tightly coupled to FNAL's 'UPS' package/configuration
  management system for finding things like GCC, Boost etc.


- This coupling is such that the user trying to build Art has no way to
  make it use system installs of the required packages (including GCC),
  even if these meet version requirements.

- `cetbuildtools` assumes GCC as the compiler, and subsequently Art code
  has been found to contain GCCisms and code non-compliant with the
  C++11/14 standard.

- If a package *A* uses `cetbuildtools`, then a package *B* which uses *A*
  will be required to also use `cetbuildtools` (and thus `UPS`). This makes
  decoupling via a buildtime "firewall" very difficult to implement.

- Most functionality in `cetbuildtools` demonstrates a fundamental
  lack of understanding of CMake and its capabilities (including
  package location, import/export targets and target properties).

- Much of `cetbuildtools` functionality is in the form of undocumented,
  heavyweight wrappers around simple core CMake. These also enforce
  source and binary layout conventions on the user which are of little benefit.

In short, `cetbuildtools` fails to implement a portable and easy to use
build interface. The primary failure is its dependence on the `UPS`
configuration management system, making any project using `cetbuildtools`
unbuildable without an entire replication of a `UPS` stack. This is
an inversion of the usual hierarchy of a build system, e.g. a Makefile,
sitting under a configuration/packaging system, e.g. RPM.


Current Status
==============

The current status of the purification of the low-level CMake build
system is described. Here the *art* packages are `cpp0x`, `cetlib`,
`fhicl-cpp` and `messagefacility` and `art` itself.

-   An LBNE GitHub organization has been established[^1].

-   The *art* repositories are forked into this organization in a way
    that "upstream" commits pushed to Fermilab Redmine repositories
    continue to be tracked.

-   A new `FNALCore` package [^2] is developed that aggregates the *art*
    packages (except the `art` package itself) as well as holds their
    purified CMake files.

-   Purified CMake files are developed for `art` itself in the
    `fnal-art` repository[^3].

-   The `lbne-build` repository[^4] was created in the LBNE GitHub
    organization. It houses a Worch[^5] configuration and tools to build
    all the 3rd-party external packages, `FNALCore` and `fnal-art` from
    source.

-   Building these packages with Worch has been tested on at least
    Ubuntu (14.04) and Scientific Linux (6.4) and in a by-hand manner on
    Mac OS X.

Plan
====

The plan going forward is meant to satisfy these goals:

-   Push the commits of the purified CMake work into "upstream"
    repositories so that they no longer need to be held in separate
    tracking forks.

-   Minimize disruption on the user base and provide an partly adiabatic
    change.

-   Provide time for ongoing testing and improving of the purified CMake
    files while furthering and allowing the other goals.

The plan is in three major parts:

1.  Continue to apply the CMake purification up through the LArSoft and
    `lbnecode` packages. In the same manner as with `fnal-art`, push
    commits to GitHub in forks which track their upstream repositories
    and in step add to `lbne-build` support to build each newly purified
    package. During this phase, Worch-related development is also needed
    in order to create UPS binary product "tarballs" from the build
    results and thus retain user-level status quo in the end.

2.  Change over from GItHub based development to pushing commits to
    upstream repositories. Do this by first purifying `lbnecode` as
    above (and in GitHub) and then porting these changes into the
    `lbnecode` Redmine git repository with all changes placed behind a
    "switch" that defaults to the UPS-entangled build. Factor
    `lbne-build` to support building this "switched" pure-CMake
    `lbnecode` package against dependencies provided by UPS.

3.  With acceptance (and hopefully assistance) by the LArSoft group,
    continue porting the CMake purification, still kept switched off by
    default, to the LArSoft Redmine repositories and updating
    `lbne-build` to follow suit. Then, do likewise for the *art*
    packages. At some suitable point "flip the switch" so the entire
    stack is built in a pure-CMake manner with Worch.

Interaction with other efforts
------------------------------

Up until step three, this effort does not interfere with others. At step
three, buy-in by LArSoft and *art* developers and the Fermilab software
builders is required. However, before even making significant process on
step one it must be determined if Fermilab will accept the changes that
will be made in steps two and three. If not accepted, LBNE will revise
this plan to remove any inefficiencies and complications that are being
retained in order to prop up the Fermilab status quo. This will likely
include removing UPS entirely as an end-user environment management
system as it brings significant complexity without commiserate benefits.

Timeline
========

No clue at this moment.

[^1]: <https://github.com/LBNE> and links there for the individual
    `fnal-*` forks.

[^2]: <https://github.com/LBNE/FNALCore>

[^3]: <https://github.com/LBNE/fnal-art>

[^4]: <https://github.com/LBNE/lbne-build>

[^5]: <https://github.com/brettviren/worch>

