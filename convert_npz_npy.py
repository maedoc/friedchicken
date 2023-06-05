# unpacks npzs for memmap purposes
import os
import glob
import numpy as np
import tqdm

fnames = glob.glob('./ready/*.npz')

for fname in tqdm.tqdm(fnames):
    npz = np.load(fname)
    for key, val in npz.items():
        fnamekey = f'{os.path.basename(fname).split(".")[0]}_{key}.npy'
        dstfname = os.path.join('./ready_npy/', fnamekey)
        if not os.path.exists(dstfname):
            np.save(dstfname, val)

