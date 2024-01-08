import multiprocessing
import warnings

import numpy as np
from qiskit import QuantumCircuit, Aer, execute
import qiskit.quantum_info as qi
from qiskit.extensions import UnitaryGate

from case_studies.case_study_interface import CaseStudyInterface
from case_studies.Quantum_Phase_Estimation.add_eigenvectors_same_eigenvalue_property import \
    AddEigenvectorsSameEigenvalueProperty
from case_studies.Quantum_Phase_Estimation.add_eigenvectors_different_eigenvalue_property import \
    AddEigenvectorsDifferentEigenvalueProperty
from case_studies.Quantum_Phase_Estimation.eigenvectors_do_not_modify_lower_reg_prop import \
    EigenvectorsDoNotModifyLowerReg
from case_studies.Quantum_Phase_Estimation.quantum_phase_estimation_oracle import PhaseEstimationOracle
from dd_regression.diff_algorithm import diff
from dd_regression.helper_functions import files_to_spreadsheet
from dd_regression.result_classes import Passed, Failed, Inconclusive

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

backend = Aer.get_backend('aer_simulator')


class QuantumPhaseEstimation(CaseStudyInterface):
    fault = "A"
    apply_verification = True

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

    def __init__(self, fault, apply_verification):
        self.fault = fault
        self.apply_verification = apply_verification
        self.properties = [AddEigenvectorsSameEigenvalueProperty, AddEigenvectorsDifferentEigenvalueProperty,
                           EigenvectorsDoNotModifyLowerReg]

    def get_algorithm_name(self):
        return "Quantum_Phase_Estimation"

    # passing circuit
    def qpe(self):
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

    def qpe_update(self):  # add x at start
        estimation_qubits = QuantumPhaseEstimation.estimation_qubits
        unitary_qubits = QuantumPhaseEstimation.unitary_qubits

        qc = QuantumCircuit(estimation_qubits + unitary_qubits, estimation_qubits)

        if self.fault == "A":  # this fault adds an x at the start

            qc.x(estimation_qubits + unitary_qubits - 1)  # we add x here

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

        elif self.fault == "B":  # remove 1 H gate in initial superposition

            for i in range(estimation_qubits):
                if i == 1:  # ends up only applying the h at 1, and not register 0
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

        elif self.fault == "C":  # add one h gate to the qubit after the estimation register (lower register with unitary qubits)

            for i in range(estimation_qubits + 1):  # this causes 1 more H to be added
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

    def test_function(self, deltas, src_passing, src_failing, inputs_to_generate, selected_properties,
                      number_of_measurements, significance_level):
        self.tests_performed += 1
        if self.test_cache.get(tuple(deltas), None) is not None:
            return self.test_cache.get(tuple(deltas), None)
        self.tests_performed_no_cache += 1

        # print(f"chosen properties {selected_properties}")

        oracle_result = PhaseEstimationOracle.test_oracle(src_passing, src_failing, deltas,
                                                          selected_properties,
                                                          inputs_to_generate=inputs_to_generate,
                                                          measurements=number_of_measurements,
                                                          significance_level=significance_level,
                                                          verification=self.apply_verification
                                                          )
        if isinstance(oracle_result, Passed):
            self.test_cache[tuple(deltas)] = Passed()
        elif isinstance(oracle_result, Failed):
            self.test_cache[tuple(deltas)] = Failed()
        elif isinstance(oracle_result, Inconclusive):
            self.test_cache[tuple(deltas)] = Inconclusive()
        return oracle_result


if __name__ == "__main__":
    # set fault = "B" or "C" to run experimnets on the other faults
    _fault = "A"
    # set apply_verification = False to run the property based test oracle without the verification step
    _apply_verification = True

    chaff_lengths = [8, 4, 2, 1]
    inputs_to_generate = [4, 2, 1]
    numbers_of_properties = [3, 2, 1]
    number_of_measurements = 4000
    significance_level = 0.003
    test_amount = 50

    qt_objs = [QuantumPhaseEstimation(_fault, _apply_verification) for _ in
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
