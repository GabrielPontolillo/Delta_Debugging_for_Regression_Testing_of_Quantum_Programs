import multiprocessing
import warnings

import numpy as np
from qiskit import QuantumCircuit, Aer

from case_studies.case_study_interface import CaseStudyInterface
from dd_regression.diff_algorithm import diff
from dd_regression.helper_functions import files_to_spreadsheet
from dd_regression.result_classes import Passed, Failed, Inconclusive
from case_studies.Quantum_Fourier_Transform.phase_difference_property import PhaseDifferenceProperty
from case_studies.Quantum_Fourier_Transform.quantum_fourier_transform_oracle import QuantumFourierTransformOracle

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

backend = Aer.get_backend('aer_simulator')


class QuantumFourierTransform(CaseStudyInterface):
    def __init__(self):
        # self.properties = [AddEigenvectorsSameEigenvalueProperty]
        self.properties = [PhaseDifferenceProperty]

    def get_algorithm_name(self):
        return "Quantum_Fourier_Transform"

    # failing circuit without parameter input for length
    # fixed length of 3
    @staticmethod
    def qft():
        estimation_qubits = 3
        qft_circuit = QuantumCircuit(estimation_qubits)
        for i in range(estimation_qubits):
            qft_circuit.h(i)
            for j in range(estimation_qubits - i - 1):
                qft_circuit.cp((np.pi / 2 ** (j + 1)), i, 1 + i + j)
        return qft_circuit

    @staticmethod
    def qft_update():
        estimation_qubits = 3
        qft_circuit = QuantumCircuit(estimation_qubits)
        for i in range(estimation_qubits):
            for j in range(estimation_qubits - i - 1):
                qft_circuit.cp((np.pi / 2 ** (j + 1)), i, 1 + i + j)
            qft_circuit.h(i)
        return qft_circuit

    def expected_deltas_to_isolate(self):
        return diff(self.passing_circuit(), self.failing_circuit())

    def passing_circuit(self):
        return self.qft()

    def failing_circuit(self):
        return self.qft_update()

    def regression_test(self, circuit_to_test):
        pass

    def test_function(self, deltas, src_passing, src_failing, inputs_to_generate, selected_properties,
                      number_of_measurements, significance_level):
        self.tests_performed += 1
        if self.test_cache.get(tuple(deltas), None) is not None:
            return self.test_cache.get(tuple(deltas), None)
        self.tests_performed_no_cache += 1

        # print(f"chosen properties {selected_properties}")

        oracle_result = QuantumFourierTransformOracle.test_oracle(src_passing, src_failing, deltas,
                                                                  selected_properties,
                                                                  inputs_to_generate=inputs_to_generate,
                                                                  measurements=number_of_measurements,
                                                                  significance_level=significance_level
                                                                  )
        if isinstance(oracle_result, Passed):
            self.test_cache[tuple(deltas)] = Passed()
        elif isinstance(oracle_result, Failed):
            self.test_cache[tuple(deltas)] = Failed()
        elif isinstance(oracle_result, Inconclusive):
            self.test_cache[tuple(deltas)] = Inconclusive()
        return oracle_result

    # generate circuit, and return if pass or fail
    # def test_function(self, deltas, passing_circ, failing_circ, inputs_to_generate=25, measurements=1000):
    #     self.tests_performed += 1
    #     # print(f"self.test_cache {self.test_cache}")
    #     if self.test_cache.get(tuple(deltas), None) is not None:
    #         # print(f"deltas already tested, returning cache of {deltas}")
    #         # print(f"cache {self.test_cache.get(tuple(deltas), None)}")
    #         return self.test_cache.get(tuple(deltas), None)
    #     # if len(deltas) == 0:
    #     #     return Passed()
    #     experiments = []
    #     verification_experiments = []
    #     init_qubit_regs = [0, 1]
    #     self.tests_performed_no_cache += 1
    #
    #     changed_circuit_list = apply_diffs(passing_circ, failing_circ, deltas, diagnostic=True)
    #
    #     add = len([x for x in deltas if isinstance(x, Addition)])
    #     rem = len([x for x in deltas if isinstance(x, Removal)])
    #     if len(passing_circ) + add - rem != len(changed_circuit_list):
    #         raise AssertionError(f"apply_diffs has gone wrong pass len {len(passing_circ)}, add {add}, rem {rem}")
    #
    #     qlength, clength = get_quantum_register(changed_circuit_list)
    #     changed_circuit = list_to_circuit(changed_circuit_list)
    #     # generate random input state vector and apply statistical test to expected output
    #     # here we need to check that qft on an arbitrary statevector, vs upshifted statevector has a phase shift of
    #     # [1, -i, -, i]
    #     for j in range(inputs_to_generate):
    #         # initialize to random state and append the applied delta modified circuit
    #         init_state = QuantumCircuit(qlength)
    #         shifted_init_state = QuantumCircuit(qlength)
    #         init_vector = random_statevector(4)
    #         # init_vector = Statevector([0, 0, 0, 0])
    #         vector_dict = init_vector.to_dict()
    #         shifted_vector = Statevector([vector_dict.get('01', 0), vector_dict.get('10', 0),
    #                                       vector_dict.get('11', 0), vector_dict.get('00', 0)])
    #
    #         init_state.initialize(init_vector, init_qubit_regs)
    #         inputted_circuit_to_test = init_state.compose(changed_circuit)
    #
    #         shifted_init_state.initialize(shifted_vector, init_qubit_regs)
    #         shifted_circuit_to_test = shifted_init_state.compose(changed_circuit)
    #
    #         base_measurements = measure_qubits(inputted_circuit_to_test, init_qubit_regs)
    #         shifted_measurements = measure_qubits(shifted_circuit_to_test, init_qubit_regs)
    #
    #         # base measurements * [1, -i, -, i] = shifted measurements
    #         modified_measurements = [
    #             {'z0': base_measurements[0].get('z0'), 'z1': base_measurements[0].get('z1'),
    #              'x1': base_measurements[0].get('x0'), 'x0': base_measurements[0].get('x1'),
    #              'y1': base_measurements[0].get('y0'), 'y0': base_measurements[0].get('y1')},
    #
    #             {'z0': base_measurements[1].get('z0'), 'z1': base_measurements[1].get('z1'),
    #              'x0': base_measurements[1].get('y0'), 'x1': base_measurements[1].get('y1'),
    #              'y0': base_measurements[1].get('x1'), 'y1': base_measurements[1].get('x0')}
    #         ]
    #         p_list = assert_equal_distributions(modified_measurements, shifted_measurements)
    #
    #         # store p_value and input state to get the p_value
    #         experiments.append((init_vector, p_list[0], p_list[1], p_list[2], p_list[3], p_list[4], p_list[5],
    #                             base_measurements, shifted_measurements))
    #
    #     exp_pairs = []
    #     for idx, experiment in enumerate(experiments):
    #         exp_pairs.append((idx, experiment[1]))
    #         exp_pairs.append((idx, experiment[2]))
    #         exp_pairs.append((idx, experiment[3]))
    #         exp_pairs.append((idx, experiment[4]))
    #         exp_pairs.append((idx, experiment[5]))
    #         exp_pairs.append((idx, experiment[6]))
    #
    #     # print(exp_pairs)
    #
    #     # check if any assert equal failed
    #     failed = holm_bonferroni_correction(exp_pairs, 0.01)
    #     #
    #     # for each failed test, check equality of final state, with initial failing circuit (on same input)
    #     for failure in failed:
    #         init_state = QuantumCircuit(qlength)
    #         init_state.initialize(experiments[failure][0], init_qubit_regs)
    #         inputted_circuit_to_test = init_state.compose(list_to_circuit(failing_circ))
    #         new_measurements = measure_qubits(inputted_circuit_to_test, init_qubit_regs)
    #         p_list = assert_equal_distributions(new_measurements, experiments[failure][7])
    #         verification_experiments.append(
    #             (init_vector, p_list[0], p_list[1], p_list[2], p_list[3], p_list[4], p_list[5],
    #              experiments[failure][7], new_measurements))
    #
    #     verification_pairs = []
    #     for idx, verification in enumerate(verification_experiments):
    #         verification_pairs.append((idx, verification[1]))
    #         verification_pairs.append((idx, verification[2]))
    #         verification_pairs.append((idx, verification[3]))
    #         verification_pairs.append((idx, verification[4]))
    #         verification_pairs.append((idx, verification[5]))
    #         verification_pairs.append((idx, verification[6]))
    #
    #     # check if any assert equal failed with initial failing circuit
    #     verification_failed = holm_bonferroni_correction(verification_pairs, 0.01)
    #
    #     # print(f"failed {failed}")
    #     # print(f"verification_failed {verification_failed}")
    #
    #     # if any state not equal, inconclusive result
    #     if len(verification_failed) > 0:
    #         print("return inconclusive")
    #         self.test_cache[tuple(deltas)] = Inconclusive()
    #         return Inconclusive()
    #     elif len(failed) > 0:
    #         print("return failed")
    #         self.test_cache[tuple(deltas)] = Failed()
    #         return Failed()
    #     else:
    #         print("return passed")
    #         self.test_cache[tuple(deltas)] = Passed()
    #         return Passed()


if __name__ == "__main__":
    chaff_lengths = [1]
    inputs_to_generate = [1]
    numbers_of_properties = [1]
    number_of_measurements = 4000
    significance_level = 0.003
    test_amount = 1

    qt_objs = [QuantumFourierTransform() for _ in
               range(len(chaff_lengths) * len(inputs_to_generate) * len(numbers_of_properties))]
    print(qt_objs)
    inputs_for_func = [(i1, i2, i3) for i1 in chaff_lengths for i2 in inputs_to_generate for i3 in
                       numbers_of_properties]
    print(inputs_for_func)
    results = [(qt_objs[i], inputs_for_func[i][0], inputs_for_func[i][1], inputs_for_func[i][2]) for i in
               range(len(qt_objs))]
    print(results)
    with multiprocessing.Pool() as pool:
        results = [pool.apply_async(qt_objs[i].analyse_results, kwds={'chaff_length': inputs_for_func[i][0],
                                                                      'inputs_to_generate': inputs_for_func[i][1],
                                                                      'number_of_properties': inputs_for_func[i][2],
                                                                      'number_of_measurements': number_of_measurements,
                                                                      'significance_level': significance_level,
                                                                      'test_amount': test_amount}) for
                   i in range(len(qt_objs))]
        for r in results:
            r.get()

    pool.join()

    files_to_spreadsheet(
        qt_objs[0].get_algorithm_name(), chaff_lengths, inputs_to_generate, numbers_of_properties,
        number_of_measurements, significance_level, test_amount
    )
