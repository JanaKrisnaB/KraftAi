from ..models.schemas import RecoveryCase, RiskAssessment, Scenario
class RevenueRiskDetector:
    """Explicit, deterministic revenue-at-risk detector; it does not authorize actions."""
    def assess(self, case: RecoveryCase) -> RiskAssessment:
        base={Scenario.FAILED_SUBSCRIPTION:.72,Scenario.CHECKOUT_ABANDONMENT:.58,Scenario.B2B_RECEIVABLE:.76}[case.scenario]
        score=min(.98, base + min(case.amount/100000,.12) + .07*case.attempt_count + (.08 if case.days_overdue>30 else 0))
        urgency='critical' if score>=.85 or case.amount>=50000 else 'high' if score>=.7 else 'standard'
        labels={Scenario.FAILED_SUBSCRIPTION:'Subscription payment failed',Scenario.CHECKOUT_ABANDONMENT:'Checkout was abandoned',Scenario.B2B_RECEIVABLE:'Invoice is overdue'}
        return RiskAssessment(risk_score=round(score,2),amount_at_risk=case.amount,risk_reason=labels[case.scenario],urgency=urgency,scenario=case.scenario,customer_segment=case.customer.segment,previous_attempts=case.attempt_count)
