import json
from pathlib import Path
from fastapi import FastAPI,HTTPException,UploadFile,File
from fastapi.responses import FileResponse
from ..models.schemas import RecoveryCase
from ..services.recovery import RecoveryOrchestrator
from ..services.sarvam import SarvamService
from evaluation import evaluate
app=FastAPI(title='Kraft AI',version='1.0.0'); audit=RecoveryOrchestrator().audit; orchestrator=RecoveryOrchestrator(audit=audit); cases={x['case_id']:RecoveryCase.model_validate(x) for x in json.loads(Path('data/recovery_cases.json').read_text())}
def get_case(case_id):
 if case_id not in cases: raise HTTPException(404,'Case not found')
 return cases[case_id]
@app.get('/')
def home(): return FileResponse('frontend/index.html')
@app.get('/health')
def health(): return {'status':'ok','environment':'Synthetic / Mock Payment Environment'}
@app.get('/v1/cases')
def list_cases(limit:int=30): return list(cases.values())[:min(limit,100)]
@app.get('/v1/cases/{case_id}')
def case(case_id:str): return get_case(case_id)
@app.get('/v1/cases/{case_id}/decision')
def decision(case_id:str): return orchestrator.decide(get_case(case_id))
@app.post('/v1/cases/{case_id}/execute')
def execute(case_id:str):
 c=get_case(case_id); d,r=orchestrator.execute(c); return {'decision':d,'execution':r,'case':c}
@app.post('/v1/recover')
def recover(case:RecoveryCase):
 d,r=orchestrator.execute(case); return {'decision':d,'execution':r,'case':case,'audit':audit.get(case.case_id)}
@app.get('/v1/audit/{case_id}')
def trail(case_id:str): return audit.get(case_id)
@app.get('/v1/evaluation')
def benchmark(): return evaluate()
@app.post('/v1/voice/transcribe')
async def transcribe(audio:UploadFile=File(...)): return {'transcript':SarvamService().transcribe(await audio.read())}
@app.post('/v1/voice/speak')
def speak(payload:dict): return SarvamService().speak(str(payload.get('text','')))
