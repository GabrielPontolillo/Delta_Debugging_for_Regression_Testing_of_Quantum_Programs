import multiprocessing
import warnings

import numpy as np
from qiskit import QuantumCircuit, Aer, execute
import qiskit.quantum_info as qi
from qiskit.extensions import UnitaryGate

from case_studies.case_study_interface import CaseStudyInterface
from case_studies.Quantum_Phase_Estimation.estimate_phase_correctly_property import EstimateExactPhase
from case_studies.Quantum_Phase_Estimation.add_eigenvectors_same_eigenvalue_property import \
    AddEigenvectorsSameEigenvalueProperty
from case_studies.Quantum_Phase_Estimation.add_eigenvectors_different_eigenvalue_property import AddEigenvectorsDifferentEigenvalueProperty
from case_studies.Quantum_Phase_Estimation.eigenvectors_do_not_modify_lower_reg_prop import EigenvectorsDoNotModifyLowerReg
from case_studies.Quantum_Phase_Estimation.quantum_phase_estimation_oracle import PhaseEstimationOracle
from dd_regression.diff_algorithm import diff
from dd_regression.helper_functions import files_to_spreadsheet
from dd_regression.result_classes import Passed, Failed, Inconclusive

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

backend = Aer.get_backend('aer_simulator')


class QuantumPhaseEstimation(CaseStudyInterface):
    # unitary_matrix = [
    #     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, np.cos(2 * 1 * np.pi / 4) + np.sin(2 * 1 * np.pi / 4) * 1j, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, np.cos(2 * 2 * np.pi / 4) + np.sin(2 * 2 * np.pi / 4) * 1j, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, np.cos(2 * 3 * np.pi / 4) + np.sin(2 * 3 * np.pi / 4) * 1j, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, np.cos(2 * 1 * np.pi / 4) + np.sin(2 * 1 * np.pi / 4) * 1j, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, np.cos(2 * 2 * np.pi / 4) + np.sin(2 * 2 * np.pi / 4) * 1j, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, np.cos(2 * 3 * np.pi / 4) + np.sin(2 * 3 * np.pi / 4) * 1j, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, np.cos(2 * 1 * np.pi / 4) + np.sin(2 * 1 * np.pi / 4) * 1j, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, np.cos(2 * 2 * np.pi / 4) + np.sin(2 * 2 * np.pi / 4) * 1j, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, np.cos(2 * 3 * np.pi / 4) + np.sin(2 * 3 * np.pi / 4) * 1j, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    # ]

    estimation_qubits = 2
    unitary_qubits = 3

    unitary_matrix = [
        [1, 0, 0, 0, 0, 0, 0, 0],
        [0, np.cos(2 * 1 * np.pi / 4) + np.sin(2 * 1 * np.pi / 4) * 1j, 0, 0, 0, 0, 0, 0],
        [0, 0, np.cos(2 * 1 * np.pi / 4) + np.sin(2 * 1 * np.pi / 4) * 1j, 0, 0, 0, 0, 0],
        [0, 0, 0, -1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, np.cos(2 * 2 * np.pi / 4) + np.sin(2 * 2 * np.pi / 4) * 1j, 0],
        [0, 0, 0, 0, 0, 0, 0, np.cos(2 * 3 * np.pi / 4) + np.sin(2 * 3 * np.pi / 4) * 1j],
    ]

    unitary_gate = UnitaryGate(unitary_matrix).control()

    def __init__(self):
        # self.properties = [AddEigenvectorsSameEigenvalueProperty]
        self.properties = [EigenvectorsDoNotModifyLowerReg]
        # self.properties = [AddEigenvectorsDifferentEigenvalueProperty]

    def get_algorithm_name(self):
        return "Quantum_Phase_Estimation"

    # passing circuit
    @staticmethod
    def qpe():
        estimation_qubits = QuantumPhaseEstimation.estimation_qubits
        unitary_qubits = QuantumPhaseEstimation.unitary_qubits

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
                qc.cp(-(np.pi / 2 ** (j + 1)), i, 1 + i + j)
            qc.h(i)
        # print(qc.draw(vertical_compression='high', fold=300))
        return qc

    # @staticmethod
    # def qpe_update():
    #     estimation_qubits = QuantumPhaseEstimation.estimation_qubits
    #     unitary_qubits = QuantumPhaseEstimation.unitary_qubits
    #
    #     qc = QuantumCircuit(estimation_qubits + unitary_qubits, estimation_qubits)
    #
    #     qc.id(0)
    #
    #     # print(qc.draw(vertical_compression='high', fold=300))
    #     return qc

    @staticmethod
    def qpe_update():
        estimation_qubits = QuantumPhaseEstimation.estimation_qubits
        unitary_qubits = QuantumPhaseEstimation.unitary_qubits

        qc = QuantumCircuit(estimation_qubits + unitary_qubits, estimation_qubits)

        qc.x(estimation_qubits + unitary_qubits - 1)

        for i in range(estimation_qubits):
            qc.h(i)

        for i in range(estimation_qubits):
            for j in range(2 ** i):
                qc.compose(QuantumPhaseEstimation.unitary_gate,
                           [i] + [x + estimation_qubits for x in range(unitary_qubits)],
                           inplace=True)

        for i in range(estimation_qubits).__reversed__():
            for j in range(estimation_qubits - i - 1).__reversed__():
                qc.cp(-(np.pi / 2 ** (j + 1)), i, 1 + i + j)
            qc.h(i)

        # print(qc.draw(vertical_compression='high', fold=300))
        return qc

    # failing circuit
    # @staticmethod
    # def qpe_update():
    #     estimation_qubits = 2
    #     unitary_qubits = 3
    #
    #     qc = QuantumCircuit(estimation_qubits + unitary_qubits, estimation_qubits)
    #     for i in range(estimation_qubits):
    #         qc.h(i)
    #
    #     for i in range(estimation_qubits):
    #         for j in range(2 ** i):
    #             qc.compose(QuantumPhaseEstimation.unitary_gate,
    #                        [i] + [x + estimation_qubits for x in range(unitary_qubits)],
    #                        inplace=True)
    #
    #     for i in range(estimation_qubits).__reversed__():
    #         for j in range(estimation_qubits - i - 1).__reversed__():
    #             qc.cp(-(np.pi / 2 ** (j + 1)), i, 1 + i + j)
    #             qc.cp((3*np.pi / 2 ** (j + 1)), i, 1 + i + j)
    #         qc.h(i)
    #
    #     # print(qc.draw(vertical_compression='high', fold=300))
    #     return qc

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
    eigenvector_eigenvalue_dict = dict()

    unitary_matrix = [
        [1, 0, 0, 0, 0, 0, 0, 0],
        [0,  np.cos(2 * 1 * np.pi / 4) + np.sin(2 * 1 * np.pi / 4) * 1j, 0, 0, 0, 0, 0, 0],
        [0, 0,  np.cos(2 * 1 * np.pi / 4) + np.sin(2 * 1 * np.pi / 4) * 1j, 0, 0, 0, 0, 0],
        [0, 0, 0, -1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0,  np.cos(2 * 2 * np.pi / 4) + np.sin(2 * 2 * np.pi / 4) * 1j, 0],
        [0, 0, 0, 0, 0, 0, 0,  np.cos(2 * 3 * np.pi / 4) + np.sin(2 * 3 * np.pi / 4) * 1j],
    ]

    # unitary_matrix = [
    #     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, np.cos(2 * 1 * np.pi / 4) + np.sin(2 * 1 * np.pi / 4) * 1j, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, np.cos(2 * 2 * np.pi / 4) + np.sin(2 * 2 * np.pi / 4) * 1j, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, np.cos(2 * 3 * np.pi / 4) + np.sin(2 * 3 * np.pi / 4) * 1j, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, np.cos(2 * 1 * np.pi / 4) + np.sin(2 * 1 * np.pi / 4) * 1j, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, np.cos(2 * 2 * np.pi / 4) + np.sin(2 * 2 * np.pi / 4) * 1j, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, np.cos(2 * 3 * np.pi / 4) + np.sin(2 * 3 * np.pi / 4) * 1j, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, np.cos(2 * 1 * np.pi / 4) + np.sin(2 * 1 * np.pi / 4) * 1j, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, np.cos(2 * 2 * np.pi / 4) + np.sin(2 * 2 * np.pi / 4) * 1j, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, np.cos(2 * 3 * np.pi / 4) + np.sin(2 * 3 * np.pi / 4) * 1j, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    # ]

    # unitary_gate = UnitaryGate(unitary_matrix)
    #
    # circuit = QuantumCircuit(4)
    # circuit.append(unitary_gate, [0, 1, 2, 3])
    #
    # print(unitary_gate.definition)
    #
    # eigenvalues, eigenvectors = np.linalg.eig(qi.Operator(unitary_gate))
    #
    # for i in range(len(eigenvalues)):
    #     eigenvalue = eigenvalues[i]
    #     eigenvector = eigenvectors[:, i]
    #
    #     # Check if the eigenvalue is already in the dictionary
    #     if eigenvalue in eigenvector_eigenvalue_dict:
    #         eigenvector_eigenvalue_dict[eigenvalue].append(eigenvector)
    #     else:
    #         eigenvector_eigenvalue_dict[eigenvalue] = [eigenvector]
    #
    # print(list(eigenvector_eigenvalue_dict.keys()))
    #
    # estimation_qubits = 2
    # unitary_qubits = 3
    # circ = QuantumCircuit(estimation_qubits + unitary_qubits)
    #
    # # eigenvalue = list(eigenvector_eigenvalue_dict)[1]
    # # eigenvector = eigenvector_eigenvalue_dict[eigenvalue][0]
    # id = 0
    #
    # eigenvalue = eigenvalues[id]
    # eigenvector = eigenvectors[:, id]
    #
    # circ = QuantumCircuit(7)
    #
    # circ.initialize(eigenvector, [2, 3, 4])
    # circ = circ.compose(QuantumPhaseEstimation.qpe(), [i for i in range(estimation_qubits+unitary_qubits)])
    #
    # circ.measure([i for i in range(estimation_qubits)], [i for i in range(estimation_qubits)].__reversed__())
    #
    # exec = execute(circ, backend, shots=1000).result()
    #
    # print(exec.get_counts())
    # print(f"eigenvector {eigenvector}")
    # print(f"eigenvalue {eigenvalue}")

    qt = QuantumPhaseEstimation()
    print(qt.passing_circuit())
    print(qt.failing_circuit())
    print(qt.expected_deltas_to_isolate())
    expected = qt.expected_deltas_to_isolate()

    passing = 0
    failing = 0
    inconclusive = 0
    for i in range(1):
        res = PhaseEstimationOracle.test_oracle(qt.passing_circuit(), qt.failing_circuit(), [],
                                                [AddEigenvectorsDifferentEigenvalueProperty, AddEigenvectorsSameEigenvalueProperty, EigenvectorsDoNotModifyLowerReg],
                                                measurements=4000, significance_level=0.003,
                                                inputs_to_generate=1)
        if isinstance(res, Passed):
            passing += 1
        elif isinstance(res, Failed):
            failing += 1
        else:
            inconclusive += 1
        print(res)

    print(f"passing {passing}")
    print(f"failing {failing}")
    print(f"inconclusive {inconclusive}")

    # chaff_lengths = [1]
    # inputs_to_generate = [1]
    # numbers_of_properties = [1]
    # number_of_measurements = 4000
    # significance_level = 0.003
    # test_amount = 5
    #
    # qt_objs = [QuantumPhaseEstimation() for _ in
    #            range(len(chaff_lengths) * len(inputs_to_generate) * len(numbers_of_properties))]
    # print(qt_objs)
    # inputs_for_func = [(i1, i2, i3) for i1 in chaff_lengths for i2 in inputs_to_generate for i3 in
    #                    numbers_of_properties]
    # print(inputs_for_func)
    # results = [(qt_objs[i], inputs_for_func[i][0], inputs_for_func[i][1], inputs_for_func[i][2]) for i in
    #            range(len(qt_objs))]
    # print(results)
    # with multiprocessing.Pool(1) as pool:
    #     results = [pool.apply_async(qt_objs[i].analyse_results, kwds={'chaff_length': inputs_for_func[i][0],
    #                                                                   'inputs_to_generate': inputs_for_func[i][1],
    #                                                                   'number_of_properties': inputs_for_func[i][2],
    #                                                                   'number_of_measurements': number_of_measurements,
    #                                                                   'significance_level': significance_level,
    #                                                                   'test_amount': test_amount}) for
    #                i in range(len(qt_objs))]
    #     for r in results:
    #         r.get()
    #
    # pool.join()
    #
    # files_to_spreadsheet(
    #     qt_objs[0].get_algorithm_name(), chaff_lengths, inputs_to_generate, numbers_of_properties,
    #     number_of_measurements, significance_level, test_amount
    # )
