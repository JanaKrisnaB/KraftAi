from ..models.schemas import Action, Diagnosis, InterventionOption, RecoveryCase, Scenario
from .base import DecisionEngine
INTERVENTION_COSTS={Action.RETRY:.50,Action.LINK:.30,Action.VOICE:2.50,Action.PROMISE:.40,Action.ESCALATE:80.,Action.DEFER:.05,Action.STOP:0.}
class RuleBasedDecisionEngine(DecisionEngine):
    """Explainable planner: ranks intervention net recovery, never executes an action."""
    def diagnose(self, case):
        root=case.failure_reason.lower().replace(' ','_')
        copy={'insufficient_funds':'The issuer declined because available balance was insufficient.','expired_card':'The stored payment credential has expired.','payment_page_timeout':'The checkout session timed out.','invoice_overdue':'The invoice is past its due date.'}
        return Diagnosis(root_cause=root,confidence=.91 if root in copy else .76,explanation=copy.get(root,f'Observed revenue-risk signal: {case.failure_reason}.'))
    def options(self,case,diagnosis):
        base={
          Action.RETRY:.52,Action.LINK:.66,Action.VOICE:.74,Action.PROMISE:.59,Action.ESCALATE:.81,Action.DEFER:.12,
        }
        root=diagnosis.root_cause
        if root in ('insufficient_funds','temporary_bank_decline'): base.update({Action.RETRY:.62,Action.LINK:.74,Action.VOICE:.81})
        if root in ('expired_card','payment_authentication_failure'): base.update({Action.RETRY:.30,Action.LINK:.76,Action.VOICE:.68})
        if case.scenario==Scenario.CHECKOUT_ABANDONMENT: base.update({Action.LINK:.70,Action.VOICE:.57,Action.PROMISE:.48})
        if case.scenario==Scenario.B2B_RECEIVABLE: base.update({Action.PROMISE:.75,Action.VOICE:.71,Action.ESCALATE:.78,Action.RETRY:.05})
        adjustment=(case.customer.history-.5)*.18
        result=[]
        for action,p in base.items():
          if action in case.tried_actions: continue
          p=max(.02,min(.95,p+adjustment))
          cost=INTERVENTION_COSTS[action]; gross=case.amount*p
          result.append(InterventionOption(action=action,probability=round(p,3),cost=cost,expected_gross_recovery=round(gross,2),expected_net_recovery=round(gross-cost,2)))
        return sorted(result,key=lambda x:x.expected_net_recovery,reverse=True)
    def plan(self,case):
        diagnosis=self.diagnose(case); options=self.options(case,diagnosis); best=options[0]
        return diagnosis, options, best, f'{best.action.value.replace("_"," ").title()} has the highest expected net recovery (₹{best.expected_net_recovery:,.2f}) across eligible economic options.'
