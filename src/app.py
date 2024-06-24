from flask import Flask, send_file, request
from docx2pdf import convert
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuração para permitir uploads grandes
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

@app.route('/convert', methods=['POST'])
def convert_docx_to_pdf():
    try:
        # Verifica se foi enviado um arquivo DOCX
        if 'file' not in request.files:
            return "Erro: Nenhum arquivo enviado.", 400

        file = request.files['file']

        # Verifica se o arquivo tem um nome e é um arquivo DOCX
        if file.filename == '':
            return "Erro: Nome de arquivo inválido.", 400
        if not file.filename.endswith('.docx'):
            return "Erro: O arquivo deve ser DOCX.", 400

        # Salva o arquivo DOCX em um local temporário
        docx_filename = secure_filename(file.filename)
        docx_path = os.path.join(app.root_path, 'uploads', docx_filename)
        file.save(docx_path)

        # Caminho para o arquivo de saída PDF
        pdf_filename = f"{os.path.splitext(docx_filename)[0]}.pdf"
        pdf_path = os.path.join(app.root_path, 'downloads', pdf_filename)

        # Converte o arquivo DOCX para PDF
        convert(docx_path, pdf_path)

        # Envia o arquivo PDF convertido como resposta
        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        return f"Erro: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
