from flask import Flask, request, send_file, jsonify, make_response
from flask_cors import CORS
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import os
import requests
import boto3
from botocore.exceptions import NoCredentialsError
import subprocess

app = Flask(__name__)
CORS(app)

# Configurações do S3
S3_BUCKET = 'http://185.228.72.82:9000/ibaverde'
S3_KEY = '89AppwYBiRtWSpAkvT0F'
S3_SECRET = '5KBTHFq2A6xiYSicbzTC3JS59YxYg8FuluEzr55b'

s3 = boto3.client('s3', aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)

@app.route('/generate-doc', methods=['POST'])
def generate_doc():
    if 'template' not in request.files:
        return jsonify({"error": "No template file provided"}), 400

    template_file = request.files['template']
    template_path = os.path.join('/tmp', template_file.filename)
    template_file.save(template_path)

    remetente = request.form.get('remetente')
    destinatario = request.form.get('destinatario')
    texto = request.form.get('texto')
    image_url = request.form.get('url')

    image_path = '/tmp/temp_image.png'
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(image_path, 'wb') as f:
            f.write(response.content)
    else:
        return jsonify({"error": "Unable to fetch the image from the URL"}), 400

    tpl = DocxTemplate(template_path)

    context = {
        'remetente': remetente,
        'destinatario': destinatario,
        'texto': texto,
        'images': InlineImage(tpl, image_path, height=Mm(100))
    }

    tpl.render(context)

    output_docx_path = os.path.join('/tmp', 'output.docx')
    tpl.save(output_docx_path)

    output_pdf_path = os.path.join('/tmp', 'output.pdf')
    subprocess.run(['unoconv', '-f', 'pdf', '-o', output_pdf_path, output_docx_path])

    try:
        s3.upload_file(output_pdf_path, S3_BUCKET, 'output.pdf')
    except NoCredentialsError:
        return jsonify({"error": "Credentials not available"}), 400

    # Limpar arquivos temporários
    os.remove(template_path)
    os.remove(image_path)
    os.remove(output_docx_path)
    os.remove(output_pdf_path)

    return jsonify({"message": "Document generated successfully", "s3_url": f"https://{S3_BUCKET}.s3.amazonaws.com/output.pdf"}), 200

if __name__ == '__main__':
    app.run(debug=True)


