% we can't read the bst format files from Python, so let's convert them
% to regular mat files

%% find runs in protocol
sid = '100307';
protocol_path = '/Users/maedoc/brainstorm_db/HCP/';
raw_bst_glob = [protocol_path 'data/*/*_notch_band_clean/data_0*.mat'];
raw_bst_fnames = dir(raw_bst_glob);

%% convert them
for i=1:size(raw_bst_fnames,1)
    f = raw_bst_fnames(i);
    fname = [f.folder filesep f.name]
    data = in_bst(fname);
    size(data.F)
    size(data.F(:,1:3:end))
    run_time = single(data.Time(1:3:end));
    run_data = single(data.F(:,1:3:end));
    % save([f.folder filesep 'data_scipy_ok.mat'], 'data', '-v7.3');
    save([f.folder filesep 'run_time.mat'], 'run_time');
    save([f.folder filesep 'run_data.mat'], 'run_data');
    size(run_data)
end