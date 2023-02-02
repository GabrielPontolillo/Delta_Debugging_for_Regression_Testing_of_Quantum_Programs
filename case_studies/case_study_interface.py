import time

from abc import ABC, abstractmethod, abstractproperty
from dd_regression.dd_algorithm import dd_repeat
from dd_regression.helper_functions import circuit_to_list, add_random_chaff, list_to_circuit, \
    determine_delta_application_valid, list_contains_list_in_same_order
from dd_regression.diff_algorithm_r import apply_diffs, diff, Removal, Addition


class CaseStudyInterface(ABC):
    test_cache = {}
    tests_performed = 0
    tests_performed_no_cache = 0

    @abstractmethod
    def get_algorithm_name(self):
        pass

    @abstractmethod
    def expected_deltas_to_isolate(self):
        """
        To analyse the data for the paper, we must specify what deltas are expected to be returned
        assuming no artifacts
        """
        pass

    @abstractmethod
    def passing_circuit(self):
        """
        Return a passing version of the quantum circuit (prior to update)
        """
        pass

    @abstractmethod
    def failing_circuit(self):
        """
        Return a failing version of the quantum circuit (prior to update)
        """
        pass

    @abstractmethod
    def regression_test(self, quantum_circuit):
        """
        Return the (property based) regression test that may be used to test each circuit
        """
        pass

    @abstractmethod
    def test_function(self, deltas, src_passing, src_failing, original_deltas):
        """
        Return a test function, similar to regression test that receives a subset of Deltas,
        """
        pass

    # def analyse_results(self):
    #     """
    #     -> in for loop
    #     -> generate random chaff and add it to the circuit
    #     -> run dd with this chaffed up circuit
    #     -> evaluate score for this run
    #     -> check the operation first
    #     -> if delete = compare position old
    #     -> if insert = first compare position old, then compare object by looking at prechaff circuit
    #      and postchaff circuit
    #     """
    #     base_circuit = self.failing_circuit()
    #     base_circuit_list = circuit_to_list(self.failing_circuit())
    #     expected_deltas = self.expected_deltas_to_isolate()
    #     expected_found = 0
    #     artifact_tally = 0
    #     expected_found_tally = 0
    #     filtered_deltas_len_tally = 0
    #     loops = 10
    #     for i in range(loops):
    #         print(f"loop number {i}")
    #         # chaff_embedded_circuit_list = add_random_chaff(base_circuit.copy())
    #         # chaff_embedded_circuit = list_to_circuit(chaff_embedded_circuit_list)
    #         chaff_embedded_circuit_list = base_circuit.copy()
    #         chaff_embedded_circuit = list_to_circuit(chaff_embedded_circuit_list)
    #
    #         bstart = time.time()
    #         deltas, passing_deltas, orig_fail_deltas = dd_repeat(self.passing_circuit(), chaff_embedded_circuit,
    #                                                              self.test_function)
    #         bend = time.time()
    #         start = time.time()
    #         # filtered_deltas = filter_artifacts(self.passing_circuit(), chaff_embedded_circuit,
    #         #                                    deltas, passing_deltas, orig_fail_deltas, self.test_function)
    #
    #         filtered_deltas = deltas
    #
    #         print("listing off deltas")
    #
    #         for filtered in filtered_deltas:
    #             if filtered.get("offset") is not None:
    #                 filtered.pop("offset")
    #
    #         filtered_copy = filtered_deltas.copy()
    #
    #         expected_found = 0
    #         for e, exp in enumerate(expected_deltas):
    #             elem_found = False
    #             if exp["operation"] == "delete":
    #                 if exp in filtered_copy:
    #                     expected_found += 1
    #             else:
    #                 target = base_circuit_list[exp.get("position_new")][0]
    #                 print(target)
    #                 print(exp.get("position_new"))
    #                 res = [x for x in filtered_copy if x.get("operation") == "insert" and chaff_embedded_circuit_list[x.get("position_new")][0] == target]
    #                 print(".................           res            ...............")
    #                 print(res)
    #                 for elem in res:
    #                     print(elem)
    #                     print(elem.get("position_new"))
    #                     after_base = base_circuit_list[exp.get("position_new") + 1:]
    #                     before_base = base_circuit_list[:exp.get("position_new")]
    #                     after_chaff = chaff_embedded_circuit_list[elem.get("position_new") + 1:]
    #                     before_chaff = chaff_embedded_circuit_list[:elem.get("position_new")]
    #                     after_check = list_contains_list_in_same_order(after_chaff, after_base)
    #                     before_check = list_contains_list_in_same_order(before_chaff, before_base)
    #                     # print("\nbefore base")
    #                     # [print(x) for x in before_base]
    #                     # print("\nbefore chaff")
    #                     # [print(x) for x in before_chaff]
    #                     # print("\nafter base")
    #                     # [print(x) for x in after_base]
    #                     # print("\nafter chaff")
    #                     # [print(x) for x in after_chaff]
    #                     # print(before_check)
    #                     # print(after_check)
    #                     if after_check and before_check:
    #                         print("after and before check passed")
    #                         print(elem)
    #                         filtered_copy.remove(elem)
    #                         expected_found += 1
    #                         break
    #         expected_found_tally += expected_found
    #         artifact_tally += len(filtered_deltas) - expected_found
    #         filtered_deltas_len_tally += len(filtered_deltas)
    #
    #         print("passing to failing orig")
    #         print_edit_sequence(expected_deltas, self.passing_circuit(), self.failing_circuit())
    #         print("passing to failing filtered chaff")
    #         print_edit_sequence(filtered_deltas, self.passing_circuit(), chaff_embedded_circuit)
    #         """current issue - compare failing circuit locations (with chaff and without)
    #             look where inserted gate matches apply only that delta, compare gates before and after?
    #         """
    #         end = time.time()
    #         print(bend - bstart)
    #         print(end - start)
    #         print(chaff_embedded_circuit)
    #         print("apply script timing")
    #         print(end - start)
    #         print(base_circuit)
    #         # print(list_to_circuit(apply_edit_script(expected_deltas, circuit_to_list(self.passing_circuit()),
    #         #                                         base_circuit_list, expected_deltas)))
    #         print_edit_sequence(diff(circuit_to_list(self.passing_circuit()), chaff_embedded_circuit_list),
    #                             self.passing_circuit(), chaff_embedded_circuit)
    #         # if artifact_tally > 0:
    #         #     assert False
    #         # print(expected_found_tally)
    #         # print(len(expected_deltas*i))
    #         # if expected_found_tally < len(expected_deltas*i):
    #         #     assert False
    #     print(f"expected_found {expected_found_tally}")
    #     print(f"length expected deltas * loops {len(expected_deltas * loops)}")
    #     print(f"artifact tally {artifact_tally}")
    #     """add length of all filtered deltas"""
    #     print(f"{(expected_found_tally*100) / len(expected_deltas*loops)}% expected deltas found")
    #     print(f"{artifact_tally*100/filtered_deltas_len_tally}% percentage of artifacts in results")
    #     print(self.get_algorithm_name())

    def analyse_results(self):
        """
        -> in for loop
        -> generate random chaff and add it to the circuit
        -> run dd with this chaffed up circuit
        -> evaluate score for this run
        -> check the operation first
        -> if delete = compare position old
        -> if insert = first compare position old, then compare object by looking at prechaff circuit
         and postchaff circuit
        """
        failing_circuit = self.failing_circuit()
        failing_circuit_list = circuit_to_list(self.failing_circuit())
        expected_deltas = self.expected_deltas_to_isolate()
        expected_found = 0
        artifacts_found = 0
        tests_with_artifacts = 0
        start = time.time()
        print(expected_deltas)
        print(failing_circuit_list)
        print(failing_circuit)
        loops = 100
        for i in range(loops):
            print(f"loop number {i}")
            chaff_embedded_circuit_list = add_random_chaff(failing_circuit.copy())
            # chaff_embedded_circuit_list = failing_circuit.copy()
            chaff_embedded_circuit = list_to_circuit(chaff_embedded_circuit_list)
            print(chaff_embedded_circuit)

            deltas, passing_deltas = dd_repeat(self.passing_circuit(), chaff_embedded_circuit, self.test_function)

            # print(f"passing deltas {passing_deltas}")
            print(f"failing deltas {deltas}")
            # print(list_to_circuit(apply_diffs(circuit_to_list(self.passing_circuit()), chaff_embedded_circuit_list, deltas)))
            self.test_cache = {}

            if Removal(location_index=4) in deltas:
                expected_found += 1

            if len(deltas) > 1:
                artifacts_found += len(deltas) - 1
                tests_with_artifacts += 1
        print(f"time taken {time.time() - start}")
        print(f"tests performed {self.tests_performed}")
        print(f"tests performed no cache{self.tests_performed_no_cache}")
        print(f"deltas {expected_found}")
        print(f"out of  {loops}")
        print(f"total amount other deltas included in output {artifacts_found}")
        print(f"tests with any amount of {tests_with_artifacts}")


        # for e, exp in enumerate(expected_deltas):
        #     filtered_deltas = deltas
        #
        #     print("listing off deltas")
        #
        #     for filtered in filtered_deltas:
        #         if filtered.get("offset") is not None:
        #             filtered.pop("offset")
        #
        #     filtered_copy = filtered_deltas.copy()
        #
        #     expected_found = 0
        #     for e, exp in enumerate(expected_deltas):
        #         elem_found = False
        #         if exp["operation"] == "delete":
        #             if exp in filtered_copy:
        #                 expected_found += 1
        #         else:
        #             target = base_circuit_list[exp.get("position_new")][0]
        #             print(target)
        #             print(exp.get("position_new"))
        #             res = [x for x in filtered_copy if
        #                    x.get("operation") == "insert" and chaff_embedded_circuit_list[x.get("position_new")][
        #                        0] == target]
        #             print(".................           res            ...............")
        #             print(res)
        #             for elem in res:
        #                 print(elem)
        #                 print(elem.get("position_new"))
        #                 after_base = base_circuit_list[exp.get("position_new") + 1:]
        #                 before_base = base_circuit_list[:exp.get("position_new")]
        #                 after_chaff = chaff_embedded_circuit_list[elem.get("position_new") + 1:]
        #                 before_chaff = chaff_embedded_circuit_list[:elem.get("position_new")]
        #                 after_check = list_contains_list_in_same_order(after_chaff, after_base)
        #                 before_check = list_contains_list_in_same_order(before_chaff, before_base)
        #                 # print("\nbefore base")
        #                 # [print(x) for x in before_base]
        #                 # print("\nbefore chaff")
        #                 # [print(x) for x in before_chaff]
        #                 # print("\nafter base")
        #                 # [print(x) for x in after_base]
        #                 # print("\nafter chaff")
        #                 # [print(x) for x in after_chaff]
        #                 # print(before_check)
        #                 # print(after_check)
        #                 if after_check and before_check:
        #                     print("after and before check passed")
        #                     print(elem)
        #                     filtered_copy.remove(elem)
        #                     expected_found += 1
        #                     break
        #     expected_found_tally += expected_found
        #     artifact_tally += len(filtered_deltas) - expected_found
        #     filtered_deltas_len_tally += len(filtered_deltas)
        #
        #     print("passing to failing orig")
        #     print_edit_sequence(expected_deltas, self.passing_circuit(), self.failing_circuit())
        #     print("passing to failing filtered chaff")
        #     print_edit_sequence(filtered_deltas, self.passing_circuit(), chaff_embedded_circuit)
        #     """current issue - compare failing circuit locations (with chaff and without)
        #         look where inserted gate matches apply only that delta, compare gates before and after?
        #     """
        #     end = time.time()
        #     print(bend - bstart)
        #     print(end - start)
        #     print(chaff_embedded_circuit)
        #     print("apply script timing")
        #     print(end - start)
        #     print(base_circuit)
        #     # print(list_to_circuit(apply_edit_script(expected_deltas, circuit_to_list(self.passing_circuit()),
        #     #                                         base_circuit_list, expected_deltas)))
        #     print_edit_sequence(diff(circuit_to_list(self.passing_circuit()), chaff_embedded_circuit_list),
        #                         self.passing_circuit(), chaff_embedded_circuit)
        #     # if artifact_tally > 0:
        #     #     assert False
        #     # print(expected_found_tally)
        #     # print(len(expected_deltas*i))
        #     # if expected_found_tally < len(expected_deltas*i):
        #     #     assert False
        # print(f"expected_found {expected_found_tally}")
        # print(f"length expected deltas * loops {len(expected_deltas * loops)}")
        # print(f"artifact tally {artifact_tally}")
        # """add length of all filtered deltas"""
        # print(f"{(expected_found_tally * 100) / len(expected_deltas * loops)}% expected deltas found")
        # print(f"{artifact_tally * 100 / filtered_deltas_len_tally}% percentage of artifacts in results")
        # print(self.get_algorithm_name())
