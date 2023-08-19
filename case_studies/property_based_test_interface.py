from abc import ABC, abstractmethod


# this class represents an individual property based test
class PropertyBasedTestInterface(ABC):
    # specifies a single property based test, what if input is the actual inputs?
    @staticmethod
    @abstractmethod
    def property_based_test(circuit, inputs_to_generate=25, measurements=1000):
        """
        inputs:
            circuit: The circuit to test
            inputs_to_generate: The amount of inputs to generate for each property based test
            measurements: The number of 'shots', measurements made of the circuit for each input generated
        outputs:
            List of Quadruples in the form [(index, initialised state vector (input), p-values for all, measurements)]
        """

    # after we receive the ouptut state from the original property based test, we must compare it to the
    # original failing circuit
    @staticmethod
    @abstractmethod
    def verification_heuristic(property_index, experiment_index, original_failing_circuit, output_distribution,
                               input_state_list, extra_info=None, measurements=1000):
        """
        inputs:
            original_failing_circuit: The original circuit that we have identified as failure-causing
            output_distribution: A list of xyz measurement results on qubits
            input_state_list: A list of inputs to run the circuit
            measurements: The number of 'shots', measurements made of the circuit for each input generated
        outputs:
            List of Quadruples in the form [(index, initialised state vector, p-values for all, measurements)]
        description:
            checks that the previously observed output distribution is equal to the output distribution observed
            from the measurement or the originally failing circuit
        """
