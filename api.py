from fastapi import FastAPI, BackgroundTasks, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from graph_workflow import ResearchWorkflow
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Agile Alpha API")

# Ensure static dir exists
os.makedirs("static", exist_ok=True)
if os.path.exists("static/assets"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory job store (since we are stateless and have no DB!)
jobs = {}

class ResearchRequest(BaseModel):
    company: str
    symbol: str

def run_research_task(task_id: str, company: str, symbol: str):
    def progress_callback(progress: int, message: str):
        if task_id in jobs:
            jobs[task_id]["progress"] = progress
            jobs[task_id]["message"] = message

    try:
        workflow_manager = ResearchWorkflow(company, symbol, progress_callback)
        workflow_app = workflow_manager.build_graph()
        
        initial_state = {
            "company": company,
            "symbol": symbol,
            "news_report": "",
            "financial_report": "",
            "quant_report": "",
            "final_strategy": "",
            "iterations": 0
        }
        
        final_state = workflow_app.invoke(initial_state)
        jobs[task_id] = {"status": "completed", "result": final_state["final_strategy"]}
    except Exception as e:
        jobs[task_id] = {"status": "failed", "error": str(e)}

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    # Save the uploaded file to the data directory
    os.makedirs("data", exist_ok=True)
    file_path = os.path.join("data", file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Re-initialize the RAG vector store so it includes the new document
    from rag_pipeline import rag_instance
    rag_instance._initialize_vector_store()
    
    return {"status": "success", "filename": file.filename}

@app.post("/api/research")
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    jobs[task_id] = {"status": "processing", "progress": 0, "message": "Initializing Agents..."}
    background_tasks.add_task(run_research_task, task_id, request.company, request.symbol)
    return {"task_id": task_id}

@app.get("/api/status/{task_id}")
async def get_status(task_id: str):
    return jobs.get(task_id, {"status": "not_found"})

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()
