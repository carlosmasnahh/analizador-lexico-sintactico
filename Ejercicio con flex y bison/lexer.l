%{
#include "parser.tab.h"
#include <stdio.h>
%}

%%

[\n]        return '\n';   // 
[0-9]+      { yylval = atoi(yytext); return NUM; }
[\t ]+      ; // ignorar espacios y tabs
"+"         return MAS;
"-"         return MENOS;
"*"         return MUL;
"/"         return DIV;
.           return yytext[0];


%%

int yywrap(void) {
    return 1;
}
