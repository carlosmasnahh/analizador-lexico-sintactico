%{
#include <stdio.h>
#include <stdlib.h>

int yylex(void);
void yyerror(const char *s);
int resultado;
%}

%token NUM
%token MAS MENOS MUL DIV

%left MAS MENOS
%left MUL DIV

%start input

%%

input:
    expresion '\n' { printf("Resultado: %d\n", resultado); }
;

expresion:
      NUM               { resultado = $1; }
    | NUM MAS NUM       { resultado = $1 + $3; }
    | NUM MENOS NUM     { resultado = $1 - $3; }
    | NUM MUL NUM       { resultado = $1 * $3; }
    | NUM DIV NUM       {
                          if ($3 == 0) {
                            printf("Error: division entre 0\n");
                            exit(1);
                          }
                          resultado = $1 / $3;
                        }
;


%%
void yyerror(const char *s) {
    fprintf(stderr, "❌ Error de sintaxis: %s\n", s);
}
