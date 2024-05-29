%% Inputs

pm.sc_name                  = 'Xonar DX ASIO(64)';
pm.fs_sc                    = 192000;           % Sampling rate sound card (Hz)
pm.freq_min                 = 5000;             % Min freq. to band pass (Hz)
pm.freq_max                 = 20000;            % Max freq. to band pass (Hz)
pm.ramp_time                = 0.005;            % Duration of sound ramp (s)
pm.d_sound                  = .5;               % Duration of sound (s)
pm.fs_ai                    = 250000;           % sampling rate national instrument (Hz)
pm.freq_high                = 4500;             % freq. for high pass filter after recording
pm.freq_low                 = 25000;            % freq. for low pass filter after recording
pm.ref                      = 20e-6;            % pm.reference pressure (Pa)
pm.mic_fac                  = 10;               % factor on the mic (V/Pa)

pm.box                  = input('Setup number: ');


%% Speakers
load(['Speaker calibration\CalibrationFile_setup' num2str(pm.box) '_right_speaker.mat'])
pm.Rp1                      = spk.lin_fit(1);   % Slope for linear fit of Right speaker calibration
pm.Rp2                      = spk.lin_fit(2);   % Intercept for linear fit of Right speaker calibration
pm.R_cal_factor             = spk.cal_factor;   % Calibration filter for Right speaker
pm.R_f_vec_cal              = spk.f_vec_h;      % frequencies to apply calibration filter to Right speaker
clear spk

load(['C:\Users\user\Google Drive\RatBehaviorRoom\Setup 1\Speaker calibration\CalibrationFile_rat42_left_speaker.mat'])
pm.Lp1                      = spk.lin_fit(1);   % Slope for linear fit of Left speaker calibration
pm.Lp2                      = spk.lin_fit(2);   % Intercept for linear fit of Left speaker calibration
pm.L_cal_factor             = spk.cal_factor;   % Calibration filter for Left speaker
pm.L_f_vec_cal              = spk.f_vec_h;      % frequencies to apply calibration filter to Left speaker
clear spk


%%
dB     = [75 70 65 60 55];
n      = numel(dB);
%RMS    = 20e-6*10.^(dB/20);

left_amp    = 10.^(dB/pm.Lp1-pm.Lp2/pm.Lp1);   %amplitude of the left sound
right_amp   = 10.^(dB/pm.Rp1-pm.Rp2/pm.Rp1);   %amplitude of the right sound

s_rng = rng;

for k=1:5
    
    sigL{k} = BPWN(pm.d_sound,pm.fs_sc,pm.L_cal_factor,pm.L_f_vec_cal,pm.freq_min,pm.freq_max,pm.ramp_time);
    
end

rng(s_rng);

for k=1:5
    
    sigR{k} = BPWN(pm.d_sound,pm.fs_sc,pm.R_cal_factor,pm.R_f_vec_cal,pm.freq_min,pm.freq_max,pm.ramp_time);
    
end

%% Initialize devices
% INITIALIZE PSYCHOTOOLBOX
pm.sc                   = init_PsyTB(pm.sc_name,pm.fs_sc);

% NATIONAL INSTRUMENT D/A
[pm.ai,pm.filename,~]   = init_NI(pm.d_sound,pm.fs_ai);

countL = 1;
countR = 1;

%%


close all
clearvars sig sig_rec db_nofilter sig_rec_ft db_filter 

side = input('Enter speaker side (1: left, 2: right)');

if side == 1
    
    countL = countL + 1;
    
    figure(1)
    hold on
    ax = gca;
    
    
    for l = 1:n
        
        for k=1:5
            
            sig{l,k}        = left_amp(l)*sigL{k};
            sig_rec{l,k}    = rec_sound(sig{l,k},'left',pm.filename,pm.ai,pm.d_sound,pm.sc);
            
            pause(1)
            
            n_sig       = numel(sig_rec{l,k});
            sig_pascal  = sig_rec{l,k}(.1*n_sig:.9*n_sig)/pm.mic_fac;
            rms_sound   = rms(sig_pascal);
            db_nofilter(l,k) = 20*log10(rms_sound/pm.ref);
            
            % high pass filter to remove power from low frequencies
            [b,a]     = butter(3,pm.freq_high/(pm.fs_ai/2),'high');
            sig_rec_ft{l,k}   = filter(b,a,sig_rec{l,k});
            
            % low pass filter to remove power from high frequencies
            [b,a]   = butter(3,pm.freq_low/(pm.fs_ai/2),'low');
            sig_rec_ft{l,k} = filter(b,a,sig_rec_ft{l,k});
            
            n_sig       = numel(sig_rec_ft{l,k});
            sig_pascal  = sig_rec_ft{l,k}(.1*n_sig:.9*n_sig)/pm.mic_fac;
            rms_sound   = rms(sig_pascal);
            db_filter(l,k) = 20*log10(rms_sound/pm.ref);
            
        end
        
%         plot(db_nofilter(l,:),'o')
%         ax.ColorOrderIndex = ax.ColorOrderIndex - 1;
        plot(db_filter(l,:),'*')
        
        disp(['target dB:   '        num2str(dB(l))]);
        disp(['achieved dB without filtering: '   num2str(mean(db_nofilter(l,:))) ' +- ' num2str(std(db_nofilter(l,:)))]);
        disp(['achieved dB with filtering: '      num2str(mean(db_filter(l,:))) ' +- ' num2str(std(db_filter(l,:)))]);
        disp('--------------------------------------------------------------');
        disp('');
        
    end
    
    sig_rec_nofilter_left   = sig_rec;
    sig_rec_filter_left     = sig_rec_ft;
    db_nofilter_left        = db_nofilter;
    db_filter_left          = db_filter;

    ylabel('output dB')
    title('left speaker')
    saveas(gcf,['C:\Users\user\Google Drive\RatBehaviorRoom\Common scripts\Speaker calibration\Test\left_profile' num2str(countL) '.png'])
    
    figure
    plot(ones(1,n),dB','o')
    hold on
    errorbar(2*ones(1,n),mean(db_filter_left,2),std(db_filter_left,0,2),'o')
    xlim([.8 2.2])
    grid on
    ylabel('recorded dB SPL')
    title('left speaker')
    set(gca,'xtick',[])
    
    saveas(gcf,['C:\Users\user\Google Drive\RatBehaviorRoom\Common scripts\Speaker calibration\Test\left_averages' num2str(countL) '.png'])
    
    figure
    errorbar(dB,mean(db_filter_left,2)-dB',std(db_filter_left,0,2),'*')
    xlabel('desired dB SPL')
    ylabel('output difference (dB SPL)')
    title('left speaker')
    
    saveas(gcf,['C:\Users\user\Google Drive\RatBehaviorRoom\Common scripts\Speaker calibration\Test\left_differences' num2str(countL) '.png'])
    
elseif side == 2
    
    countR = countR + 1;
    
    figure(2)
    hold on
    ax = gca;
    
    
    for l = 1:n
        
        for k=1:5
            
            sig{l,k}        = right_amp(l)*sigR{k};
            sig_rec{l,k}    = rec_sound(sig{l,k},'right',pm.filename,pm.ai,pm.d_sound,pm.sc);
            
            pause(1)
            
            n_sig       = numel(sig_rec{l,k});
            sig_pascal  = sig_rec{l,k}(.1*n_sig:.9*n_sig)/pm.mic_fac;
            rms_sound   = rms(sig_pascal);
            db_nofilter(l,k) = 20*log10(rms_sound/pm.ref);
            
            % high pass filter to remove power from low frequencies
            [b,a]     = butter(3,pm.freq_high/(pm.fs_ai/2),'high');
            sig_rec_ft{l,k}   = filter(b,a,sig_rec{l,k});
            
            % low pass filter to remove power from high frequencies
            [b,a]   = butter(3,pm.freq_low/(pm.fs_ai/2),'low');
            sig_rec_ft{l,k} = filter(b,a,sig_rec_ft{l,k});
            
            n_sig       = numel(sig_rec_ft{l,k});
            sig_pascal  = sig_rec_ft{l,k}(.1*n_sig:.9*n_sig)/pm.mic_fac;
            rms_sound   = rms(sig_pascal);
            db_filter(l,k) = 20*log10(rms_sound/pm.ref);
            
        end
        
%         plot(db_nofilter(l,:),'o')
%         ax.ColorOrderIndex = ax.ColorOrderIndex - 1;
        plot(db_filter(l,:),'*')
        
        disp(['target dB:   '        num2str(dB(l))]);
        disp(['achieved dB without filtering: '   num2str(mean(db_nofilter(l,:))) ' +- ' num2str(std(db_nofilter(l,:)))]);
        disp(['achieved dB with filtering: '      num2str(mean(db_filter(l,:))) ' +- ' num2str(std(db_filter(l,:)))]);
        disp('--------------------------------------------------------------');
        disp('');
        
    end
    
    sig_rec_nofilter_right   = sig_rec;
    sig_rec_filter_right     = sig_rec_ft;
    db_nofilter_right        = db_nofilter;
    db_filter_right          = db_filter;
    
    ylabel('output dB')
    title('right speaker')
    
%     saveas(gcf,['C:\Users\user\Google Drive\RatBehaviorRoom\Common scripts\Speaker calibration\Test\right_profile' num2str(countR) '.png'])
    
    figure
    plot(ones(1,n),dB','o')
    hold on
    errorbar(2*ones(1,n),mean(db_filter,2),std(db_filter,0,2),'o')
    xlim([.8 2.2])
    grid on
    ylabel('recorded dB SPL')
    title('right speaker')
    set(gca,'xtick',[])
    
%     saveas(gcf,['C:\Users\user\Google Drive\RatBehaviorRoom\Common scripts\Speaker calibration\Test\right_averages' num2str(countR) '.png'])
    
    figure
    errorbar(dB,mean(db_filter,2)-dB',std(db_filter,0,2),'*')
    xlabel('desired dB SPL')
    ylabel('output difference (dB SPL)')
    title('right speaker')
    
%     saveas(gcf,['C:\Users\user\Google Drive\RatBehaviorRoom\Common scripts\Speaker calibration\Test\right_differences' num2str(countR) '.png'])
    
end

