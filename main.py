from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from book_parser import BookParser
from embeddings import VectorStore
from scratch_assessor import ScratchAssessor
import json, uuid

app = FastAPI(title="Story Grammar VectorDB API", version="1.0.0")

vector_store = VectorStore()
assessor = ScratchAssessor(vector_store)
parser = BookParser()


class ChatRequest(BaseModel):
    session_id: str
    book_id: str
    message: str


@app.post("/upload-book")
async def upload_book(file: UploadFile = File(...)):
    content = await file.read()
    book_data = json.loads(content)
    book_id = str(uuid.uuid4())
    story_grammar = parser.extract_story_grammar(book_data)
    vector_store.store_story(book_id, story_grammar)
    return {"book_id": book_id, "story_grammar": story_grammar}


@app.post("/chat")
async def chat_iteration(req: ChatRequest):
    result = assessor.assess(req.session_id, req.book_id, req.message)
    return result


@app.get("/story-summary/{book_id}")
async def story_summary(book_id: str):
    summary = vector_store.get_story_summary(book_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Book not found")
    return summary


@app.get("/assessment/{session_id}")
async def get_assessment(session_id: str):
    return assessor.get_session_score(session_id)
