function [rKelly, in] = calibrationFactor1(rKelly, in)
% ----------------------------------------------------------------------------------------------------------------------------
% SCRIPT TO CREATE A MAPPING BETWEEN INPUT TONE AMPLITUDE AND LOUDNESS (dB)
% ----------------------------------------------------------------------------------------------------------------------------

%% Create signal

% create white noise (truncated gaussian between -1 and 1)

%sig = noise(.2,in.n_samp_sc_cal);
sig = .2*randn(1,in.n_samp_sc_cal);

sig(sig>1) = NaN;
disp(['Number of elements truncated: ' num2str(sum(isnan(sig)))]);
sig(isnan(sig)) = 0;

% %%
% 
% f = in.freq_min-1000:50:in.freq_max+1000;
% 
% sig = zeros(1,in.n_samp_sc_cal);
% 
% for i=1:length(f)
%     
%     sig = sig + 1/length(f)*sin(2*pi*f(i)*in.time_sc_cal);
%     
% end

%%

% add ramp

nr = floor(in.fs_sc * in.ramp_time);
r  = (0.5*(1-cos(linspace(0, pi, nr)))).^2;
r  = [r, ones(1, in.n_samp_sc_cal - nr * 2), fliplr(r)];

sig2 = in.amp * sig .* r;

% play and record sound

sig_rec     = rec_sound(sig2,in.speaker_side,in.filename,in.ai,in.s_dur_cal,in.pa_handle);

sig_bef_cal = sig_rec;

%% Compute fft and calibration factor

[fft_bef_cal,f_vec_h,n_int] =  fft_intervals(sig_rec,in.time_cons,in.fs_ai,in.smooth_fac);

% calibration factor

cal_factor  = 1./fft_bef_cal;    % the calibration must be 1/amp at each frequency bin


%% plot the signals before calibration

% figure('Position',[558   208   789   626])
% subplot(2,2,1)
% hist(sig,64)
% xlim([-1 1])
% title('Input pre-cal')
% box off; %axis tight
% 
% subplot(2,2,2)
% hist(sig_rec,64)
% title('Output pre-cal')
% box off; axis tight
% drawnow
% 
% subplot(2,2,3)
% plot(in.f_vec_sc_cal/1000,abs(fft(sig))*2/in.n_samp_sc_cal,'k')
% xlim([2 23])
% xlabel('Frequency (kHz)')
% ylabel('Abs FFT')
% box off; %axis tight
% 
% subplot(2,2,4)
% % plot(f_vec_h/1000,abs(fft_bef_cal)*2/int_samp,'k'); hold on
% % plot(f_vec_h/1000,smooth(abs(fft_bef_cal),10)*2/int_samp,'r')
% xlim([2 23])
% xlabel('Frequency (kHz)')
% ylabel('Abs FFT')
% % legend('Raw','Smoothed')
% box off; %axis tight
% drawnow

%% SAVE RESULTS

getnow = datevec(now);     % get the current time

in.date               = date;                                    % day
in.time               = [num2str(getnow(4)) num2str(getnow(5))]; % save the hour and minutes

rKelly.cal_factor           = cal_factor;                              % calibration factor (multiply in freq. domin.ain)
rKelly.f_vec_h              = f_vec_h;                                 % half spectrum frequency vector
rKelly.sig_bef_cal          = sig_bef_cal;                             % signal before calibration
rKelly.fft_bef_cal          = fft_bef_cal;                             % abs fft of signal before calibration

% filename = ['calibrationParam_' in.date '_' in.time '_' num2str(in.speaker_side)];
% save(filename,'in','rKelly')                                % save the structure

end