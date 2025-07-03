%{
#include "parser.tab.h"
#include <stdio.h>
%}

%%

[\n]        return '\n';   // ✅ Añadir esta línea si no existe
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
