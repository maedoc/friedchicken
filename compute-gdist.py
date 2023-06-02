import sys
import os
import numpy as np
import gdist
import scipy.io
import glob

print(sys.argv)
path, = sys.argv[1:]

opath = path + '.gdist.mat'
if os.path.exists(opath):
    print(f'{opath} exists, not overwriting')

mat = scipy.io.loadmat(path)
vtx = mat['Vertices'] # nvtx,3
tri = mat['Faces'].astype(np.int32) # ntri,3
assert tri.min() == 1
assert vtx.shape[1] == tri.shape[1] == 3
gd = gdist.local_gdist_matrix(vtx, tri, 20.0, is_one_indexed=True).tocsr()
gd.data = gd.data.astype(np.float32)
scipy.io.savemat(path + '.gdist.mat', {'gdist': gd.tocsr()})
