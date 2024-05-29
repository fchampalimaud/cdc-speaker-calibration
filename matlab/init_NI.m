function [ai,filename_log,nch] = init_NI(duration,fs_ai)


ch                         = 1;                        % channel to use
nch                        = length(ch);               % number of channels
ai                         = daq.createSession('ni');  % create the ai session

addAnalogInputChannel(ai,'Dev1',ch, 'Voltage');        % add ai channels

ai.Channels.Range          = [-10 10];                 % if the mic is at 10V/Pa, this should work fine
ai.DurationInSeconds       = duration;                 % set the duration (s)
ai.Rate                    = fs_ai;                    % set the sampling rate (Hz)
ai.Channels.TerminalConfig = 'SingleEnded';            % 'SingleEnded' if using the MIC, otherwise 'Referenced' (or commment this line)
filename_log               = 'log.bin';                % filename to log the ai data