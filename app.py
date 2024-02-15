import os
from flask import Flask, request, jsonify
from noisereduce import reduce_noise
from pedalboard import *
import librosa
import soundfile as sf

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_audio():
  # Check if file is present
  if 'audio' not in request.files:
    return jsonify({'error': 'No audio file provided'}), 400

  # Get audio file
  print('audio received')
  audio_file = request.files['audio']


  # Read audio data
  with audio_file.open() as f:
    audio, sr = librosa.load(f, sr=None)

  # Reduce noise and apply effects
  reduced_noise = reduce_noise(y=audio, sr=sr, stationary=True, prop_decrease=0.75)

  board = Pedalboard([
    NoiseGate(threshold_db=-30, ratio=1.5, release_ms=250),
    Compressor(threshold_db=-16, ratio=2.5),
    LowShelfFilter(cutoff_frequency_hz=400, gain_db=10, q=1),
    Gain(gain_db=10)
  ])

  effected = board(reduced_noise, sr)

  # Save processed audio to temporary file
  temp_file = f'/tmp/{audio_file.filename}'
  sf.write(temp_file, effected, sr)

  # Return processed audio
  with open(temp_file, 'rb') as f:
    audio_data = f.read()

  # Clean up temporary file
  os.remove(temp_file)

  return jsonify({'data': audio_data})

if __name__ == '__main__':
  app.run(debug=True)
