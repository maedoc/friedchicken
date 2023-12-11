import numpy as np
import glob
import scipy.io
import json
import gdist, os
import scipy.io
import scipy.sparse.linalg as sla
import tqdm
import sys


sid, = sys.argv[1:]

say = lambda msg: print(msg, end=', ', flush=True)

bstdb = '/tmp/brainstorm_db'
with open(f'/tmp/badchans2.json', 'r') as fd:
    badchans2 = json.load(fd)
runs = glob.glob(f'{bstdb}/hcp/data/{sid}/*/run_data.mat')
say(f'{sid} has {len(runs)} runs')


cortex = f'{bstdb}/hcp/anat/{sid}/tess_cortex_mid.mat'
cortex_gdist = cortex + '.gdist.mat'
if not os.path.exists(cortex_gdist):
    max_dist = 40.0
    mat = scipy.io.loadmat(cortex)
    vtx = mat['Vertices'] # nvtx,3
    tri = mat['Faces'].astype(np.int32) # ntri,3
    assert tri.min() == 1
    assert vtx.shape[1] == tri.shape[1] == 3
    gd = gdist.local_gdist_matrix(vtx, tri, max_dist, is_one_indexed=True).tocsr()
    gd.data = gd.data.astype(np.float32)
    scipy.io.savemat(cortex_gdist, {'gdist': gd, 'max_dist': max_dist})
else:
    gd_mat = scipy.io.loadmat(cortex_gdist)
    gd = gd_mat['gdist']
    max_dist = gd_mat['max_dist']
say('gdist')

cortex_lceigs = cortex + '.lceigs.npz'
if not os.path.exists(cortex_lceigs):
    k = 5.0
    lc = gd.copy()
    lc.data = np.exp(-lc.data/k).astype('f')
    d1, p1 = sla.eigs(lc, 100)
    lc.data = np.exp(-(lc.data/k)**2).astype('f')
    d2, p2 = sla.eigs(lc, 100)
    np.savez(cortex_lceigs, d1=d1, p1=p1, d2=d2, p2=p2, k=k)
lc = np.load(cortex_lceigs)
say('lc')

def load_run(sid, run_fname):

    run_data = scipy.io.loadmat(run_fname)['run_data']
    run_time = scipy.io.loadmat(run_fname.replace('run_data.mat', 'run_time.mat'))['run_time'][0]
    sfreq = 1 / (run_time[1] - run_time[0])

    # per run load gain & channel list
    folder = os.path.dirname(run_fname)
    gain_mat = scipy.io.loadmat(os.path.join(folder, 'headmodel_surf_os_meg.mat'))
    chan4d = scipy.io.loadmat(os.path.join(folder, 'channel_4d_acc1.mat'))
    cortex = scipy.io.loadmat(f'{bstdb}/hcp/anat/{sid}/tess_cortex_mid.mat')

    # bad channels differ per run
    runslug = os.path.basename(folder).split('_')[0][4:]
    badnames = badchans2[str(sid)][runslug]
    badmask = np.array([_[0] in badnames for _ in chan4d['Channel']['Name'][0,:]])
    assert badmask.sum() == len(badnames)

    # keep channels which have finite gain and not on the bad channel list
    okchan = np.c_[np.isfinite(gain_mat['Gain']).all(axis=1), ~badmask].all(axis=1)

    # retain normal orientation and project to harmonics
    gain_xyz = gain_mat['Gain'][okchan].reshape((okchan.sum(), -1, 3))
    gain = np.sum(gain_xyz * cortex['VertNormals'], axis=2) # (okchan.sum(), nvtx)
    pgain = gain @ lc['p1']
    # drop first & last 5 seconds
    chop = 5*int(sfreq)
    run_data = run_data[okchan]*1e12 # rescale to ~(-1,1)
    run_data, run_time = run_data[:,chop:-chop], run_time[chop:-chop]

    assert np.allclose(pgain.imag, 0)
    return pgain.real.T.astype('f')  @ run_data

all_runs_fname = f'megmodes-{sid}.npy'
catruns = []
for i, run in enumerate(runs):
    catruns.append(load_run(sid,run).astype('f'))
    say(i)
catruns = np.concatenate(catruns, axis=1).T.copy()
np.save(all_runs_fname, catruns)
print(f'{all_runs_fname} done.')
