import hashlib
from ..models.schemas import Action, ExecutionResult
from .base import PaymentGateway
class MockPaymentGateway(PaymentGateway):
 """Synthetic gateway only—no real payment is initiated."""
 def execute(self,case,action,probability):
  seed=int(hashlib.sha256(f'{case.case_id}:{action}:{case.intervention_count}'.encode()).hexdigest()[:8],16)/0xffffffff
  if action==Action.ESCALATE: return ExecutionResult(success=False,status='escalated',reference='mock-human-queue',detail='Synthetic human recovery queue.')
  if action==Action.DEFER: return ExecutionResult(success=False,status='deferred',reference='mock-defer',detail='Synthetic deferred action.')
  if action==Action.STOP: return ExecutionResult(success=False,status='stopped',reference='mock-stop',detail='No contact made.')
  success=seed<probability
  status='recovered' if success else 'not_recovered'
  ref=f'mock-{action.value}-{case.case_id}'
  return ExecutionResult(success=success,status=status,reference=ref,amount_recovered=case.amount if success else 0,detail='Synthetic / Mock Payment Environment.')
