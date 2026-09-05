from backend.app.agents.decision_engine import RuleBasedDecisionEngine
from backend.app.models.schemas import *
def case(): return RecoveryCase(case_id='x',scenario=Scenario.FAILED_SUBSCRIPTION,customer=Customer(id='c',voice_opt_in=True,history=.7),amount=4999,failure_reason='insufficient funds')
def test_economic_selection():
 e=RuleBasedDecisionEngine(); _,opts,best,_=e.plan(case()); assert best.expected_net_recovery==max(x.expected_net_recovery for x in opts)
def test_policy_overrides_ai():
 from backend.app.policies.engine import PolicyEngine
 x=case(); x.customer.opted_out=True; assert PolicyEngine().authorize(x,RuleBasedDecisionEngine().plan(x)[2].action).final_action==Action.STOP
