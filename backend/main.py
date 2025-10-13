

from fastapi import FastAPI, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sqlalchemy.orm import Session
import os
import shutil
import pdfplumber
from sentence_transformers import SentenceTransformer, util

# once the model is getting loaded 
model = SentenceTransformer('all-MiniLM-L6-v2')
from models import Resume, JobRole
import csv
from database import SessionLocal, init_db


app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

init_db()



@app.post("/admin/upload-jobroles/")
def upload_jobroles(csv_file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = csv_file.file.read().decode("utf-8").splitlines()
    reader = csv.DictReader(content)
    added = []
    for row in reader:
        # Expecting columns: title, qualification, experience, techstack
        job = JobRole(
            title=row.get("title", ""),
            qualification=row.get("qualification", ""),
            experience=row.get("experience", ""),
            techstack=row.get("techstack", "")
        )
        db.add(job)
        added.append(job.title)
    db.commit()
    return {"added": added}

@app.get("/admin/jobroles/")
def list_jobroles(db: Session = Depends(get_db)):
    roles = db.query(JobRole).all()
    return [{"id": r.id, "title": r.title, "qualification": r.qualification, "experience": r.experience, "techstack": r.techstack} for r in roles]


@app.get("/")
def root():
    return {"message": "Resume Shortlisting API"}


@app.post("/upload-resumes/")
def upload_resumes(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    # Delete all previous resumes from the database
    db.query(Resume).delete()
    db.commit()
    saved_files = []
    for file in files:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # Use file name as the resume name
        resume = Resume(name=file.filename, file_path=file_location, match=0.0, color="red", is_new=1)
        db.add(resume)
        saved_files.append(file.filename)
    db.commit()
    return {"filenames": saved_files, "message": "File(s) uploaded successfully."}




@app.get("/shortlist/")
def get_shortlist(db: Session = Depends(get_db)):
    # Use job_roles table for requirements
    job_roles = db.query(JobRole).all()
    resumes = db.query(Resume).filter_by(is_new=1).all()

    # Prepare embeddings for each job role
    job_roles_info = []
    for role in job_roles:
        text = f"{role.title} {role.qualification} {role.experience} {role.techstack}"
        embedding = model.encode(text, convert_to_tensor=True)
        job_roles_info.append({
            "id": role.id,
            "title": role.title,
            "embedding": embedding
        })

    results = []
    seen = set()
    for res in resumes:
        unique_key = (res.file_path, res.name)
        if unique_key in seen:
            continue
        seen.add(unique_key)
        try:
            with pdfplumber.open(res.file_path) as pdf:
                text = " ".join([page.extract_text() or "" for page in pdf.pages])
        except Exception:
            text = ""
        resume_embedding = model.encode(text, convert_to_tensor=True)

        # Find best matching job role
        best_match = None
        best_similarity = -1
        best_title = None
        for role in job_roles_info:
            similarity = float(util.cos_sim(role["embedding"], resume_embedding).item())
            if similarity > best_similarity:
                best_similarity = similarity
                best_title = role["title"]

        match_percent = int(best_similarity * 100)
        if match_percent >= 80:
            color = "green"
        elif match_percent >= 50:
            color = "yellow"
        else:
            color = "red"
        res.match = match_percent
        res.color = color
        res.is_new = 0  # Mark as processed
        db.commit()
        results.append({
            "name": res.name,
            "match": match_percent,
            "color": color,
            "best_title": best_title,
            "best_similarity": match_percent
        })
    return {"results": results}
