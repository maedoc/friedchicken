#!/bin/bash

sid=$1

# 'final' dir on hdd and work dir on ssd
fdir=/mnt/data/duke/hcp-meg/dwi/$sid
wdir=/mnt/work/duke/hcp-dwi/$sid

set -eu
if [[ -f $fdir/10M.tck ]]; then echo $sid done, exit early!; exit 0; fi
rm -rf $wdir $fdir
mkdir -p $wdir $fdir
pushd $wdir

mrconvert -fslgrad /mnt/s3-hcp/HCP_1200/$sid/T1w/Diffusion/{bvecs,bvals,data.nii.gz} dwi.mif
mrconvert /mnt/s3-hcp/HCP_1200/$sid/T1w/T1w_acpc_dc_restore.nii.gz t1.mif

# cf https://osf.io/fkyht BATMAN protocol w/ mrtrix
# assuming eddy correct & coreg w/ T1 already, since it's HCP
dwi2mask dwi.mif mask.mif
dwi2response dhollander dwi.mif wm.txt gm.txt csf.txt -nthreads 4
dwi2fod msmt_csd dwi.mif -mask mask.mif wm.txt wmfod.mif gm.txt gmfod.mif csf.txt csffod.mif -nthreads 4
5ttgen fsl t1.mif 5tt.mif
5tt2gmwmi 5tt.mif gwmwi.mif
tckgen -act 5tt.mif -backtrack -seed_gmwmi gwmwi.mif -select 10M wmfod.mif 10M.tck -nthreads 4

# no sift since we're going to do vertex wise connectivity
popd

rsync -rav $wdir/ $fdir/
rm -rf $wdir
