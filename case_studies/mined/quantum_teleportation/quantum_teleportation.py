import csv
import multiprocessing
import warnings

import numpy as np
from qiskit import QuantumCircuit, Aer

from case_studies.case_study_interface import CaseStudyInterface
from case_studies.mined.quantum_teleportation.different_paths_same_outcome import DifferentPathsSameOutcomeProperty
from case_studies.mined.quantum_teleportation.equal_output_property import EqualOutputProperty
from case_studies.mined.quantum_teleportation.teleportation_oracle import TeleportationOracle
from case_studies.mined.quantum_teleportation.uniform_superposition_property import UniformSuperpositionProperty
from dd_regression.diff_algorithm import diff
from dd_regression.result_classes import Passed, Failed, Inconclusive

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

backend = Aer.get_backend('aer_simulator')


class QuantumTeleportationMined(CaseStudyInterface):
    def __init__(self):
        self.properties = [EqualOutputProperty, UniformSuperpositionProperty, DifferentPathsSameOutcomeProperty]

    # passing and failing circuits mined from:
    # https://github.com/oreilly-qc/oreilly-qc.github.io/blob/2746abfe96b9f4a9a218dd049b06f4bca30c0681/samples/QCEngine/ch04_basic_teleportation.js
    def get_algorithm_name(self):
        return "Quantum Teleportation Mined"

    # passing circuit
    @staticmethod
    def quantum_teleportation():
        # Translation of the QCengine code assuming use_conditionals()
        # not encoding any state to teleport, will be done in tests
        # alice = 0
        # ep = 1
        # bob = 2
        # entangle()
        qc = QuantumCircuit(3)
        qc.h(1)  # ep.had()
        qc.cx(1, 2)  # bob.cnot(ep)
        # alice_send()
        qc.cx(0, 1)  # ep.cnot(alice);
        qc.h(0)  # alice.had();
        # bob_receive() (option 3, but translating ifs into controlled gates)
        # same semantics, but easier to implement in qiskit
        # a1 = alice = register 0
        # a2 = ep = register 1
        qc.cp(np.pi, 0, 2)  # if (a1) bob.phase(180);
        qc.cx(1, 2)  # if (a2) bob.not();
        return qc

    # failing circuit
    @staticmethod
    def quantum_teleportation_update():
        # Translation of the QCengine code assuming use_conditionals()
        # not encoding any state to teleport, will be done in tests
        # alice = 0
        # ep = 1
        # bob = 2
        # entangle()
        qc = QuantumCircuit(3)
        qc.h(1)  # ep.had()
        qc.cx(1, 2)  # bob.cnot(ep)
        # alice_send()
        qc.cx(0, 1)  # ep.cnot(alice);
        qc.h(0)  # alice.had();
        # bob_receive() (option 3, but translating ifs into controlled gates)
        # same semantics, but easier to implement in qiskit
        # a1 = alice = register 0
        # a2 = ep = register 1
        qc.cx(0, 2)  # if (a1) bob.not();
        qc.cp(np.pi, 1, 2)  # if (a2) bob.phase(180);
        return qc

    def expected_deltas_to_isolate(self):
        return diff(self.passing_circuit(), self.failing_circuit())

    def passing_circuit(self):
        return self.quantum_teleportation()

    def failing_circuit(self):
        return self.quantum_teleportation_update()

    def regression_test(self, circuit_to_test):
        pass

    def test_function(self, deltas, src_passing, src_failing, inputs_to_generate, selected_properties, number_of_measurements, significance_level):
        self.tests_performed += 1
        if self.test_cache.get(tuple(deltas), None) is not None:
            return self.test_cache.get(tuple(deltas), None)
        self.tests_performed_no_cache += 1

        # print(f"chosen properties {selected_properties}")

        oracle_result = TeleportationOracle.test_oracle(src_passing, src_failing, deltas,
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
    chaff_lengths = [4]
    inputs_to_generate = [3]
    number_of_properties = 3
    number_of_measurements = 1000
    significance_level = 0.003
    test_amount = 10

    qpe_objs = [QuantumTeleportationMined() for _ in range(len(chaff_lengths) * len(inputs_to_generate))]
    print(qpe_objs)
    inputs_for_func = [(i1, i2) for i1 in chaff_lengths for i2 in inputs_to_generate]
    print(inputs_for_func)
    results = [(qpe_objs[i], inputs_for_func[i][0], inputs_for_func[i][1]) for i in range(len(qpe_objs))]
    print(results)
    with multiprocessing.Pool() as pool:
        results = [pool.apply_async(qpe_objs[i].analyse_results, kwds={'chaff_length': inputs_for_func[i][0],
                                                                       'inputs_to_generate': inputs_for_func[i][1],
                                                                       'number_of_properties': number_of_properties,
                                                                       'number_of_measurements': number_of_measurements,
                                                                       'significance_level': significance_level,
                                                                       'test_amount': test_amount}) for
                   i in range(len(qpe_objs))]
        for r in results:
            r.get()

    pool.join()

    rows = []
    row = []
    row.append("X")
    for i in range(len(chaff_lengths)):
        row.append(f"inserted deltas {chaff_lengths[i]*2}")
    rows.append(row)
    for i in range(len(inputs_to_generate)):
        row = []
        row.append(f"inputs/test {inputs_to_generate[i]}")
        for j in range(len(chaff_lengths)):
            f = open(
                f"{qpe_objs[0].get_algorithm_name()}_chaff_length{chaff_lengths[j]}_inputs_to_gen{inputs_to_generate[i]}.txt",
                "r")
            row.append(f.read())
        rows.append(row)

    with open("test_results.csv", 'w', newline='') as file:
        writer = csv.writer(file, dialect='excel')
        writer.writerows(rows)