"""
RISC-V CPU Core Implementation
Main simulation engine for RV32I processor
"""

import sys
import os
from typing import Dict, List, Optional, Tuple

# Add the parent directory to the path to handle imports properly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.instructions import RV32I_Instructions, InstructionType
except ImportError:
    # Try relative import if absolute import fails
    from ..utils.instructions import RV32I_Instructions, InstructionType

class RISCVCore:
    """RISC-V RV32I CPU Core Simulator"""
    
    def __init__(self, memory_size: int = 1024 * 1024):  # 1MB default
        # Initialize components
        self.instructions = RV32I_Instructions()
        
        # CPU State
        self.registers = [0] * 32  # 32 general-purpose registers
        self.pc = 0  # Program counter
        self.memory = bytearray(memory_size)
        self.memory_size = memory_size
        
        # Pipeline state
        self.pipeline = {
            'IF': None,  # Instruction Fetch
            'ID': None,  # Instruction Decode
            'EX': None,  # Execute
            'MEM': None, # Memory Access
            'WB': None   # Write Back
        }
        
        # Performance counters
        self.cycle_count = 0
        self.instruction_count = 0
        self.stall_count = 0
        self.branch_count = 0
        self.branch_taken = 0
        
        # Control signals
        self.halt = False
        self.debug_mode = False
        
        # Execution trace
        self.trace = []
        
        # Cache simulation (simple direct-mapped)
        self.icache = {'size': 1024, 'line_size': 32, 'data': {}, 'hits': 0, 'misses': 0}
        self.dcache = {'size': 1024, 'line_size': 32, 'data': {}, 'hits': 0, 'misses': 0}
    
    def reset(self):
        """Reset CPU state"""
        self.registers = [0] * 32
        self.pc = 0
        self.cycle_count = 0
        self.instruction_count = 0
        self.stall_count = 0
        self.branch_count = 0
        self.branch_taken = 0
        self.halt = False
        self.trace = []
        
        # Clear pipeline
        for stage in self.pipeline:
            self.pipeline[stage] = None
    
    def load_program(self, program: List[int], start_address: int = 0):
        """Load program into memory"""
        for i, instruction in enumerate(program):
            addr = start_address + (i * 4)
            if addr + 3 >= self.memory_size:
                raise ValueError("Program too large for memory")
            
            # Store instruction as little-endian
            self.memory[addr] = instruction & 0xFF
            self.memory[addr + 1] = (instruction >> 8) & 0xFF
            self.memory[addr + 2] = (instruction >> 16) & 0xFF
            self.memory[addr + 3] = (instruction >> 24) & 0xFF
        
        self.pc = start_address
    
    def fetch_instruction(self, address: int) -> int:
        """Fetch 32-bit instruction from memory with cache simulation"""
        if address + 3 >= self.memory_size:
            raise ValueError(f"Invalid memory address: {address}")
        
        # Simple cache simulation
        cache_line = address // self.icache['line_size']
        if cache_line in self.icache['data']:
            self.icache['hits'] += 1
        else:
            self.icache['misses'] += 1
            self.icache['data'][cache_line] = True
        
        # Fetch instruction (little-endian)
        instruction = (self.memory[address] |
                      (self.memory[address + 1] << 8) |
                      (self.memory[address + 2] << 16) |
                      (self.memory[address + 3] << 24))
        
        return instruction
    
    def read_memory(self, address: int, size: int) -> int:
        """Read data from memory with size in bytes"""
        if address + size - 1 >= self.memory_size:
            raise ValueError(f"Invalid memory address: {address}")
        
        # Cache simulation for data access
        cache_line = address // self.dcache['line_size']
        if cache_line in self.dcache['data']:
            self.dcache['hits'] += 1
        else:
            self.dcache['misses'] += 1
            self.dcache['data'][cache_line] = True
        
        value = 0
        for i in range(size):
            value |= self.memory[address + i] << (i * 8)
        
        return value
    
    def write_memory(self, address: int, value: int, size: int):
        """Write data to memory with size in bytes"""
        if address + size - 1 >= self.memory_size:
            raise ValueError(f"Invalid memory address: {address}")
        
        # Cache simulation for data access
        cache_line = address // self.dcache['line_size']
        self.dcache['data'][cache_line] = True
        
        for i in range(size):
            self.memory[address + i] = (value >> (i * 8)) & 0xFF
    
    def read_register(self, reg_num: int) -> int:
        """Read register value (x0 always returns 0)"""
        if reg_num == 0:
            return 0
        if 0 <= reg_num < 32:
            return self.registers[reg_num]
        raise ValueError(f"Invalid register number: {reg_num}")
    
    def write_register(self, reg_num: int, value: int):
        """Write register value (x0 writes are ignored)"""
        if reg_num == 0:
            return  # x0 is hardwired to zero
        if 0 <= reg_num < 32:
            self.registers[reg_num] = value & 0xFFFFFFFF
        else:
            raise ValueError(f"Invalid register number: {reg_num}")
    
    def execute_instruction(self, instruction: int) -> bool:
        """Execute a single instruction. Returns True if execution should continue."""
        decoded = self.instructions.decode_instruction(instruction)
        opcode = decoded['opcode']
        
        # Add to execution trace
        if self.debug_mode:
            self.trace.append({
                'pc': self.pc,
                'instruction': instruction,
                'decoded': decoded,
                'registers_before': self.registers.copy()
            })
        
        # Handle NOP or invalid instructions
        if instruction == 0x00000013:  # NOP (addi x0, x0, 0)
            self.pc += 4
            return True
        elif instruction == 0x00000000:  # All zeros - treat as halt
            return False
        
        # Instruction execution logic
        if opcode == 0b0110011:  # R-type ALU operations
            return self._execute_r_type(decoded)
        elif opcode == 0b0010011:  # I-type ALU operations
            return self._execute_i_type_alu(decoded)
        elif opcode == 0b0000011:  # Load instructions
            return self._execute_load(decoded)
        elif opcode == 0b0100011:  # Store instructions
            return self._execute_store(decoded)
        elif opcode == 0b1100011:  # Branch instructions
            return self._execute_branch(decoded)
        elif opcode == 0b1101111:  # JAL
            return self._execute_jal(decoded)
        elif opcode == 0b1100111:  # JALR
            return self._execute_jalr(decoded)
        elif opcode == 0b0110111:  # LUI
            return self._execute_lui(decoded)
        elif opcode == 0b0010111:  # AUIPC
            return self._execute_auipc(decoded)
        else:
            print(f"Warning: Unsupported opcode: {opcode:07b} (0x{instruction:08x}) at PC {self.pc:08x}")
            # Skip unsupported instruction
            self.pc += 4
            return True
    
    def _execute_r_type(self, decoded: Dict) -> bool:
        """Execute R-type instructions"""
        rs1_val = self.read_register(decoded['rs1'])
        rs2_val = self.read_register(decoded['rs2'])
        funct3 = decoded['funct3']
        funct7 = decoded['funct7']
        
        result = 0
        
        if funct3 == 0b000:  # ADD/SUB
            if funct7 == 0b0000000:  # ADD
                result = (rs1_val + rs2_val) & 0xFFFFFFFF
            elif funct7 == 0b0100000:  # SUB
                result = (rs1_val - rs2_val) & 0xFFFFFFFF
        elif funct3 == 0b001:  # SLL
            result = (rs1_val << (rs2_val & 0x1F)) & 0xFFFFFFFF
        elif funct3 == 0b010:  # SLT
            result = 1 if self._signed(rs1_val) < self._signed(rs2_val) else 0
        elif funct3 == 0b011:  # SLTU
            result = 1 if rs1_val < rs2_val else 0
        elif funct3 == 0b100:  # XOR
            result = rs1_val ^ rs2_val
        elif funct3 == 0b101:  # SRL/SRA
            shift_amount = rs2_val & 0x1F
            if funct7 == 0b0000000:  # SRL
                result = rs1_val >> shift_amount
            elif funct7 == 0b0100000:  # SRA
                result = self._signed(rs1_val) >> shift_amount
                result = result & 0xFFFFFFFF
        elif funct3 == 0b110:  # OR
            result = rs1_val | rs2_val
        elif funct3 == 0b111:  # AND
            result = rs1_val & rs2_val
        
        self.write_register(decoded['rd'], result)
        self.pc += 4
        return True
    
    def _execute_i_type_alu(self, decoded: Dict) -> bool:
        """Execute I-type ALU instructions"""
        rs1_val = self.read_register(decoded['rs1'])
        imm = self.instructions.sign_extend((decoded['raw'] >> 20) & 0xFFF, 12)
        funct3 = decoded['funct3']
        
        result = 0
        
        if funct3 == 0b000:  # ADDI
            result = (rs1_val + imm) & 0xFFFFFFFF
        elif funct3 == 0b010:  # SLTI
            result = 1 if self._signed(rs1_val) < imm else 0
        elif funct3 == 0b011:  # SLTIU
            result = 1 if rs1_val < (imm & 0xFFFFFFFF) else 0
        elif funct3 == 0b100:  # XORI
            result = rs1_val ^ imm
        elif funct3 == 0b110:  # ORI
            result = rs1_val | imm
        elif funct3 == 0b111:  # ANDI
            result = rs1_val & imm
        elif funct3 == 0b001:  # SLLI
            shamt = imm & 0x1F  # Only lower 5 bits for shift amount
            result = (rs1_val << shamt) & 0xFFFFFFFF
        elif funct3 == 0b101:  # SRLI/SRAI
            shamt = imm & 0x1F  # Only lower 5 bits for shift amount
            funct7 = (imm >> 5) & 0x7F
            if funct7 == 0b0000000:  # SRLI
                result = rs1_val >> shamt
            elif funct7 == 0b0100000:  # SRAI
                result = self._signed(rs1_val) >> shamt
                result = result & 0xFFFFFFFF
        
        self.write_register(decoded['rd'], result)
        self.pc += 4
        return True
    
    def _execute_load(self, decoded: Dict) -> bool:
        """Execute load instructions"""
        rs1_val = self.read_register(decoded['rs1'])
        imm = self.instructions.sign_extend((decoded['raw'] >> 20) & 0xFFF, 12)
        address = (rs1_val + imm) & 0xFFFFFFFF
        funct3 = decoded['funct3']
        
        if funct3 == 0b000:  # LB
            value = self.read_memory(address, 1)
            value = self.instructions.sign_extend(value, 8)
        elif funct3 == 0b001:  # LH
            value = self.read_memory(address, 2)
            value = self.instructions.sign_extend(value, 16)
        elif funct3 == 0b010:  # LW
            value = self.read_memory(address, 4)
        elif funct3 == 0b100:  # LBU
            value = self.read_memory(address, 1)
        elif funct3 == 0b101:  # LHU
            value = self.read_memory(address, 2)
        
        self.write_register(decoded['rd'], value)
        self.pc += 4
        return True
    
    def _execute_store(self, decoded: Dict) -> bool:
        """Execute store instructions"""
        rs1_val = self.read_register(decoded['rs1'])
        rs2_val = self.read_register(decoded['rs2'])
        
        # Extract immediate for S-type
        imm_11_5 = (decoded['raw'] >> 25) & 0x7F
        imm_4_0 = (decoded['raw'] >> 7) & 0x1F
        imm = (imm_11_5 << 5) | imm_4_0
        imm = self.instructions.sign_extend(imm, 12)
        
        address = (rs1_val + imm) & 0xFFFFFFFF
        funct3 = decoded['funct3']
        
        if funct3 == 0b000:  # SB
            self.write_memory(address, rs2_val, 1)
        elif funct3 == 0b001:  # SH
            self.write_memory(address, rs2_val, 2)
        elif funct3 == 0b010:  # SW
            self.write_memory(address, rs2_val, 4)
        
        self.pc += 4
        return True
    
    def _execute_branch(self, decoded: Dict) -> bool:
        """Execute branch instructions"""
        rs1_val = self.read_register(decoded['rs1'])
        rs2_val = self.read_register(decoded['rs2'])
        funct3 = decoded['funct3']
        
        # Extract immediate for B-type
        imm_12 = (decoded['raw'] >> 31) & 0x1
        imm_10_5 = (decoded['raw'] >> 25) & 0x3F
        imm_4_1 = (decoded['raw'] >> 8) & 0xF
        imm_11 = (decoded['raw'] >> 7) & 0x1
        
        imm = (imm_12 << 12) | (imm_11 << 11) | (imm_10_5 << 5) | (imm_4_1 << 1)
        imm = self.instructions.sign_extend(imm, 13)
        
        self.branch_count += 1
        branch_taken = False
        
        if funct3 == 0b000:  # BEQ
            branch_taken = rs1_val == rs2_val
        elif funct3 == 0b001:  # BNE
            branch_taken = rs1_val != rs2_val
        elif funct3 == 0b100:  # BLT
            branch_taken = self._signed(rs1_val) < self._signed(rs2_val)
        elif funct3 == 0b101:  # BGE
            branch_taken = self._signed(rs1_val) >= self._signed(rs2_val)
        elif funct3 == 0b110:  # BLTU
            branch_taken = rs1_val < rs2_val
        elif funct3 == 0b111:  # BGEU
            branch_taken = rs1_val >= rs2_val
        
        if branch_taken:
            self.pc = (self.pc + imm) & 0xFFFFFFFF
            self.branch_taken += 1
        else:
            self.pc += 4
        
        return True
    
    def _execute_jal(self, decoded: Dict) -> bool:
        """Execute JAL instruction"""
        # Extract immediate for J-type
        imm_20 = (decoded['raw'] >> 31) & 0x1
        imm_10_1 = (decoded['raw'] >> 21) & 0x3FF
        imm_11 = (decoded['raw'] >> 20) & 0x1
        imm_19_12 = (decoded['raw'] >> 12) & 0xFF
        
        imm = (imm_20 << 20) | (imm_19_12 << 12) | (imm_11 << 11) | (imm_10_1 << 1)
        imm = self.instructions.sign_extend(imm, 21)
        
        # Save return address
        self.write_register(decoded['rd'], self.pc + 4)
        
        # Jump
        self.pc = (self.pc + imm) & 0xFFFFFFFF
        return True
    
    def _execute_jalr(self, decoded: Dict) -> bool:
        """Execute JALR instruction"""
        rs1_val = self.read_register(decoded['rs1'])
        imm = self.instructions.sign_extend((decoded['raw'] >> 20) & 0xFFF, 12)
        
        # Save return address
        self.write_register(decoded['rd'], self.pc + 4)
        
        # Jump to rs1 + imm (with bit 0 cleared)
        self.pc = (rs1_val + imm) & 0xFFFFFFFE
        return True
    
    def _execute_lui(self, decoded: Dict) -> bool:
        """Execute LUI instruction"""
        imm = (decoded['raw'] >> 12) & 0xFFFFF
        result = imm << 12
        self.write_register(decoded['rd'], result)
        self.pc += 4
        return True
    
    def _execute_auipc(self, decoded: Dict) -> bool:
        """Execute AUIPC instruction"""
        imm = (decoded['raw'] >> 12) & 0xFFFFF
        result = (self.pc + (imm << 12)) & 0xFFFFFFFF
        self.write_register(decoded['rd'], result)
        self.pc += 4
        return True
    
    def _signed(self, value: int) -> int:
        """Convert 32-bit unsigned to signed"""
        if value & 0x80000000:
            return value - 0x100000000
        return value
    
    def run(self, max_cycles: int = 100000) -> Dict:
        """Run the CPU simulation"""
        while not self.halt and self.cycle_count < max_cycles:
            try:
                # Fetch instruction
                instruction = self.fetch_instruction(self.pc)
                
                # Execute instruction
                if not self.execute_instruction(instruction):
                    self.halt = True
                    break
                
                self.instruction_count += 1
                self.cycle_count += 1
                
                # Simple halt condition (infinite loop detection)
                if instruction == 0x00000013:  # NOP (addi x0, x0, 0)
                    break
                    
            except Exception as e:
                print(f"Execution error at PC {self.pc:08x}: {e}")
                break
        
        return self.get_stats()
    
    def get_stats(self) -> Dict:
        """Get performance statistics"""
        cpi = self.cycle_count / self.instruction_count if self.instruction_count > 0 else 0
        branch_prediction_accuracy = self.branch_taken / self.branch_count if self.branch_count > 0 else 0
        
        icache_hit_rate = self.icache['hits'] / (self.icache['hits'] + self.icache['misses']) if (self.icache['hits'] + self.icache['misses']) > 0 else 0
        dcache_hit_rate = self.dcache['hits'] / (self.dcache['hits'] + self.dcache['misses']) if (self.dcache['hits'] + self.dcache['misses']) > 0 else 0
        
        return {
            'cycles': self.cycle_count,
            'instructions': self.instruction_count,
            'cpi': cpi,
            'branches': self.branch_count,
            'branches_taken': self.branch_taken,
            'branch_accuracy': branch_prediction_accuracy,
            'icache_hit_rate': icache_hit_rate,
            'dcache_hit_rate': dcache_hit_rate,
            'pc': self.pc
        }
    
    def print_state(self):
        """Print current CPU state"""
        print(f"PC: 0x{self.pc:08x}")
        print("Registers:")
        for i in range(0, 32, 4):
            print(f"  x{i:2d}-x{i+3:2d}: ", end="")
            for j in range(4):
                if i + j < 32:
                    print(f"0x{self.registers[i+j]:08x} ", end="")
            print()
        
        stats = self.get_stats()
        print(f"\nStats: {stats['instructions']} instructions, {stats['cycles']} cycles, CPI: {stats['cpi']:.2f}")
        print(f"Cache hit rates - I$: {stats['icache_hit_rate']:.1%}, D$: {stats['dcache_hit_rate']:.1%}")
