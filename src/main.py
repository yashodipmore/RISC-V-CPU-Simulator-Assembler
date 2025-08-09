"""
Main entry point for RISC-V CPU Simulator
Provides command-line interface and interactive features
"""

import sys
import os
import argparse
from typing import List, Optional

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__)))

from cpu.core import RISCVCore
from assembler.parser import AssemblyParser

class RISCVSimulator:
    """Main RISC-V Simulator Application"""
    
    def __init__(self):
        self.cpu = RISCVCore()
        self.assembler = AssemblyParser()
        self.debug_mode = False
    
    def load_assembly_file(self, filename: str) -> List[int]:
        """Load and assemble a RISC-V assembly file"""
        try:
            with open(filename, 'r') as f:
                assembly_code = f.read()
            
            print(f"Assembling {filename}...")
            machine_code = self.assembler.assemble(assembly_code)
            print(f"Successfully assembled {len(machine_code)} instructions")
            
            return machine_code
        
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Assembly error: {e}")
            sys.exit(1)
    
    def run_program(self, program: List[int], debug: bool = False, trace: bool = False):
        """Run a program on the RISC-V simulator"""
        # Reset CPU state
        self.cpu.reset()
        self.cpu.debug_mode = debug or trace
        
        # Load program into memory
        self.cpu.load_program(program)
        
        print("Starting RISC-V simulation...")
        print("=" * 50)
        
        if debug:
            self.run_debug_mode()
        else:
            # Run simulation
            stats = self.cpu.run()
            self.print_results(stats, trace)
    
    def run_debug_mode(self):
        """Interactive debugging mode"""
        print("Debug mode - Commands: step, run, print, quit")
        
        while not self.cpu.halt:
            command = input(f"PC:{self.cpu.pc:08x}> ").strip().lower()
            
            if command == 'step' or command == 's':
                # Execute one instruction
                try:
                    instruction = self.cpu.fetch_instruction(self.cpu.pc)
                    self.cpu.execute_instruction(instruction)
                    self.cpu.instruction_count += 1
                    self.cpu.cycle_count += 1
                    print(f"Executed: 0x{instruction:08x}")
                except Exception as e:
                    print(f"Execution error: {e}")
                    break
            
            elif command == 'run' or command == 'r':
                # Run until halt
                stats = self.cpu.run()
                self.print_results(stats)
                break
            
            elif command == 'print' or command == 'p':
                # Print CPU state
                self.cpu.print_state()
            
            elif command == 'quit' or command == 'q':
                break
            
            elif command == 'help' or command == 'h':
                print("Commands:")
                print("  step (s) - Execute one instruction")
                print("  run (r)  - Run until completion")
                print("  print (p)- Print CPU state")
                print("  quit (q) - Exit debugger")
            
            else:
                print("Unknown command. Type 'help' for available commands.")
    
    def print_results(self, stats: dict, show_trace: bool = False):
        """Print simulation results"""
        print("\nSimulation Complete!")
        print("=" * 50)
        print(f"Instructions executed: {stats['instructions']}")
        print(f"Cycles taken: {stats['cycles']}")
        print(f"CPI (Cycles per Instruction): {stats['cpi']:.2f}")
        print(f"Final PC: 0x{stats['pc']:08x}")
        
        if stats['branches'] > 0:
            print(f"Branches: {stats['branches']}")
            print(f"Branches taken: {stats['branches_taken']}")
            print(f"Branch accuracy: {stats['branch_accuracy']:.1%}")
        
        print(f"I-Cache hit rate: {stats['icache_hit_rate']:.1%}")
        print(f"D-Cache hit rate: {stats['dcache_hit_rate']:.1%}")
        
        if show_trace:
            self.print_execution_trace()
    
    def print_execution_trace(self):
        """Print execution trace if available"""
        if self.cpu.trace:
            print("\nExecution Trace:")
            print("-" * 60)
            for entry in self.cpu.trace[-10:]:  # Show last 10 instructions
                pc = entry['pc']
                instr = entry['instruction']
                print(f"PC:{pc:08x} INSTR:0x{instr:08x}")
    
    def benchmark_mode(self, programs: List[str]):
        """Run benchmark suite"""
        print("RISC-V Benchmark Suite")
        print("=" * 50)
        
        results = []
        for program_file in programs:
            print(f"\nRunning {program_file}...")
            program = self.load_assembly_file(program_file)
            
            self.cpu.reset()
            self.cpu.load_program(program)
            stats = self.cpu.run()
            
            results.append({
                'program': program_file,
                'stats': stats
            })
            
            print(f"  Instructions: {stats['instructions']}")
            print(f"  CPI: {stats['cpi']:.2f}")
            print(f"  Cache hit rate: {stats['icache_hit_rate']:.1%}")
        
        # Summary
        print("\nBenchmark Summary:")
        print("-" * 50)
        total_instructions = sum(r['stats']['instructions'] for r in results)
        avg_cpi = sum(r['stats']['cpi'] for r in results) / len(results)
        
        print(f"Total instructions: {total_instructions}")
        print(f"Average CPI: {avg_cpi:.2f}")
        
        for result in results:
            name = result['program'].split('/')[-1]
            cpi = result['stats']['cpi']
            print(f"  {name}: {cpi:.2f} CPI")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='RISC-V CPU Simulator')
    parser.add_argument('program', nargs='?', help='Assembly program file to run')
    parser.add_argument('--debug', '-d', action='store_true', help='Run in debug mode')
    parser.add_argument('--trace', '-t', action='store_true', help='Show execution trace')
    parser.add_argument('--benchmark', '-b', action='store_true', help='Run benchmark suite')
    parser.add_argument('--stats', '-s', action='store_true', help='Show detailed statistics')
    
    args = parser.parse_args()
    
    simulator = RISCVSimulator()
    
    if args.benchmark:
        # Run benchmark suite
        benchmark_programs = [
            'examples/fibonacci.s',
            'examples/sorting.s'
        ]
        simulator.benchmark_mode(benchmark_programs)
    
    elif args.program:
        # Run single program
        program = simulator.load_assembly_file(args.program)
        simulator.run_program(program, args.debug, args.trace or args.stats)
    
    else:
        # Interactive mode
        print("RISC-V Simulator v1.0")
        print("Interactive Mode - Enter assembly file path or 'quit' to exit")
        
        while True:
            try:
                filename = input("> ").strip()
                if filename.lower() in ['quit', 'exit', 'q']:
                    break
                
                if filename:
                    program = simulator.load_assembly_file(filename)
                    simulator.run_program(program, debug=True)
            
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()
