#!/usr/bin/env python3
"""
RISC-V Simulator Demonstration Script
Shows off all the key features of the simulator
"""

import os
import sys

def run_demo():
    print("🚀 RISC-V CPU Simulator Demonstration")
    print("=" * 60)
    print()
    
    # Change to project directory
    project_dir = r"c:\Users\morey\OneDrive\Desktop\risc v\New folder"
    os.chdir(project_dir)
    
    demos = [
        {
            'title': '1. Basic Arithmetic Operations',
            'command': 'python src\\main.py examples\\arithmetic.s',
            'description': 'Demonstrates basic ALU operations and register usage'
        },
        {
            'title': '2. Fibonacci Sequence Calculator',  
            'command': 'python src\\main.py examples\\fibonacci_simple.s',
            'description': 'Shows loop structures, branches, and memory operations'
        },
        {
            'title': '3. Performance Analysis',
            'command': 'python src\\main.py --stats examples\\arithmetic.s',
            'description': 'Detailed performance metrics and cache analysis'
        },
        {
            'title': '4. Test Suite Execution',
            'command': 'python tests\\test_suite.py',
            'description': 'Comprehensive testing of all simulator components'
        }
    ]
    
    for demo in demos:
        print(f"📋 {demo['title']}")
        print(f"   {demo['description']}")
        print(f"   Command: {demo['command']}")
        print()
        
        input("Press Enter to run this demo...")
        print("-" * 60)
        
        # Execute the command
        exit_code = os.system(demo['command'])
        
        print("-" * 60)
        print(f"✅ Demo completed (exit code: {exit_code})")
        print()
        input("Press Enter to continue to next demo...")
        print()
    
    print("🎉 All demonstrations completed!")
    print()
    print("📚 Next Steps:")
    print("   • Explore the source code in src/ directory")
    print("   • Try writing your own RISC-V assembly programs")
    print("   • Extend the simulator with new features")
    print("   • Use for computer architecture education/research")
    print()
    print("📖 Documentation:")
    print("   • README.md - Complete project overview")
    print("   • PROJECT_SUMMARY.md - Technical highlights")
    print("   • QUICK_START.md - Getting started guide")

if __name__ == "__main__":
    run_demo()
