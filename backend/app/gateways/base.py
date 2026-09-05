from abc import ABC,abstractmethod
class PaymentGateway(ABC):
 @abstractmethod
 def execute(self, case, action, probability): ...
