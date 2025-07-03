@echo off
bison -d parser.y
flex lexer.l
gcc -o calc parser.tab.c lex.yy.c main.c -lm
calc
pause
