// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

(INIT)      // INIT R0 WITH SCREEN OFFSET
    @SCREEN
    D=A
    @R0     
    M=D     

(MAIN)
    @R0     // IF R0=KBD RESET OFFSET
    D=M
    @KBD
    D=D-A
    @INIT
    D;JEQ

    @KBD    // IF KEY PRESSED PAINT BLACK ELSE WHITE
    D=M

    @BLACK  
    D;JGT

    @WHITE  
    0;JMP

(INC)       // INCREMENT SCREEN OFFSET COUNTER
    @R0
    M=M+1   

    @MAIN
    0;JMP

(BLACK)     
    @R0
    A=M
    M=-1

    @INC
    0;JMP

(WHITE)    
    @R0
    A=M
    M=0

    @INC
    0;JMP
