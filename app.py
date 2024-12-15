from flask import Flask, render_template, request, send_file, flash
import PyPDF2
import io

app = Flask(__name__)

# Set max content length to 16MB (adjust as needed)
app.config['MAX_CONTENT_LENGTH'] = 150 * 1024 * 1024  # 16MB
app.secret_key = 'your_secret_key'  # Required for flash messages

# Count Pages Route
@app.route('/count_pages', methods=['POST'])
def count_pages():
    if 'pdf_files' not in request.files or len(request.files.getlist('pdf_files')) == 0:
        flash("No files selected")
        return render_template('index.html')

    pdf_files = request.files.getlist('pdf_files')
    page_count = []

    for file in pdf_files:
        if file.filename == '':
            flash("One or more files are empty.")
            return render_template('index.html')
        
        pdf_reader = PyPDF2.PdfReader(file)
        page_count.append(f"{file.filename}: {len(pdf_reader.pages)} pages")

    flash('\n'.join(page_count))
    return render_template('index.html')

# Rotate Pages Route
@app.route('/rotate_page', methods=['POST'])
def rotate_page():
    if 'pdf_file' not in request.files or request.files['pdf_file'].filename == '':
        flash("No file selected or the file is empty.")
        return render_template('index.html')

    if not request.form.get('angle') or not request.form.get('pages'):
        flash("Missing angle or page data for rotation.")
        return render_template('index.html')

    pdf_file = request.files['pdf_file']
    angle = int(request.form['angle'])
    pages_input = request.form['pages']

    # Parse pages input (e.g., "1, 3-5")
    pages_to_rotate = set()
    for part in pages_input.split(','):
        if '-' in part:
            start, end = part.split('-')
            pages_to_rotate.update(range(int(start)-1, int(end)))
        else:
            pages_to_rotate.add(int(part)-1)

    pdf_reader = PyPDF2.PdfReader(pdf_file)
    pdf_writer = PyPDF2.PdfWriter()

    for i, page in enumerate(pdf_reader.pages):
        if i in pages_to_rotate:
            page.rotate(angle)  # Use rotate() for latest PyPDF2 version
        pdf_writer.add_page(page)

    # Save rotated PDF to a BytesIO stream
    output = io.BytesIO()
    pdf_writer.write(output)
    output.seek(0)

    return send_file(output, as_attachment=True, download_name="rotated_pdf.pdf", mimetype='application/pdf')

# Merge PDFs Route
@app.route('/merge_pdfs', methods=['POST'])
def merge_pdfs():
    if 'pdf_files' not in request.files or len(request.files.getlist('pdf_files')) == 0:
        flash("No files selected to merge")
        return render_template('index.html')

    pdf_files = request.files.getlist('pdf_files')
    pdf_writer = PyPDF2.PdfWriter()

    for file in pdf_files:
        if file.filename == '':
            flash("One or more files are empty.")
            return render_template('index.html')
        
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

    # Save merged PDF to a BytesIO stream
    output = io.BytesIO()
    pdf_writer.write(output)
    output.seek(0)

    return send_file(output, as_attachment=True, download_name="merged_pdf.pdf", mimetype='application/pdf')

# Home Route
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
