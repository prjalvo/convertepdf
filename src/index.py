from flask import Flask, request, send_file, jsonify, make_response
from flask_cors import CORS
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import os
import requests
import subprocess

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

@app.route('/generate-doc', methods=['POST'])
def generate_doc():
    # Check if the template file is in the request
    if 'template' not in request.files:
        return jsonify({"error": "No template file provided"}), 400

    template_file = request.files['template']
    template_path = os.path.join(UPLOAD_FOLDER, template_file.filename)
    template_file.save(template_path)

    # Get other parameters
    remetente = request.form.get('remetente')
    destinatario = request.form.get('destinatario')
    texto = request.form.get('texto')
    image_url = request.form.get('url')

    # Download the image from the URL
    image_path = 'temp_image.png'
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(image_path, 'wb') as f:
            f.write(response.content)
    else:
        return jsonify({"error": "Unable to fetch the image from the URL"}), 400

    # Load the template
    tpl = DocxTemplate(template_path)

    # Prepare context
    context = {
        'remetente': remetente,
        'destinatario': destinatario,
        'texto': texto,
        'images': InlineImage(tpl, image_path, height=Mm(100))
    }

    # Render the document
    tpl.render(context)

    # Save the DOCX document
    output_docx_path = os.path.join(OUTPUT_FOLDER, 'output.docx')
    tpl.save(output_docx_path)

    # Convert DOCX to PDF using unoconv
    output_pdf_path = os.path.join(OUTPUT_FOLDER, 'output.pdf')
    subprocess.run(['unoconv', '-f', 'pdf', '-o', output_pdf_path, output_docx_path])

    # Clean up temporary files
    os.remove(template_path)
    os.remove(image_path)

    # Create a response object
    response = make_response()
    response.status_code = 200
    response.headers['Content-Type'] = 'application/json'

    with open(output_docx_path, 'rb') as f:
        docx_data = f.read()
    with open(output_pdf_path, 'rb') as f:
        pdf_data = f.read()

    # Add both files to the response
    #response.data = jsonify({
    #    'docx': docx_data,
    #    'pdf': pdf_data
    #}).data

    # Set file download headers
    #response.headers['Content-Disposition'] = 'attachment; filename=output.docx, output.pdf'

    return send_file(output_pdf_path, as_attachment=True)
    #response.headers['Content-Disposition'] = 'attachment; filename=output.docx, output.pdf'

    # Clean up output files
    os.remove(output_docx_path)
    os.remove(output_pdf_path)

    #return response
    #return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

