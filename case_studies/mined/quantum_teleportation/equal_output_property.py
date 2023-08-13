import warnings

from qiskit import QuantumCircuit, Aer
from qiskit.quantum_info import random_statevector

from case_studies.property_based_test_interface import PropertyBasedTestInterface
from dd_regression.assertions.assert_equal import assert_equal, assert_equal_state
from dd_regression.helper_functions import get_quantum_register, list_to_circuit

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

backend = Aer.get_backend('aer_simulator')


class EqualOutputProperty(PropertyBasedTestInterface):
    @staticmethod
    def property_based_test(circuit, inputs_to_generate=25, measurements=1000):
        # print("inside equal output property based test call")
        experiments = []

        for i in range(inputs_to_generate):
            # initialize to random state and append the applied delta modified circuit
            qlength, clength = get_quantum_register(circuit)
            init_state = QuantumCircuit(qlength)
            init_vector = random_statevector(2)
            init_state.initialize(init_vector, 0)
            inputted_circuit_to_test = init_state + circuit

            # create a new circuit with just state initialization to compare with
            qc = QuantumCircuit(1)
            qc.initialize(init_vector, 0)

            # compare the output of the merged circuit to test, with an empty circuit initialised to expected state
            p_value_x, p_value_y, p_value_z, measurements_1, measurements_2 = \
                assert_equal(inputted_circuit_to_test, 2, qc, 0, measurements=measurements)

            # add a tuple of 3 elements index, initialised vector, p values, measurements
            experiments.append([i, init_vector, (p_value_x, p_value_y, p_value_z), (measurements_1, measurements_2)])

        return experiments

    @staticmethod
    def verification_heuristic(property_idx, exp_idx, original_failing_circuit, output_distribution, input_state_list,
                               measurements=1000):
        qlength, clength = get_quantum_register(original_failing_circuit)
        init_state = QuantumCircuit(qlength)

        init_state.initialize(input_state_list, 0)
        inputted_circuit_to_test = init_state + list_to_circuit(original_failing_circuit)

        p_value_x, p_value_y, p_value_z, _, _ = assert_equal_state(inputted_circuit_to_test, 2, output_distribution,
                                                                   measurements=measurements)

        return [property_idx, exp_idx, (p_value_x, p_value_y, p_value_z)]
