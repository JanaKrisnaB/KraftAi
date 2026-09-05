import os
from .base import PaymentGateway
class RazorpayGateway(PaymentGateway):
 """Credential-gated adapter. It never impersonates Razorpay when unavailable."""
 def __init__(self): self.key_id=os.getenv('RAZORPAY_KEY_ID'); self.key_secret=os.getenv('RAZORPAY_KEY_SECRET')
 @property
 def configured(self): return bool(self.key_id and self.key_secret)
 def execute(self,case,action,probability):
  if not self.configured: raise RuntimeError('Razorpay Test Mode credentials are not configured; use the mock gateway.')
  raise NotImplementedError('Live Razorpay execution is intentionally not enabled by this demo adapter.')
