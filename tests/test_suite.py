"""
Test suite for RISC-V CPU Simulator
Comprehensive testing of all components
"""

import unittest
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from cpu.core import RISCVCore
from assembler.parser import AssemblyParser
from utils.instructions import RV32I_Instructions

class TestRISCVInstructions(unittest.TestCase):
    """Test RISC-V instruction encoding and decoding"""
    
    def setUp(self):
        self.instructions = RV32I_Instructions()
    
    def test_register_mapping(self):
        """Test register name to number mapping"""
        self.assertEqual(self.instructions.get_register_number('x0'), 0)
        self.assertEqual(self.instructions.get_register_number('zero'), 0)
        self.assertEqual(self.instructions.get_register_number('ra'), 1)
        self.assertEqual(self.instructions.get_register_number('sp'), 2)
        self.assertEqual(self.instructions.get_register_number('a0'), 10)
    
    def test_r_type_encoding(self):
        """Test R-type instruction encoding"""
        # ADD x1, x2, x3
        result = self.instructions.encode_r_type(0b0000000, 3, 2, 0b000, 1, 0b0110011)
        expected = 0b00000000001100010000000010110011
        self.assertEqual(result, expected)
    
    def test_i_type_encoding(self):
        """Test I-type instruction encoding"""
        # ADDI x1, x2, 100
        result = self.instructions.encode_i_type(100, 2, 0b000, 1, 0b0010011)
        expected = 0b00000110010000010000000010010011
        self.assertEqual(result, expected)
    
    def test_sign_extend(self):
        """Test sign extension"""
        # Positive number
        self.assertEqual(self.instructions.sign_extend(0x7FF, 12), 0x7FF)
        # Negative number
        self.assertEqual(self.instructions.sign_extend(0x800, 12), -2048)

class TestRISCVCore(unittest.TestCase):
    """Test RISC-V CPU core functionality"""
    
    def setUp(self):
        self.cpu = RISCVCore()
    
    def test_register_operations(self):
        """Test register read/write operations"""
        # Test normal register
        self.cpu.write_register(1, 0x12345678)
        self.assertEqual(self.cpu.read_register(1), 0x12345678)
        
        # Test x0 is always zero
        self.cpu.write_register(0, 0x12345678)
        self.assertEqual(self.cpu.read_register(0), 0)
    
    def test_memory_operations(self):
        """Test memory read/write operations"""
        # Write and read word
        self.cpu.write_memory(0x1000, 0x12345678, 4)
        result = self.cpu.read_memory(0x1000, 4)
        self.assertEqual(result, 0x12345678)
        
        # Write and read byte
        self.cpu.write_memory(0x2000, 0xAB, 1)
        result = self.cpu.read_memory(0x2000, 1)
        self.assertEqual(result, 0xAB)
    
    def test_program_loading(self):
        """Test program loading into memory"""
        program = [0x00100093, 0x00200113]  # addi x1, x0, 1; addi x2, x0, 2
        self.cpu.load_program(program)
        
        # Check program is loaded correctly
        instr1 = self.cpu.fetch_instruction(0)
        instr2 = self.cpu.fetch_instruction(4)
        self.assertEqual(instr1, 0x00100093)
        self.assertEqual(instr2, 0x00200113)
    
    def test_add_instruction(self):
        """Test ADD instruction execution"""
        self.cpu.reset()
        self.cpu.write_register(2, 10)
        self.cpu.write_register(3, 20)
        
        # ADD x1, x2, x3 (encoded: 0x003100b3)
        instruction = 0x003100b3
        self.cpu.execute_instruction(instruction)
        
        # Check result
        self.assertEqual(self.cpu.read_register(1), 30)
        self.assertEqual(self.cpu.pc, 4)
    
    def test_addi_instruction(self):
        """Test ADDI instruction execution"""
        self.cpu.reset()
        self.cpu.write_register(2, 10)
        
        # ADDI x1, x2, 100 (encoded: 0x06410093)
        instruction = 0x06410093
        self.cpu.execute_instruction(instruction)
        
        # Check result
        self.assertEqual(self.cpu.read_register(1), 110)
        self.assertEqual(self.cpu.pc, 4)

class TestAssemblyParser(unittest.TestCase):
    """Test assembly parser functionality"""
    
    def setUp(self):
        self.parser = AssemblyParser()
    
    def test_simple_instruction_parsing(self):
        """Test parsing of simple instructions"""
        result = self.parser.parse_line("addi x1, x2, 100")
        expected = {
            'instruction': 'addi',
            'args': ['x1', 'x2', '100'],
            'address': 0
        }
        self.assertEqual(result, expected)
    
    def test_label_parsing(self):
        """Test label parsing"""
        result = self.parser.parse_line("main: addi x1, x0, 1")
        self.assertIn('main', self.parser.labels)
        self.assertEqual(self.parser.labels['main'], 0)
    
    def test_comment_removal(self):
        """Test comment removal"""
        result = self.parser.parse_line("addi x1, x0, 1  # This is a comment")
        expected = {
            'instruction': 'addi',
            'args': ['x1', 'x0', '1'],
            'address': 0
        }
        self.assertEqual(result, expected)
    
    def test_pseudo_instruction_expansion(self):
        """Test pseudo-instruction expansion"""
        # Test NOP expansion
        code = self.parser.assemble_instruction('nop', [])
        expected = self.parser.assemble_instruction('addi', ['x0', 'x0', '0'])
        self.assertEqual(code, expected)
    
    def test_simple_program_assembly(self):
        """Test assembling a simple program"""
        program = """
        main:
            addi x1, x0, 10
            addi x2, x0, 20
            add x3, x1, x2
        """
        
        machine_code = self.parser.assemble(program)
        self.assertEqual(len(machine_code), 3)
        
        # Verify first instruction (addi x1, x0, 10)
        expected_first = self.parser.instructions.encode_i_type(10, 0, 0b000, 1, 0b0010011)
        self.assertEqual(machine_code[0], expected_first)

class TestIntegration(unittest.TestCase):
    """Integration tests for complete simulation"""
    
    def setUp(self):
        self.cpu = RISCVCore()
        self.parser = AssemblyParser()
    
    def test_fibonacci_program(self):
        """Test Fibonacci program execution"""
        fibonacci_program = """
        main:
            addi x1, x0, 0      # x1 = 0 (first number)
            addi x2, x0, 1      # x2 = 1 (second number)
            addi x3, x0, 5      # x3 = 5 (counter)
            addi x4, x0, 0      # x4 = 0 (index)
        
        loop:
            beq x4, x3, end     # if index == counter, exit
            add x5, x1, x2      # x5 = x1 + x2
            addi x1, x2, 0      # x1 = x2
            addi x2, x5, 0      # x2 = x5
            addi x4, x4, 1      # index++
            jal x0, loop        # jump to loop
        
        end:
            addi x0, x0, 0      # nop (infinite loop)
            jal x0, end
        """
        
        # Assemble and run
        machine_code = self.parser.assemble(fibonacci_program)
        self.cpu.load_program(machine_code)
        
        # Run with limited cycles to prevent infinite loop
        stats = self.cpu.run(max_cycles=1000)
        
        # Check that we executed some instructions
        self.assertGreater(stats['instructions'], 0)
        self.assertGreater(stats['cycles'], 0)
    
    def test_arithmetic_operations(self):
        """Test various arithmetic operations"""
        program = """
        main:
            addi x1, x0, 15     # x1 = 15
            addi x2, x0, 10     # x2 = 10
            add x3, x1, x2      # x3 = 25
            sub x4, x1, x2      # x4 = 5
            slli x5, x1, 2      # x5 = 60 (15 << 2)
            and x6, x1, x2      # x6 = 10 (15 & 10)
            or x7, x1, x2       # x7 = 15 (15 | 10)
        """
        
        machine_code = self.parser.assemble(program)
        self.cpu.load_program(machine_code)
        stats = self.cpu.run()
        
        # Check results
        self.assertEqual(self.cpu.read_register(1), 15)
        self.assertEqual(self.cpu.read_register(2), 10)
        self.assertEqual(self.cpu.read_register(3), 25)
        self.assertEqual(self.cpu.read_register(4), 5)
        self.assertEqual(self.cpu.read_register(5), 60)
        self.assertEqual(self.cpu.read_register(6), 10)
        self.assertEqual(self.cpu.read_register(7), 15)

def run_all_tests():
    """Run all test suites"""
    print("Running RISC-V Simulator Test Suite")
    print("=" * 50)
    
    # Create test suite using the recommended method
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(loader.loadTestsFromTestCase(TestRISCVInstructions))
    test_suite.addTest(loader.loadTestsFromTestCase(TestRISCVCore))
    test_suite.addTest(loader.loadTestsFromTestCase(TestAssemblyParser))
    test_suite.addTest(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
