# Simple Arithmetic Test Program
# Tests various RISC-V arithmetic operations

main:
    addi x1, x0, 15     # x1 = 15
    addi x2, x0, 10     # x2 = 10
    add x3, x1, x2      # x3 = 25 (15 + 10)
    sub x4, x1, x2      # x4 = 5 (15 - 10)
    slli x5, x1, 2      # x5 = 60 (15 << 2)
    and x6, x1, x2      # x6 = 10 (15 & 10)
    or x7, x1, x2       # x7 = 15 (15 | 10)
    xor x8, x1, x2      # x8 = 5 (15 ^ 10)
    
    # Test immediate operations
    addi x9, x1, 100    # x9 = 115 (15 + 100)
    andi x10, x1, 7     # x10 = 7 (15 & 7)
    ori x11, x1, 240    # x11 = 255 (15 | 240)
    
    # Test comparisons
    slt x12, x2, x1     # x12 = 1 (10 < 15)
    slt x13, x1, x2     # x13 = 0 (15 < 10)
    
end:
    # Infinite loop to halt
    jal x0, end
