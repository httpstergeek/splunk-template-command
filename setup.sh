#!/usr/bin/env bash


BASEDIR=$(pwd)

echo $(pip install --prefix=${BASEDIR}/bin  'splunk-sdk==1.6.0' )
echo $(pip install --prefix=${BASEDIR}/bin  requests )
$(mv "${BASEDIR}/bin/lib/python2.7/site-packages/splunklib" "${BASEDIR}/bin")
$(mv "${BASEDIR}/bin/lib/python2.7/site-packages/requests" "${BASEDIR}/bin")
$(rm -rf "${BASEDIR}/bin/lib")
