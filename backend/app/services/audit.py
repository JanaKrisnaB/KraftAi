from collections import defaultdict
from ..models.schemas import AuditEvent
class AuditTrail:
 def __init__(self): self.events=defaultdict(list)
 def record(self,case_id,event_type,component,decision='',reason='',policy_result='',amount_recovered=0):
  event=AuditEvent(case_id=case_id,event_type=event_type,component=component,decision=decision,reason=reason,policy_result=policy_result,amount_recovered=amount_recovered); self.events[case_id].append(event); return event
 def get(self,case_id): return self.events[case_id]
