function [res,spk] = Calibrate(rigID,side)

%% Clear n close
clearvars -except rigID side
close all
clc

speakerID = 2;

in.rig_name  = num2str(rigID);                % Setup ID number
in.spkr_no   = num2str(speakerID);

if side == 2
    input('Please ensure the calibration mic is correctly positioned in front of RIGHT speaker. Then hit any key.')
    in.speaker_side  = 'right';     % speaker to use, 'left', 'rigth', 'both'
else
    input('Please ensure the calibration mic is correctly positioned in front of LEFT speaker. Then hit any key.')
    in.speaker_side  = 'left';      % speaker to use, 'left', 'rigth', 'both'
end

%eval(['cd(''C:\Users\user\Google D

%% Input parameters
in.fs_sc               = 192000;                        % sampling rate sound card (Hz)
in.fs_ai               = 250000;                        % sampling rate national instrument (Hz)
in.name_audio          = 'Xonar DX ASIO(64)';           % name sound card (IMPORTANT: ASIO)


in.s_dur_cal           = 30;                            % total duration of sound played for calibration (s)
in.s_dur_db            = 15;                            % total duration of sound played for dB estimation (s)
in.s_dur_st            = 5;                             % total duration of sound played for dB estimation (s)
in.ramp_time           = 0.005;                         % ramp time (s)
in.ref                 = 20e-6;                         % in.reference pressure (Pa)
in.mic_fac             = 10;                            % factor on the mic (V/Pa)
in.att_min             = -.65;                          % minimum speaker attenuation value (log)
in.att_steps           = 15;                            % number of attenuation steps
in.att_max             = -.1;                           % maximum speaker attenuation value (log)

in.smooth_fac          = 1;                             % smoothing factor fft
in.time_cons           = 0.025;                         % time cons to estimate the psd (s)
in.freq_min            = 5000;                          % minimum frequence to consider to pass band
in.freq_max            = 20000;                         % maximum frequence to consider to pass band
in.freq_high           = 4500;                          % freq. for high pass filter after recording
in.freq_low            = 25000;                         % freq. for low pass filter after recording
in.amp                 = 0.8; %change to .85 for calibration of headphones!


%% 1) Perform calibration of speaker

[in,res,spk] = runCalibration2(in);


%% Save
filename = ['C:\Speaker Calibration\Calibration Files\CalibrationFile_setup' in.rig_name '_' in.speaker_side '_speaker.mat'];
save(filename,'spk')

filename = ['C:\Speaker Calibration\Calibration Files\CalibrationFileALL_setup' in.rig_name '_' in.speaker_side '_speaker.mat'];
save(filename,'in', 'res','spk')


