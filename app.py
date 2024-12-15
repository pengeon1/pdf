from flask import Flask, render_template, request, jsonify, send_file
from PyPDF2 import PdfReader, PdfWriter
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/count_pages', methods=['POST'])
def count_pages():
    pdf_files = request.files.getlist('pdf_files')  # Handle multiple files
    results = []
    
    try:
        for pdf_file in pdf_files:
            # Read the PDF
            reader = PdfReader(pdf_file)
            num_pages = len(reader.pages)
            results.append(f"File: {pdf_file.filename} has {num_pages} pages.")
        
        # Return results as a JSON response
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 400

@app.route('/rotate_page', methods=['POST'])
def rotate_page():
    pdf_file = request.files['pdf_file']
    angle = int(request.form['angle'])
    pages = request.form['pages']
    
    try:
        # Parse page numbers input
        page_numbers = parse_page_numbers(pages)

        # Read the input PDF and prepare a writer
        reader = PdfReader(pdf_file)
        writer = PdfWriter()

        # Iterate over the pages and rotate selected ones
        for i, page in enumerate(reader.pages):
            if i in page_numbers:
                page.rotate(angle)  # Rotate the page
            writer.add_page(page)

        # Write the output PDF to a byte stream (in-memory)
        output_pdf_stream = io.BytesIO()
        writer.write(output_pdf_stream)
        output_pdf_stream.seek(0)  # Reset stream position for downloading

        # Return the output PDF as a file download
        return send_file(output_pdf_stream, as_attachment=True, download_name="rotated_output.pdf", mimetype='application/pdf')
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 400

@app.route('/merge_pdfs', methods=['POST'])
def merge_pdfs():
    files = request.files.getlist('pdf_files')
    writer = PdfWriter()
    
    try:
        # Merge all PDF files
        for pdf in files:
            reader = PdfReader(pdf)
            for page in reader.pages:
                writer.add_page(page)

        # Write the output PDF to a byte stream (in-memory)
        output_pdf_stream = io.BytesIO()
        writer.write(output_pdf_stream)
        output_pdf_stream.seek(0)  # Reset stream position for downloading

        # Return the merged PDF as a file download
        return send_file(output_pdf_stream, as_attachment=True, download_name="merged_output.pdf", mimetype='application/pdf')
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 400

def parse_page_numbers(pages):
    page_numbers = set()
    for part in pages.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            page_numbers.update(range(start-1, end))
        else:
            page_numbers.add(int(part)-1)
    return page_numbers

if __name__ == '__main__':
    app.run(debug=True)
