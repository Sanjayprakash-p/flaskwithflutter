from flask import Flask, request,send_file, jsonify
from pedalboard.io import AudioFile
from pedalboard import *
import noisereduce as nr
app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    print('request received')
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        file.save('uploaded_audio.wav')  # Save the file to disk
        
    sr=44100
    with AudioFile('uploaded_audio.wav').resampled_to(sr) as f:
        audio = f.read(f.frames)

    reduced_noise = nr.reduce_noise(y=audio, sr=sr, stationary=True, prop_decrease=1)

    board = Pedalboard([
        NoiseGate(threshold_db=-30, ratio=1.5, release_ms=250),
        Compressor(threshold_db=-16, ratio=2.5),
        LowShelfFilter(cutoff_frequency_hz=400, gain_db=10, q=1),
        Gain(gain_db=10)])

    effected = board(reduced_noise, sr)


    with AudioFile('ouput1.wav', 'w', sr, effected.shape[0]) as f:
        f.write(effected)
    print('sucess')
    return send_file('ouput1.wav', as_attachment=True), 200
    

if __name__ == '__main__':
    app.run(debug=True)


