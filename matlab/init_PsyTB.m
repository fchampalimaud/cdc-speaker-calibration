function pa_handle = init_PsyTB(name_audio,fs_sound)

InitializePsychSound(1);                                        % initialize
devices    = PsychPortAudio('GetDevices',[],[]);  

% get the audio devices
for i = 1:length(devices)
    comp_string(i) = strcmp(devices(i).DeviceName,name_audio);  % find the right one
end

% device_id = devices(find(comp_string==1)).DeviceIndex;        % get the ID number
device_id  = devices((comp_string==1)).DeviceIndex;  %!!!!      % get the ID number
nrchannels = 2;                                                 % nchannels psychotoolbox
mode       = 1;                                                 % play only
aggressive = 1;                                                 % don't be aggressive
pa_handle   = PsychPortAudio('Open', device_id, mode, aggressive, fs_sound, nrchannels, 64,.01);