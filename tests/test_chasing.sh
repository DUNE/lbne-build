#!/bin/bash

if [ -n "$1" ] ; then
    workdir="$1" ; shift
else
    workdir="$(mktemp -d)"
fi

set -x 
set -e

mkdir -p $workdir

dsurl () {
    local name=$1; shift
    if [ -n "$(echo cpp0x cetlib messagefacility fhicl-cpp | grep "$name")" ] ; then
	echo "https://github.com/LBNE/fnal-${name}.git"
    else
	echo "https://github.com/LBNE/${name}.git"
    fi
}
usurl () {
    echo "http://cdcvs.fnal.gov/projects/${1}"
}

cloneit () {
    local name="$1" ; shift
    local which="$1" ; shift

    local remote_url="$(dsurl $name)"
    local clonedir="$workdir/dnstream-${name}.git"
    if [ "$which" = "up" ] ; then
	remote_url="$(usurl $name)"
	clonedir="$workdir/upstream-${name}.git"
    fi    

    if [ -d "$clonedir" ] ; then
	echo "Clone already done: $clonedir"
	return
    fi

    git clone --bare "$remote_url" "$clonedir"
}

usdszip () {
    local name="$1" ; shift
    local repo="$workdir/$name"
    if [ -d "$repo" ] ; then
	echo "Local repo already made: $repo"
	return
    fi

    mkdir -p "$repo"
    cd "$repo"

    git init
    git remote add upstream "$workdir/upstream-${name}.git"
    git remote add dnstream "$workdir/dnstream-${name}.git"
    git fetch upstream
    git fetch dnstream
}    

chase_tags () {
    local name=$1 ; shift
    local start=$1; shift

    cd "$workdir/$name"

    if [ -n "$(git branch -a | grep integration)" ] ; then
	echo "Removing prior integration branch!"
	git checkout integration
	git branch -D dummy || true
	git checkout -b dummy
	git branch -D integration
    fi

    git checkout -b integration $start
    git branch -D dummy || true

    for tag in $@
    do
	local newtag="${tag}-p0"
	if [ -n "$(git tag | grep ^${newtag}$)" ] ; then
	    echo "Tag exists on ${name}: $newtag"
	    continue
	fi
	git merge -m "Merge $name $tag" "$tag"
	git tag -a -m "Purified $name $tag" "$newtag"
	git push --tags dnstream integration
    done
}

twerkit () {
    local name=$1 ; shift
    cloneit $name up
    cloneit $name down
    usdszip $name
    chase_tags $name $@
}


twerk_subtrees () {
    twerkit cpp0x 98218a91217edc5c1e8ad8bb3983f4d8d3f3565b v1_04_0{5..8}
    twerkit cetlib 104ff97611e8d5af7e7726422f635f2106408791 v1_07_0{0..3} v1_08_0{0..1}
    twerkit fhicl-cpp 793bcce1e04abeb0b644abf65cf68ebe9217b034 v2_19_05 v3_00_0{0..1} v3_01_0{0..3} v3_02_00
    twerkit messagefacility 1dcf11eafe1ac2612a0e222ac3fcc90fcdbeccea v1_11_1{4..5} v1_13_00
}


twerk_fnalcore () {
    cloneit FNALCore down
    git clone $workdir/dnstream-FNALCore.git $workdir/FNALCore
    for name in cpp0x cetlib messagefacility fhicl-cpp
    do
	git remote add ${name}-upstream $workdir/dnstream-${name}.git
	git fetch ${name}-upstream
    done
}

twerk_subtrees
twerk_fnalcore
