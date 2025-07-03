all:
	bison -d parser.y
	flex lexer.l
	gcc -o calc parser.tab.c lex.yy.c main.c `pkg-config --cflags --libs gtk+-3.0`
