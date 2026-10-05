"""FastAPI entry point for Kraft AI.

Paths are derived from this module, so the server can be started from the project
root, `backend/`, or an IDE/debugger working directory.
"""
import json
import sys
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evaluation import evaluate
from ..models.schemas import RecoveryCase
from ..services.recovery import RecoveryOrchestrator
from ..services.sarvam import SarvamService

app = FastAPI(title="Kraft AI", version="1.0.0")
audit = RecoveryOrchestrator().audit
orchestrator = RecoveryOrchestrator(audit=audit)
CASES_PATH = PROJECT_ROOT / "data" / "recovery_cases.json"
FRONTEND_PATH = PROJECT_ROOT / "frontend" / "index.html"
cases = {
    item["case_id"]: RecoveryCase.model_validate(item)
    for item in json.loads(CASES_PATH.read_text(encoding="utf-8"))
}


def get_case(case_id: str) -> RecoveryCase:
    if case_id not in cases:
        raise HTTPException(404, "Case not found")
    return cases[case_id]


@app.get("/")
def home() -> FileResponse:
    return FileResponse(FRONTEND_PATH)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "environment": "Synthetic / Mock Payment Environment"}


@app.get("/v1/cases")
def list_cases(limit: int = 30) -> list[RecoveryCase]:
    return list(cases.values())[: min(limit, 100)]


@app.get("/v1/cases/{case_id}")
def case(case_id: str) -> RecoveryCase:
    return get_case(case_id)


@app.get("/v1/cases/{case_id}/decision")
def decision(case_id: str):
    return orchestrator.decide(get_case(case_id))


@app.post("/v1/cases/{case_id}/execute")
def execute(case_id: str):
    selected_case = get_case(case_id)
    decision_result, execution = orchestrator.execute(selected_case)
    return {"decision": decision_result, "execution": execution, "case": selected_case}


@app.post("/v1/recover")
def recover(recovery_case: RecoveryCase):
    decision_result, execution = orchestrator.execute(recovery_case)
    return {"decision": decision_result, "execution": execution, "case": recovery_case, "audit": audit.get(recovery_case.case_id)}


@app.get("/v1/audit/{case_id}")
def trail(case_id: str):
    return audit.get(case_id)


@app.get("/v1/evaluation")
def benchmark():
    return evaluate(cases_path=str(CASES_PATH))


@app.post("/v1/voice/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    return {"transcript": SarvamService().transcribe(await audio.read())}


@app.post("/v1/voice/speak")
def speak(payload: dict):
    return SarvamService().speak(str(payload.get("text", "")))
