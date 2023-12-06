import multiprocessing
import warnings

import numpy as np
from qiskit import QuantumCircuit, Aer

from case_studies.case_study_interface import CaseStudyInterface
from dd_regression.diff_algorithm import diff
from dd_regression.helper_functions import files_to_spreadsheet
from dd_regression.result_classes import Passed, Failed, Inconclusive
from case_studies.Quantum_Fourier_Transform.phase_shift_property import PhaseShiftProperty
from case_studies.Quantum_Fourier_Transform.up_shift_property import UpShiftProperty
from case_studies.Quantum_Fourier_Transform.identity_property import IdentityProperty
from case_studies.Quantum_Fourier_Transform.quantum_fourier_transform_oracle import QuantumFourierTransformOracle

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

backend = Aer.get_backend('aer_simulator')


class QuantumFourierTransform(CaseStudyInterface):
    def __init__(self):
        self.properties = [IdentityProperty, UpShiftProperty, PhaseShiftProperty]
        # self.properties = [IdentityProperty]

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

    # @staticmethod # 1
    # def qft_update(): # remove controlled pi/2 rotation
    #     estimation_qubits = 3
    #     qft_circuit = QuantumCircuit(estimation_qubits)
    #     qft_circuit.h(0)
    #     qft_circuit.cp(np.pi / 2, 0, 1)
    #     qft_circuit.cp(np.pi / 4, 0, 2)
    #     qft_circuit.h(1)
    #     qft_circuit.h(2)
    #     return qft_circuit

    # @staticmethod # 2
    # def qft_update(): # add cp 3pi/2
    #     estimation_qubits = 3
    #     qft_circuit = QuantumCircuit(estimation_qubits)
    #     qft_circuit.h(0)
    #     qft_circuit.cp(np.pi / 2, 0, 1)
    #     qft_circuit.cp(np.pi / 4, 0, 2)
    #     qft_circuit.h(1)
    #     qft_circuit.cp(np.pi / 2, 1, 2)
    #     qft_circuit.cp(3*np.pi / 2, 1, 2)
    #     qft_circuit.h(2)
    #     return qft_circuit

    @staticmethod # 3
    def qft_update(): # add x to register 0 at the start
        estimation_qubits = 3
        qft_circuit = QuantumCircuit(estimation_qubits)
        qft_circuit.x(0)
        qft_circuit.h(0)
        qft_circuit.cp(np.pi / 2, 0, 1)
        qft_circuit.cp(np.pi / 4, 0, 2)
        qft_circuit.h(1)
        qft_circuit.cp(np.pi / 2, 1, 2)
        qft_circuit.h(2)
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
                                                                  significance_level=significance_level,
                                                                  verification=False
                                                                  )
        if isinstance(oracle_result, Passed):
            self.test_cache[tuple(deltas)] = Passed()
        elif isinstance(oracle_result, Failed):
            self.test_cache[tuple(deltas)] = Failed()
        elif isinstance(oracle_result, Inconclusive):
            self.test_cache[tuple(deltas)] = Inconclusive()
        return oracle_result


if __name__ == "__main__":
    qt = QuantumFourierTransform()
    print(qt.passing_circuit())
    print(qt.failing_circuit())
    print(qt.expected_deltas_to_isolate())
    expected = qt.expected_deltas_to_isolate()

    # passing = 0
    # failing = 0
    # inconclusive = 0
    # for i in range(10):
    #     res = QuantumFourierTransformOracle.test_oracle(qt.passing_circuit(), qt.failing_circuit(), expected,
    #                                                     [IdentityProperty],
    #                                                     measurements=4000, significance_level=0.003,
    #                                                     inputs_to_generate=1)
    #     if isinstance(res, Passed):
    #         passing += 1
    #     elif isinstance(res, Failed):
    #         failing += 1
    #     else:
    #         inconclusive += 1
    #     print(res)
    #
    # print(f"passing {passing}")
    # print(f"failing {failing}")
    # print(f"inconclusive {inconclusive}")

    chaff_lengths = [8, 4, 2, 1]
    inputs_to_generate = [4, 2, 1]
    numbers_of_properties = [3, 2, 1]
    number_of_measurements = 4000
    significance_level = 0.003
    test_amount = 50

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
