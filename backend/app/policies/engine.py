from ..models.schemas import Action, CaseState, RecoveryCase, PolicyResult
class PolicyEngine:
    MAX_RETRIES=2; MAX_INTERVENTIONS=3; CONTACT_START=8; CONTACT_END=20; HIGH_VALUE=50000
    def authorize(self, case: RecoveryCase, action: Action)->PolicyResult:
        checks=[]
        if case.customer.opted_out: return self._no(Action.STOP,CaseState.STOPPED,checks,'Customer opted out: no contact is permitted.')
        checks.append('✓ Customer contact consent')
        if case.disputed: return self._no(Action.ESCALATE,CaseState.ESCALATED,checks,'Disputed cases require human escalation.')
        checks.append('✓ Dispute check')
        if case.intervention_count>=self.MAX_INTERVENTIONS: return self._no(Action.ESCALATE,CaseState.ESCALATED,checks,'Intervention limit reached; escalating to human.')
        checks.append('✓ Intervention limit')
        if not self.CONTACT_START<=case.current_hour<self.CONTACT_END: return self._no(Action.DEFER,CaseState.DEFERRED,checks,'Outside permitted 08:00–20:00 contact window.')
        checks.append('✓ Contact window')
        if action==Action.RETRY and case.attempt_count>=self.MAX_RETRIES: return self._no(Action.LINK,CaseState.AWAITING,checks,'Retry limit reached; retry prohibited and payment link substituted.')
        checks.append('✓ Retry limit')
        if action==Action.VOICE and not case.customer.voice_opt_in: return self._no(Action.LINK,CaseState.AWAITING,checks,'Voice consent not granted; payment link substituted.')
        checks.append('✓ Voice consent' if action==Action.VOICE else '✓ Voice consent not required')
        if case.amount>=self.HIGH_VALUE: checks.append('✓ High-value audit flag attached')
        return PolicyResult(approved=True,final_action=action,policy_checks=checks,reason='All deterministic guardrails passed.',next_state=CaseState.AWAITING)
    def _no(self,a,s,c,r): return PolicyResult(approved=a not in (Action.STOP,),final_action=a,policy_checks=c,reason=r,next_state=s)
