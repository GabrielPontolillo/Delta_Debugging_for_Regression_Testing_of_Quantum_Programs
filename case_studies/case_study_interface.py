import time

from abc import ABC, abstractmethod
from dd_regression.dd_algorithm import dd_repeat, filter_artifacts
from dd_regression.helper_functions import circuit_to_list, add_random_chaff, list_to_circuit


class CaseStudyInterface(ABC):
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
        base_circuit = self.failing_circuit()
        base_circuit_list = circuit_to_list(self.failing_circuit())
        expected_deltas = self.expected_deltas_to_isolate()
        found = 0
        for i in range(1):
            chaff_embedded_circuit_list = add_random_chaff(base_circuit.copy())
            chaff_embedded_circuit = list_to_circuit(chaff_embedded_circuit_list)
            bstart = time.time()
            deltas, passing_deltas, orig_fail_deltas = dd_repeat(self.passing_circuit(), chaff_embedded_circuit,
                                                                 self.test_function)
            bend = time.time()
            start = time.time()
            filtered_deltas = filter_artifacts(self.passing_circuit(), chaff_embedded_circuit,
                                               deltas, passing_deltas, orig_fail_deltas, self.test_function)
            for delta in expected_deltas:
                if delta["operation"] == "delete":
                    if any(idx['position_old'] == delta['position_old'] for idx in filtered_deltas):
                        print("delete found")
                        found += 1
                else:
                    print(f"delta {delta}")
                    print(chaff_embedded_circuit)
                    print(chaff_embedded_circuit_list)
                    print(base_circuit)
                    print(base_circuit_list)
                    for filtered_delta in filtered_deltas:
                        if filtered_delta["operation"] == "insert":
                            print(filtered_delta["position_new"])
                            print(chaff_embedded_circuit_list[filtered_delta['position_new']])
                            print(delta["position_new"])
                            print(base_circuit_list[delta['position_new']])
                            print("insert found")
                        if filtered_delta["operation"] == "insert" and filtered_delta["position_old"] == delta["position_old"]:
                            found += 1
                    # if any(idx.get('position_new') is not None and idx['position_old'] == delta['position_old'] and
                    #    base_circuit_list[delta['position_new']] == chaff_embedded_circuit_list[idx['position_new']]
                    #        for idx in filtered_deltas):

            """current issue - position_old is varying for insert
            """
            end = time.time()
            print(bend - bstart)
            print(end - start)
            print(filtered_deltas)
            print(expected_deltas)
        print(found)
        print()


        # filtered_deltas = self.run_dd()
        # need to know what it was before chaff was added
        # compare the position_new parts as those are the ones changed

        # found = 0
        # not_found = 0
        # for delta in filtered_deltas:
        #     if delta[""] == expected_deltas:
        #         found += 1
        #     else:
        #         not_found += 1
        # should never be able to find more than expected deltas
        # assert found <= len(expected_deltas)
        # percent_deltas_isolated = (found/len(expected_deltas)) * 100
        # percent_chaff_isolated = (1 - found/len(filtered_deltas)) * 100
        # return percent_deltas_isolated, percent_chaff_isolated

    def run_dd(self):
        deltas, orig_fail_deltas = dd_repeat(self.passing_circuit(), self.failing_circuit(), self.test_function)
        filtered_deltas = filter_artifacts(self.passing_circuit(), self.failing_circuit(),
                                           deltas, orig_fail_deltas, self.test_function)
        return filtered_deltas

    # def analyse_results(self):
    #     pre_chaff_circuit_list = circuit_to_list(self.failing_circuit())
    #     expected_deltas = self.expected_deltas_to_isolate()
    #     filtered_deltas = self.run_dd()
    #     # need to know what it was before chaff was added
    #     # compare the position_new parts as those are the ones changed
    #     print(filtered_deltas)
    #     print(expected_deltas)
    #     found = 0
    #     not_found = 0
    #     for delta in filtered_deltas:
    #         if delta[""] == expected_deltas:
    #             found += 1
    #         else:
    #             not_found += 1
    #     # should never be able to find more than expected deltas
    #     assert found <= len(expected_deltas)
    #     percent_deltas_isolated = (found/len(expected_deltas)) * 100
    #     percent_chaff_isolated = (1 - found/len(filtered_deltas)) * 100
    #     return percent_deltas_isolated, percent_chaff_isolated

