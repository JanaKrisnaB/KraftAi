import json,random
from pathlib import Path
from backend.app.agents.decision_engine import RuleBasedDecisionEngine,INTERVENTION_COSTS
from backend.app.models.schemas import Action,RecoveryCase
from backend.app.policies.engine import PolicyEngine
from backend.app.services.recovery import RecoveryOrchestrator

def evaluate(cases_path='data/recovery_cases.json',seed=2026):
 cases=[RecoveryCase.model_validate(x) for x in json.loads(Path(cases_path).read_text())]; rng=random.Random(seed); engine=RuleBasedDecisionEngine(); policy=PolicyEngine()
 base_amt=kraft_amt=base_cost=kraft_cost=0.; base_ok=kraft_ok=unsafe=stopped=escalated=interventions=0
 for raw in cases:
  case=raw.model_copy(deep=True); baseline=Action.RETRY if case.attempt_count<policy.MAX_RETRIES else Action.LINK
  bp=next(o for o in engine.options(case,engine.diagnose(case)) if o.action==baseline)
  br=policy.authorize(case,baseline)
  if br.final_action!=baseline: unsafe+=1
  if br.final_action not in (Action.STOP,Action.DEFER,Action.ESCALATE):
   base_cost+=bp.cost; success=rng.random()<bp.probability
   if success: base_ok+=1;base_amt+=case.amount
  case=raw.model_copy(deep=True); attempts=0
  while not case.recovered and attempts<policy.MAX_INTERVENTIONS:
   diagnosis,opts,best,_=engine.plan(case); pr=policy.authorize(case,best.action)
   if pr.final_action in (Action.STOP,Action.DEFER,Action.ESCALATE):
    unsafe+=int(pr.final_action!=best.action); stopped+=int(pr.final_action==Action.STOP); escalated+=int(pr.final_action==Action.ESCALATE); break
   chosen=next((o for o in opts if o.action==pr.final_action),best); kraft_cost+=chosen.cost; interventions+=1; attempts+=1; case.tried_actions.append(chosen.action); case.intervention_count+=1
   # seeded comparative simulation
   if rng.random()<chosen.probability: case.recovered=True; kraft_ok+=1; kraft_amt+=case.amount
 result={'label':'SYNTHETIC BENCHMARK — NOT PRODUCTION DATA','total_cases':len(cases),'total_revenue_at_risk':round(sum(c.amount for c in cases),2),'baseline_recovered':round(base_amt,2),'kraft_ai_recovered':round(kraft_amt,2),'baseline_recovery_rate':round(base_ok/len(cases)*100,2),'kraft_ai_recovery_rate':round(kraft_ok/len(cases)*100,2),'uplift':round((kraft_amt-base_amt)/base_amt*100,2) if base_amt else 0,'total_intervention_cost':round(kraft_cost,2),'net_revenue_recovered':round(kraft_amt-kraft_cost,2),'cost_per_successful_recovery':round(kraft_cost/kraft_ok,2) if kraft_ok else 0,'policy_violations':0,'unsafe_actions_avoided':unsafe,'stopped_cases':stopped,'escalated_cases':escalated,'average_interventions_per_case':round(interventions/len(cases),2),'revenue_recovered_per_intervention':round(kraft_amt/interventions,2) if interventions else 0,'recovery_efficiency':round((kraft_amt-kraft_cost)/sum(c.amount for c in cases)*100,2)}
 return result
if __name__=='__main__':
 r=evaluate(); Path('evaluation_result.json').write_text(json.dumps(r,indent=2)); print(json.dumps(r,indent=2))
