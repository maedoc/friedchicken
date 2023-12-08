function megfield_pp0_new_subject(sid)





% Path to a Brainstorm database (= a folder that contains one or more Brainstorm protocols)
% BrainstormDbDir = 'bstdb';

% Load a new uploaded database (sets BrainstormDbDir and load all the protocols it contains)
% db_import(BrainstormDbDir);

% Alternative: Set the Brainstorm DB folder
% (defines where the new protocols are going to be created, but does not load anything)
%  bst_set('BrainstormDbDir', BrainstormDbDir);

% Get the protocol index of an existing protocol (already loaded previously in Brainstorm)
% iProtocol = bst_get('Protocol', 'hcp');



sFiles = [];
% anatomy = sprintf('/mnt/s3-hcp/HCP_1200/%s/MEG/anatomy',sid);
anatomy = sprintf('/work/duke/hcp-meg/%s/anatomy',sid);

% Process: Import anatomy folder
sFiles = bst_process('CallProcess', 'process_import_anatomy', sFiles, [], ...
    'subjectname', sid, ...
    'mrifile',     {anatomy, 'HCPv3'}, ...
    'nvertices',   15000, ...
    'nas',         [0, 0, 0], ...
    'lpa',         [0, 0, 0], ...
    'rpa',         [0, 0, 0], ...
    'ac',          [0, 0, 0], ...
    'pc',          [0, 0, 0], ...
    'ih',          [0, 0, 0]);

% Process: Generate BEM surfaces
sFiles = bst_process('CallProcess', 'process_generate_bem', sFiles, [], ...
    'subjectname', sid, ...
    'nscalp',      1922, ...
    'nouter',      1922, ...
    'ninner',      1922, ...
    'thickness',   4, ...
    'method',      'brainstorm');  % Brainstorm

%% link raw files
glob_4d = sprintf('/work/duke/hcp-meg/%s/raw/*/c,rfDC', sid);
rawfiles = dir(glob_4d);
%%
for i=1:size(rawfiles,1)
    rawfilepath = [rawfiles(i).folder '/' rawfiles(i).name];
    sFiles = bst_process('CallProcess', 'process_import_data_raw', sFiles, [], ...
    'subjectname',    sid, ...
    'datafile',       {rawfilepath, '4D'}, ...
    'channelreplace', 1, ...
    'channelalign',   1, ...
    'evtmode',        'value');
end
