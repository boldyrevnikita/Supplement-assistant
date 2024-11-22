from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import time
import jwt
import json
import requests
import base64

app = Flask(__name__)
cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type' 

# Чтение закрытого ключа из JSON-файла
with open(r'C:\Users\Никита\Desktop\yandex_ocr_test\authorized_key.json', 'r') as f: 
    obj = json.load(f)
    private_key = obj['private_key']
    key_id = obj['id']
    service_account_id = obj['service_account_id']

def generate_jwt():
    now = int(time.time())
    payload = {
        'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        'iss': service_account_id,
        'iat': now,
        'exp': now + 3600
    }

    # Формирование JWT.
    encoded_token = jwt.encode(
        payload,
        private_key,
        algorithm='PS256',
        headers={'kid': key_id}
    )
    
    return encoded_token

def encode_file(file_path):
    with open(file_path, "rb") as fid:
        file_content = fid.read()
    return base64.b64encode(file_content).decode("utf-8")

@app.route('/process_image', methods=['POST'])
@cross_origin()
def process_image():
    # Получаем файл из запроса
    # file = request.files.get('file')
    
    # if not file:
    #    return jsonify({"error": "No file provided"}), 400
    
    # Сохраняем файл временно
    # file_path = f'temp_{file.filename}'
    # file.save(file_path)

    # Генерация JWT токена
    encoded_token = generate_jwt()

    # Получение IAM токена
    data = {"jwt": encoded_token}
    url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url=url, headers=headers, data=json.dumps(data))
    
    if response.status_code != 200:
        return jsonify({"error": "Failed to obtain IAM token"}), response.status_code
    
    iam_token = response.json().get('iamToken')

    # Кодирование файла в base64
    # content = encode_file(file_path)

    content = request.json['base64Image']

    content = content.split(',')[1]

    print("content ", content)

    # Отправка запроса на распознавание текста
    ocr_data = {
        "mimeType": 'text/plain',
        "languageCodes": ["*"],
        "content": content
    }
    
    ocr_url = "https://ocr.api.cloud.yandex.net/ocr/v1/recognizeText"
    
    ocr_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {iam_token}",
        "x-folder-id": "b1gusd5l6ejd01nltjij",
        "x-data-logging-enabled": "true"
    }
    
    ocr_response = requests.post(url=ocr_url, headers=ocr_headers, data=json.dumps(ocr_data))
    
    # Удаляем временный файл
    # import os
    # os.remove(file_path)

    return jsonify(ocr_response.json()), ocr_response.status_code

if __name__ == '__main__':
    app.run(debug=True)