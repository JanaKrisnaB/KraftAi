from evaluation import evaluate
def test_evaluation():
 a=evaluate(seed=7); b=evaluate(seed=7); assert a==b and a['total_cases']==500 and a['label'].startswith('SYNTHETIC')
