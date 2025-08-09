# Simple Fibonacci Sequence Calculator in RISC-V Assembly
# Calculates the first 5 numbers in the Fibonacci sequence

main:
    # Initialize registers
    addi x1, x0, 0      # x1 = 0 (first Fibonacci number)
    addi x2, x0, 1      # x2 = 1 (second Fibonacci number)  
    addi x3, x0, 5      # x3 = 5 (counter)
    addi x4, x0, 0      # x4 = 0 (current index)
    
fibonacci_loop:
    # Check if we've calculated enough numbers
    beq x4, x3, end_program
    
    # Calculate next Fibonacci number: x5 = x1 + x2
    add x5, x1, x2
    
    # Update for next iteration  
    addi x1, x2, 0      # x1 = x2 (move x2 to x1)
    addi x2, x5, 0      # x2 = x5 (move x5 to x2)
    
    # Increment counter
    addi x4, x4, 1
    
    # Store result in memory (optional - for demonstration)
    slli x6, x4, 2      # x6 = x4 * 4 (word offset)
    addi x7, x0, 1000   # Base address for results (smaller address)
    add x8, x7, x6      # Calculate final address
    sw x2, 0(x8)        # Store Fibonacci number
    
    # Continue loop
    jal x0, fibonacci_loop

end_program:
    # Program complete - infinite loop to halt
    jal x0, end_program
