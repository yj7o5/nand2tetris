// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// Swap R0 with R1 if R0 > R1 to allow fewer loop operations

// Put your code here.

    @i      // i = 0
    M=1
    @2      // set R2 = 0
    M=0

    @0
    D=M     // D=R0
    @1
    D=M-D   // D=R1-R0
    @LOOP
    D;JGT   // if D > 0 goto LOOP
    @0
    D=M    
    @j
    M=D     
    @1
    D=M     
    @0
    M=D     
    @j
    D=M
    @1
    M=D    

(LOOP)
    @i
    D=M     // set D = i
    @0      
    D=D-M   // set D = D - R0
    @END
    D;JGT   // if D > 0 goto END
    @1
    D=M     // set D = R2
    @2      
    M=D+M  // set R2 = D + R1
    @i
    M=M+1   // increment i

    @LOOP
    0;JMP

(END)
    @END
    0;JMP   // terminate via inf. loop
