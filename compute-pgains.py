import os
import numpy as np
import scipy.io
import glob

bst = '/mnt/data/duke/brainstorm_db/HCP'
sids = [_ for _ in os.listdir(f'{bst}/data') if _ not in '@default_study protocol.mat']

for sid in sids:
    headmodels = glob.glob(f'{bst}/data/{sid}/*/headmodel_surf_os_meg.mat')
    for headmodel in headmodels:

        tess_path = f'{bst}/anat/{sid}/tess_cortex_mid.mat'
        gain_path = headmodel
        lceigs_path = f'/mnt/meso/scratch/mwoodman/tess_cortex/{sid}.lceigs.npz'

        opath = gain_path[:-3] + 'pgain.npy'
        if os.path.exists(opath):
            print(opath, 'exists, not overwriting')
            continue

        cortex = scipy.io.loadmat(tess_path)
        gain = scipy.io.loadmat(gain_path)

        # filter nan channels
        ok = np.isfinite(gain['Gain']).all(axis=1)
        gain_xyz = gain['Gain'][ok].reshape((248, -1, 3))

        # cf https://neuroimage.usc.edu/brainstorm/Tutorials/HeadModel
        gain = np.sum(gain_xyz * cortex['VertNormals'], axis=2)

        # project gain to lceigs
        p = np.load(lceigs_path)['p']
        pgain = gain @ p
        np.save(opath, pgain)
        print(opath)
