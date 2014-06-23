'''
Created on Jun 20, 2014

@author: Gregory
'''
from nose import with_setup
from UnitTesting import BlackBox
import unittest



class UnitTestClass(unittest.TestCase):
    
    def my_setup_function(self):
        print('start')
    
    def my_teardown_function(self):
        print('finsished')
    
    @with_setup(my_setup_function, my_teardown_function)
    def test_level_troll(self):
        troll_object = BlackBox.leveltroll()
        troll_object.timezone_string = "central"
        assert troll_object.set_timezone()
        
    def test_Arb(self):
        assert 'a' == 'a'
        
    def test_arb2(self):
        assert 10 > 2
        
        
class UnitTestClass2(unittest.TestCase):
    
    def test_Arb3(self):
        assert 10 + 2 == 12
    


