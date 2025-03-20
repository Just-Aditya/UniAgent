from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from datetime import datetime
import requests
from passlib.context import CryptContext
import smtplib
from email.mime.text import MIMEText
from fastapi.responses import StreamingResponse
import gridfs  # GridFS for file storage in MongoDB
from bson import ObjectId

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client.university_agent
fs = gridfs.GridFS(db)  # Initialize GridFS for file storage

# Collections
users_collection = db.users
mentors_collection = db.mentors
mentees_collection = db.mentees
meetings_collection = db.meetings
documents_collection = db.documents

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize FastAPI
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Function to send emails
def send_email(recipient_email, subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_USER
        msg["To"] = recipient_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, recipient_email, msg.as_string())

        print(f"✅ Email sent to {recipient_email}")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")

# ✅ User Login
class UserLogin(BaseModel):
    user_id: str
    password: str

@app.post("/login")
def login(request: UserLogin):
    user = users_collection.find_one({"user_id": request.user_id})
    if user and pwd_context.verify(request.password, user["password"]):
        return {"status": "success", "message": "Login successful", "role": user["role"]}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# ✅ Query-Based AI Chatbot
class QueryRequest(BaseModel):
    university_name: str
    query: str

@app.post("/query")
def query_agent(request: QueryRequest):
    headers = {"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}", "Content-Type": "application/json"}
    url = "https://api.groq.com/openai/v1/chat/completions"
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": f"You are an AI assistant for KIIT answer everything that is realated to academic in kiit and genuine answer that is available on internet."},
            {"role": "user", "content": request.query}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            return {"response": result.get("choices", [{}])[0].get("message", {}).get("content", "No valid response.")}
        else:
            return {"response": f"Error: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"response": f"Exception occurred: {str(e)}"}
    
@app.post("/upload_document/")
async def upload_document(
    file: UploadFile = File(...),
    mentee_id: str = Form(...),
    mentor_id: str = Form(...),
    comment: str = Form(""),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    file_id = fs.put(file.file, filename=file.filename, content_type=file.content_type)

    document_data = {
        "mentee_id": mentee_id,
        "mentor_id": mentor_id,
        "document_name": file.filename,
        "file_id": str(file_id),
        "comment": comment,
        "timestamp": datetime.utcnow(),
        "mentor_remark": None
    }
    documents_collection.insert_one(document_data)

    backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
    download_url = f"{backend_url}/download/{file_id}"

    mentor = mentors_collection.find_one({"mentor_id": mentor_id})
    if mentor and "email" in mentor:
        subject = "New Document Uploaded"
        body = f"""
        Hello {mentor['name']},

        A new document has been uploaded by your mentee ({mentee_id}).

        🔗 **Download Link:** {download_url}

        📝 **Mentee's Comment:**  
        {comment}

        Best regards,  
        University AI Assistant
        """
        background_tasks.add_task(send_email, mentor["email"], subject, body)

    return JSONResponse(content={"message": "Document uploaded successfully!", "download_link": download_url})


# ✅ Leave Request with Mentor Approval
class LeaveRequest(BaseModel):
    university_name: str
    employee_id: str
    leave_type: str

@app.post("/leave")
def leave_request(request: LeaveRequest):
    mentee = mentees_collection.find_one({"mentee_id": request.employee_id})
    if not mentee:
        raise HTTPException(status_code=404, detail="Mentee not found.")

    mentor = mentors_collection.find_one({"mentor_id": mentee["mentor_id"]})
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found.")

    if mentee["cgpa"] >= mentor["cgpa_threshold"] and mentee["leave_days"] < mentor["leave_limit"]:
        return {"status": "approved", "message": "Leave approved."}
    
    return {"status": "denied", "message": "Leave denied based on criteria."}

# 📌 **5️⃣ Meeting Scheduling & Email Notifications**
class MeetingRequest(BaseModel):
    mentor_id: str
    meeting_date: str
    meeting_time: str
    location: str
    message: str

def send_meeting_emails(emails, meeting_details):
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        for email in emails:
            msg_body = f"""
            📅 Meeting Scheduled
            - Date: {meeting_details['date']}
            - Time: {meeting_details['time']}
            - Location: {meeting_details['location']}
            
             Message From Your Mentor: 
            {meeting_details['message']}
            """

            msg = MIMEText(msg_body, "plain")
            msg["Subject"] = "Mentor-Mentee Meeting"
            msg["From"] = EMAIL_USER
            msg["To"] = email
            server.sendmail(EMAIL_USER, email, msg.as_string())

    print("✅ Meeting emails sent successfully!")


@app.post("/schedule_meeting")
def schedule_meeting(request: MeetingRequest, background_tasks: BackgroundTasks):
    mentees = list(mentees_collection.find({"mentor_id": request.mentor_id}))  # Convert to list
    mentee_emails = [mentee["email"] for mentee in mentees if "email" in mentee]

    print(f"📝 Mentees found: {mentees}")  # Debugging Step 1
    print(f"📧 Sending emails to: {mentee_emails}")  # Debugging Step 2

    if not mentee_emails:
        raise HTTPException(status_code=404, detail="No mentees found with emails.")

    meeting_details = {
        "date": request.meeting_date,
        "time": request.meeting_time,
        "location": request.location,
        "message": request.message
    }

    background_tasks.add_task(send_meeting_emails, mentee_emails, meeting_details)
    return {"status": "success", "message": "Meeting scheduled and invitations sent."}


# 📌 **4️⃣ Certificate Generation & Mentor Verification**
class CertificateRequest(BaseModel):
    university_name: str
    user_id: str
    certificate_type: str

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
import os
import requests
from datetime import datetime
from fastapi import HTTPException

def generate_certificate(user_id: str, certificate_type: str, university_name: str):
    folder_path = "certificates"
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f"{user_id}_{certificate_type}.pdf")

    print(f"🔹 Generating certificate for {user_id} ({certificate_type}) from {university_name}")
    print(f"📄 Saving certificate to: {file_path}")

    # ✅ KIIT logo URL
    kiit_logo_url = "https://upload.wikimedia.org/wikipedia/en/thumb/0/07/KIIT_logo.svg/1200px-KIIT_logo.svg.png"
    logo_path = os.path.join(folder_path, "kiit_logo.png")

    # ✅ Download the logo if not already downloaded
    if not os.path.exists(logo_path):
        try:
            response = requests.get(kiit_logo_url, timeout=10)
            if response.status_code == 200:
                with open(logo_path, "wb") as f:
                    f.write(response.content)
                print("✅ KIIT logo downloaded successfully.")
            else:
                print(f"⚠ Failed to download KIIT logo: {response.status_code}")
        except Exception as e:
            print(f"⚠ Error downloading KIIT logo: {e}")

    try:
        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4

        # ✅ Add decorative border
        c.setStrokeColor(colors.gold)
        c.setLineWidth(4)
        c.rect(20, 20, width - 40, height - 40, stroke=True, fill=False)

        # ✅ Add KIIT University logo
        if os.path.exists(logo_path):
            c.drawImage(logo_path, width / 2 - 50, height - 120, width=100, height=100, preserveAspectRatio=True)
        else:
            print("⚠ KIIT Logo not found! Skipping logo.")

        # ✅ Add certificate title
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(colors.darkgreen)
        c.drawCentredString(width / 2, height - 160, f"CERTIFICATE OF {certificate_type.upper()}")

        # ✅ Add recipient details
        c.setFont("Helvetica", 16)
        c.setFillColor(colors.black)
        c.drawCentredString(width / 2, height - 220, "This is to certify that")
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2, height - 260, f"{user_id}")
        c.setFont("Helvetica", 16)
        c.drawCentredString(width / 2, height - 300, "has successfully completed the requirements for this certification")
        c.drawCentredString(width / 2, height - 340, f"from KIIT")

        # ✅ Add issue date
        date_str = datetime.now().strftime("%d %B, %Y")
        c.drawCentredString(width / 2, height - 380, f"Issued on: {date_str}")

        # ✅ Add signature placeholders
        c.line(100, height - 450, 300, height - 450)
        c.line(350, height - 450, 550, height - 450)

        c.setFont("Helvetica", 12)
        c.drawCentredString(200, height - 470, "Registrar")
        c.drawCentredString(450, height - 470, "Dean of Academics")

        # ✅ Save the certificate
        c.showPage()
        c.save()
        print(f"✅ Certificate saved successfully: {file_path}")

        return f"/download_certificate/{user_id}_{certificate_type}.pdf"

    except Exception as e:
        print(f"❌ Error generating certificate: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate certificate: {str(e)}")

@app.get("/download_certificate/{filename}")
def download_certificate(filename: str):
    file_path = os.path.join("certificates", filename)
    
    # Check if the file exists before serving
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Certificate not found")

    # Serve the file as a response
    return FileResponse(
        file_path, 
        media_type="application/pdf",
        filename=filename
    )

@app.post("/certificate")
def certificate_request(request: CertificateRequest):
    student = mentees_collection.find_one({"mentee_id": request.user_id})

    if not student:
        print("❌ Mentee not found in database.")
        raise HTTPException(status_code=403, detail="Student not found in university records.")

    print(f"✅ Mentee Found: {student}")

    mentor = mentors_collection.find_one({"mentor_id": student["mentor_id"]})

    if not mentor:
        print("❌ Mentor not found in database.")
        raise HTTPException(status_code=403, detail="Mentor not found.")

    print(f"✅ Mentor Found: {mentor}")

    if not mentor.get("approve_certificates", False):
        print("❌ Mentor has not approved certificates.")
        raise HTTPException(status_code=403, detail="Mentor approval required.")

    print(f"✅ Mentor Approval Passed: {mentor['approve_certificates']}")

    file_path = generate_certificate(request.user_id, request.certificate_type, request.university_name)

    return {"status": "success", "message": "Certificate generated.", "file": file_path}


@app.get("/download/{file_id}")
async def download_document(file_id: str):
    try:
        # ✅ Retrieve file from GridFS
        file_obj = fs.get(ObjectId(file_id))
        
        # ✅ Serve file as a streaming response (no need for temp storage)
        return StreamingResponse(
            file_obj, 
            media_type=file_obj.content_type,
            headers={"Content-Disposition": f'attachment; filename="{file_obj.filename}"'}
        )
    except gridfs.errors.NoFile:
        raise HTTPException(status_code=404, detail="File not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
