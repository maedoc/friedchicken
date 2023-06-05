# combine gain matrix, bad channels and decimated sensor data, for a final set of files
import os
import time
import numpy as np
import scipy.io
import glob
import h5py
import json
import pylab as pl

bst = '/mnt/data/duke/brainstorm_db/HCP'
dest = '/home/duke/src/megfield/ready'
decim = 3
spot_check = False
sids = [_ for _ in os.listdir(f'{bst}/data') if _ not in '@default_study protocol.mat @inter']
with open('./badchans2.json', 'r') as fd:
    badchans2 = json.load(fd)

# TODO move this into the MATLAB script which dumps bst to v7.3 to avoid 2x copies
t_start = time.time()
t_now = lambda: f'[t={time.time() - t_start:0.1f}] '
for sid in sids:
    runs = glob.glob(f'{bst}/data/{sid}/*_notch_band_clean/data_scipy_ok.mat')

    tess_path = f'{bst}/anat/{sid}/tess_cortex_mid.mat'
    lceigs_path = f'/mnt/meso/scratch/mwoodman/tess_cortex/{sid}.lceigs.npz'
    cortex = scipy.io.loadmat(tess_path)
    lceigs = np.load(lceigs_path)

    for i, runfname in enumerate(runs):
        folder = os.path.dirname(runfname)
        runslug = os.path.basename(folder).split('_')[0][4:]
        ofname = f'{dest}/{sid}_{runslug}.npz'
        if os.path.exists(ofname):
            print(f'{t_now()} {ofname} exists, skipping')
            continue

        # load gain
        gain_mat = scipy.io.loadmat(os.path.join(folder, 'headmodel_surf_os_meg.mat'))

        # and channel list
        chan4d = scipy.io.loadmat(os.path.join(folder, 'channel_4d_acc1.mat'))

        # bad channels
        badnames = badchans2[sid][runslug]
        badmask = np.array([_[0] in badnames for _ in chan4d['Channel']['Name'][0,:]])
        assert badmask.sum() == len(badnames)

        # keep channels which have finite gain and not on the bad channel list
        okchan = np.c_[np.isfinite(gain_mat['Gain']).all(axis=1), ~badmask].all(axis=1)
        print(t_now(), sid, runslug, okchan.sum(), 'ok channels, ', end='', flush=True)

        # retain normal orientation and project to harmonics
        gain_xyz = gain_mat['Gain'][okchan].reshape((okchan.sum(), -1, 3))
        gain = np.sum(gain_xyz * cortex['VertNormals'], axis=2) # (okchan.sum(), nvtx)
        pgain = gain @ lceigs['p']
        print(pgain.shape, 'pgain.shape, ', end='', flush=True)

        # open run data
        run = h5py.File(runfname)
        t = run['data']['Time']
        sfreq = 1/(t[1,0] - t[0,0])
        print('h5py file open, loading F, ', end='', flush=True)

        # check sampling is ok
        if spot_check:
            # spot check the decimation: 3x would be nice, 4x is rough
            onesec = run['data']['F'][5*2035:6*2035, okchan]*1e12 # scale ~-1 to 1
            print(onesec.mean(), onesec.std())
            onet = t[5*2035:6*2035]
            #pl.imshow(onesec.T, aspect='auto')
            pl.plot(onet, onesec[:,:5], 'k.-')
            pl.plot(onet[::decim], onesec[::decim,:5], 'bo-', alpha=0.4)
            print(runfname, run['data']['F'].shape, sfreq, sfreq/decim)

        # otherwise save to new file
        else:
            tic = time.time()
            F = run['data']['F'][:, :]
            toc = time.time()
            mb = F.nbytes / 2**20
            mbps = mb / (toc - tic)
            print(f'F.shape {F.shape} {mb:0.1f} MB loaded in {toc-tic:0.1f} s = {mbps:0.1f} MB/s, ', end='', flush=True)
            dF = (F[::decim, okchan]*1e12).astype('f') # scale ~-1 to 1
            dt = run['data']['Time'][::decim].astype('f')
            print('time loaded, ', end='', flush=True)
            dsfreq = sfreq / decim
            # TODO chop 1st and last 5s for filter transient
            chop = int(sfreq*5)
            dF, dt = dF[chop:-chop], dt[chop:-chop]
            assert gain.shape[0] == dF.shape[1]
            print(pgain.shape, dF.shape, dt.shape, ', writing ', ofname,  end=' ', flush=True)
            np.savez(ofname, pgain=pgain, dF=dF, dt=dt, p=lceigs['p'], d=lceigs['d'])
            print('done.', flush=True)

        if spot_check:
            pl.show()
