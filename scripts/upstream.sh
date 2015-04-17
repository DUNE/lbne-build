#!/bin/bash

do_init () {
    local name="$1" ; shift
    local ghprefix="$1";

    if [ -d $name ] ; then
	return
    fi

    git clone http://cdcvs.fnal.gov/projects/$name
    cd $name/
    git remote add github git@github.com:LBNE/${ghprefix}${name}.git
    git fetch github
    cd ..
}


do_init_all () {
    for repo in cpp0x cetlib fhicl-cpp messagefacility art 
    do
	do_init $repo fnal-
    done

    for repo in larana lbnecode larsim larreco larpandora larexamples larevt lareventdisplay lardata larcore
    do
	do_init $repo
    done
}
    

cmd="$1" ; shift
do_$cmd $@
