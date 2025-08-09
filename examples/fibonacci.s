# Fibonacci Sequence Calculator in RISC-V Assembly
# Calculates the first 10 numbers in the Fibonacci sequence

.text
main:
    # Initialize registers
    addi x1, x0, 0      # x1 = 0 (first Fibonacci number)
    addi x2, x0, 1      # x2 = 1 (second Fibonacci number)
    addi x3, x0, 10     # x3 = 10 (counter)
    addi x4, x0, 0      # x4 = 0 (current index)
    
    # Print first two numbers (assuming they're already in x1 and x2)
    
fibonacci_loop:
    # Check if we've calculated enough numbers
    beq x4, x3, end_program
    
    # Calculate next Fibonacci number: x5 = x1 + x2
    add x5, x1, x2
    
    # Update for next iteration
    mv x1, x2           # x1 = previous x2
    mv x2, x5           # x2 = new Fibonacci number
    
    # Increment counter
    addi x4, x4, 1
    
    # Store result in memory (optional - for demonstration)
    slli x6, x4, 2      # x6 = x4 * 4 (word offset)
    addi x7, x0, 0x1000 # Base address for results
    add x8, x7, x6      # Calculate final address
    sw x2, 0(x8)        # Store Fibonacci number
    
    # Continue loop
    j fibonacci_loop

end_program:
    # Program complete - infinite loop to halt
    j end_program

.data
# Reserve space for results
results: .space 40  # Space for 10 words
