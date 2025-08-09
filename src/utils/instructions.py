"""
RISC-V RV32I Instruction Set Architecture Implementation
Comprehensive instruction definitions and encoding utilities
"""

from enum import Enum
from typing import Dict, Tuple, List
import struct

class InstructionType(Enum):
    R_TYPE = "R"  # Register-register operations
    I_TYPE = "I"  # Immediate operations
    S_TYPE = "S"  # Store operations
    B_TYPE = "B"  # Branch operations
    U_TYPE = "U"  # Upper immediate operations
    J_TYPE = "J"  # Jump operations

class Opcode(Enum):
    # R-type instructions
    ADD_SUB = 0b0110011
    SLL = 0b0110011
    SLT = 0b0110011
    SLTU = 0b0110011
    XOR = 0b0110011
    SRL_SRA = 0b0110011
    OR = 0b0110011
    AND = 0b0110011
    
    # I-type instructions
    ADDI = 0b0010011
    SLTI = 0b0010011
    SLTIU = 0b0010011
    XORI = 0b0010011
    ORI = 0b0010011
    ANDI = 0b0010011
    SLLI = 0b0010011
    SRLI_SRAI = 0b0010011
    
    # Load instructions
    LB = 0b0000011
    LH = 0b0000011
    LW = 0b0000011
    LBU = 0b0000011
    LHU = 0b0000011
    
    # Store instructions
    SB = 0b0100011
    SH = 0b0100011
    SW = 0b0100011
    
    # Branch instructions
    BEQ = 0b1100011
    BNE = 0b1100011
    BLT = 0b1100011
    BGE = 0b1100011
    BLTU = 0b1100011
    BGEU = 0b1100011
    
    # Jump instructions
    JAL = 0b1101111
    JALR = 0b1100111
    
    # Upper immediate
    LUI = 0b0110111
    AUIPC = 0b0010111
    
    # System instructions
    ECALL = 0b1110011
    EBREAK = 0b1110011

class RV32I_Instructions:
    """Complete RISC-V RV32I instruction set implementation"""
    
    def __init__(self):
        self.instructions = {
            # R-type instructions
            'add': {
                'type': InstructionType.R_TYPE,
                'opcode': 0b0110011,
                'funct3': 0b000,
                'funct7': 0b0000000,
                'description': 'Add registers'
            },
            'sub': {
                'type': InstructionType.R_TYPE,
                'opcode': 0b0110011,
                'funct3': 0b000,
                'funct7': 0b0100000,
                'description': 'Subtract registers'
            },
            'sll': {
                'type': InstructionType.R_TYPE,
                'opcode': 0b0110011,
                'funct3': 0b001,
                'funct7': 0b0000000,
                'description': 'Shift left logical'
            },
            'slt': {
                'type': InstructionType.R_TYPE,
                'opcode': 0b0110011,
                'funct3': 0b010,
                'funct7': 0b0000000,
                'description': 'Set less than'
            },
            'sltu': {
                'type': InstructionType.R_TYPE,
                'opcode': 0b0110011,
                'funct3': 0b011,
                'funct7': 0b0000000,
                'description': 'Set less than unsigned'
            },
            'xor': {
                'type': InstructionType.R_TYPE,
                'opcode': 0b0110011,
                'funct3': 0b100,
                'funct7': 0b0000000,
                'description': 'Exclusive OR'
            },
            'srl': {
                'type': InstructionType.R_TYPE,
                'opcode': 0b0110011,
                'funct3': 0b101,
                'funct7': 0b0000000,
                'description': 'Shift right logical'
            },
            'sra': {
                'type': InstructionType.R_TYPE,
                'opcode': 0b0110011,
                'funct3': 0b101,
                'funct7': 0b0100000,
                'description': 'Shift right arithmetic'
            },
            'or': {
                'type': InstructionType.R_TYPE,
                'opcode': 0b0110011,
                'funct3': 0b110,
                'funct7': 0b0000000,
                'description': 'Bitwise OR'
            },
            'and': {
                'type': InstructionType.R_TYPE,
                'opcode': 0b0110011,
                'funct3': 0b111,
                'funct7': 0b0000000,
                'description': 'Bitwise AND'
            },
            
            # I-type instructions
            'addi': {
                'type': InstructionType.I_TYPE,
                'opcode': 0b0010011,
                'funct3': 0b000,
                'description': 'Add immediate'
            },
            'slti': {
                'type': InstructionType.I_TYPE,
                'opcode': 0b0010011,
                'funct3': 0b010,
                'description': 'Set less than immediate'
            },
            'sltiu': {
                'type': InstructionType.I_TYPE,
                'opcode': 0b0010011,
                'funct3': 0b011,
                'description': 'Set less than immediate unsigned'
            },
            'xori': {
                'type': InstructionType.I_TYPE,
                'opcode': 0b0010011,
                'funct3': 0b100,
                'description': 'XOR immediate'
            },
            'ori': {
                'type': InstructionType.I_TYPE,
                'opcode': 0b0010011,
                'funct3': 0b110,
                'description': 'OR immediate'
            },
            'andi': {
                'type': InstructionType.I_TYPE,
                'opcode': 0b0010011,
                'funct3': 0b111,
                'description': 'AND immediate'
            },
            'slli': {
                'type': InstructionType.I_TYPE,
                'opcode': 0b0010011,
                'funct3': 0b001,
                'funct7': 0b0000000,
                'description': 'Shift left logical immediate'
            },
            'srli': {
                'type': InstructionType.I_TYPE,
                'opcode': 0b0010011,
                'funct3': 0b101,
                'funct7': 0b0000000,
                'description': 'Shift right logical immediate'
            },
            'srai': {
                'type': InstructionType.I_TYPE,
                'opcode': 0b0010011,
                'funct3': 0b101,
                'funct7': 0b0100000,
                'description': 'Shift right arithmetic immediate'
            },
            
            # Load instructions
            'lb': {
                'type': InstructionType.I_TYPE,
                'opcode': 0b0000011,
                'funct3': 0b000,
                'description': 'Load byte'
            },
            'lh': {
                'type': InstructionType.I_TYPE,
                'opcode': 0b0000011,
                'funct3': 0b001,
                'description': 'Load halfword'
            },
            'lw': {
                'type': InstructionType.I_TYPE,
                'opcode': 0b0000011,
                'funct3': 0b010,
                'description': 'Load word'
            },
            'lbu': {
                'type': InstructionType.I_TYPE,
                'opcode': 0b0000011,
                'funct3': 0b100,
                'description': 'Load byte unsigned'
            },
            'lhu': {
                'type': InstructionType.I_TYPE,
                'opcode': 0b0000011,
                'funct3': 0b101,
                'description': 'Load halfword unsigned'
            },
            
            # Store instructions
            'sb': {
                'type': InstructionType.S_TYPE,
                'opcode': 0b0100011,
                'funct3': 0b000,
                'description': 'Store byte'
            },
            'sh': {
                'type': InstructionType.S_TYPE,
                'opcode': 0b0100011,
                'funct3': 0b001,
                'description': 'Store halfword'
            },
            'sw': {
                'type': InstructionType.S_TYPE,
                'opcode': 0b0100011,
                'funct3': 0b010,
                'description': 'Store word'
            },
            
            # Branch instructions
            'beq': {
                'type': InstructionType.B_TYPE,
                'opcode': 0b1100011,
                'funct3': 0b000,
                'description': 'Branch if equal'
            },
            'bne': {
                'type': InstructionType.B_TYPE,
                'opcode': 0b1100011,
                'funct3': 0b001,
                'description': 'Branch if not equal'
            },
            'blt': {
                'type': InstructionType.B_TYPE,
                'opcode': 0b1100011,
                'funct3': 0b100,
                'description': 'Branch if less than'
            },
            'bge': {
                'type': InstructionType.B_TYPE,
                'opcode': 0b1100011,
                'funct3': 0b101,
                'description': 'Branch if greater than or equal'
            },
            'bltu': {
                'type': InstructionType.B_TYPE,
                'opcode': 0b1100011,
                'funct3': 0b110,
                'description': 'Branch if less than unsigned'
            },
            'bgeu': {
                'type': InstructionType.B_TYPE,
                'opcode': 0b1100011,
                'funct3': 0b111,
                'description': 'Branch if greater than or equal unsigned'
            },
            
            # Jump instructions
            'jal': {
                'type': InstructionType.J_TYPE,
                'opcode': 0b1101111,
                'description': 'Jump and link'
            },
            'jalr': {
                'type': InstructionType.I_TYPE,
                'opcode': 0b1100111,
                'funct3': 0b000,
                'description': 'Jump and link register'
            },
            
            # Upper immediate instructions
            'lui': {
                'type': InstructionType.U_TYPE,
                'opcode': 0b0110111,
                'description': 'Load upper immediate'
            },
            'auipc': {
                'type': InstructionType.U_TYPE,
                'opcode': 0b0010111,
                'description': 'Add upper immediate to PC'
            }
        }
        
        # Register name mapping
        self.register_map = {
            'x0': 0, 'zero': 0,
            'x1': 1, 'ra': 1,
            'x2': 2, 'sp': 2,
            'x3': 3, 'gp': 3,
            'x4': 4, 'tp': 4,
            'x5': 5, 't0': 5,
            'x6': 6, 't1': 6,
            'x7': 7, 't2': 7,
            'x8': 8, 's0': 8, 'fp': 8,
            'x9': 9, 's1': 9,
            'x10': 10, 'a0': 10,
            'x11': 11, 'a1': 11,
            'x12': 12, 'a2': 12,
            'x13': 13, 'a3': 13,
            'x14': 14, 'a4': 14,
            'x15': 15, 'a5': 15,
            'x16': 16, 'a6': 16,
            'x17': 17, 'a7': 17,
            'x18': 18, 's2': 18,
            'x19': 19, 's3': 19,
            'x20': 20, 's4': 20,
            'x21': 21, 's5': 21,
            'x22': 22, 's6': 22,
            'x23': 23, 's7': 23,
            'x24': 24, 's8': 24,
            'x25': 25, 's9': 25,
            'x26': 26, 's10': 26,
            'x27': 27, 's11': 27,
            'x28': 28, 't3': 28,
            'x29': 29, 't4': 29,
            'x30': 30, 't5': 30,
            'x31': 31, 't6': 31
        }
    
    def encode_r_type(self, funct7: int, rs2: int, rs1: int, funct3: int, rd: int, opcode: int) -> int:
        """Encode R-type instruction"""
        return (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
    
    def encode_i_type(self, imm: int, rs1: int, funct3: int, rd: int, opcode: int) -> int:
        """Encode I-type instruction"""
        imm = imm & 0xFFF  # 12-bit immediate
        return (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
    
    def encode_s_type(self, imm: int, rs2: int, rs1: int, funct3: int, opcode: int) -> int:
        """Encode S-type instruction"""
        imm_11_5 = (imm >> 5) & 0x7F
        imm_4_0 = imm & 0x1F
        return (imm_11_5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm_4_0 << 7) | opcode
    
    def encode_b_type(self, imm: int, rs2: int, rs1: int, funct3: int, opcode: int) -> int:
        """Encode B-type instruction"""
        imm_12 = (imm >> 12) & 0x1
        imm_10_5 = (imm >> 5) & 0x3F
        imm_4_1 = (imm >> 1) & 0xF
        imm_11 = (imm >> 11) & 0x1
        return (imm_12 << 31) | (imm_10_5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm_4_1 << 8) | (imm_11 << 7) | opcode
    
    def encode_u_type(self, imm: int, rd: int, opcode: int) -> int:
        """Encode U-type instruction"""
        imm = imm & 0xFFFFF  # 20-bit immediate
        return (imm << 12) | (rd << 7) | opcode
    
    def encode_j_type(self, imm: int, rd: int, opcode: int) -> int:
        """Encode J-type instruction"""
        imm_20 = (imm >> 20) & 0x1
        imm_10_1 = (imm >> 1) & 0x3FF
        imm_11 = (imm >> 11) & 0x1
        imm_19_12 = (imm >> 12) & 0xFF
        return (imm_20 << 31) | (imm_19_12 << 12) | (imm_11 << 20) | (imm_10_1 << 21) | (rd << 7) | opcode
    
    def get_register_number(self, reg_name: str) -> int:
        """Convert register name to number"""
        if reg_name in self.register_map:
            return self.register_map[reg_name]
        raise ValueError(f"Unknown register: {reg_name}")
    
    def decode_instruction(self, instruction: int) -> Dict:
        """Decode a 32-bit instruction"""
        opcode = instruction & 0x7F
        rd = (instruction >> 7) & 0x1F
        funct3 = (instruction >> 12) & 0x7
        rs1 = (instruction >> 15) & 0x1F
        rs2 = (instruction >> 20) & 0x1F
        funct7 = (instruction >> 25) & 0x7F
        
        return {
            'opcode': opcode,
            'rd': rd,
            'funct3': funct3,
            'rs1': rs1,
            'rs2': rs2,
            'funct7': funct7,
            'raw': instruction
        }
    
    def sign_extend(self, value: int, bits: int) -> int:
        """Sign extend a value"""
        sign_bit = 1 << (bits - 1)
        if value & sign_bit:
            # Negative number - extend with 1s
            return value | (~((1 << bits) - 1))
        return value
