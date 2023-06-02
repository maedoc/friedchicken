# read bad channel information into a single json
import os
import glob
import tqdm
import json

def read_badchan(fname):
    # TODO switch to a regex?
    with open(fname,'r') as fd:
        txt = fd.read()
    #print(txt)
    class badchannel:
        pass
    exec(txt, locals())
    sid, meg, run, *_  = os.path.basename(fname).split('_')
    return {'sid': sid, 'run': run, 'bads': list(getattr(badchannel,'all',[]))}

#fname = '/mnt/s3-hcp/HCP_1200/100307/MEG/Restin/baddata/100307_MEG_3-Restin_baddata_badchannels.txt'
#print(read_badchan(fname))

if not os.path.exists('badchans.json'):
    with open('./hcp-meg-ids.txt', 'r') as fd:
        sids = [l.strip() for l in fd.readlines()]

    all_badchan_fnames = []
    for sid in tqdm.tqdm(sids):
        fnames = glob.glob(f'/mnt/s3-hcp/HCP_1200/{sid}/MEG/*/baddata/*_baddata_badchannels.txt')
        # print(sid, fnames)
        all_badchan_fnames.extend(fnames)

    all_bads = []
    for fname in tqdm.tqdm(all_badchan_fnames):
        all_bads.append(read_badchan(fname))

    with open('badchans.json', 'w') as out:
        json.dump(all_bads, out)

if not os.path.exists('badchans2.json'):
    with open('badchans.json', 'r') as fd:
        bads = json.load(fd)

    bads2 = {}
    for bad in bads:
        sid = bad['sid']
        run = bad['run']
        if sid not in bads2:
            bads2[sid] = {}
        if run not in bads2[sid]:
            bads2[sid][run] = bad['bads']
        else:
            raise ValueError('duplicate run?', bads2[sid], sid, run, bad['bads'])

    with open('badchans2.json', 'w') as fd:
        json.dump(bads2, fd)

