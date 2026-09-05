from backend.app.gateways.mock import MockPaymentGateway
from backend.app.models.schemas import *
from backend.app.services.recovery import RecoveryOrchestrator
def case(): return RecoveryCase(case_id='deterministic',scenario=Scenario.FAILED_SUBSCRIPTION,customer=Customer(id='c',voice_opt_in=True),amount=4999,failure_reason='insufficient funds')
def test_audit_event_created():
 o=RecoveryOrchestrator(); o.decide(case()); assert any(x.event_type=='RISK_DETECTED' for x in o.audit.get('deterministic'))
def test_mock_gateway(): assert MockPaymentGateway().execute(case(),Action.LINK,.7).detail=='Synthetic / Mock Payment Environment.'
def test_recovery_state_transition():
 o=RecoveryOrchestrator(); c=case(); o.execute(c); assert c.state in (CaseState.RECOVERED,CaseState.REPLAN,CaseState.ESCALATED)
