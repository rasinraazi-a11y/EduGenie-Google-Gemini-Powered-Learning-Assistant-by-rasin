import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai

load_dotenv()
app=FastAPI(title="EduGenie")
app.mount("/static",StaticFiles(directory="static"),name="static")
MODEL=os.getenv("GEMINI_MODEL","gemini-2.5-flash")
class Request(BaseModel):
    text:str=Field(...,min_length=1,max_length=12000)
    level:str="Beginner"
    count:int=5
def generate(prompt):
    key=os.getenv("GEMINI_API_KEY")
    if not key: raise HTTPException(503,"Gemini API key missing. Add it to .env.")
    try:
        client=genai.Client(api_key=key)
        return client.models.generate_content(model=MODEL,contents=prompt).text or "No response generated."
    except Exception as e: raise HTTPException(502,f"Gemini request failed: {e}")
@app.get("/",response_class=HTMLResponse)
def home():
    return open("static/index.html",encoding="utf-8").read()
@app.post("/api/{mode}")
def tool(mode:str,r:Request):
    prompts={
    "ask":f"Answer as EduGenie for a {r.level} learner. Explain clearly with examples.\nQuestion: {r.text}",
    "explain":f"Explain this for a {r.level} learner with definition, steps, example and recap: {r.text}",
    "quiz":f"Create {max(1,min(r.count,15))} multiple-choice questions (A-D) about {r.text}, level {r.level}. Add answer key and brief explanations.",
    "summarize":f"Summarize these notes for a {r.level} learner. Include main idea, key points, terms and quick revision.\n{r.text}",
    "recommend":f"Create a practical learning roadmap for this goal at {r.level} level. Include prerequisites, 5 ordered steps and practice activities. Do not invent URLs.\n{r.text}"}
    if mode not in prompts: raise HTTPException(404,"Unknown tool")
    return {"result":generate(prompts[mode])}
