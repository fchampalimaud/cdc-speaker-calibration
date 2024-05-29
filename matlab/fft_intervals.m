function [fft_av,f_vec_h,n_int,int_samp,RMS] =  fft_intervals(sig_rec,time_cons,fs_ai,smooth_fac)

n_int       = floor(length(sig_rec)/(time_cons*fs_ai));			% number of intervals
int_samp    = (time_cons*fs_ai);                                % interval in samples

fft_int     = zeros(int_samp,n_int-9);

for i = 5:n_int-5	
	sig_fft      = sig_rec((i)*int_samp+1:(i+1)*int_samp);      % interval to consider
	fft_int(:,i) = abs(fft(sig_fft)).^2;                           % abs value signal
end

f_vec       = fs_ai*(0:int_samp-1)/int_samp;	% frequency vector
fft_av      = sqrt(mean(fft_int,2));                  % take the mean of all intervals

% single-sided spectrum

f_vec_h     = f_vec(1:end/2+1);
fft_av      = fft_av(1:end/2+1);
fft_av      = smooth(fft_av,smooth_fac);


freq1 = 2500;
freq2 = 35000;

n1 = floor(freq1*time_cons)+1;
n2 = floor(freq2*time_cons)+1;

% f_vec_h_rat = f_vec_h(n1:n2);
% N = n2-n1 + 1;

sum_fft = 2*sum(fft_int(n1:n2,:))/int_samp;
rms_fft = sqrt(sum_fft/int_samp);

RMS     = mean(rms_fft,2);