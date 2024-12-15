from flask import Flask, request, render_template, send_file
from PyPDF2 import PdfReader, PdfWriter
import os
from io import BytesIO

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/pdfs/'
MERGED_FOLDER = 'merged_pdfs/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MERGED_FOLDER, exist_ok=True)

# Route to serve the index.html
@app.route('/')
def index():
    return render_template('index.html')

# Route to count the number of pages in a PDF
@app.route('/count_pages', methods=['POST'])
def count_pages():
    pdf_file = request.files['pdf_file']
    pdf_reader = PdfReader(pdf_file)
    page_count = len(pdf_reader.pages)
    return f"Page count: {page_count}"

# Route to rotate specific pages in a PDF
@app.route('/rotate_pages', methods=['POST'])
def rotate_pages():
    pdf_file = request.files['pdf_file']
    pages_to_rotate = request.form.get('pages_to_rotate')  # Pages as a comma-separated list
    rotation_degree = int(request.form.get('rotation_degree'))  # Degree of rotation: 90, 180, 270

    pdf_reader = PdfReader(pdf_file)
    pdf_writer = PdfWriter()

    pages_to_rotate = [int(page) - 1 for page in pages_to_rotate.split(',')]  # Convert to 0-based indexing

    for i, page in enumerate(pdf_reader.pages):
        if i in pages_to_rotate:
            page.rotate_clockwise(rotation_degree)
        pdf_writer.add_page(page)

    # Saving rotated PDF to memory (instead of a file)
    output_pdf = BytesIO()
    pdf_writer.write(output_pdf)
    output_pdf.seek(0)

    return send_file(output_pdf, as_attachment=True, download_name="rotated_output.pdf", mimetype='application/pdf')

# Route to merge multiple PDFs
@app.route('/merge_pdfs', methods=['POST'])
def merge_pdfs():
    files = request.files.getlist('pdf_files')  # List of PDF files
    output_filename = request.form.get('output_filename', 'merged_output.pdf')

    pdf_writer = PdfWriter()

    for file in files:
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

    # Saving merged PDF to memory
    output_pdf = BytesIO()
    pdf_writer.write(output_pdf)
    output_pdf.seek(0)

    return send_file(output_pdf, as_attachment=True, download_name=output_filename, mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
