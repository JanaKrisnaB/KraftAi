from ..agents.decision_engine import RuleBasedDecisionEngine
from ..gateways.mock import MockPaymentGateway
from ..models.schemas import Action, CaseState, Decision, RecoveryCase
from ..policies.engine import PolicyEngine
from .audit import AuditTrail
from .risk import RevenueRiskDetector
class RecoveryOrchestrator:
 def __init__(self,audit=None,gateway=None): self.audit=audit or AuditTrail(); self.detector=RevenueRiskDetector(); self.engine=RuleBasedDecisionEngine(); self.policy=PolicyEngine(); self.gateway=gateway or MockPaymentGateway()
 def decide(self,case):
  risk=self.detector.assess(case); self.audit.record(case.case_id,'RISK_DETECTED','risk_detector',reason=f'₹{case.amount:,.2f} at risk; {risk.risk_reason}')
  diagnosis,options,best,reason=self.engine.plan(case); self.audit.record(case.case_id,'DIAGNOSIS','decision_engine',decision=diagnosis.root_cause,reason=diagnosis.explanation)
  self.audit.record(case.case_id,'PLANNER','decision_engine',decision=best.action.value,reason=reason)
  policy=self.policy.authorize(case,best.action); self.audit.record(case.case_id,'POLICY','policy_engine',decision=policy.final_action.value,reason=policy.reason,policy_result='approved' if policy.approved else 'blocked')
  selected=next((o for o in options if o.action==policy.final_action),best)
  return Decision(case_id=case.case_id,risk_score=risk.risk_score,recovery_probability=selected.probability,root_cause=diagnosis.root_cause,recommended_action=best.action,final_action=policy.final_action,approved=policy.approved,reason=reason if policy.final_action==best.action else policy.reason,policy_checks=policy.policy_checks,next_state=policy.next_state,expected_net_recovery=selected.expected_net_recovery,intervention_cost=selected.cost,alternative_economics=options)
 def execute(self,case):
  decision=self.decide(case)
  if decision.final_action in (Action.STOP,Action.DEFER,Action.ESCALATE):
   case.state=decision.next_state; self.audit.record(case.case_id,'STATE_TRANSITION','orchestrator',decision=case.state.value,reason=decision.reason); return decision,None
  result=self.gateway.execute(case,decision.final_action,decision.recovery_probability); case.intervention_count+=1; case.tried_actions.append(decision.final_action)
  self.audit.record(case.case_id,'EXECUTION','mock_gateway',decision=decision.final_action.value,reason=result.detail)
  if result.success:
   case.recovered=True; case.state=CaseState.RECOVERED; self.audit.record(case.case_id,'RECOVERY','orchestrator',decision='recovered',amount_recovered=result.amount_recovered)
  elif case.intervention_count>=self.policy.MAX_INTERVENTIONS:
   case.state=CaseState.ESCALATED; self.audit.record(case.case_id,'STATE_TRANSITION','orchestrator',decision='escalated',reason='No more bounded interventions allowed.')
  else:
   case.state=CaseState.REPLAN; self.audit.record(case.case_id,'OBSERVATION','orchestrator',decision='replan',reason='Synthetic outcome not recovered; remaining options will be replanned.')
  return decision,result
