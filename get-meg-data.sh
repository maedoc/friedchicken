#!/bin/bash

set -eux
sid=$1

./mc mirror hcp/hcp-openaccess/HCP_1200/$sid/MEG/anatomy HCP_${sid}_anatomy
./mc mirror hcp/hcp-openaccess/HCP_1200/$sid/unprocessed/MEG HCP_${sid}_unprocessed_MEG
# HCP_100307_MEG_restin_baddata

