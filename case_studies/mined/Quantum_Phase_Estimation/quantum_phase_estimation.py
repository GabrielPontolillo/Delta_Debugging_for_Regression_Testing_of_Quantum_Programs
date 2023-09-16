import csv
import multiprocessing
import warnings
import qiskit.quantum_info as qi
from qiskit.circuit.random import random_circuit
import random
import numpy as np

from qiskit import QuantumCircuit, Aer, execute
from qiskit.extensions import UnitaryGate
import qiskit.quantum_info as qi

from case_studies.case_study_interface import CaseStudyInterface
from case_studies.mined.Quantum_Phase_Estimation.phase_estimation_oracle import PhaseEstimationOracle
from case_studies.mined.Quantum_Phase_Estimation.add_eigenvectors_same_eigenvalue import AddEigenvectorsSameEigenvalueProperty
from dd_regression.helper_functions import files_to_spreadsheet
from dd_regression.diff_algorithm import diff
from dd_regression.result_classes import Passed, Failed, Inconclusive
from dd_regression.assertions.assert_equal import measure_qubits

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

backend = Aer.get_backend('aer_simulator')


class QuantumPhaseEstimation(CaseStudyInterface):
    unitary_matrix = [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, np.cos(5 * np.pi / 8) - np.sin(5 * np.pi / 8) * 1j, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, np.cos(6 * np.pi / 8) - np.sin(6 * np.pi / 8) * 1j, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, np.cos(np.pi / 4) - np.sin(np.pi / 4) * 1j, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, np.cos(3 * np.pi / 8) - np.sin(3 * np.pi / 8) * 1j, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, np.cos(2 * np.pi / 8) - np.sin(2 * np.pi / 8) * 1j, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, np.cos(np.pi / 8) - np.sin(np.pi / 8) * 1j, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, np.cos(np.pi / 8) + np.sin(np.pi / 8) * 1j, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 / np.sqrt(2) - 1j / np.sqrt(2), 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, np.cos(7 * np.pi / 8) + np.sin(7 * np.pi / 8) * 1j]
    ]

    unitary_gate = UnitaryGate(unitary_matrix).control()

    def __init__(self):
        self.properties = [AddEigenvectorsSameEigenvalueProperty]
        # self.properties = [EqualOutputProperty]
        pass

    def get_algorithm_name(self):
        return "Quantum_Phase_Estimation"

    # passing circuit
    @staticmethod
    def qpe():
        estimation_qubits = 4
        unitary_qubits = 4

        qc = QuantumCircuit(estimation_qubits + unitary_qubits, estimation_qubits)
        for i in range(estimation_qubits):
            qc.h(i)

        for i in range(estimation_qubits):
            for j in range(2 ** i):
                qc.compose(QuantumPhaseEstimation.unitary_gate, [i] + [x + estimation_qubits for x in range(unitary_qubits)],
                           inplace=True)

        for i in range(estimation_qubits).__reversed__():
            for j in range(estimation_qubits - i - 1).__reversed__():
                qc.cp(-(np.pi / 2 ** (j + 1)), i, 1 + i + j)
            qc.h(i)

        # print(qc.draw(vertical_compression='high', fold=300))
        return qc

    # failing circuit
    @staticmethod
    def qpe_update():
        estimation_qubits = 4
        unitary_qubits = 4

        qc = QuantumCircuit(estimation_qubits + unitary_qubits, estimation_qubits)
        for i in range(estimation_qubits):
            qc.h(i)

        for i in range(estimation_qubits):
            for j in range(2 ** i):
                qc.compose(QuantumPhaseEstimation.unitary_gate,
                           [i] + [x + estimation_qubits for x in range(unitary_qubits)],
                           inplace=True)

        for i in range(estimation_qubits).__reversed__():
            for j in range(estimation_qubits - i - 1).__reversed__():
                qc.cp(-(np.pi / 2 ** (j + 2)), i, 1 + i + j)
            qc.h(i)

        # print(qc.draw(vertical_compression='high', fold=300))
        return qc

    def expected_deltas_to_isolate(self):
        # if all diffs are relevant
        passing = [circuitIns for circuitIns in self.passing_circuit().data]
        failing = [circuitIns for circuitIns in self.failing_circuit().data]
        return diff(passing, failing)

    def passing_circuit(self):
        return self.qpe()

    def failing_circuit(self):
        return self.qpe_update()

    def regression_test(self, quantum_circuit):
        pass

    def test_function(self, deltas, src_passing, src_failing, inputs_to_generate, selected_properties,
                      number_of_measurements, significance_level):
        print("apply test function")
        self.tests_performed += 1
        if self.test_cache.get(tuple(deltas), None) is not None:
            return self.test_cache.get(tuple(deltas), None)
        self.tests_performed_no_cache += 1

        # print(f"chosen properties {selected_properties}")

        oracle_result = PhaseEstimationOracle.test_oracle(src_passing, src_failing, deltas,
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


if __name__ == "__main__":
    # eigenvector_idx = 3
    # matrix = [
    #     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, np.cos(5*np.pi/8)-np.sin(5*np.pi/8)*1j, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, np.cos(6*np.pi/8)-np.sin(6*np.pi/8)*1j, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, np.cos(np.pi/4)-np.sin(np.pi/4)*1j, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, np.cos(3*np.pi/8)-np.sin(3*np.pi/8)*1j, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, np.cos(2*np.pi/8)-np.sin(2*np.pi/8)*1j, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, np.cos(np.pi/8)-np.sin(np.pi/8)*1j, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, np.cos(np.pi/8)+np.sin(np.pi/8)*1j, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-1, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1/np.sqrt(2)-1j/np.sqrt(2), 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, np.cos(7*np.pi/8)+np.sin(7*np.pi/8)*1j]
    # ]
    #
    # gate = UnitaryGate(matrix)
    #
    # print("values")
    # print(np.around(np.linalg.eig(qi.Operator(gate))[0], 2))
    # # print(np.around(np.linalg.eig(qi.Operator(gate))[1], 2))
    #
    # backend = Aer.get_backend("aer_simulator")
    # estimation_qubits = 4
    # unitary_qubits = 4
    #
    # circ = QuantumCircuit(estimation_qubits + unitary_qubits)
    #
    # print("chosen vector")
    # print(np.around(np.linalg.eig(qi.Operator(gate))[1][eigenvector_idx], 2))
    # state = qi.Statevector(np.linalg.eig(qi.Operator(gate))[1][eigenvector_idx])
    #
    # print("multiplied")
    # print(np.around(np.matmul(matrix, np.linalg.eig(qi.Operator(gate))[1][eigenvector_idx]), 2))
    #
    # np.matmul(matrix, np.linalg.eig(qi.Operator(gate))[1][eigenvector_idx])
    #
    # circ.initialize(state, [i+estimation_qubits for i in range(unitary_qubits)])
    #
    # circ = circ.compose(QuantumPhaseEstimation.qpe(), [i for i in range(estimation_qubits+unitary_qubits)])
    #
    # circ.measure([i for i in range(estimation_qubits)], [i for i in range(estimation_qubits)].__reversed__())
    #
    # exec = execute(circ, backend, shots=1000).result()
    # print(exec.get_counts())

    qp = QuantumPhaseEstimation()
    print(qp.expected_deltas_to_isolate())

    # qp = QuantumPhaseEstimation()
    # print(qp.unitary_gate.control().definition)
    #
    # passing = [circuitIns for circuitIns in qp.passing_circuit().data]
    # failing = [circuitIns for circuitIns in qp.failing_circuit().data]
    #
    # # passing[4].operation.definition = 1
    # # failing[4].operation.definition = 1
    # print(passing[4])
    # print(failing[4])
    #
    # print(passing[4] == failing[4])
    # print(passing[4].operation == failing[4].operation)
    # print(passing[4].operation.name == failing[4].operation.name)
    # print(passing[4].operation.num_qubits == failing[4].operation.num_qubits)
    # print(passing[4].operation.num_clbits == failing[4].operation.num_clbits)
    # print(passing[4].operation.params == failing[4].operation.params)
    # print(passing[4].operation.definition == failing[4].operation.definition)
    #
    # print(passing[3].operation.definition)
    # print(failing[3])
    #
    # print(passing[3] == failing[3])
    # print(passing[3].operation == failing[3].operation)
    # print(passing[3].operation.name == failing[3].operation.name)
    # print(passing[3].operation.num_qubits == failing[3].operation.num_qubits)
    # print(passing[3].operation.num_clbits == failing[3].operation.num_clbits)
    # print(passing[3].operation.params == failing[3].operation.params)
    # print(passing[3].operation.definition == failing[3].operation.definition)

    chaff_lengths = [0]
    inputs_to_generate = [1]
    numbers_of_properties = [1]
    number_of_measurements = 4000
    significance_level = 0.003
    test_amount = 1

    qt_objs = [QuantumPhaseEstimation() for _ in
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
