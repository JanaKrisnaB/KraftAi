from abc import ABC, abstractmethod
from ..models.schemas import RecoveryCase, Diagnosis, InterventionOption
class DecisionEngine(ABC):
 @abstractmethod
 def diagnose(self, case: RecoveryCase)->Diagnosis: ...
 @abstractmethod
 def options(self, case: RecoveryCase, diagnosis: Diagnosis)->list[InterventionOption]: ...
