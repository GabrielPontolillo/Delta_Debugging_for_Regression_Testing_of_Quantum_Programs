from abc import ABC, abstractmethod, abstractproperty


# this class represents a property based test oracle to be used within DD
# multiple property based tests may be imported within, returning, pass, fail, or inconclusive
class PropertyBasedTestOracleInterface(ABC):
    # specifies a property based test oracle, which imports multiple properties
    # executes them, and returns a result from the composition (with statistical correction)
    @staticmethod
    @abstractmethod
    def test_oracle(passing_circuit, failing_circuit, deltas, property_classes, measurements, inputs_to_generate=25):
        """
        inputs:
            passing_circuit: The passing circuit
            failing_circuit: The failing circuit
            deltas: The deltas to apply to the passing circuit in order to get a merged combination
            inputs_to_generate: The amount of inputs to generate for each property based test
            measurements: The number of 'shots', measurements made of the circuit for each input generated
        outputs:
            Pass, Fail, or Inconclusive
        description:
            - Deltas are applied to the passing circuit to generate the merged circuit to test
            - Individual property based tests are imported, instantiated, running the property_based_test function
            - p-values are composed, executing the holm-bonferroni corrections to correct for multiple test problem
            - Failure causing inputs, and the test they failed with are recorded, and re-executed using the
            verification heuristic
            - holm bonferroni correction is applied again for the heuristic
            - if any state that originally failed is not equal return inconclusive
            - if all states that originally failed are equal return failure
            - if failures are originally detected return pass
        """


