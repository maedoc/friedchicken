import numpy as np
import time
import tqdm
import torch

# load data y G d nt ns nm {{{
npz = np.load('ready/100307_4-Restin.npz')
y = npz['dF']
t = npz['dt']
G = npz['pgain'].astype('f')
d = npz['d']
assert y.shape[1] == G.shape[0] # num sensors
assert G.shape[1] == d.shape[0] # num modes/channels
nt = y.shape[0]
ns = G.shape[0]
nm = d.shape[0]
# }}}

# move to torch
dev = 'cuda'
nm = nm
nt = 8192
y = torch.tensor(y[:nt,:]).to(dev) # (nt, ns)
dy = torch.diff(y, dim=0)
G = torch.tensor(G[:,:nm]).to(dev) # (ns, nm)
d = torch.tensor(d[:nm]).to(dev) # (nm, )
x = torch.zeros((nt, nm), device=dev, requires_grad=True)

fl = 32 # ~50 ms :(
fl = 1024 # ~1.5s :) 
a1 = torch.ones((nm, 1, fl), device=dev, requires_grad=True)
a2 = torch.ones((nm, 1, fl), device=dev, requires_grad=True)
b = torch.ones((nm,), device=dev, requires_grad=True)
c = torch.ones((nm,nm), device=dev, requires_grad=True)

N = lambda y,yh,sd: torch.distributions.Normal(y,sd).log_prob(yh)
t_zero = torch.tensor(0, device=dev)
t_one = torch.tensor(1, device=dev)

def loss(x):
    # fits well but useless for prediction
    yh = (a*x*d) @ G.T # (nt, ns)
    dyh = torch.diff(yh, dim=0)
    sd = torch.tensor(0.1, device=dev)
    lp = torch.sum(N(y, yh, sd)) \
       + torch.sum(N(dy, dyh, sd)) \
       + torch.sum(N(x, t_zero, t_one))
    return -lp


def loss(x):
    "2 convolutions separated by dense + relu"
    # xn = x[:-3] + a[2]*x[:-3] + a[1]*x[1:-2] + a[0]*x[2:-1]
    xi = torch.relu(c @ torch.conv1d(x.T, a1, groups=nm)).T
    xn = torch.conv1d(xi.T, a2, groups=nm).T
    yh = (x * b * d) @ G.T
    dyh = torch.diff(yh, dim=0)

    sd = torch.tensor(0.1, device=dev)

    lp = torch.sum(N(y, yh, sd)) \
            + torch.sum(N(x[2*(fl-1):], xn, sd)) \
            + torch.sum(N(x, t_zero, t_one))
    return -lp



print(f'initial loss {loss(x)}', flush=True)
trace = []
for lr in [0.001]:
    opt = torch.optim.AdamW([a1,a2,c,x,b], lr=lr)
    tic = time.time()
    niter = 100000
    for i in range(niter+1):
        l = loss(x)
        l.backward()
        mse = l / (nt*ns)
        trace.append(mse.cpu().detach().numpy())
        ngl =  torch.linalg.norm(x.grad)
        if i%(niter//10) == 0:
            toc = time.time()
            print(f'{lr} {i} {toc-tic:0.1f}s mse {mse:0.4f} ngl {ngl:0.2f}', flush=True)
            tic = toc
        opt.step()
        opt.zero_grad()

import pylab as pl
xi = torch.relu(c @ torch.conv1d(x.T, a1, groups=nm)).T
xn = torch.conv1d(xi.T, a2, groups=nm).T
yh = (x * b * d) @ G.T
n_yh = yh.cpu().detach().numpy()
n_y = y.cpu().detach().numpy()

pl.figure(figsize=(25, 20))
pl.subplot(121)
nch = 30
y_ = np.r_[:nch]
pl.plot(n_y[:1000,:nch]+y_, 'k')
pl.plot(n_yh[:1000,:nch]+y_, 'r')

pl.subplot(224)
pl.semilogy(trace)

pl.tight_layout()
pl.savefig('n_yh.jpg')
