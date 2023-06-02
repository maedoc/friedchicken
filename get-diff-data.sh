#!/bin/bash

sid=$1

fdir=/mnt/data/duke/hcp-meg/dwi/$sid
mkdir -p $fdir
for f in HCP_1200/$sid/T1w/Diffusion/{bvecs,bvals,data.nii.gz} HCP_1200/$sid/T1w/T1w_acpc_dc_restore.nii.gz
do
	cp -v /mnt/s3-hcp/$f $fdir/$(basename $f)
done

