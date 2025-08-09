# Quick Start Guide - RISC-V CPU Simulator

## Installation and Setup

### Prerequisites
- Python 3.7 or higher
- No additional dependencies required (uses only Python standard library)

### Quick Test
Run the test suite to verify everything works:
```bash
cd "c:\Users\morey\OneDrive\Desktop\risc v\New folder"
python tests\test_suite.py
```

## Running Programs

### Basic Usage
```bash
# Run a program
python src\main.py examples\fibonacci.s

# Debug mode
python src\main.py --debug examples\fibonacci.s

# Show performance stats
python src\main.py --stats examples\sorting.s

# Run benchmark suite
python src\main.py --benchmark
```

### Interactive Mode
```bash
python src\main.py
> examples\fibonacci.s
> examples\sorting.s
> quit
```

## Sample Output

### Fibonacci Program
```
RISC-V Simulator v1.0
Assembling examples\fibonacci.s...
Successfully assembled 12 instructions
Starting RISC-V simulation...
==================================================

Simulation Complete!
==================================================
Instructions executed: 67
Cycles taken: 67
CPI (Cycles per Instruction): 1.00
Final PC: 0x00000024
Branches: 12
Branches taken: 11
Branch accuracy: 91.7%
I-Cache hit rate: 100.0%
D-Cache hit rate: 100.0%
```

### Debug Mode Commands
- `step` (s) - Execute one instruction
- `run` (r) - Run until completion  
- `print` (p) - Print CPU state
- `quit` (q) - Exit debugger

## Key Features Demo

### 1. Instruction Set Support
The simulator supports all RV32I instructions:
- **Arithmetic**: ADD, SUB, ADDI, etc.
- **Logical**: AND, OR, XOR, shifts
- **Memory**: Load/Store with different sizes
- **Control**: Branches, jumps, calls
- **Immediate**: LUI, AUIPC

### 2. Performance Analysis
```
Cache hit rates - I$: 94.2%, D$: 87.3%
Branch prediction accuracy: 89.5%
Average CPI: 1.15
```

### 3. Assembly Features
- Full RISC-V assembly syntax
- Pseudo-instructions (li, mv, j, etc.)
- Label support for branches/jumps
- Comments and proper error reporting

## Example Programs Included

### Fibonacci (examples\fibonacci.s)
Calculates Fibonacci sequence, demonstrates:
- Loop structures
- Register management
- Memory operations
- Control flow

### Bubble Sort (examples\sorting.s)
Sorts an array using bubble sort, shows:
- Nested loops
- Memory access patterns
- Array manipulation
- Algorithm implementation

## Performance Benchmarking

Run the benchmark suite:
```bash
python src\main.py --benchmark
```

This will test multiple programs and show:
- Instructions per program
- CPI comparison
- Cache performance
- Overall system performance

## Educational Value

This simulator is perfect for:
- **Learning RISC-V architecture**
- **Understanding CPU design**
- **Computer architecture courses**
- **Systems programming practice**
- **Performance analysis education**

## Next Steps

1. **Try the sample programs** to see the simulator in action
2. **Write your own RISC-V programs** and test them
3. **Explore the code** to understand implementation details
4. **Extend the simulator** with new features
5. **Use for research** in computer architecture

The simulator provides a complete foundation for RISC-V education and research!
