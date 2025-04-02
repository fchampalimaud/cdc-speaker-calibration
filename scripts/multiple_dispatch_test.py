from speaker_calibration.sound import create_sound_file, pure_tone

signal = pure_tone(2, 96000)

create_sound_file(signal, "test")
create_sound_file(signal, signal, "test2")
