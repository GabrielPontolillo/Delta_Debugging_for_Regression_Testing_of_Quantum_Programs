from abc import ABC, abstractmethod
from dd_regression.dd_algorithm import dd_repeat, filter_artifacts


class CaseStudyInterface(ABC):
    @abstractmethod
    def expected_deltas_to_isolate(self):
        """
        To analyse the data for the paper, we must specify what deltas are expected to be returned
        assuming no artifacts
        """
        pass

    @abstractmethod
    def passing_circuit(self):
        """
        Return a passing version of the quantum circuit (prior to update)
        """
        pass

    @abstractmethod
    def failing_circuit(self):
        """
        Return a failing version of the quantum circuit (prior to update)
        """
        pass

    @abstractmethod
    def regression_test(self, quantum_circuit):
        """
        Return the (property based) regression test that may be used to test each circuit
        """
        pass

    @abstractmethod
    def test_function(self, deltas, src_passing, src_failing, ):
        """
        Return a test function, similar to regression test that receives a subset of Deltas,
        """
        pass

    @abstractmethod
    def run_dd(self):
        dd_repeat(self.passing_circuit(), self.failing_circuit(), self.test_function())

