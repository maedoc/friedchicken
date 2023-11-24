sids = {
    '102816'
'104012'
'105923'
'106521'
'108323'
'109123'
'111514'
'112920'
'113922'
    }

for i=1:length(sids)
   
megfield_pp0_new_subject(sids{i})
megfield_pp2_clean_and_gain(sids{i})
end

megfield_pp3_convert_all_runs