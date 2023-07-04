import os
import json
import glob
import tqdm
import numpy as np
import torch
import time


class MEGData(torch.utils.data.Dataset):

    def __init__(self, path, win_size=1024, win_olap=256, win_pred=256):
        self.fnames = np.array(glob.glob(os.path.join(path, '*_dt.npy')))
        self.sfreq = self._check_sfreq()
        self.win_size = win_size
        self.win_olap = win_olap
        self.win_pred = win_pred
        self.fname_wins = np.array([self._fname_nwin(fn) for fn in self.fnames])
        self.cumul_wins = np.cumsum(self.fname_wins)
        self.ngot = 0
        self.ttime = 0

    def _check_sfreq(self):
        t0, t1 = np.lib.format.open_memmap(self.fnames[0])[:2]
        return float(1/(t1 - t0))

    def _fname_nwin(self, fname):
        t = self._mmkey(fname)
        nt = t.shape[0] - self.win_size
        nwin = nt // (self.win_size - self.win_olap)
        return nwin

    def __len__(self):
        return self.fname_wins.sum()

    def _mmkey(self, fname, key=None):
        fname = fname.replace('dt', key) if key else fname
        return np.lib.format.open_memmap(fname)

    def __getitem__(self, idx):
        tic = time.time()
        if isinstance(idx, int):
            idx = np.r_[idx]
        fids = np.digitize(idx, self.cumul_wins)  # file ids for each idx
        fnames = self.fnames[fids]                # file names for each idx
        wids = idx - np.r_[0, self.cumul_wins][fids]        # window in file
        maxs = 231
        wins = []
        gain = []
        for fname, wid in zip(fnames, wids):
            dF = self._mmkey(fname, 'dF')
            i0, i1 = wid*self.win_olap , wid*self.win_olap+self.win_size+self.win_pred
            win = dF[i0:i1].copy()[:,:maxs]
            wins.append(win.T)
            # obs, pred = win[:-self.win_pred], win[-self.win_pred:]

            g = self._mmkey(fname, 'pgain')[:maxs].copy()
            # weighting by d makes projection to sources unbalanced
            # g = g * self._mmkey(fname, 'd')
            gain.append(g.astype('f'))

        wins = np.array(wins)
        gain = np.array(gain)
        if idx.size == 1:
            wins, gain = wins[0], gain[0]
        # TODO subject/task encoding
        ret = wins[..., :-self.win_pred].copy(), gain, wins[..., -self.win_pred:].copy()
        toc = time.time()
        self.ngot += idx.size
        self.ttime += toc - tic
        return ret

    @staticmethod
    def _test():
        data = MEGData('./ready_npy', win_size=256, win_olap=0)
        print(len(data), 'items, ~', int(len(data)*256/data.sfreq/3600), 'hours')
        idx = np.random.randint(0, len(data), size=32)
        b = data[idx]
        print(b[0].shape, b[1].shape, b[2].shape)

        # ok so seems ready for dataloader batch
        dataloader = torch.utils.data.DataLoader(data, batch_size=64, shuffle=True)
        obs, g, pred = next(iter(dataloader))
        print(obs.shape, g.shape, pred.shape)
        # this is ready to plugin into the safari examples I guess.

if __name__ == '__main__':
    MEGData._test()
