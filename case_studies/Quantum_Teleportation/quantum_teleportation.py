import warnings

import numpy as np
from qiskit import QuantumCircuit, Aer

from case_studies.case_study_interface import CaseStudyInterface
from case_studies.Quantum_Teleportation.equal_output_property import EqualOutputProperty
from case_studies.Quantum_Teleportation.quantum_teleportation_oracle import TeleportationOracle
from dd_regression.diff_algorithm import diff
from dd_regression.result_classes import Passed, Failed, Inconclusive

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)

backend = Aer.get_backend('aer_simulator')


class QuantumTeleportationMined(CaseStudyInterface):
    def __init__(self):
        # self.properties = [EqualOutputProperty, UniformSuperpositionProperty, DifferentPathsSameOutcomeProperty]
        self.properties = [EqualOutputProperty]

    # passing and failing circuits mined from:
    # https://github.com/oreilly-qc/oreilly-qc.github.io/blob/2746abfe96b9f4a9a218dd049b06f4bca30c0681/samples/QCEngine/ch04_basic_teleportation.js
    def get_algorithm_name(self):
        return "Quantum_Teleportation_Mined"

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

    # @staticmethod #pi to pi/2
    # def quantum_teleportation_update():
    #     # Translation of the QCengine code assuming use_conditionals()
    #     # not encoding any state to teleport, will be done in tests
    #     # alice = 0
    #     # ep = 1
    #     # bob = 2
    #     # entangle()
    #     qc = QuantumCircuit(3)
    #     qc.h(1)  # ep.had()
    #     qc.cx(1, 2)  # bob.cnot(ep)
    #     # alice_send()
    #     qc.cx(0, 1)  # ep.cnot(alice);
    #     qc.h(0)  # alice.had();
    #     # bob_receive() (option 3, but translating ifs into controlled gates)
    #     # same semantics, but easier to implement in qiskit
    #     # a1 = alice = register 0
    #     # a2 = ep = register 1
    #     qc.cp(np.pi/2, 0, 2)  # if (a1) bob.phase(180);
    #     qc.cx(1, 2)  # if (a2) bob.not();
    #     return qc

    # @staticmethod
    # def quantum_teleportation_update(): #remove h
    #     # Translation of the QCengine code assuming use_conditionals()
    #     # not encoding any state to teleport, will be done in tests
    #     # alice = 0
    #     # ep = 1
    #     # bob = 2
    #     # entangle()
    #     qc = QuantumCircuit(3)
    #     qc.h(1)  # ep.had()
    #     qc.cx(1, 2)  # bob.cnot(ep)
    #     # alice_send()
    #     qc.cx(0, 1)  # ep.cnot(alice);
    #     # qc.h(0)  # alice.had();
    #     # bob_receive() (option 3, but translating ifs into controlled gates)
    #     # same semantics, but easier to implement in qiskit
    #     # a1 = alice = register 0
    #     # a2 = ep = register 1
    #     qc.cp(np.pi, 0, 2)  # if (a1) bob.phase(180);
    #     qc.cx(1, 2)  # if (a2) bob.not();
    #     return qc

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
    qt = QuantumTeleportationMined()
    print(qt.passing_circuit())
    print(qt.failing_circuit())
    print(qt.expected_deltas_to_isolate())
    expected = qt.expected_deltas_to_isolate()
    print("------------\nexpected pass -----")
    for i in range(1):
        res = TeleportationOracle.test_oracle(qt.passing_circuit(), qt.failing_circuit(), [], [EqualOutputProperty],
                                              measurements=1000, significance_level=0.003, inputs_to_generate=1)
        print(res)
    print("------------\nexpected fail -----")
    for i in range(1):
        res = TeleportationOracle.test_oracle(qt.passing_circuit(), qt.failing_circuit(), expected,
                                              [EqualOutputProperty], measurements=1000, significance_level=0.003,
                                              inputs_to_generate=1)
        print(res)
    print("------------\nfirst delta alone")
    for i in range(1):
        res = TeleportationOracle.test_oracle(qt.passing_circuit(), qt.failing_circuit(), [expected[0]],
                                              [EqualOutputProperty],
                                              measurements=1000, significance_level=0.003, inputs_to_generate=1)
        print(res)
    print("------------\nsecond delta alone")
    for i in range(1):
        res = TeleportationOracle.test_oracle(qt.passing_circuit(), qt.failing_circuit(), [expected[1]],
                                              [EqualOutputProperty],
                                              measurements=1000, significance_level=0.003, inputs_to_generate=1)
        print(res)
    print("------------\nthird delta alone")
    for i in range(1):
        res = TeleportationOracle.test_oracle(qt.passing_circuit(), qt.failing_circuit(), [expected[2]],
                                              [EqualOutputProperty],
                                              measurements=1000, significance_level=0.003, inputs_to_generate=1)
        print(res)
    print("------------\nfourth delta alone")
    for i in range(1):
        res = TeleportationOracle.test_oracle(qt.passing_circuit(), qt.failing_circuit(), [expected[3]],
                                              [EqualOutputProperty],
                                              measurements=1000, significance_level=0.003, inputs_to_generate=1)
        print(res)
    print("------------\n0, 1")
    for i in range(1):
        res = TeleportationOracle.test_oracle(qt.passing_circuit(), qt.failing_circuit(), [expected[0], expected[1]],
                                              [EqualOutputProperty],
                                              measurements=1000, significance_level=0.003, inputs_to_generate=1)
        print(res)
    print("------------\n0, 2")
    pass_res = 0
    fail_res = 0
    incon_res = 0
    for i in range(10000):
        res = TeleportationOracle.test_oracle(qt.passing_circuit(), qt.failing_circuit(), [expected[0], expected[2]],
                                              [EqualOutputProperty],
                                              measurements=5000, significance_level=0.003, inputs_to_generate=1)
        if isinstance(res, Passed):
            pass_res += 1
        elif isinstance(res, Failed):
            fail_res += 1
        else:
            incon_res += 1
        print(res)
    print(f"pass_res {pass_res}")
    print(f"fail_res {fail_res}")
    print(f"inconclusive_res {incon_res}")
    print("------------\n0, 3")
    for i in range(1):
        res = TeleportationOracle.test_oracle(qt.passing_circuit(), qt.failing_circuit(), [expected[0], expected[3]],
                                              [EqualOutputProperty],
                                              measurements=1000, significance_level=0.003, inputs_to_generate=1)
        print(res)
    print("------------\n1, 2")
    for i in range(1):
        res = TeleportationOracle.test_oracle(qt.passing_circuit(), qt.failing_circuit(), [expected[1], expected[2]],
                                              [EqualOutputProperty],
                                              measurements=1000, significance_level=0.003, inputs_to_generate=1)
        print(res)
    print("------------\n1, 3")
    for i in range(1):
        res = TeleportationOracle.test_oracle(qt.passing_circuit(), qt.failing_circuit(), [expected[1], expected[3]],
                                              [EqualOutputProperty],
                                              measurements=1000, significance_level=0.003, inputs_to_generate=1)
        print(res)
    print("------------\n2, 3")
    for i in range(1):
        res = TeleportationOracle.test_oracle(qt.passing_circuit(), qt.failing_circuit(), [expected[2], expected[3]],
                                              [EqualOutputProperty],
                                              measurements=1000, significance_level=0.003, inputs_to_generate=1)
        print(res)
    print("------------\n0, 1, 2")
    for i in range(1):
        res = TeleportationOracle.test_oracle(qt.passing_circuit(), qt.failing_circuit(),
                                              [expected[0], expected[1], expected[2]],
                                              [EqualOutputProperty],
                                              measurements=1000, significance_level=0.003, inputs_to_generate=1)
        print(res)
    print("------------\n0, 1, 3")
    for i in range(1):
        res = TeleportationOracle.test_oracle(qt.passing_circuit(), qt.failing_circuit(),
                                              [expected[0], expected[1], expected[3]],
                                              [EqualOutputProperty],
                                              measurements=1000, significance_level=0.003, inputs_to_generate=1)
        print(res)
    print("------------\n0, 2, 3")
    for i in range(1):
        res = TeleportationOracle.test_oracle(qt.passing_circuit(), qt.failing_circuit(),
                                              [expected[0], expected[2], expected[3]],
                                              [EqualOutputProperty],
                                              measurements=1000, significance_level=0.003, inputs_to_generate=1)
        print(res)
    print("------------\n1, 2, 3")
    for i in range(1):
        res = TeleportationOracle.test_oracle(qt.passing_circuit(), qt.failing_circuit(),
                                              [expected[1], expected[2], expected[3]],
                                              [EqualOutputProperty],
                                              measurements=1000, significance_level=0.003, inputs_to_generate=1)
        print(res)

    # init_state = QuantumCircuit(3)
    # init_vector = random_statevector(2)
    # init_state.initialize(init_vector, 0)
    # inputted_circuit_to_test = init_state.compose(qt.failing_circuit())
    # print(inputted_circuit_to_test.draw(vertical_compression='high', fold=300))
    # res = measure_qubits(inputted_circuit_to_test, [0, 1, 2], 1000, ['x', 'y', 'z'])
    # print(res)
    #
    # changed_circuit_list = apply_diffs(qt.passing_circuit(), [expected[0], expected[2]])
    # changed_circuit = list_to_circuit(changed_circuit_list)
    # init_state = QuantumCircuit(3)
    # init_state.initialize(init_vector, 0)
    # inputted_circuit_to_test = init_state.compose(changed_circuit)
    # print(inputted_circuit_to_test.draw(vertical_compression='high', fold=300))
    # res = measure_qubits(inputted_circuit_to_test, [0, 1, 2], 1000, ['x', 'y', 'z'])
    # print(res)

    # print("second delta alone")
    # res = TeleportationOracle.test_oracle(qt.passing_circuit(), qt.failing_circuit(), [expected[1]],
    #                                       [EqualOutputProperty],
    #                                       measurements=10000, significance_level=0.003, inputs_to_generate=1)
    # for i in range(1):
    #     print(res)


    # chaff_lengths = [2]
    # inputs_to_generate = [1]
    # numbers_of_properties = [1]
    # number_of_measurements = 10000
    # significance_level = 0.003
    # test_amount = 1
    #
    # qt_objs = [QuantumTeleportationMined() for _ in range(len(chaff_lengths) * len(inputs_to_generate) * len(numbers_of_properties))]
    # print(qt_objs)
    # inputs_for_func = [(i1, i2, i3) for i1 in chaff_lengths for i2 in inputs_to_generate for i3 in numbers_of_properties]
    # print(inputs_for_func)
    # results = [(qt_objs[i], inputs_for_func[i][0], inputs_for_func[i][1], inputs_for_func[i][2]) for i in range(len(qt_objs))]
    # print(results)
    # with multiprocessing.Pool() as pool:
    #     results = [pool.apply_async(qt_objs[i].analyse_results, kwds={'chaff_length': inputs_for_func[i][0],
    #                                                                    'inputs_to_generate': inputs_for_func[i][1],
    #                                                                    'number_of_properties': inputs_for_func[i][2],
    #                                                                    'number_of_measurements': number_of_measurements,
    #                                                                    'significance_level': significance_level,
    #                                                                    'test_amount': test_amount}) for
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
