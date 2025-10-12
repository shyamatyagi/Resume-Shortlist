

from fastapi import FastAPI, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sqlalchemy.orm import Session
import os
import shutil
import pdfplumber
from models import Requirement, Resume, JobRole
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
    saved_files = []
    for file in files:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # Extract candidate name (simple: first line of PDF)
        try:
            with pdfplumber.open(file_location) as pdf:
                first_page = pdf.pages[0]
                text = first_page.extract_text() or ""
                name = text.split('\n')[0] if text else file.filename
        except Exception:
            name = file.filename
        resume = Resume(name=name, file_path=file_location, match=0.0, color="red")
        db.add(resume)
        saved_files.append(file.filename)
    db.commit()
    return {"filenames": saved_files}


@app.post("/requirements/")
def add_requirement(requirement: str = Form(...), db: Session = Depends(get_db)):
    req = Requirement(text=requirement)
    db.add(req)
    db.commit()
    db.refresh(req)
    return {"id": req.id, "requirement": req.text}


@app.get("/shortlist/")
def get_shortlist(db: Session = Depends(get_db)):
    requirements = db.query(Requirement).all()
    resumes = db.query(Resume).all()
    req_keywords = set()
    for req in requirements:
        req_keywords.update([w.strip().lower() for w in req.text.split(",")])
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
        text_words = set([w.strip().lower() for w in text.split()])
        match_count = len(req_keywords & text_words)
        match_percent = int((match_count / len(req_keywords)) * 100) if req_keywords else 0
        
        if match_percent >= 80:
            color = "green"
        elif match_percent >= 50:
            color = "yellow"
        else:
            color = "red"
        res.match = match_percent
        res.color = color
        db.commit()
        results.append({"name": res.name, "match": match_percent, "color": color})
    return {"results": results}
