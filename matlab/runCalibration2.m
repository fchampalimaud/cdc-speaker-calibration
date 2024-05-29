function [in,rKelly,calTech] = runCalibration2(in)


%% Initial computations

% in.att_fac             = in.att_min:in.att_step:in.att_max;                     % amplification factor
in.log_att = linspace(in.att_min,in.att_max,in.att_steps);% linspace(-.75,-.56,18); %linspace(-.65,-.1,15) (-1.0,-.3,15)
in.att_fac = 10.^in.log_att;

in.n_samp_sc_cal       = in.s_dur_cal*in.fs_sc;                                 % number of sound samples for Sound Card (calibration)
in.n_samp_ai_cal       = in.s_dur_cal*in.fs_ai;                                 % number of sound samples for National Instruments (calibration)

in.time_sc_cal         = (1:in.n_samp_sc_cal)/in.fs_sc;                         % time vector for Sound Card (s) (calibration)
in.time_ai_cal         = (1:in.n_samp_ai_cal)/in.fs_ai;                         % time vector for National Instruments (s) (calibration)

in.f_vec_sc_cal        = ((0:in.n_samp_sc_cal-1)/in.n_samp_sc_cal)*in.fs_sc;    % frequency vector for Sound Card (calibration)
in.f_vec_ai_cal        = ((0:in.n_samp_ai_cal-1)/in.n_samp_ai_cal)*in.fs_ai;    % frequency vector for National Instruments (calibration)


in.n_samp_sc_db        = in.s_dur_db*in.fs_sc;                                  % number of sound samples for Sound Card (dB estimation)
in.n_samp_ai_db        = in.s_dur_db*in.fs_ai;                                  % number of sound samples for National Instruments (dB estimation)

in.time_sc_db          = (1:in.n_samp_sc_db)/in.fs_sc;                          % time vector for Sound Card (s) (dB estimation)
in.time_ai_db          = (1:in.n_samp_ai_db)/in.fs_ai;                          % time vector for National Instruments (s) (dB estimation)

in.f_vec_sc_db         = ((0:in.n_samp_sc_db-1)/in.n_samp_sc_db)*in.fs_sc;      % frequency vector for Sound Card (dB estimation)
in.f_vec_ai_db         = ((0:in.n_samp_ai_db-1)/in.n_samp_ai_db)*in.fs_ai;      % frequency vector for National Instruments (dB estimation)

in.n_samp_sc_st        = in.s_dur_st*in.fs_sc;                                  % number of sound samples for Sound Card (dB estimation)
in.n_samp_ai_st        = in.s_dur_st*in.fs_ai;                                  % number of sound samples for National Instruments (dB estimation)

in.time_sc_st          = (1:in.n_samp_sc_st)/in.fs_sc;                          % time vector for Sound Card (s) (dB estimation)
in.time_ai_st          = (1:in.n_samp_ai_st)/in.fs_ai;                          % time vector for National Instruments (s) (dB estimation)

in.f_vec_sc_st         = ((0:in.n_samp_sc_st-1)/in.n_samp_sc_st)*in.fs_sc;      % frequency vector for Sound Card (dB estimation)
in.f_vec_ai_st         = ((0:in.n_samp_ai_st-1)/in.n_samp_ai_st)*in.fs_ai;      % frequency vector for National Instruments (dB estimation)

%% Initialize
% INITIALIZE PSYCHOTOOLBOX
in.pa_handle           = init_PsyTB(in.name_audio,in.fs_sc);

% NATIONAL INSTRUMENT D/A
[in.ai,in.filename,~]  = init_NI(in.s_dur_cal,in.fs_ai);

rKelly = struct();

%% Generate parameters
disp('Computing calibration factor')
[rKelly, in] = calibrationFactor1(rKelly, in);

clear in.ai
[in.ai,in.filename,~] = init_NI(in.s_dur_db,in.fs_ai);
 
%% Run calibration
disp('Computing amplification response curve')
for n = 1:numel(in.att_fac)
    
    [rKelly, in] = calibraTOR1(rKelly, in, n);
    
end

figure(2)
plot(in.log_att,rKelly.db_spl_aft_cal)
% hold on
% plot(in.att_fac,rKelly.dB_fft)
xlabel('log of amplification factor')
ylabel('dB SPL')


figure(3)
plot(in.att_fac,rKelly.rms_sound_aft_cal)
% hold on
% plot(in.att_fac,rKelly.RMS_fft)
xlabel('amplification factor')
ylabel('rms of sound')

rKelly.p = polyfit(in.log_att, rKelly.db_spl_aft_cal, 1);

fitlm(in.log_att, rKelly.db_spl_aft_cal)

disp(['Slope: ' num2str(rKelly.p(1)) ', Intercept: ' num2str(rKelly.p(2))])

%% Test fit

clear in.ai
[in.ai,in.filename,~] = init_NI(in.s_dur_st,in.fs_ai);

tdB     = 70:-5:20;

for j = 1:length(tdB)
    
    att           = (tdB(j) - rKelly.p(2))/rKelly.p(1);
    att           = 10.^att;

    disp('--------------------------------')
    disp(['target dB:   '        num2str(tdB(j))]);
    [rKelly, in] = testCalibration2(rKelly, in, j, att);

end

figure(4)
plot(tdB,rKelly.dB_spl_test)
hold on
% plot(tdB,rKelly.dB_fft_test)
plot(tdB,tdB)
xlabel('desired dB')
ylabel('recorded dB')

%% Output variables

calTech.cal_factor = rKelly.cal_factor;
calTech.f_vec_h    = rKelly.f_vec_h;
calTech.lin_fit    = rKelly.p;

figure(4)
saveas(gcf,['C:\Speaker Calibration\Calibration Files\_' in.speaker_side '_Figure4_TestdB.png'])
% close(gcf)
figure(3)
saveas(gcf,['C:\Speaker Calibration\Calibration Files\_' in.speaker_side '_Figure3_RMSfit.png'])
% close(gcf)
figure(2)
saveas(gcf,['C:\Speaker Calibration\Calibration Files\_' in.speaker_side '_Figure2_dBfit.png'])
% close(gcf)
figure(1)
saveas(gcf,['C:\Speaker Calibration\Calibration Files\_' in.speaker_side '_Figure1_ffts.png'])
% close(gcf)


