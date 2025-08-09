# Bubble Sort Implementation in RISC-V Assembly
# Sorts an array of integers using bubble sort algorithm

.text
main:
    # Initialize array parameters
    addi x1, x0, 8      # Array length
    addi x2, x0, 0x1000 # Array base address
    
    # Initialize test data in memory
    addi x3, x0, 64     # First element
    sw x3, 0(x2)
    addi x3, x0, 34
    sw x3, 4(x2)
    addi x3, x0, 25
    sw x3, 8(x2)
    addi x3, x0, 12
    sw x3, 12(x2)
    addi x3, x0, 22
    sw x3, 16(x2)
    addi x3, x0, 11
    sw x3, 20(x2)
    addi x3, x0, 90
    sw x3, 24(x2)
    addi x3, x0, 5
    sw x3, 28(x2)

bubble_sort:
    addi x4, x0, 0      # i = 0 (outer loop counter)
    
outer_loop:
    beq x4, x1, sort_complete  # if i == length, exit
    
    addi x5, x0, 0      # j = 0 (inner loop counter)
    sub x6, x1, x4      # length - i
    addi x6, x6, -1     # length - i - 1
    
inner_loop:
    beq x5, x6, outer_next     # if j == length-i-1, next outer iteration
    
    # Calculate addresses for array[j] and array[j+1]
    slli x7, x5, 2      # j * 4
    add x8, x2, x7      # address of array[j]
    
    lw x9, 0(x8)        # Load array[j]
    lw x10, 4(x8)       # Load array[j+1]
    
    # Compare and swap if necessary
    blt x9, x10, no_swap    # if array[j] < array[j+1], no swap needed
    
    # Swap elements
    sw x10, 0(x8)       # array[j] = array[j+1]
    sw x9, 4(x8)        # array[j+1] = array[j]
    
no_swap:
    addi x5, x5, 1      # j++
    j inner_loop
    
outer_next:
    addi x4, x4, 1      # i++
    j outer_loop

sort_complete:
    # Verification: Load sorted values (optional)
    lw x11, 0(x2)       # Load first element
    lw x12, 4(x2)       # Load second element
    lw x13, 8(x2)       # Load third element
    
    # Infinite loop to halt execution
    j sort_complete

.data
array: .space 32       # Space for 8 integers
