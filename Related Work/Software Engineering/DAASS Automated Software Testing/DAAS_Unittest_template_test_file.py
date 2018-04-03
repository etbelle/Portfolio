"""
This is a template for creating a test case.
Each section of this template is annotated and explained.
For further information, refer to the Quick Start Guide or the DAASS Software Testing Documentation.

To run from test loader/runner:
Modify the file name to have "test_" at the begining. This is required for the loader to be able to discover it.

Note about annotations:
A comment containing #~ means that it requires the developers input.
"""

import unittest       #Required for all Unittest testing. https://docs.python.org/3.3/library/unittest.html
import os             #Primarily used for file and path manipulation. https://docs.python.org/3.3/library/os.html
import sys            #A module that allows interaction with the interpreter. Such as data structure sizes and module data. https://docs.python.org/2/library/sys.html
import shutil         #A useful extension to the os library for common, but more advanced, opperations. https://docs.python.org/3.3/library/shutil.html
import pickle         #A module that allows for serialization and de-serialization of object structures. Primarily used by ANSA for DM related tasks. https://docs.python.org/3.3/library/pickle.html
import zipfile        #This module allows for the manipulation of .zip files. All testing resources are zipped initially and need to be unziped to be used. https://docs.python.org/3.3/library/zipfile.html

"""
This first section is to get a few different file/directory paths so that the test can pull from the required areas.
Since the file structure for daass, the testing suite, and the testing resources all follow the same hiarchy, we can use
that to manipulate our location within all three directories really easily.
"""
original_path = os.path.dirname(os.path.abspath(__file__))

#Current path to script are testing.
current_path = original_path.replace("test_suite/","")

#Allows script to see full import path
sys.path.append(current_path)

from daass.___.___ import ____   #~Import the script you would like to test from its location.
from ansa import session, ___  #~Deppending on the task, import one, or many, ANSA libraries. Refer to Function list in the ANSA script edit window.

# Directory to models for system tests
PATH_TEST_RESOURCE = pickle.loads(session.BetaGetVariable("PATH_TEST_RESOURCE")) 
_TEST_RESOURCE = PATH_TEST_RESOURCE + "/____"  #~This is the path to the testing resources you would like to use to test with.

# Using scratch to work on temp file paths
PATH_SCRATCH_TESTING = pickle.loads(session.BetaGetVariable("PATH_SCRATCH")) + "/testing_temp" #This is an extra sandbox location if you need to do file manipulation outside of the test resources. 
os.makedirs(PATH_SCRATCH_TESTING, exist_ok=True)


"""
The setupUpModule and tearDownModule functions are a way for the unittest package 
to prepare a test case.

These functions are only used when this script is run as a standalone testcase. 
This is because the discover function within the Unittest loader does not recognize nor
pull them into the system test.
"""
def setUpModule():
    """
    In order to run the tests, we need to unzip the related material in the testing resource repository.
    """
    dm_zip = zipfile.ZipFile(_TEST_RESOURCE + "/____.zip", "r")  #~the name of the zip file you need to extract.
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
            
        

class function_or_system_tests(unittest.TestCase): #The class name does not matter.
    """
    Classes within the Unittest framework lend themselves to be easily used for either function related, or system level test cases.
    This allows for the individual unit tests be defined within their respective class functions. 
    """
    
    """
    Much like the setupUpModule and tearDownModule functions, setUpClass and tearDownClass work like constructors and destructors for the testing class.
    Use these functions if there is class level setup.
    """
    @classmethod #Required for the cls variable
    def setUpClass(cls): #Name matters, do not change
        return 0
    
    @classmethod #required for the cls variable
    def tearDownClass(cls): #Name matters, do not change
        return 0
    
    """
    Unlike the setUpClass and tearDownClass functions, setUp and tearDown run at the begining and end of every test. 
    These are best used for small, but necissary opperations that bring precision to tests.
    """
    def setUp(self): #Name matters, do not change
        session.New("discard") #We create a new ANSA session at the begining of each test to make sure there are no confounding variables influencing the test outcome.
        

    def tearDown(self): #Name matters, do not change
        return 0

    """
    Unit test functions are what drive the Unittest framework.
    Once an assert statement has been ran within a function and it returns a failure, the test function will terminate.
    This means that if you have multiple assert statements within a single function, if your first test fails, you won't see the outcome of your second assert.
    """    
    def test_(self): #Name matters, "test_" must be in front of developer defined function name. 
        self.assert___(x) #~Refer to the Unittest documentation for types of assert statements.
        return 0
     

if __name__ == "__main__":
    sys.argv=[""]
    
    unittest.main(exit=False) #We use exit=False to stop Unittest from closing our ANSA session once it is done running.