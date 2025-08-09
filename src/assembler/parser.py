"""
RISC-V Assembly Language Parser and Assembler
Converts RISC-V assembly code to machine code
"""

import re
import sys
import os
from typing import Dict, List, Tuple, Optional

# Add the parent directory to the path to handle imports properly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.instructions import RV32I_Instructions
except ImportError:
    # Try relative import if absolute import fails
    from ..utils.instructions import RV32I_Instructions

class AssemblyParser:
    """RISC-V Assembly Language Parser"""
    
    def __init__(self):
        self.instructions = RV32I_Instructions()
        self.labels = {}  # Label name -> address mapping
        self.symbols = {}  # Symbol table for constants
        self.current_address = 0
        self.errors = []
        
        # Pseudo-instruction mappings
        self.pseudo_instructions = {
            'nop': ['addi', 'x0', 'x0', '0'],
            'li': self._expand_li,
            'la': self._expand_la,
            'mv': lambda args: ['addi', args[0], args[1], '0'],
            'not': lambda args: ['xori', args[0], args[1], '-1'],
            'neg': lambda args: ['sub', args[0], 'x0', args[1]],
            'j': lambda args: ['jal', 'x0', args[0]],
            'jr': lambda args: ['jalr', 'x0', args[0], '0'],
            'ret': ['jalr', 'x0', 'ra', '0'],
            'beqz': lambda args: ['beq', args[0], 'x0', args[1]],
            'bnez': lambda args: ['bne', args[0], 'x0', args[1]],
            'blez': lambda args: ['bge', 'x0', args[0], args[1]],
            'bgez': lambda args: ['bge', args[0], 'x0', args[1]],
            'bltz': lambda args: ['blt', args[0], 'x0', args[1]],
            'bgtz': lambda args: ['blt', 'x0', args[0], args[1]]
        }
    
    def _expand_li(self, args: List[str]) -> List[List[str]]:
        """Expand load immediate pseudo-instruction"""
        rd, imm = args[0], int(args[1])
        
        if -2048 <= imm <= 2047:
            # Fits in 12-bit immediate
            return [['addi', rd, 'x0', str(imm)]]
        else:
            # Need LUI + ADDI
            upper = (imm + 0x800) >> 12  # Add 0x800 for proper rounding
            lower = imm & 0xFFF
            if lower & 0x800:  # Sign extend
                lower = lower - 0x1000
            
            instructions = [['lui', rd, str(upper)]]
            if lower != 0:
                instructions.append(['addi', rd, rd, str(lower)])
            return instructions
    
    def _expand_la(self, args: List[str]) -> List[List[str]]:
        """Expand load address pseudo-instruction"""
        # For now, treat as load immediate
        return self._expand_li(args)
    
    def parse_line(self, line: str) -> Optional[Dict]:
        """Parse a single line of assembly"""
        # Remove comments and strip whitespace
        line = re.sub(r'#.*', '', line).strip()
        if not line:
            return None
        
        # Handle assembler directives
        if line.startswith('.'):
            return self._handle_directive(line)
        
        # Check for label
        label_match = re.match(r'^(\w+):\s*(.*)', line)
        if label_match:
            label = label_match.group(1)
            self.labels[label] = self.current_address
            line = label_match.group(2).strip()
            if not line:
                return None
        
        # Parse instruction
        parts = re.split(r'[,\s]+', line)
        if not parts or not parts[0]:
            return None
        
        instruction = parts[0].lower()
        args = [arg.strip() for arg in parts[1:] if arg.strip()]
        
        return {
            'instruction': instruction,
            'args': args,
            'address': self.current_address
        }
    
    def _handle_directive(self, line: str) -> Optional[Dict]:
        """Handle assembler directives like .text, .data, .space"""
        parts = line.split()
        directive = parts[0].lower()
        
        if directive == '.text':
            # Text section - executable code
            return None  # Just ignore for now
        elif directive == '.data':
            # Data section
            return None  # Just ignore for now
        elif directive.startswith('.space'):
            # Reserve space - skip over it
            if len(parts) > 1:
                try:
                    space_size = int(parts[1])
                    self.current_address += space_size
                except ValueError:
                    pass
            return None
        elif directive.startswith('.word'):
            # Word data - could implement later
            return None
        else:
            # Unknown directive - just ignore
            return None
    
    def assemble_instruction(self, instruction: str, args: List[str]) -> int:
        """Assemble a single instruction to machine code"""
        if instruction in self.pseudo_instructions:
            # Handle pseudo-instructions
            expansion = self.pseudo_instructions[instruction]
            if callable(expansion):
                expanded = expansion(args)
                if isinstance(expanded, list) and len(expanded) > 0:
                    if isinstance(expanded[0], list):
                        # Multiple instructions - only handle first one for now
                        return self.assemble_instruction(expanded[0][0], expanded[0][1:])
                    else:
                        # Single instruction expansion
                        return self.assemble_instruction(expanded[0], expanded[1:])
            else:
                # Static expansion
                return self.assemble_instruction(expansion[0], expansion[1:])
        
        if instruction not in self.instructions.instructions:
            raise ValueError(f"Unknown instruction: {instruction}")
        
        instr_info = self.instructions.instructions[instruction]
        instr_type = instr_info['type']
        
        if instr_type.value == 'R':
            return self._assemble_r_type(instruction, args, instr_info)
        elif instr_type.value == 'I':
            return self._assemble_i_type(instruction, args, instr_info)
        elif instr_type.value == 'S':
            return self._assemble_s_type(instruction, args, instr_info)
        elif instr_type.value == 'B':
            return self._assemble_b_type(instruction, args, instr_info)
        elif instr_type.value == 'U':
            return self._assemble_u_type(instruction, args, instr_info)
        elif instr_type.value == 'J':
            return self._assemble_j_type(instruction, args, instr_info)
        else:
            raise ValueError(f"Unknown instruction type: {instr_type}")
    
    def _assemble_r_type(self, instruction: str, args: List[str], instr_info: Dict) -> int:
        """Assemble R-type instruction"""
        if len(args) != 3:
            raise ValueError(f"{instruction} requires 3 arguments")
        
        rd = self.instructions.get_register_number(args[0])
        rs1 = self.instructions.get_register_number(args[1])
        rs2 = self.instructions.get_register_number(args[2])
        
        return self.instructions.encode_r_type(
            instr_info['funct7'], rs2, rs1, instr_info['funct3'], rd, instr_info['opcode']
        )
    
    def _assemble_i_type(self, instruction: str, args: List[str], instr_info: Dict) -> int:
        """Assemble I-type instruction"""
        if instruction in ['lb', 'lh', 'lw', 'lbu', 'lhu']:
            # Load instructions: rd, offset(rs1)
            if len(args) != 2:
                raise ValueError(f"{instruction} requires 2 arguments")
            
            rd = self.instructions.get_register_number(args[0])
            
            # Parse offset(register) format
            match = re.match(r'^(-?\d+)\((\w+)\)$', args[1])
            if not match:
                raise ValueError(f"Invalid memory operand: {args[1]}")
            
            offset = int(match.group(1))
            rs1 = self.instructions.get_register_number(match.group(2))
            
            return self.instructions.encode_i_type(offset, rs1, instr_info['funct3'], rd, instr_info['opcode'])
        
        elif instruction == 'jalr':
            # JALR: rd, rs1, imm
            if len(args) == 2:
                # jalr rd, rs1 (imm = 0)
                rd = self.instructions.get_register_number(args[0])
                rs1 = self.instructions.get_register_number(args[1])
                imm = 0
            elif len(args) == 3:
                rd = self.instructions.get_register_number(args[0])
                rs1 = self.instructions.get_register_number(args[1])
                imm = self._parse_immediate(args[2])
            else:
                raise ValueError(f"{instruction} requires 2 or 3 arguments")
            
            return self.instructions.encode_i_type(imm, rs1, instr_info['funct3'], rd, instr_info['opcode'])
        
        else:
            # Regular I-type: rd, rs1, imm
            if len(args) != 3:
                raise ValueError(f"{instruction} requires 3 arguments")
            
            rd = self.instructions.get_register_number(args[0])
            rs1 = self.instructions.get_register_number(args[1])
            imm = self._parse_immediate(args[2])
            
            # Special handling for shift immediate instructions
            if instruction in ['slli', 'srli', 'srai']:
                # For shift instructions, we need to encode funct7 in the immediate field
                funct7 = instr_info.get('funct7', 0)
                if instruction == 'slli':
                    # SLLI: imm[11:5] = 0000000, imm[4:0] = shamt
                    encoded_imm = (funct7 << 5) | (imm & 0x1F)
                elif instruction == 'srli':
                    # SRLI: imm[11:5] = 0000000, imm[4:0] = shamt  
                    encoded_imm = (funct7 << 5) | (imm & 0x1F)
                elif instruction == 'srai':
                    # SRAI: imm[11:5] = 0100000, imm[4:0] = shamt
                    encoded_imm = (funct7 << 5) | (imm & 0x1F)
                return self.instructions.encode_i_type(encoded_imm, rs1, instr_info['funct3'], rd, instr_info['opcode'])
            else:
                return self.instructions.encode_i_type(imm, rs1, instr_info['funct3'], rd, instr_info['opcode'])
    
    def _assemble_s_type(self, instruction: str, args: List[str], instr_info: Dict) -> int:
        """Assemble S-type instruction"""
        if len(args) != 2:
            raise ValueError(f"{instruction} requires 2 arguments")
        
        rs2 = self.instructions.get_register_number(args[0])
        
        # Parse offset(register) format
        match = re.match(r'^(-?\d+)\((\w+)\)$', args[1])
        if not match:
            raise ValueError(f"Invalid memory operand: {args[1]}")
        
        offset = int(match.group(1))
        rs1 = self.instructions.get_register_number(match.group(2))
        
        return self.instructions.encode_s_type(offset, rs2, rs1, instr_info['funct3'], instr_info['opcode'])
    
    def _assemble_b_type(self, instruction: str, args: List[str], instr_info: Dict) -> int:
        """Assemble B-type instruction"""
        if len(args) != 3:
            raise ValueError(f"{instruction} requires 3 arguments")
        
        rs1 = self.instructions.get_register_number(args[0])
        rs2 = self.instructions.get_register_number(args[1])
        
        # Calculate branch offset
        target = self._parse_immediate(args[2])
        if isinstance(target, str) and target in self.labels:
            offset = self.labels[target] - self.current_address
        else:
            offset = target
        
        return self.instructions.encode_b_type(offset, rs2, rs1, instr_info['funct3'], instr_info['opcode'])
    
    def _assemble_u_type(self, instruction: str, args: List[str], instr_info: Dict) -> int:
        """Assemble U-type instruction"""
        if len(args) != 2:
            raise ValueError(f"{instruction} requires 2 arguments")
        
        rd = self.instructions.get_register_number(args[0])
        imm = self._parse_immediate(args[1])
        
        return self.instructions.encode_u_type(imm, rd, instr_info['opcode'])
    
    def _assemble_j_type(self, instruction: str, args: List[str], instr_info: Dict) -> int:
        """Assemble J-type instruction"""
        if len(args) != 2:
            raise ValueError(f"{instruction} requires 2 arguments")
        
        rd = self.instructions.get_register_number(args[0])
        
        # Calculate jump offset
        target = self._parse_immediate(args[1])
        if isinstance(target, str) and target in self.labels:
            offset = self.labels[target] - self.current_address
        else:
            offset = target
        
        return self.instructions.encode_j_type(offset, rd, instr_info['opcode'])
    
    def _parse_immediate(self, imm_str: str):
        """Parse immediate value (supports decimal, hex, binary, and labels)"""
        imm_str = imm_str.strip()
        
        # Check if it's a label
        if re.match(r'^[a-zA-Z_]\w*$', imm_str):
            return imm_str  # Return as string, will be resolved later
        
        # Parse numeric immediate
        if imm_str.startswith('0x') or imm_str.startswith('0X'):
            return int(imm_str, 16)
        elif imm_str.startswith('0b') or imm_str.startswith('0B'):
            return int(imm_str, 2)
        else:
            return int(imm_str)
    
    def assemble(self, assembly_code: str) -> List[int]:
        """Assemble complete assembly program"""
        lines = assembly_code.strip().split('\n')
        self.current_address = 0
        self.labels.clear()
        self.errors.clear()
        
        # First pass: collect labels and calculate addresses
        parsed_instructions = []
        for line_num, line in enumerate(lines, 1):
            try:
                parsed = self.parse_line(line)
                if parsed:
                    parsed_instructions.append(parsed)
                    self.current_address += 4
            except Exception as e:
                self.errors.append(f"Line {line_num}: {e}")
        
        if self.errors:
            raise ValueError("Assembly errors:\n" + "\n".join(self.errors))
        
        # Second pass: generate machine code
        machine_code = []
        for parsed in parsed_instructions:
            try:
                self.current_address = parsed['address']
                code = self.assemble_instruction(parsed['instruction'], parsed['args'])
                machine_code.append(code)
            except Exception as e:
                self.errors.append(f"Address {parsed['address']:08x}: {e}")
        
        if self.errors:
            raise ValueError("Assembly errors:\n" + "\n".join(self.errors))
        
        return machine_code
    
    def disassemble(self, machine_code: List[int], start_address: int = 0) -> str:
        """Disassemble machine code to assembly"""
        assembly = []
        
        for i, instruction in enumerate(machine_code):
            address = start_address + (i * 4)
            try:
                decoded = self.instructions.decode_instruction(instruction)
                asm_line = self._decode_to_assembly(decoded, address)
                assembly.append(f"{address:08x}: {asm_line}")
            except Exception as e:
                assembly.append(f"{address:08x}: .word 0x{instruction:08x}  # {e}")
        
        return "\n".join(assembly)
    
    def _decode_to_assembly(self, decoded: Dict, address: int) -> str:
        """Convert decoded instruction back to assembly"""
        opcode = decoded['opcode']
        
        # This is a simplified disassembler - you could expand this
        # to provide full instruction names and operands
        return f".word 0x{decoded['raw']:08x}  # Decoded: opcode={opcode:07b}"
