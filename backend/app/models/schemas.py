from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field

class Scenario(str, Enum):
    FAILED_SUBSCRIPTION='failed_subscription'; CHECKOUT_ABANDONMENT='checkout_abandonment'; B2B_RECEIVABLE='b2b_receivable'
class Action(str, Enum):
    RETRY='retry_payment'; LINK='payment_link'; VOICE='voice_recovery'; PROMISE='promise_to_pay'; ESCALATE='escalate_human'; DEFER='defer'; STOP='stop'
class CaseState(str, Enum):
    DETECTED='detected'; PLANNED='planned'; AWAITING='awaiting_payment'; RECOVERED='recovered'; STOPPED='stopped'; ESCALATED='escalated'; DEFERRED='deferred'; REPLAN='replan'
class Customer(BaseModel):
    id: str; name: str='Customer'; segment: str='standard'; history: float=0.5; opted_out: bool=False; voice_opt_in: bool=False
class RecoveryCase(BaseModel):
    case_id: str; scenario: Scenario; customer: Customer; amount: float=Field(gt=0); currency: str='INR'; failure_reason: str
    attempt_count: int=0; intervention_count: int=0; days_overdue: int=0; hours_since_abandonment: int=0; current_hour: int=12
    disputed: bool=False; promise_to_pay: bool=False; recovered: bool=False; state: CaseState=CaseState.DETECTED; tried_actions: list[Action]=Field(default_factory=list)
class RiskAssessment(BaseModel): risk_score: float; amount_at_risk: float; risk_reason: str; urgency: str; scenario: Scenario; customer_segment: str; previous_attempts: int
class Diagnosis(BaseModel): root_cause: str; confidence: float; explanation: str
class InterventionOption(BaseModel): action: Action; probability: float; cost: float; expected_gross_recovery: float; expected_net_recovery: float
class PolicyResult(BaseModel): approved: bool; final_action: Action; policy_checks: list[str]; reason: str; next_state: CaseState
class Decision(BaseModel):
    case_id: str; risk_score: float; recovery_probability: float; root_cause: str; recommended_action: Action; final_action: Action
    approved: bool; reason: str; policy_checks: list[str]; next_state: CaseState; expected_net_recovery: float; intervention_cost: float; alternative_economics: list[InterventionOption]
class AuditEvent(BaseModel):
    timestamp: datetime=Field(default_factory=lambda: datetime.now(timezone.utc)); case_id: str; event_type: str; component: str; decision: str=''; reason: str=''; policy_result: str=''; amount_recovered: float=0
class ExecutionResult(BaseModel): success: bool; status: str; reference: str; amount_recovered: float=0; detail: str=''
