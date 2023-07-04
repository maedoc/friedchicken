![](friedchicken.png)

# megfield

a transformer neural field model for MEG data.  kind of messy right now.

## preprocessing

Using Brainstorm, the MEG data for HCP used scripts

- megfield_pp0_new_subject.m - create subject and populate with 
  - anatomy
  - BEM surfaces
  - raw MEG files
- megfield_pp1_noise_cov.m - noise cov
  - compute noise covariance with Rnoise run
- megfield_pp2.m processes the runs
- megfiedl_pp3.m exports the runs
- meg-prep-rewrite.ipynb 
  - downloads the data for the brainstorm functions
  - runs postprocessing to put data into mode space

## TODO

- [ ] compare parcellations in reconstruction error
