#!/bin/bash

i=0
for sid in $(cat HCP_1200_sids.txt)
do
	maybe_meg=$(ls /mnt/s3-hcp/HCP_1200/$sid | grep MEG)
	if [[ ! -z "$maybe_meg" ]]; then
		echo $sid >> HCP_1200_meg_sids.txt
	fi
	echo $i $sid $maybe_meg
	i=$(($i + 1))
done
