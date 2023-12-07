# Delta Debugging for the Regression testing of quantum programs.

### Repository layout and description:
- **Results and graphs.xslx**: Contains all experiment data, grouped in one spreadsheet. We draw from the data within the sheet to draw various graphs (featuring the figures from the paper, as well as values cited in the results section).

- **properties.md**: Contains a description of the properties tested by the property based tests in the **property.py* files below 

- **case_studies** (package): Contains experiment set-ups (passing and failing versions of a quantum algorithm, property based test oracle, regression tests) for each quantum algorithm being tested.
    - **(name_of_algorithm)** (package): Contains files relating to an algorithm.
        - ***oracle.py**: Contains an oracle that evaluates multiple properties, verifies the properties to identify inconclusive outcomes, and performs the Holm-Bonferroni correction to correct the error rate due to running multiple statistical tests.
        - ***property.py**: Contains an individual property based test, which contains to components: A method to run the property based test to evaluate the property, and a method to verify whether an observed failure is the same as the original failure.
        - **(name_of_algorithm).py**: Contains passing and failing versions of the algorithm, regression test, test function that calls the oracle, main method that runs the case with multiple configurations.
        
    - **case_study_interface.py**: The interface that is implementeed by (name_of_algorithm.py) files, contains code to run the case study experiment and store the results to a file, as well as describes expected methods for each case study.
    - **property_based_test_interface.py**: The interface that is implemented by *property.py files, describes the two methods that are expected to be contained within proeprty based test files.
    - **property_based_test_oracle_interface.py**: The interface that is implemented by *oracle.py files, describes the structure of property based test oracles.
    
- **dd_regression** (package): Contains all code related to the execution of delta debugging, property based testing, and diffing
    - **assertions.py**: Contains statistical assertions that may be called within property based tests.
    - **dd_algorithm.py**: Contains the delta debugging algorithm, and related functions.
    - **diff_algorithm.py**: Contains the diffing algorithm, as well as an algorithm to apply diffs to a circuit, and classes for each diff type: Addition, Removal.
    - **helper_functions.py**: Contains loose function that may be used throughout the project.
    - **result_classes.py**: Contains classes for property based test oracle outcomes: Passed, Failed and Inconclusive. 
    
------
    
 ### Reproducing the experiments:
 
 1) Within the (name_of_algoirthm).py files in each case study, scroll down to the "\_\_main__".
 2) Modify the fault = "A" variable to the fault you want to test ("A", "B", "C").
 3) Modify the apply_verification = True to False to turn off verification. 
 4) The rest of the independent variables can be modified by changing the *chaff_lengths*, *inputs_to_generate*, *numbers_of_properties* variables, but by default are lists containing all values in the paper.
 5) Running the file will start a multiprocessing pool utilising all threads available on the pc, and evaluate the case study with the *selected fault*, *apply verification in the property based tests as specified*, and all combinations of independent variables as in each list. it will then generate a CSV file containing the results of all experiments for that specific fault and verification combination.
 6) Repeat this process for all case studies, and group all CSV files as in **Results and graphs.xslx**
 
 ### Properties evaluated within the property based test oracle:
 
 Each case study has a propery based test oracle, which calls 3 properties. In the folder structure, the files that contain the property based tests end in *property.py*.
 
 A detailed description on all of the tested properties can be found in the *properties.md* file as can be seen in the above structure. 