import os
import io
import json
from datetime import datetime
from flask import Flask, render_template, request
from PIL import Image
import torch
import torchvision.transforms as transforms
from torchvision import models
import requests
import serial
import time
from youtubesearchpython import VideosSearch
import subprocess
ser = serial.Serial('/dev/ttyUSB0', 9600)
time.sleep(2)  


app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ARCHIVE_FILE = 'archive.json'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

API_KEY = ""

# 감정 분석용 모델
emotion_model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet18', weights='IMAGENET1K_V1')
emotion_model.eval()

# 풍경 인식용 Places365 모델 로드
def load_places365_model():
    model = models.resnet18(num_classes=365)
    checkpoint = torch.hub.load_state_dict_from_url(
        'http://places2.csail.mit.edu/models_places365/resnet18_places365.pth.tar',
        map_location=torch.device('cpu')
    )
    state_dict = {str.replace(k, 'module.', ''): v for k, v in checkpoint['state_dict'].items()}
    model.load_state_dict(state_dict)
    model.eval()
    return model

places365_model = load_places365_model()

# Places365 클래스 로드
with open('categories_places365.txt') as f:
    classes = [line.strip().split(' ')[0][3:] for line in f.readlines()]

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def get_music_recommendation(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    res = requests.post(url, headers=headers, json=data)
    if res.status_code == 200:
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"Error: {res.status_code}, {res.text}"

def predict_emotion(image):
    outputs = emotion_model(image.unsqueeze(0))
    _, predicted = torch.max(outputs, 1)
    classes = ['happy', 'sad', 'angry', 'surprised']
    return classes[predicted % len(classes)]

def predict_scene(image):
    outputs = places365_model(image.unsqueeze(0))
    _, idx = torch.max(outputs, 1)
    return classes[idx]

def save_to_archive(entry):
    archive = []
    if os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE, 'r') as f:
            archive = json.load(f)
    archive.insert(0, entry)  # 최신이 위로
    with open(ARCHIVE_FILE, 'w') as f:
        json.dump(archive, f, indent=4, ensure_ascii=False)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        emotion = None
        scene = None
        music_recommendation = None
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if 'text' in request.form and request.form['text'].strip() != "":
            text = request.form['text'].strip()
            prompt = f"'{text}'라는 감정 상태에 어울리는 클래식 곡명을 추천해줘.출력은 곡명 작곡가명만 하고 1곡만만 EX) 월광소나타 3악장,베토벤 이런식으로"
            music_recommendation = get_music_recommendation(prompt)
            title,composer=music_recommendation.split(",")
            
            ser.write(b'PLAY\n')
            

            save_to_archive({
                'type': 'text',
                'timestamp': timestamp,
                'text': text,
                'emotion': None,
                'scene': None,
                'music': music_recommendation
            })
            play_youtube_audio(title,composer)
            return render_template('index.html', music=music_recommendation)

        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                image_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(image_path)
                image = Image.open(image_path).convert('RGB')
                input_tensor = transform(image)

                emotion = predict_emotion(input_tensor)
                scene = predict_scene(input_tensor)

                prompt = f"사람의 감정은 {emotion}이고, 풍경은 {scene}이야. 이 분위기에 어울리는 클래식 음악을 추천해줘.출력은 곡명 작곡가명만 하고 1곡만만 EX) 월광소나타 3악장,베토벤 이런식으로"
                music_recommendation = get_music_recommendation(prompt)
                ser.write(b'PLAY\n')
                title,composer=music_recommendation.split(",")
                play_youtube_audio(title,composer)

                save_to_archive({
                    'type': 'image',
                    'timestamp': timestamp,
                    'filename': file.filename,
                    'emotion': emotion,
                    'scene': scene,
                    'music': music_recommendation
                })

                return render_template('index.html',
                                       emotion=emotion,
                                       scene=scene,
                                       music=music_recommendation)

    return render_template('index.html')
def play_youtube_audio(title,composer):
    print("Start Music", end="")
    # 1. 검색어 조합
    query = f"{title} {composer}"
    # 2. 유튜브에서 첫 번째 결과 찾기
    results = VideosSearch(query, limit=1).result()
    if results['result']:
        url = results['result'][0]['link']
        print(f"재생할 URL: {url}")
        # 3. mpv로 오디오만 재생 (--no-video)
        subprocess.run(['mpv', '--no-video', url])
        print(url)
    else:
        print("검색 결과 없음!")
@app.route('/archive')
def archive():
    if os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE, 'r') as f:
            records = json.load(f)
    else:
        records = []
    return render_template('archive.html', records=records)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
