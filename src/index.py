from flask import Flask, request, send_file, jsonify
import requests
import io

app = Flask(__name__)

@app.route('/get-pdf', methods=['POST'])
def get_pdf():
    api_url = "https://185.228.72.82:9002/generate-doc"

    # Parâmetros da solicitação
    data = {
        'remetente': request.form.get('remetente'),
        'destinatario': request.form.get('destinatario'),
        'texto': request.form.get('texto'),
        'url': request.form.get('url')
    }

    # Arquivo de template
    template_file = request.files.get('template')
    if not template_file:
        return jsonify({"error": "No template file provided"}), 400

    files = {
        'template': template_file
    }

    try:
        # Enviar solicitação POST para a API
        response = requests.post(api_url, files=files, data=data)

        # Verificar se a solicitação foi bem-sucedida
        if response.status_code == 200:
            # Retornar o PDF na resposta
            return send_file(io.BytesIO(response.content), attachment_filename='output.pdf', as_attachment=True)
        else:
            return jsonify({"error": "Failed to generate PDF", "status": response.status_code, "message": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)



