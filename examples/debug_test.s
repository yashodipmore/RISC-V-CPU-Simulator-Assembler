# Debug Test Program
# Simple program to test basic operations

main:
    addi x1, x0, 10     # x1 = 10
    addi x2, x0, 20     # x2 = 20  
    add x3, x1, x2      # x3 = 30
    addi x4, x0, 0      # x4 = 0 (halt indicator)
    beq x4, x0, end     # if x4 == 0, go to end

end:
    addi x0, x0, 0      # nop - should halt here
