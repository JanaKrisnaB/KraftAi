from backend.app.models.schemas import *
from backend.app.policies.engine import PolicyEngine
def c(**kw): return RecoveryCase(case_id='x',scenario=Scenario.FAILED_SUBSCRIPTION,customer=Customer(id='c'),amount=4999,failure_reason='insufficient funds',**kw)
def test_opted_out_customer_stops(): assert PolicyEngine().authorize(c(customer=Customer(id='c',opted_out=True)),Action.LINK).final_action==Action.STOP
def test_disputed_case_escalates(): assert PolicyEngine().authorize(c(disputed=True),Action.LINK).final_action==Action.ESCALATE
def test_outside_contact_hours_defers(): assert PolicyEngine().authorize(c(current_hour=22),Action.LINK).final_action==Action.DEFER
def test_retry_limit(): assert PolicyEngine().authorize(c(attempt_count=2),Action.RETRY).final_action==Action.LINK
def test_intervention_limit(): assert PolicyEngine().authorize(c(intervention_count=3),Action.LINK).final_action==Action.ESCALATE
def test_voice_requires_consent(): assert PolicyEngine().authorize(c(),Action.VOICE).final_action==Action.LINK
