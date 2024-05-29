function [rKelly, in] = calibraTOR1(rKelly, in, n)
% create white noise
rng(10);

%noise_bef = noise(.2,in.n_samp_sc_db);
noise_bef = .2*randn(1,in.n_samp_sc_db);


% Correct noise

f_vec_sc_h = in.f_vec_sc_db(1:end/2+1); % single-sided freq vector 
int_samp   = (in.time_cons*in.fs_ai);   % interval in samples

f_interp             = interp1(rKelly.f_vec_h,.5*int_samp*rKelly.cal_factor,f_vec_sc_h);	% by default not all the frequencies will be here, so interpolate (linearly)
calibration_to_use   = [f_interp f_interp(end-1:-1:2)];	                   % everything must be symmetric
freq_to_use          = (f_vec_sc_h>in.freq_min) & (f_vec_sc_h<in.freq_max);  % frequencies to use

% freq_to_cut          = (f_vec_sc_h>10000) & (f_vec_sc_h<12000);
% freq_to_use          = freq_to_use.*not(freq_to_cut);

m    = in.n_samp_sc_db/in.fs_sc;
n5Hz = 50;
fix  = (0.5*(1-cos(linspace(0, pi, n5Hz)))).^2;

freq_to_use(m*in.freq_min-n5Hz+2:m*in.freq_min+1)  = fix;
freq_to_use(m*in.freq_max+1:m*in.freq_max+n5Hz) = fix(end:-1:1);

filter_to_use        = [freq_to_use freq_to_use(end-1:-1:2)];              % symmetry again

% %no filter
% filter_to_use(:)   = 1;

noise_cal            = ifft(fft(noise_bef).*calibration_to_use.*filter_to_use);
                                            
%noise_vec            = noise_cal;% ./ max(abs(noise_cal));   % normalize to make sure it's between -1 and 1
noise_vec              = noise_cal*.2/rms(noise_cal);
noise_vec(noise_vec>1) = NaN;

disp(['Number of elements truncated: ' num2str(sum(isnan(noise_vec)))]);
noise_vec(isnan(noise_vec)) = 0;

% create ramp (sinusoidal)

nr = floor(in.fs_sc * in.ramp_time);																
r  = (0.5*(1-cos(linspace(0, pi, nr)))).^2;
r  = [r, ones(1, length(noise_vec) - nr * 2), fliplr(r)];

% apply ramp

noise_ramp = noise_vec .*r;		


%% NOW PLAY AND RECORD THE CALIBRATED SOUNDS

% create sound
sig         = noise_ramp;

% apply attenuation factor
sig         = sig*in.att_fac(n);

sig_rec     = rec_sound(sig,in.speaker_side,in.filename,in.ai,in.s_dur_db,in.pa_handle);

sig_aft_cal = sig_rec;

% high pass filter to remove power from low frequencies
[b,a] = butter(3,in.freq_high/(in.fs_ai/2),'high');
sig_aft_cal = filter(b,a,sig_aft_cal);

% low pass filter to remove power from high frequencies
[b,a] = butter(3,in.freq_low/(in.fs_ai/2),'low');
sig_aft_cal = filter(b,a,sig_aft_cal);

%% Check that spectrum is flat

[fft_aft_cal,f_vec_h,~,int_samp,RMS] =  fft_intervals(sig_rec,in.time_cons,in.fs_ai,in.smooth_fac);


%% plot signals after calibration

% figure('Position',[558   208   789   626])
% subplot(2,3,1)
% hist(noise_bef,64)
% % xlim([-1 1])
% title('Input pre-cal')
% box off; %axis tight
% 
% subplot(2,3,2)
% hist(noise_vec,64)
% % xlim([-1 1])
% title('Input post-cal')
% box off; %axis tight
% 
% subplot(2,3,3)
% hist(sig_rec,64)
% title('Output post-cal')
% box off; axis tight
% drawnow
% 
% subplot(2,3,4)
% plot(in.f_vec_sc_db/1000,abs(fft(noise_bef))*2/int_samp,'k')
% xlim([2 23])
% xlabel('Frequency (kHz)')
% ylabel('Abs FFT')
% box off; %axis tight
% 
% subplot(2,3,5)
% plot(in.f_vec_sc_db/1000,abs(fft(noise_vec))*2/int_samp,'k')
% xlim([2 23])
% xlabel('Frequency (kHz)')
% ylabel('Abs FFT')
% box off; %axis tight
% 
% subplot(2,3,6)
% % plot(f_vec_h/1000,abs(fft_aft_cal)*2/int_samp,'k'); hold on
% % plot(f_vec_h/1000,smooth(abs(fft_aft_cal),10)*2/int_samp,'r')
% xlim([2 23])
% xlabel('Frequency (kHz)')
% ylabel('Abs FFT')
% % legend('Raw','Smoothed')
% box off; %axis tight
% drawnow

%% estimate dB

sig_aft_cal_pascal = sig_aft_cal(.1*in.n_samp_ai_db:.9*in.n_samp_ai_db)/in.mic_fac;
sig_bef_cal_pascal = rKelly.sig_bef_cal(.1*in.n_samp_ai_db:.9*in.n_samp_ai_db)/in.mic_fac;

rms_sound_aft_cal  = rms(sig_aft_cal_pascal);
rms_sound_bef_cal  = rms(sig_bef_cal_pascal);

RMS_fft            = RMS/in.mic_fac;

db_spl_aft_cal     = 20*log10(rms_sound_aft_cal/in.ref);
db_spl_bef_cal     = 20*log10(rms_sound_bef_cal/in.ref);
dB_fft             = 20*log10(RMS_fft/in.ref);

disp(['Attenuation factor: '        num2str(in.att_fac(n))]);
disp(['dB SPL after calibration: '  num2str(db_spl_aft_cal)]);
disp(['dB SPL before calibration: ' num2str(db_spl_bef_cal)]);
disp('----------------------------------------');
%disp(['dB SPL with fft: ' num2str(dB_fft)]);
            

%% Final plot before and after

% figure('Position',[558   208   789   626])
figure(1)
subplot(1,3,1)
hold on
plot(f_vec_h/1000,abs(rKelly.fft_bef_cal)*2/int_samp,'k')
xlim([.02 22])
ax = gca;
ax.XScale = 'log';
ax.XTick  = [.1 1 10];
% set(gca, 'XScale','log')
xlabel('frequency (kHz)')
ylabel('ABS FFT')
title('Before calibration')

subplot(1,3,2)
hold on
plot(f_vec_h/1000,abs(fft_aft_cal)*2/int_samp)
xlim([5 22])
ax = gca;
ax.XScale = 'log';
ax.XTick  = [.1 1 10];
% set(gca, 'XScale','log')
xlabel('frequency (kHz)')
ylabel('ABS FFT')
title('After calibration')

subplot(1,3,3)
plot(in.f_vec_ai_db/1000,abs(fft(sig_aft_cal)*2/in.n_samp_ai_db))
xlim([5 22])
ax = gca;
ax.XScale = 'log';
ax.XTick  = [.1 1 10];
% set(gca, 'XScale','log')
xlabel('frequency (kHz)')
ylabel('ABS FFT')
title('After calibration')
drawnow

%% SAVE RESULTS

rKelly.db_spl_aft_cal(n)    = db_spl_aft_cal;       % dB SPL after calibration
rKelly.db_spl_bef_cal(n)    = db_spl_bef_cal;       % dB SPL before calibration
rKelly.sig_aft_cal{n}       = sig_aft_cal;          % signal after calibration
rKelly.fft_aft_cal{n}       = fft_aft_cal;          % abs fft of signal after calibration
rKelly.rms_sound_aft_cal(n) = rms_sound_aft_cal;    % rms of sound after calibration
rKelly.noise_cal{n}         = noise_cal;            % calibrated input noise

rKelly.RMS_fft(n)           = RMS_fft;    % rms of sound calculated with fft
rKelly.dB_fft(n)            = dB_fft;     % dB SPL calculated with fft


% filename = ['calibrationResults_' in.date '_' in.time '_' num2str(in.speaker_side)];
% save(filename,'in','rKelly')                                % save the structure
