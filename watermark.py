import hashlib
import io
import os
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import pdfplumber
from PyPDF2 import PdfReader, PdfWriter
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
def compute_hash(data):
    """Compute SHA-384 hash of the provided data."""
    hash_obj = hashlib.sha384()
    hash_obj.update(data)
    return hash_obj.hexdigest()

def extract_images_from_pdf(pdf_path):
    """Extract images from a PDF file and return their hashes."""
    image_hashes = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for img in page.images:
                x0, top, x1, bottom = img['x0'], img['top'], img['x1'], img['bottom']
                img_obj = page.within_bbox((x0, top, x1, bottom)).to_image(resolution=300)
                image_bytes = io.BytesIO()
                img_obj.save(image_bytes, format='PNG')
                image_hash = compute_hash(image_bytes.getvalue())
                image_hashes.append(image_hash)
    return image_hashes

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file and return it."""
    text_content = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text_content += page.extract_text() + "\n"
    return text_content.strip()

def extract_metadata_from_pdf(pdf_path):
    """Extract metadata from the PDF file."""
    with pdfplumber.open(pdf_path) as pdf:
        return pdf.metadata

def calculate_hashes(pdf_path):
    """Extract text and images from a PDF and calculate their hashes."""
    text_content = extract_text_from_pdf(pdf_path)
    text_hash = compute_hash(text_content.encode('utf-8'))
    image_hashes = extract_images_from_pdf(pdf_path)
    return text_hash, image_hashes

def generate_combined_hash(text_hash, image_hashes):
    """Generate an overall combined hash from text and image hashes."""
    combined_data = text_hash + ''.join(image_hashes)
    return compute_hash(combined_data.encode('utf-8'))

def add_metadata_to_pdf(input_pdf_path, output_pdf_path, new_metadata):
    """Add metadata to the PDF."""
    with open(input_pdf_path, 'rb') as input_pdf_file:
        pdf_reader = PdfReader(input_pdf_file)
        pdf_writer = PdfWriter()

        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

        original_metadata = pdf_reader.metadata
        updated_metadata = {**original_metadata, **new_metadata}
        pdf_writer.add_metadata(updated_metadata)

        with open(output_pdf_path, 'wb') as output_pdf_file:
            pdf_writer.write(output_pdf_file)

def verify_keywords_in_pdf(pdf_path):
    """Verify the keywords in the PDF metadata."""
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        metadata = pdf_reader.metadata
        keywords = metadata.get('/Keywords', 'No Keywords Found')
        text_hash, image_hashes = calculate_hashes(pdf_path)
        combined_hash = generate_combined_hash(text_hash, image_hashes)

        if keywords == combined_hash:
            return "Data Integrity Verified"
        else:
            return "Data has been manipulated"


@app.get("/")
async def read_root():
    return {"message": "Hi"}


@app.post("/verify/")
async def verify_pdf(file: UploadFile = File(...)):
    # Save the uploaded PDF to a temporary file
    pdf_path = f'temp/{file.filename}'
    os.makedirs('temp', exist_ok=True)

    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    # Verify the PDF
    return verify_keywords_in_pdf(pdf_path)
@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    # Save the uploaded PDF to a temporary file
    pdf_path = f'temp/{file.filename}'
    os.makedirs('temp', exist_ok=True)

    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    # Calculate hashes and create new metadata
    text_hash, image_hashes = calculate_hashes(pdf_path)
    combined_hash = generate_combined_hash(text_hash, image_hashes)
    new_metadata = {
        '/Title': 'Uploaded PDF',
        '/Keywords': combined_hash
    }

    # Define output file path
    output_pdf_path = f'temp/updated_{file.filename}'
    
    # Add metadata to the PDF
    add_metadata_to_pdf(pdf_path, output_pdf_path, new_metadata)

    # Verify the PDF
    return FileResponse(output_pdf_path, media_type='application/pdf', filename=os.path.basename(output_pdf_path))

if __name__ == "__main__":
    os.makedirs('temp', exist_ok=True)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
