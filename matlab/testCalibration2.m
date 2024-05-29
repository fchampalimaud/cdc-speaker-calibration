function [rKelly, in] = testCalibration2(rKelly, in, n, att)
% create white noise

rng(10);
noise_bef = noise(.2,in.n_samp_sc_st);								

% Correct noise

f_vec_sc_h = in.f_vec_sc_st(1:end/2+1); % single-sided freq vector 
int_samp   = (in.time_cons*in.fs_ai);   % interval in samples

f_interp             = interp1(rKelly.f_vec_h,.5*int_samp*rKelly.cal_factor,f_vec_sc_h);	% by default not all the frequencies will be here, so interpolate (linearly)
calibration_to_use   = [f_interp f_interp(end-1:-1:2)];	                   % everything must be symmetric
freq_to_use          = ( (f_vec_sc_h>in.freq_min) & (f_vec_sc_h<in.freq_max) );  % frequencies to use

% freq_to_cut          = (f_vec_sc_h>10000) & (f_vec_sc_h<12000);
% freq_to_use          = freq_to_use.*not(freq_to_cut);

m    = in.n_samp_sc_st/in.fs_sc;
n5Hz = 15;
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

%att = (in.target_RMS-rKelly.p(2))/rKelly.p(1);
sig         = sig*att;

% record sound
sig_rec     = rec_sound(sig,in.speaker_side,in.filename,in.ai,in.s_dur_st,in.pa_handle);

[~,~,~,~,RMS] =  fft_intervals(sig_rec,in.time_cons,in.fs_ai,1);

RMS_fft = RMS/in.mic_fac;
dB_fft  = 20*log10(RMS_fft/in.ref);

% high pass filter to remove power from low frequencies
[b,a]     = butter(3,in.freq_high/(in.fs_ai/2),'high');
sig_rec   = filter(b,a,sig_rec);

% low pass filter to remove power from high frequencies
[b,a] = butter(3,in.freq_low/(in.fs_ai/2),'low');
sig_rec = filter(b,a,sig_rec);

% Calculate dB
sig_pascal = sig_rec(.1*in.n_samp_ai_st:.9*in.n_samp_ai_st)/in.mic_fac;
rms_sound  = rms(sig_pascal);
db_spl     = 20*log10(rms_sound/in.ref);


disp(['achieved dB: '        num2str(db_spl)]);
%disp(['achieved dB with fft: '        num2str(dB_fft)]);

rKelly.dB_spl_test(n) = db_spl;
rKelly.dB_fft_test(n) = dB_fft;

