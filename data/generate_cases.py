import json,random
from pathlib import Path
from backend.app.models.schemas import Customer,RecoveryCase,Scenario
NAMES=['Rahul','Aarav','Priya','Ananya','Vikram','Meera','Karan','Isha','Neha','Arjun']
REASONS={Scenario.FAILED_SUBSCRIPTION:['insufficient funds','expired card','temporary bank decline','payment authentication failure'],Scenario.CHECKOUT_ABANDONMENT:['payment page timeout','user abandoned checkout','authentication interruption'],Scenario.B2B_RECEIVABLE:['invoice overdue','payment promised','payment reminder required']}
def generate(count=500,seed=42):
 r=random.Random(seed); cases=[]
 for i in range(count):
  scenario=r.choice(list(Scenario)); segment=r.choices(['standard','growth','enterprise'],[.63,.26,.11])[0]; amount=round(r.lognormvariate(8.2 if scenario!=Scenario.B2B_RECEIVABLE else 10, .75),2)
  c=RecoveryCase(case_id=f'KRAFT-{i+1:04}',scenario=scenario,customer=Customer(id=f'C-{i+1:04}',name=r.choice(NAMES),segment=segment,history=round(r.uniform(.2,.95),2),opted_out=r.random()<.035,voice_opt_in=r.random()<.58),amount=amount,failure_reason=r.choice(REASONS[scenario]),attempt_count=r.choices([0,1,2],[.45,.4,.15])[0],intervention_count=r.choices([0,1,2,3],[.6,.25,.1,.05])[0],days_overdue=r.randint(0,90) if scenario==Scenario.B2B_RECEIVABLE else 0,hours_since_abandonment=r.randint(1,48) if scenario==Scenario.CHECKOUT_ABANDONMENT else 0,current_hour=r.randint(0,23),disputed=r.random()<.025,promise_to_pay=r.random()<.12)
  cases.append(c.model_dump(mode='json'))
 return cases
if __name__=='__main__':
    output=Path(__file__).with_name('recovery_cases.json'); output.write_text(json.dumps(generate(),indent=2)); print(f'Generated 500 synthetic cases at {output}')
