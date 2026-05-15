from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from main import QAChatbot


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)

class AskBatchRequest(BaseModel):
    questions: list[str] = Field(..., min_length=1)


app = FastAPI(title="QA Chatbot API", version="1.0.0")
bot = QAChatbot()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/ask")
def ask_question(payload: AskRequest):
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        last_chunk = None
        for chunk in bot.ask_single_stream(question):
            last_chunk = chunk

        if last_chunk is None:
            raise HTTPException(status_code=500, detail="No response from model.")

        if hasattr(last_chunk, "model_dump"):
            return last_chunk.model_dump()
        return {"answer": str(last_chunk)}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/api/ask-stream")
def ask_question_stream(payload: AskRequest):
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    def token_generator():
        for token in bot.ask_single_stream_text(question):
            yield token

    return StreamingResponse(token_generator(), media_type="text/plain; charset=utf-8")

@app.post("/api/ask-batch")
def ask_question_batch(payload: AskBatchRequest):
    cleaned = [q.strip() for q in payload.questions if q and q.strip()]
    if not cleaned:
        raise HTTPException(status_code=400, detail="Questions cannot be empty.")

    try:
        results = bot.ask_batch(cleaned)
        return [r.model_dump() if hasattr(r, "model_dump") else {"answer": str(r)} for r in results]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
