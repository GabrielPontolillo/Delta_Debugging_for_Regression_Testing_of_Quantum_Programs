import warnings
import multiprocessing

import numpy as np
from qiskit import QuantumCircuit, Aer

from case_studies.case_study_interface import CaseStudyInterface
from case_studies.Quantum_Teleportation.equal_output_property import EqualOutputProperty
from case_studies.Quantum_Teleportation.quantum_teleportation_oracle import TeleportationOracle
from case_studies.Quantum_Teleportation.different_paths_same_outcome_property import DifferentPathsSameOutcomeProperty
from case_studies.Quantum_Teleportation.uniform_superposition_property import UniformSuperpositionProperty
from dd_regression.diff_algorithm import diff
from dd_regression.helper_functions import files_to_spreadsheet
from dd_regression.result_classes import Passed, Failed, Inconclusive

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

backend = Aer.get_backend('aer_simulator')


class QuantumTeleportationMined(CaseStudyInterface):
    fault = "A"
    apply_verification = True

    def __init__(self):
        self.properties = [EqualOutputProperty, UniformSuperpositionProperty, DifferentPathsSameOutcomeProperty]

    def get_algorithm_name(self):
        return "Quantum_Teleportation"

    # passing circuit from:
    # https://github.com/oreilly-qc/oreilly-qc.github.io/commit/2746abfe96b9f4a9a218dd049b06f4bca30c0681
    # passing circuit
    @staticmethod
    def quantum_teleportation():
        # Translation of the QCengine code.
        qc = QuantumCircuit(3)
        qc.h(1)
        qc.cx(1, 2)
        qc.cx(0, 1)
        qc.h(0)
        qc.cp(np.pi, 0, 2)
        qc.cx(1, 2)
        return qc

    @staticmethod  # 1
    def quantum_teleportation_update():  # remove h
        qc = QuantumCircuit(3)

        if fault == "A":
            # this fault removes a hadamard
            qc.h(1)
            qc.cx(1, 2)
            qc.cx(0, 1)
            # removed hadamard here
            qc.cp(np.pi, 0, 2)
            qc.cx(1, 2)
        elif fault == "B":
            # this fault adds a controlled phase
            qc.h(1)
            qc.cx(1, 2)
            qc.cx(0, 1)
            qc.h(0)
            qc.cp(np.pi, 0, 2)
            qc.cp(np.pi/2, 0, 2)  # added here
            qc.cx(1, 2)
        elif fault == "C":
            # this fault adds an x gate
            qc.x(2)  # added here
            qc.h(1)
            qc.cx(1, 2)
            qc.cx(0, 1)
            qc.h(0)
            qc.cp(np.pi, 0, 2)
            qc.cx(1, 2)

        return qc

    def expected_deltas_to_isolate(self):
        return diff(self.passing_circuit(), self.failing_circuit())

    def passing_circuit(self):
        return self.quantum_teleportation()

    def failing_circuit(self):
        return self.quantum_teleportation_update()

    def test_function(self, deltas, src_passing, src_failing, inputs_to_generate, selected_properties,
                      number_of_measurements, significance_level):
        self.tests_performed += 1
        if self.test_cache.get(tuple(deltas), None) is not None:
            return self.test_cache.get(tuple(deltas), None)
        self.tests_performed_no_cache += 1

        # print(f"chosen properties {selected_properties}")

        oracle_result = TeleportationOracle.test_oracle(src_passing, src_failing, deltas,
                                                        selected_properties,
                                                        inputs_to_generate=inputs_to_generate,
                                                        measurements=number_of_measurements,
                                                        significance_level=significance_level,
                                                        verification=apply_verification
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
    fault = "A"
    # set apply_verification = False to run the property based test oracle without the verification step
    apply_verification = True
    chaff_lengths = [8, 4, 2, 1]
    inputs_to_generate = [4, 2, 1]
    numbers_of_properties = [3, 2, 1]
    number_of_measurements = 4000
    significance_level = 0.003
    test_amount = 50

    qt_objs = [QuantumTeleportationMined() for _ in
               range(len(chaff_lengths) * len(inputs_to_generate) * len(numbers_of_properties))]

    print(qt_objs)
    inputs_for_func = [(i1, i2, i3) for i1 in chaff_lengths for i2 in inputs_to_generate for i3 in
                       numbers_of_properties]
    print(inputs_for_func)
    results = [(qt_objs[i], inputs_for_func[i][0], inputs_for_func[i][1], inputs_for_func[i][2]) for i in
               range(len(qt_objs))]
    print(results)
    with multiprocessing.Pool(14) as pool:
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
