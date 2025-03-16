from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image
import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import qrcode
from io import BytesIO
from PIL import Image as PILImage

# Load API keys
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
AGNO_API_KEY = os.getenv("AGNO_API_KEY")

# Initialize FastAPI
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all domains for testing
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Define Request Models
class QueryRequest(BaseModel):
    university_name: str
    query: str

class LeaveRequest(BaseModel):
    university_name: str
    employee_id: str
    leave_type: str

class CertificateRequest(BaseModel):
    university_name: str
    user_id: str
    certificate_type: str

# Define Tools
def check_leave_balance(employee_id, leave_type, university_name):
    return True  # Assume balance exists

def generate_certificate(user_id, certificate_type, university_name):
    # Create folder if it doesn't exist
    folder_path = "certificates"
    os.makedirs(folder_path, exist_ok=True)
    
    # Define the filename and path
    file_path = os.path.join(folder_path, f"{user_id}_{certificate_type}.pdf")
    
    # Register fonts (assuming these are in a 'fonts' directory)
    fonts_dir = "fonts"
    os.makedirs(fonts_dir, exist_ok=True)
    
    # You would need to download these fonts and place them in the fonts directory
    # For now, we'll use standard fonts that come with ReportLab
    try:
        pdfmetrics.registerFont(TTFont('Garamond', os.path.join(fonts_dir, 'Garamond.ttf')))
        pdfmetrics.registerFont(TTFont('GaramondBold', os.path.join(fonts_dir, 'GaramondBold.ttf')))
    except:
        # If custom fonts aren't available, we'll use standard fonts
        pass
    
    # Create a QR code for verification
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f"Certificate ID: {user_id}-{certificate_type}")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR to a temporary file
    qr_path = os.path.join(folder_path, f"qr_{user_id}_{certificate_type}.png")
    qr_img.save(qr_path)
    
    # Create PDF
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    
    # Add border
    c.setStrokeColor(colors.gold)
    c.setLineWidth(3)
    c.rect(0.5*inch, 0.5*inch, width - inch, height - inch, stroke=True, fill=False)
    
    # Add fancy border corners
    c.setLineWidth(2)
    corner_size = 0.5*inch
    # Top-left
    c.line(0.5*inch, 0.5*inch + corner_size, 0.5*inch, 0.5*inch)
    c.line(0.5*inch, 0.5*inch, 0.5*inch + corner_size, 0.5*inch)
    # Top-right
    c.line(width - 0.5*inch - corner_size, 0.5*inch, width - 0.5*inch, 0.5*inch)
    c.line(width - 0.5*inch, 0.5*inch, width - 0.5*inch, 0.5*inch + corner_size)
    # Bottom-left
    c.line(0.5*inch, height - 0.5*inch - corner_size, 0.5*inch, height - 0.5*inch)
    c.line(0.5*inch, height - 0.5*inch, 0.5*inch + corner_size, height - 0.5*inch)
    # Bottom-right
    c.line(width - 0.5*inch - corner_size, height - 0.5*inch, width - 0.5*inch, height - 0.5*inch)
    c.line(width - 0.5*inch, height - 0.5*inch, width - 0.5*inch, height - 0.5*inch - corner_size)
    
    # Add university logo placeholder
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.lightblue)
    c.rect(width/2 - 1*inch, height - 2.5*inch, 2*inch, 1.5*inch, fill=True)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width/2, height - 1.75*inch, f"{university_name} Logo")
    
    # Add university name
    try:
        c.setFont("GaramondBold", 24)
    except:
        c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width/2, height - 3.2*inch, university_name.upper())
    
    # Add certificate title
    certificate_titles = {
        "graduation": "CERTIFICATE OF GRADUATION",
        "completion": "CERTIFICATE OF COURSE COMPLETION",
        "merit": "CERTIFICATE OF MERIT",
        "achievement": "CERTIFICATE OF ACHIEVEMENT",
        "participation": "CERTIFICATE OF PARTICIPATION"
    }
    
    title = certificate_titles.get(certificate_type.lower(), f"CERTIFICATE OF {certificate_type.upper()}")
    
    try:
        c.setFont("GaramondBold", 22)
    except:
        c.setFont("Helvetica-Bold", 22)
    c.setFillColor(colors.darkred)
    c.drawCentredString(width/2, height - 4*inch, title)
    
    # Add certificate text
    try:
        c.setFont("Garamond", 16)
    except:
        c.setFont("Helvetica", 16)
    c.setFillColor(colors.black)
    
    # Certificate body text
    if certificate_type.lower() == "graduation":
        c.drawCentredString(width/2, height - 5*inch, f"This is to certify that")
        try:
            c.setFont("GaramondBold", 20)
        except:
            c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width/2, height - 5.5*inch, f"Student ID: {user_id}")
        try:
            c.setFont("Garamond", 16)
        except:
            c.setFont("Helvetica", 16)
        c.drawCentredString(width/2, height - 6*inch, "has successfully completed all the requirements for the degree of")
        c.drawCentredString(width/2, height - 6.5*inch, "BACHELOR OF SCIENCE")
        c.drawCentredString(width/2, height - 7*inch, f"from {university_name}")
    else:
        c.drawCentredString(width/2, height - 5*inch, f"This is to certify that")
        try:
            c.setFont("GaramondBold", 20)
        except:
            c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width/2, height - 5.5*inch, f"Student ID: {user_id}")
        try:
            c.setFont("Garamond", 16)
        except:
            c.setFont("Helvetica", 16)
        c.drawCentredString(width/2, height - 6*inch, f"has successfully completed the requirements for this certificate")
        c.drawCentredString(width/2, height - 6.5*inch, f"at {university_name}")
    
    # Add date
    date_str = datetime.now().strftime("%d %B, %Y")
    c.drawCentredString(width/2, height - 7.5*inch, f"Awarded on this {date_str}")
    
    # Add signature placeholders
    c.setStrokeColor(colors.black)
    c.line(width/4, height - 8.5*inch, width/2 - 0.5*inch, height - 8.5*inch)
    c.line(width/2 + 0.5*inch, height - 8.5*inch, width*3/4, height - 8.5*inch)
    
    try:
        c.setFont("Garamond", 12)
    except:
        c.setFont("Helvetica", 12)
    c.drawCentredString(width/4 + 0.5*inch, height - 8.8*inch, "University Registrar")
    c.drawCentredString(width*3/4 - 0.5*inch, height - 8.8*inch, "University President")
    
    # Add certificate ID and QR code
    try:
        c.setFont("Garamond", 10)
    except:
        c.setFont("Helvetica", 10)
    
    # Add QR code - now using the temp file
    c.drawImage(qr_path, width - 1.5*inch, inch, width=inch, height=inch)
    
    c.drawString(inch, inch, f"Certificate ID: {user_id}-{certificate_type}")
    c.drawString(inch, inch - 0.2*inch, f"Verify at: {university_name.lower().replace(' ', '')}.edu/verify")
    
    # Add watermark
    c.saveState()
    c.setFillColor(colors.lightgrey)
    c.setFont("Helvetica", 60)
    c.rotate(45)
    c.drawCentredString(height/2, 0, f"{university_name}")
    c.restoreState()
    
    # Save the PDF
    c.save()
    
    # Clean up the temporary QR code file
    try:
        os.remove(qr_path)
    except:
        pass
    
    return f"/download_certificate/{user_id}_{certificate_type}.pdf"

def handle_query(query, university_name):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": f"You are an AI assistant for {university_name}.\n\n"
                                              "Here are some important details about {university_name}:\n"
                                              "- If asked about history, provide general university facts (like founding year, key achievements, etc.).\n"
                                              "- If asked about policies, answer strictly based on known university policies.\n"
                                              "- Backlog exams are held every semester in December and May.\n"
                                              "- Students are allowed a maximum of 10 casual leaves per semester.\n"
                                              "- Certificates can only be issued for academic achievements and must be requested via the student portal.\n"
                                              "- If the answer is unknown, say 'I am not sure but you can check the official university website.'"},
            {"role": "user", "content": query}
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "No valid response.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Exception occurred: {str(e)}"

@app.get("/download_certificate/{filename}")
def download_certificate(filename: str):
    file_path = os.path.join("certificates", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/pdf', filename=filename)
    raise HTTPException(status_code=404, detail="Certificate not found")

# FastAPI Routes
@app.post("/query")
def query_agent(request: QueryRequest):
    response = handle_query(request.query, request.university_name)
    return {"response": response}

@app.post("/leave")
def leave_request(request: LeaveRequest):
    if check_leave_balance(request.employee_id, request.leave_type, request.university_name):
        return {"status": "approved", "message": f"Your leave is approved at {request.university_name}."}
    else:
        return {"status": "denied", "message": f"Insufficient leave balance at {request.university_name}."}

@app.post("/certificate")
def certificate_request(request: CertificateRequest):
    file_path = generate_certificate(request.user_id, request.certificate_type, request.university_name)
    return {"status": "success", "message": f"Certificate generated for {request.university_name}.", "file": file_path}

# Run FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)