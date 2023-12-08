function megfield_pp3_convert_all_runs()

% we can't read the bst format files from Python, so let's convert them
% to regular mat files

% find runs in protocol
protocol_path = '/tmp/brainstorm_db/hcp/data';
raw_bst_glob = [protocol_path '/*/*_notch_band_clean/data_0*.mat'];
raw_bst_fnames = dir(raw_bst_glob);

% convert them
for i=1:size(raw_bst_fnames,1)
    f = raw_bst_fnames(i);
    fname = [f.folder filesep f.name];
    fprintf('converting run %d: %s\r\n', i, fname);

    % sFile = in_bst_data(fname, 'F').F;
    % fid = fopen(sFile.filename, 'r', sFile.byteorder);
    % run_data = single(in_fread_bst(sFile, fid, [0 sFile.header.nsamples-1], []));
    % run_time = single((0:(sFile.header.nsamples-1))/sFile.header.sfreq);
    % run_data = run_data(:,1:3:end);
    % run_time = run_time(:,1:3:end);
    % fclose(fid);

    % in_bst seems to use java and borks w/ mcr
    data = in_bst(fname);
    run_time = single(data.Time(1:3:end));
    run_data = single(data.F(:,1:3:end));

    save([f.folder filesep 'run_time.mat'], 'run_time');
    save([f.folder filesep 'run_data.mat'], 'run_data');
end