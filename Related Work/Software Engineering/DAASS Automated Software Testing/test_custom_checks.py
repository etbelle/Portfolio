print("Testing custom_checks.py")
import unittest       #Required for all Unittest testing. https://docs.python.org/3.3/library/unittest.html
import os             #Primarily used for file and path manipulation. https://docs.python.org/3.3/library/os.html
import sys            #A module that allows interaction with the interpreter. Such as data structure sizes and module data. https://docs.python.org/2/library/sys.html
import shutil         #A useful extension to the os library for common, but more advanced, opperations. https://docs.python.org/3.3/library/shutil.html
import pickle         #A module that allows for serialization and de-serialization of object structures. Primarily used by ANSA for DM related tasks. https://docs.python.org/3.3/library/pickle.html
from ansa import session, utils, base, constants  #~Deppending on the task, import one, or many, ANSA libraries. Refer to Function list in the ANSA script edit window.
import zipfile        #This module allows for the manipulation of .zip files. All testing resources are zipped initially and need to be unziped to be used. https://docs.python.org/3.3/library/zipfile.html

original_path = os.path.dirname(os.path.abspath(__file__))

#Current path to script are testing.
current_path = original_path.replace("test_suite/","")

#Allows script to see full import path
sys.path.append(current_path)
import custom_checks   #~Import the script you would like to test from the location that it's located in.

# Directory to models for system tests
PATH_TEST_RESOURCE = pickle.loads(session.BetaGetVariable("PATH_TEST_RESOURCE")) 
_TEST_RESOURCE = PATH_TEST_RESOURCE + "/pre/utility/custom_checks"  #~This is the path to the testing resources you would like to use to test with.

# Using scratch to work on temp file paths
PATH_SCRATCH_TESTING = pickle.loads(session.BetaGetVariable("PATH_SCRATCH")) + "/testing_temp" #This is an extra sandbox location if you need to do file manipulation outside of the test resources. 
os.makedirs(PATH_SCRATCH_TESTING, exist_ok=True)

"""
pull_parts_from_exec_output()
pull_parts_from_resources()
determine_print_message()

These three functions defined below are used to streamline the creation of new tests for the custom_checks script.

To test each _exec function within the custom_checks script, it requires that a part, or parts, are provided as an argument.
In an attempt to prepare the variable for the developer, the three functions are used to prepare the input, prepare the output, and select the output response required for the assert statement. 
Though these three functions may not be used for each system test, the general feel and format for each test still follows the same type of functionality.

- Retrieve the models from the ANSA session
- Prep them for the exec function
- Run the exec function
- Compare the names of the parts retrieved from exec functions report to the names of the active models in ANSA.
- Sometimes it may be more logical to track the number of items in the group rather than the objects name.
"""

def pull_parts_from_exec_output(report, error_class_search = False, type_code = 3288):
    """
    Helper Function for system tests. Grabs part names from resources loaded into ANSA and returns them as a set.
    
    @report checkreport object returned. by a exec function within the custom_checks script
    
    @error_class string of what type of status is expected
    
    @type_code integer representaion of a ANSA enties type.
    
    @returns set containing strings which are the names of the parts within the part objects.
    """
    entity_names = []
    #part data = ._type: 3288
    #material data = ._type: 2001
    #connection = ._type: 3323
    for issues in report.issues:
        if error_class_search:
             if not issues.status == error_class_search:
                  print("Wrong Error Class " + issues.status + " for entity " + str(issues.description))
                  print("Searching for error: " + error_class_search)
                  continue
                   
        for entity_types in issues.entities:
            if entity_types._type == type_code:
                entity_names.append(str(entity_types._name))
        
    return set(entity_names)    
     
    
    
def pull_parts_from_resources(_parts):
    """
    This function pulls the part names from a list of provided part objects. 
    
    @_parts list of part objects
    
    @returns set containing strings which are the names of the parts within the part objects.
    """
    part_name_regression = [part._name for part in _parts]
    return set(part_name_regression)


def determine_print_message(group_names_minus_exec_names, exec_names_minus_group_names):
    """
    This function determines what print message we should provide to user.
    The conditions are based on the difference of two sets of part names.
    
    @group_names_minus_exec_names  set strings: a set of strings that are the part names, derived from a check_report object that was the output of an exec function call.
    
    @exec_names_minus_group_names  set strings: a set of strings that are the parts names, derived from the ansa session .  
    
    @return string of the what will be seen for an error message if the test fails.
    """ 
    
    print_error = ""
    if((len(group_names_minus_exec_names) > 0) and (len(exec_names_minus_group_names) == 0)):
        print_error = "More samples than issues: "
    elif((len(group_names_minus_exec_names) == 0) and (len(exec_names_minus_group_names) > 0)):
        print_error = "Less samples than issues: "
    elif((len(group_names_minus_exec_names) is not 0) and (len(exec_names_minus_group_names) is not 0)): 
        print_error = "Both samples and issues have names that are unaccounted for. Test List: " + str(group_names_minus_exec_names) + ", issues list: " + str(exec_names_minus_group_names)
    
    return print_error



def setUpModule():
    """
    In order to run the tests, we need to unzip the related material in the testing resource repository.
    """
    dm_zip = zipfile.ZipFile(_TEST_RESOURCE + "/custom_checks.ansa.zip", "r")  #~the name of the zip file you need to extract.
    dm_zip.extractall(_TEST_RESOURCE)


def tearDownModule():
    """
    After we have run all of our test cases, we need to clean up any unzipped or temporary files.
    """
    
    for root, dirs, files in os.walk(_TEST_RESOURCE, topdown=False):
        for name in files:
            if ".zip" not in name:
                os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
            

class check_bar_thickness(unittest.TestCase): #The class name does not matter.
    """
    Tests for the Check Bar Thickness section of the custom_checks script.
    """        
    
    def setUp(self): #Name matters, do not change
        session.New("discard")
        utils.Merge(_TEST_RESOURCE + "/custom_checks.ansa")
        self.CBEAM_regression_set = {(('E', 1000000.0), ('A', 1.0), ('L', 10.0))}
        self.CROD_regression_set = {(('E', 1000000.0), ('A', 1.0), ('L', 10.0))}
        self.CBAR_regression_set = {(('E', 1000000.0), ('A', 1.0), ('L', 10.0))}
        parts = base.GetPartFromName("test_get_one_d_info_elements")
        
        self.entities = base.CollectEntities(constants.NASTRAN, parts, "__ELEMENTS__")
        for each in self.entities:
            if 536 == each._type:
                self.CBEAM_ent = each
            elif 540 == each._type:
                self.CROD_ent = each
            elif 532 == each._type:
                self.CBAR_ent = each
        
        return 0


    def tearDown(self): #Name matters, do not change
        return 0

    def test_entities_size_regression(self):
        """
        This is to verify that there are only three entities within the list of entities.
        
        Entities tthat should exist: 'CBEAM','CROD','CBAR'
        """ 
        
        self.assertTrue(len(self.entities) == 3)
        
 
    def test_CBEAM_get_one_d_info_regression(self):  
        """
        This function regression tests the the custom_checks.get_one_d_info function with a CBEAM entity.
        
        Function tested: custom_checks.get_one_d_info(ANSAElement)
        """
        
        outputs = []
        E, A, L = custom_checks.get_one_d_info(self.CBEAM_ent)   
        outputs.append((('E',E), ('A',A) ,('L',L)))

        outputs_set = set(outputs)
        self.assertEqual(outputs_set - self.CROD_regression_set, {(('E', 10000000.0), ('A', 1.0), ('L', 10.0))}, "CBEAM values failed regression test.") 
        
        return 0
     
    
    def test_CROD_get_one_d_info_regression(self):
        """
        This function regression tests the the custom_checks.get_one_d_info function with a CROD entity.
        
        Function tested: custom_checks.get_one_d_info(ANSAElement)
        """
        
        outputs = []
        E, A, L = custom_checks.get_one_d_info(self.CROD_ent)   
        outputs.append((('E',E), ('A',A) ,('L',L)))

        outputs_set = set(outputs)
        self.assertEqual(outputs_set - self.CROD_regression_set, {(('E', 10000000.0), ('A', 1.0), ('L', 10.0))}, "CROD values failed regression test.") 
        
        return 0
        

    def test_CBAR_get_one_d_info_regression(self):
        """
        This function regression tests the the custom_checks.get_one_d_info function with a CBAR entity.
        
        Function tested: custom_checks.get_one_d_info(ANSAElement)
        """
        
        outputs = []
        E, A, L = custom_checks.get_one_d_info(self.CBAR_ent)   
        outputs.append((('E',E), ('A',A) ,('L',L)))

        outputs_set = set(outputs)
        #print(str(outputs_set - self.CROD_regression_set))
        self.assertEqual(outputs_set - self.CROD_regression_set, {(('E', 10000000.0), ('A', 1.0), ('L', 10.0))}, "CBAR values failed regression test.") 
        
        return 0


    def test_bar_stiffness_system(self):
        """
        System test starting with the following top level function:
        
        custom_checks._ExecCheckBarStiffness(ANSAPart, _ ) -> [CheckReport]
        """
        
        #Check failure part
        failure_part = base.GetPartFromName("CheckBarStiffness_error_elements")
        failure_entity = base.CollectEntities(constants.NASTRAN, failure_part, "__ELEMENTS__")
        
        nada = 'None'
        output = custom_checks._ExecCheckBarStiffness(failure_entity, nada) #second input is unused.
        report = output[0]
        
        #Making sure the only return is just the report object within a list.
        self.assertEqual(len(report.issues), 1, "The size of the return list is > 1. List contents: " + str([x for x in report.issues]))
        
        #Verify that the single issue that arose is accounted for.
        self.assertEqual(report.type, "CC Bar Stiffness: Bar elements with error prone stiffness")
        self.assertEqual(report.issues[0].status, "error")
        self.assertEqual(report.issues[0].type, "Error") 
        
        
        #Check ok part
        ok_part = base.GetPartFromName("CheckBarStiffness_ok_elements")
        ok_entity = base.CollectEntities(constants.NASTRAN, ok_part, "__ELEMENTS__")
        
        output2 = custom_checks._ExecCheckBarStiffness(ok_entity, nada) #second input is unused.
        report2 = output2[0]
        
        #Making sure the only return is just the report object within a list.
        self.assertEqual(len(report2.issues), 0, "The size of the return list is > 1. List contents: " + str([x for x in report2.issues]))

        #Verify that the single issue that arose is accounted for.
        self.assertEqual(report2.type, "CC Bar Stiffness: Bar elements with error prone stiffness")
        
        
class solid_check(unittest.TestCase):
    """
    Tests for the Check solid section of the custom_checks script.
    """        

    def setUp(self): 
        session.New("discard")
        utils.Merge(_TEST_RESOURCE + "/custom_checks.ansa")
        
        self.fails_group = base.GetPartFromName("CheckSolidPartElements_fail")
        self.fail_parts = base.CollectEntities(constants.NASTRAN, self.fails_group, "ANSAPART")
        self.fail_n_parts = len(self.fail_parts)
        
        self.pass_group = base.GetPartFromName("CheckSolidPartElements_ok")
        self.pass_parts = base.CollectEntities(constants.NASTRAN, self.pass_group, "ANSAPART")
                  
        return 0    
    
    
    def tearDown(self):
        return 0
        
        
    def test_solid_without_elements_regression(self):
        """
        Regression test for the following custom_checks function:
        
        custom_checks.solid_without_elements(ANSAPart) -> Bool
        """
        for x in self.pass_parts:
            self.assertEqual(custom_checks.solid_without_elements(x), False)
        
        for y in self.fail_parts:
            self.assertEqual(custom_checks.solid_without_elements(y), True)
    
    
    def test_solid_part_system(self):
        """
        System test starting with the following top level function:
        
        custom_checks._ExecCheckSolidPartElements(ANSAPart, _ ) -> [CheckReport]
        """

        nada = None #blank variable to pass to _exec function
        
        #            #
        #Pass section#
        #            #
        
        base.Or(self.pass_parts)
        output1 = custom_checks._ExecCheckSolidPartElements(self.pass_parts, nada)
        report1 = output1[0]          
        
        #Making sure the only return is just the report object within a list.
        self.assertEqual(len(report1.issues), 0, "There is a problem in the following file(s): " + str([x.issues.entities._name for x in report1.issues]))
        
        
        #            #
        #fail section#
        #            #
        
        base.Or(self.fail_parts)
        output2 = custom_checks._ExecCheckSolidPartElements(self.fail_parts, nada)
        report2 = output2[0]
        #Making sure the only return is just the report object within a list.
        self.assertEqual(len(report2.issues), self.fail_n_parts, "The size of the return list is different. List contents: " + str([x for x in report2.issues]))  
        
        part_name_regression = [part._name for part in self.fail_parts]
        
        part_in_issues = []
        for issue in report2.issues:
            part_in_issues += issue.entities
        
        part_names_in_issues = [part._name for part in part_in_issues]    
        
        set_names = set(part_names_in_issues)
        set_names_regression = set(part_name_regression)
        
        regression_difference = set_names_regression - set_names
        new_difference = set_names - set_names_regression
        
        print_error = determine_print_message(regression_difference, new_difference)
            
        self.assertEqual(set_names, set_names_regression, print_error)    
        
 
class material_check(unittest.TestCase):
    """
    Tests for the Check material section of the custom_checks script.
    """      

    def setUp(self): 
        session.New("discard")
        utils.Merge(_TEST_RESOURCE + "/custom_checks.ansa")
        
        self.warn_group = base.GetPartFromName("CheckMaterials_custom_id_warn")
        self.warn_parts = base.CollectEntities(constants.NASTRAN, self.warn_group, "ANSAPART")
        self.warn_n_parts = len(self.warn_parts)
        
        self.mismatch_group = base.GetPartFromName("CheckMaterials_matdb_fields_mismatch")
        self.mismatch_parts = base.CollectEntities(constants.NASTRAN, self.mismatch_group, "ANSAPART")
        self.mismatch_n_parts = len(self.mismatch_parts)
        
        self.ok_group = base.GetPartFromName("CheckMaterials_ok")
        self.ok_parts = base.CollectEntities(constants.NASTRAN, self.ok_group, "ANSAPART")
        
        self.fail_group = base.GetPartFromName("custom_id_beyond_range_fail")
        self.fail_parts = base.CollectEntities(constants.NASTRAN, self.fail_group, "ANSAPART")
        self.fail_n_parts = len(self.fail_parts)
        
        return 0    
 

    def test_material_exec_system(self):
        """
        System test starting with the following top level function:
        
        custom_checks._ExecCheckMaterials(ANSAPart, _ ) -> [CheckReport]
        """
        nada = None #blank variable to pass to _exec function
        
        
        #                    #
        #warn section#
        #                   #
        
        base.Or(self.warn_parts)
        output1 = custom_checks._ExecCheckMaterials(self.warn_parts, nada)
        report1 = output1[0]        
      
        part_set_names = pull_parts_from_exec_output(report1, "warning")
        
        part_set_names_regression = pull_parts_from_resources(self.warn_parts)
        
        group_names_minus_exec_names = part_set_names_regression - part_set_names
        exec_names_minus_group_names = part_set_names - part_set_names_regression
        
        print_error = determine_print_message(group_names_minus_exec_names, exec_names_minus_group_names)
        
        self.assertEqual(part_set_names, part_set_names_regression, print_error)
        
        
        #                           #
        #mismatch section#
        #                          #
        
        base.Or(self.mismatch_parts)
        output2 = custom_checks._ExecCheckMaterials(self.mismatch_parts, nada)
        report2 = output2[0]        
        #Making sure the only return is just the report object within a list.
        self.assertEqual(len(report2.issues), self.mismatch_n_parts, "The size of the return list is different. List contents: " + str([x for x in report2.issues]))
         
        part_set_names = pull_parts_from_exec_output(report2, "error")

        part_set_names_regression = pull_parts_from_resources(self.mismatch_parts)
        
        group_names_minus_exec_names = part_set_names_regression - part_set_names
        exec_names_minus_group_names = part_set_names - part_set_names_regression
        
        print_error = determine_print_message(group_names_minus_exec_names, exec_names_minus_group_names)
        
        self.assertEqual(part_set_names, part_set_names_regression, print_error)
        
        
        #                #
        #ok section#
        #                #
        
        base.Or(self.ok_parts)
        output3 = custom_checks._ExecCheckMaterials(self.ok_parts, nada)
        report3 = output3[0]
        
        #Making sure the only return is just the report object within a list.
        self.assertEqual(len(report3.issues), 0, "There is a problem in the following file(s): " + str([x.issues.entities._name for x in report3.issues])) 


        #                 #
        #fail section#
        #                #

        base.Or(self.fail_parts)
        output4 = custom_checks._ExecCheckMaterials(self.fail_parts, nada)
        report4 = output4[0]
        #Making sure the only return is just the report object within a list.
        self.assertEqual(len(report4.issues), self.fail_n_parts, "The size of the return list is different. List contents: " + str([x for x in report4.issues]))  
        
        part_set_names = pull_parts_from_exec_output(report4, "error")
        
        part_set_names_regression = pull_parts_from_resources(self.fail_parts)
        
        group_names_minus_exec_names = part_set_names_regression - part_set_names
        exec_names_minus_group_names = part_set_names - part_set_names_regression
        
        print_error = determine_print_message(group_names_minus_exec_names, exec_names_minus_group_names)
        
        self.assertEqual(part_set_names, part_set_names_regression, print_error)



class NoGeometry_check(unittest.TestCase):
    """
    Tests for the Check NoGeometry section of the custom_checks script.
    """  

    def setUp(self): 
        session.New("discard")
        utils.Merge(_TEST_RESOURCE + "/custom_checks.ansa")
        
        self.fail_group = base.GetPartFromName("CheckNoGeometry_fail")
        self.fail_parts = base.CollectEntities(constants.NASTRAN, self.fail_group, "ANSAPART")
        self.fail_n_parts = len(self.fail_parts)
        
        self.ok_group = base.GetPartFromName("CheckNoGeometry_ok")
        self.ok_parts = base.CollectEntities(constants.NASTRAN, self.ok_group, "ANSAPART")
        
        return 0
            

    def test_NoGeometry_exec_system(self):
        
        """
        System test starting with the following top level function:
        
        custom_checks._ExecCheckNoGeometry(ANSAPart, _ ) -> [CheckReport]
        """
        nada = None #blank variable to pass to _exec function
        
        #                 #
        #fail section#
        #                #
        
        base.Or(self.fail_parts)
        output1 = custom_checks._ExecCheckNoGeometry(self.fail_parts, nada)
        report1 = output1[0]        
       
        part_set_names = pull_parts_from_exec_output(report1, "error")
        
        part_set_names_regression = pull_parts_from_resources(self.fail_parts)
        
        group_names_minus_exec_names = part_set_names_regression - part_set_names
        exec_names_minus_group_names = part_set_names - part_set_names_regression
        
        print_error = determine_print_message(group_names_minus_exec_names, exec_names_minus_group_names)
        
        self.assertEqual(part_set_names, part_set_names_regression, print_error)


        #                    #
        #pass section#
        #                   #
        
        base.Or(self.ok_parts)
        output2 = custom_checks._ExecCheckNoGeometry(self.ok_parts, nada)
        report2 = output2[0]          
        
        #Making sure the only return is just the report object within a list.
        self.assertEqual(len(report2.issues), 0, "There is a problem in the following file(s): " + str([x.issues.entities._name for x in report2.issues])) 

 
 
class IntExt_check(unittest.TestCase):
    """
    Tests for the Check Interior/Exterior section of the custom_checks script.
    """  

    def setUp(self): 
        session.New("discard")
        utils.Merge(_TEST_RESOURCE + "/custom_checks.ansa")
        
        self.fail_group = base.GetPartFromName("CheckIsIntExt_error")
        self.fail_parts = base.CollectEntities(constants.NASTRAN, self.fail_group, "__CONNECTIONS__", True) 
        self.fail_n_parts = len(self.fail_parts)
        
        self.ok_group = base.GetPartFromName("CheckIsIntExt_ok")
        self.ok_parts = base.CollectEntities(constants.NASTRAN, self.ok_group, "__CONNECTIONS__", True)
        
        return 0
            

    def test_IntExt_exec_system(self):
        """
        System test starting with the following top level function:
        
        custom_checks._ExecCheckIsIntExt(ANSAPart, _ ) -> [CheckReport]
        """
        
        nada = None #blank variable to pass to _exec function
        
        #                 #
        #fail section#
        #                #
        
        base.Or(self.fail_parts)
        output1 = custom_checks._ExecCheckIsIntExt(self.fail_parts, nada)
        report1 = output1[0]        
       
        part_set_names = pull_parts_from_exec_output(report1, "error", 3323)
        
        part_set_names_regression = pull_parts_from_resources(self.fail_parts)
        
        group_names_minus_exec_names = part_set_names_regression - part_set_names
        exec_names_minus_group_names = part_set_names - part_set_names_regression
        
        print_error = determine_print_message(group_names_minus_exec_names, exec_names_minus_group_names)
        
        self.assertEqual(part_set_names, part_set_names_regression, print_error)


        #                    #
        #pass section#
        #                   #
        
        base.Or(self.ok_parts)
        output2 = custom_checks._ExecCheckIsIntExt(self.ok_parts, nada)
        report2 = output2[0]          
        
        #Making sure the only return is just the report object within a list.
        self.assertEqual(len(report2.issues), 0, "There is a problem in the following file(s): " + str([x.issues.entities._name for x in report2.issues]))        


class Realized_check(unittest.TestCase):
    """
    Tests for the Check Realized Part section of the custom_checks script.
    """  

    def setUp(self): 
        session.New("discard")
        utils.Merge(_TEST_RESOURCE + "/custom_checks.ansa")
        
        self.fail_group = base.GetPartFromName("CheckRealized_error")
        self.fail_parts = base.CollectEntities(constants.NASTRAN, self.fail_group, "__CONNECTIONS__", True) 
        self.fail_n_parts = len(self.fail_parts)
        
        self.ok_group = base.GetPartFromName("CheckRealized_ok")
        self.ok_parts = base.CollectEntities(constants.NASTRAN, self.ok_group, "__CONNECTIONS__", True)
        
        return 0
            

    def test_Realized_exec_system(self):
        """
        System test starting with the following top level function:
        
        custom_checks._ExecRealized(ANSAPart, _ ) -> [CheckReport]
        """
                
        nada = None #blank variable to pass to _exec function
        
        #                 #
        #fail section#
        #                #
        
        base.Or(self.fail_parts)
        output1 = custom_checks._ExecRealized(self.fail_parts, nada)
        report1 = output1[0]       
        
        part_set_names = pull_parts_from_exec_output(report1, "error", 3323)
        
        part_set_names_regression = pull_parts_from_resources(self.fail_parts)
        
        group_names_minus_exec_names = part_set_names_regression - part_set_names
        exec_names_minus_group_names = part_set_names - part_set_names_regression
        
        print_error = determine_print_message(group_names_minus_exec_names, exec_names_minus_group_names)
        
        self.assertEqual(part_set_names, part_set_names_regression, print_error)


        #                    #
        #pass section#
        #                   #
        
        base.Or(self.ok_parts)
        output2 = custom_checks._ExecRealized(self.ok_parts, nada)
        report2 = output2[0]          
        
        #Making sure the only return is just the report object within a list.
        self.assertEqual(len(report2.issues), 0, "There is a problem in the following file(s): " + str([x.issues.entities._name for x in report2.issues]))        
        
        
class Mass_Cross_check(unittest.TestCase):
    """
    Tests for the Check Mass Cross section of the custom_checks script.
    """  

    def setUp(self): 
        session.New("discard")
        utils.Merge(_TEST_RESOURCE + "/custom_checks.ansa")
        
        self.fail_group = base.GetPartFromName("CheckMass_error")
        self.fail_parts = base.CollectEntities(constants.NASTRAN, self.fail_group, "ANSAPART", True) 
        self.fail_n_parts = len(self.fail_parts)
        
        self.ok_group = base.GetPartFromName("CheckMass_ok")
        self.ok_parts = base.CollectEntities(constants.NASTRAN, self.ok_group, "ANSAPART", True)
        
        return 0
            

    def test_Mass_exec_system(self):
        """
        System test starting with the following top level function:
        
        custom_checks._ExecuteMass(ANSAPart, _ ) -> [CheckReport]
        """ 
               
        nada = None #blank variable to pass to _exec function
        
        #                 #
        #fail section#
        #                #
        
        base.Or(self.fail_parts)
        output1 = custom_checks._ExecuteMass(self.fail_parts, nada)
        report1 = output1[0]       
        
        part_set_names = pull_parts_from_exec_output(report1, "warning", 3288)
        
        part_set_names_regression = pull_parts_from_resources(self.fail_parts)
        
        group_names_minus_exec_names = part_set_names_regression - part_set_names
        exec_names_minus_group_names = part_set_names - part_set_names_regression
        
        print_error = determine_print_message(group_names_minus_exec_names, exec_names_minus_group_names)
        
        self.assertEqual(part_set_names, part_set_names_regression, print_error)


        #                    #
        #pass section#
        #                   #
        
        base.Or(self.ok_parts)
        output2 = custom_checks._ExecuteMass(self.ok_parts, nada)
        report2 = output2[0]          
        
        #Making sure the only return is just the report object within a list.
        self.assertEqual(len(report2.issues), 0, "There is a problem in the following file(s): " + str([x.issues.entities._name for x in report2.issues]))        
        


class shell_thickness_check(unittest.TestCase):
    """
    Tests for the Check Shell Thickness section of the custom_checks script.
    """  

    def setUp(self): 
        session.New("discard")
        utils.Merge(_TEST_RESOURCE + "/custom_checks.ansa")
        
        self.fail_group = base.GetPartFromName("CheckPshell_error")
        self.fail_parts = base.CollectEntities(constants.NASTRAN, self.fail_group, "ANSAPART", True) 
        self.fail_n_parts = len(self.fail_parts)
        
        self.ok_group = base.GetPartFromName("CheckPshell_ok")
        self.ok_parts = base.CollectEntities(constants.NASTRAN, self.ok_group, "ANSAPART", True)
        
        return 0
            

    def test_shell_thickness_exec_system(self):
        """
        System test starting with the following top level function:
        
        custom_checks._ExecutePshell(ANSAPart, _ ) -> [CheckReport]
        """ 
      
        nada = None #blank variable to pass to _exec function
        
        #                 #
        #fail section#
        #                #
        
        base.Or(self.fail_parts)
        output1 = custom_checks._ExecutePshell(self.fail_parts, nada)
        report1 = output1[0]       
        
        part_set_names = pull_parts_from_exec_output(report1, "error", 3288)
        
        part_set_names_regression = pull_parts_from_resources(self.fail_parts)
        
        group_names_minus_exec_names = part_set_names_regression - part_set_names
        exec_names_minus_group_names = part_set_names - part_set_names_regression
        
        print_error = determine_print_message(group_names_minus_exec_names, exec_names_minus_group_names)
        
        self.assertEqual(part_set_names, part_set_names_regression, print_error)


        #                    #
        #pass section#
        #                   #
        
        base.Or(self.ok_parts)
        output2 = custom_checks._ExecutePshell(self.ok_parts, nada)
        report2 = output2[0]          
        
        #Making sure the only return is just the report object within a list.
        self.assertEqual(len(report2.issues), 0, "There is a problem in the following file(s): " + str([x.issues.entities._name for x in report2.issues]))        



class Connectivity_Check(unittest.TestCase):

    """
    Tests for the Check Connectivity/Hierarchy section of the custom_checks script.
    """  

    def setUp(self): 
        session.New("discard")
        utils.Merge(_TEST_RESOURCE + "/custom_checks.ansa")
        
        self.fail_group = base.GetPartFromName("CheckConnectivity_error")
        self.fail_parts = base.CollectEntities(constants.NASTRAN, self.fail_group, "ANSAPART", True) 
        self.fail_n_parts = len(self.fail_parts)
        
        self.warn_group = base.GetPartFromName("CheckConnectivity_warning")
        self.warn_parts = base.CollectEntities(constants.NASTRAN, self.warn_group, "ANSAPART", True) 
        self.warn_n_parts = len(self.warn_parts)
        
        self.ok_group = base.GetPartFromName("CheckConnectivity_ok")
        self.ok_parts = base.CollectEntities(constants.NASTRAN, self.ok_group, "ANSAPART", True)
        
        return 0
            

    def test_connectivity_exec_system(self):
        """
        System test starting with the following top level function:
        
        custom_checks._ExecCheckConnectivity([ANSAPart], _ ) -> [CheckReport]
        """ 
          
        nada = None #blank variable to pass to _exec function
        
        #                 #
        #fail section#
        #                #
              
        for part in self.fail_parts:
            base.Or(part)
            output = custom_checks._ExecCheckConnectivity([part], nada)
            correct_status = "error"
            self.assertTrue(output[0].status == correct_status, "Part " + str(output[0].description) + " Has the status " + str(output[0].status) + " which is not " + correct_status + ".") 


        #                        #
        #Warning section#
        #                        #

        for part in self.warn_parts:
            base.Or(part)
            output = custom_checks._ExecCheckConnectivity([part], nada)
            correct_status = "warning"
            self.assertTrue(output[0].status == correct_status, "Part " + str(output[0].description) + " Has the status " + str(output[0].status) + " which is not " + correct_status + ".") 



        #                    #
        #pass section#
        #                   #
        for part in self.ok_parts:       
            base.Or(part)
            output2 = custom_checks._ExecCheckConnectivity(part, nada)
            report2 = output2[0]
            self.assertEqual(len(report2.issues), 0, "There is a problem in the following file(s): " + part._name)        
        
               

if __name__ == "__main__":
    sys.argv=[""]
    
    unittest.main(exit=False) 