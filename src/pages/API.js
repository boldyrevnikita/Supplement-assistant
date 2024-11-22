const fs = require('fs');
const jwt = require('jsonwebtoken');
const axios = require('axios');

// Read the private key from the JSON file
const authData = JSON.parse(fs.readFileSync('C:\\Users\\Никита\\Desktop\\yandex_ocr_test\\authorized_key.json', 'utf8'));
const privateKey = authData.private_key;
const keyId = authData.id;
const serviceAccountId = authData.service_account_id;

const now = Math.floor(Date.now() / 1000);
const payload = {
    aud: 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
    iss: serviceAccountId,
    iat: now,
    exp: now + 3600
};

// Generate the JWT token
const encodedToken = jwt.sign(payload, privateKey, {
    algorithm: 'PS256',
    header: { kid: keyId }
});

// Write the token to a file
fs.writeFileSync('jwt_token.txt', encodedToken);
console.log(encodedToken);

// Prepare data for the token request
const data = { jwt: encodedToken };
const urlToken = 'https://iam.api.cloud.yandex.net/iam/v1/tokens';
const headersToken = { 'Content-Type': 'application/json' };

// Request IAM token
axios.post(urlToken, data, { headers: headersToken })
    .then(response => {
        const iamToken = response.data.iamToken;
        console.log(response.data);

        // Encode the file to base64
        const encodeFile = (filePath) => {
            const fileContent = fs.readFileSync(filePath);
            return Buffer.from(fileContent).toString('base64');
        };

        const content = encodeFile('C:\\Users\\Никита\\Desktop\\yandex_ocr_test\\test_photo3.jpg');
        console.log("content ", content);

        // Prepare data for OCR request
        const ocrData = {
            mimeType: 'text/plain',
            languageCodes: ['*'],
            content: content
        };

        const urlOcr = 'https://ocr.api.cloud.yandex.net/ocr/v1/recognizeText';
        const headersOcr = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${iamToken}`,
            'x-folder-id': 'b1gusd5l6ejd01nltjij',
            'x-data-logging-enabled': 'true'
        };

        // Request OCR processing
        return axios.post(urlOcr, ocrData, { headers: headersOcr });
    })
    .then(response => {
        console.log(response.data);
    })
    .catch(error => {
        console.error(error);
    });