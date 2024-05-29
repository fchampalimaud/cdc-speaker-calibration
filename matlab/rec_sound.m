function sig_rec = rec_sound(sig_to_play,speaker_side,filename_log,ai,duration,pa_handle)

ch  = 1;
nch = length(ch);

if strcmp(speaker_side,'left')==1
    sig_to_play = [sig_to_play; 0*sig_to_play];                   % zero the right channel
elseif strcmp(speaker_side,'right')==1
    sig_to_play = [0*sig_to_play; sig_to_play];                   % zero the left channel
elseif strcmp(speaker_side,'both')==1
    sig_to_play = [sig_to_play; sig_to_play];                     % same thing on both channels
end

fid1 = fopen(filename_log,'w');  % open the log data file
lh   = addlistener(ai,'DataAvailable',@(src, event)logData(src, event, fid1));  % add a listener for logging the data

PsychPortAudio('FillBuffer', pa_handle, sig_to_play);            % fill the buffer
% --------------------------------------------------------

% --------------------------------------------------------
% Trigger the background acquisition
% --------------------------------------------------------
ai.startBackground;                             % start the background acquisition
% --------------------------------------------------------

% --------------------------------------------------------
% Trigger the sound and wait enough
% --------------------------------------------------------
PsychPortAudio('Start', pa_handle, 1, 0, 1);     % trigger the sound
pause(duration+0.2);                           % wait for acquisition and sound to be over
% --------------------------------------------------------

% --------------------------------------------------------
% Stop the ai device and get the logged data
% --------------------------------------------------------
ai.stop;                                        % stop the device
pause(0.2)
delete(lh);                                     % delete the listener
fclose(fid1);                                   % close the log file
pause(0.2)
fid2 = fopen(filename_log,'r');                 % open it again
[data,~] = fread(fid2,[nch+1,inf],'double');    % read the data
fclose(fid2);                                   % close it again
sig_rec = data(ch+1,:);                         % place the data in a matrix

PsychPortAudio('DeleteBuffer');

end

function logData(src, evt, fid)
% Add the time stamp and the data values to data. To write data sequentially,
% transpose the matrix.

%   Copyright 2011 The MathWorks, Inc.

data = [evt.TimeStamps, evt.Data]' ;
fwrite(fid,data,'double');
end