grammar OPLang;

@lexer::header {
from lexererr import *
}

@lexer::members {
def emit(self):
    tk = self.type
    if tk == self.UNCLOSE_STRING:       
        result = super().emit();
        raise UncloseString(result.text);
    elif tk == self.ILLEGAL_ESCAPE:
        result = super().emit();
        raise IllegalEscape(result.text);
    elif tk == self.ERROR_CHAR:
        result = super().emit();
        raise ErrorToken(result.text); 
    else:
        return super().emit();
}

options{
	language=Python3;
}

program: classdecllist EOF; // write for program rule here using vardecl and funcdecl

// -----------Parser----------------

// class
classdecllist: classdecl classdecllist | classdecl;
classdecl: CLASS ID classextends classbody;
classextends: EXTENDS ID | ;
classbody: LP classmemlist RP;
classmemlist: classmem classmemlist | ;
classmem: attrdecl | methoddecl;

// method
methoddecl: constructor | method | destructor;
constructor: defaultcon | copycon | user_definedcon;
defaultcon: ID LB RB blockstmt_no_return;
copycon: ID LB ID AMPERSAND? OTHER RB blockstmt_no_return;
user_definedcon: ID paramdecl blockstmt_no_return;
method: STATIC? (typ | VOID) AMPERSAND? ID paramdecl blockstmt;
destructor: TILDE ID LB RB blockstmt_no_return;
typ: primitivetyp | classtyp | arraytyp;
paramdecl: LB paramnullist RB;
paramnullist: paramprime | ;
paramprime: param SEMICOLON paramprime | param;
param: typ AMPERSAND? idlist;
idlist: ID COMMA idlist | ID;

// attribute
attrdecllist: attrdecl attrdecllist | attrdecl;
attrdecl: mutattr | immutattr;
mutattr: (STATIC? | FINAL STATIC | STATIC FINAL) typ AMPERSAND? attrlist SEMICOLON;
immutattr: (FINAL STATIC? | STATIC FINAL) typ attrlist SEMICOLON;
attrlist: attrmem COMMA attrlist | attrmem;
attrmem: idlist attrinit;
attrinit: ASSIGN expr | ;

// variable
vardecllist: vardecl vardecllist | vardecl;
vardecl: mutvar | immutvar;
mutvar: typ AMPERSAND? varlist SEMICOLON;
immutvar: FINAL typ varlist SEMICOLON;
varlist: varmem COMMA varlist | varmem;
varmem: idlist varinit;
varinit: ASSIGN expr | ;

// arraylit, booleanlit
arraylit: LP arraymemlist RP;
arraymemlist: arraymem COMMA arraymemlist | arraymem | ;
arraymem: INTLIT | FLOATLIT | STRINGLIT | booleanlit | NEW ID LB argnullist RB;
booleanlit: TRUE | FALSE;

// expression
exprlist: expr COMMA exprlist | expr;
expr: expr1 (GREATER_EQ | LESS_EQ | GREATER | LESS) expr1 | expr1;
expr1: expr2 (EQ | NEQ) expr2 | expr2;
expr2: expr2 (AND | OR) expr3 | expr3;
expr3: expr3 (ADD | SUB) expr4 | expr4;
expr4: expr4 (MUL | DIV_I | DIV_F | MOD) expr5 | expr5;
expr5: expr5 CONCAT expr6 | expr6;
expr6: (NOT) expr6 | expr7;
expr7: (ADD | SUB) expr7 | expr8;
expr8: expr9 postfixlist;
postfixlist: postfix postfixlist | ;
postfix : LSB expr RSB 
          | DOT ID // field access 
          | DOT ID LB argnullist RB; // method call 
expr9: NEW ID LB argnullist RB | expr10 ;
expr10: THIS | ID | NIL | primitivelit | arraylit | subexpr;

argnullist: argprime | ;
argprime: expr COMMA argprime | expr;
primitivelit: INTLIT | FLOATLIT | STRINGLIT | booleanlit;
subexpr: LB expr RB;

// statement
stmtlist: stmt stmtlist | ;
stmt: blockstmt | assignstmt | ifstmt | forstmt | breakstmt | continuestmt | returnstmt | methodinstmt;
blockstmt: LP vardecllist? stmtlist RP;
blockstmt_no_return: LP vardecllist? stmtlist_no_return RP;
stmtlist_no_return: stmt_no_return stmtlist_no_return | ;
stmt_no_return: blockstmt_no_return 
              | assignstmt | ifstmt | forstmt 
              | breakstmt | continuestmt | methodinstmt;

assignstmt: lhs ASSIGN expr SEMICOLON;
lhs: ID | expr9 postfix postfixlist;

ifstmt: IF expr THEN stmt | IF expr THEN stmt ELSE stmt;

forstmt: FOR ID ASSIGN expr (TO | DOWNTO) expr DO stmt;

breakstmt: BREAK SEMICOLON;

continuestmt: CONTINUE SEMICOLON;

returnstmt: RETURN expr SEMICOLON;

methodinstmt: (expr9 postfix postfixlist) LB argnullist RB SEMICOLON;

// type
primitivetyp: INT | FLOAT | STRING | BOOLEAN;
classtyp: ID;
arraytyp: (primitivetyp | classtyp) AMPERSAND? LSB INTLIT RSB;

// -----------Lexer-----------------

// keywords
BOOLEAN: 'boolean';
BREAK: 'break';
CLASS: 'class';
CONTINUE: 'continue';
DO: 'do';
ELSE: 'else';
EXTENDS: 'extends';
FLOAT: 'float';
IF: 'if';
INT: 'int';
NEW: 'new';
STRING: 'string';
THEN: 'then';
FOR: 'for';
RETURN: 'return';
TRUE: 'true';
FALSE: 'false';
VOID: 'void';
NIL: 'nil';
THIS: 'this';
FINAL: 'final';
STATIC: 'static';
TO: 'to';
DOWNTO: 'downto';
OTHER: 'other';
// operator
ADD: '+';
SUB: '-';
MUL: '*';
DIV_F: '/';
DIV_I: '\\';
MOD: '%';
NEQ: '!=';
EQ: '==';
LESS: '<';
GREATER: '>';
LESS_EQ: '<=';
GREATER_EQ: '>=';
OR: '||';
AND: '&&';
NOT: '!';
CONCAT: '^';
ASSIGN: ':=';

//special char
TILDE: '~';
AMPERSAND: '&';

// separator
LSB: '[';
RSB: ']';
LP: '{';
RP: '}';
LB: '(';
RB: ')';
SEMICOLON: ';';
COLON: ':';
DOT: '.';
COMMA: ',';

//identifier
ID: [_a-zA-Z] [_a-zA-Z0-9]*;
//comment
WS : [ \b\f\t\r\n]+ -> skip ; // skip spaces, tabs 
LINE_COMMENT: 	'#' ~[\n\r]* -> skip;
BLOCK_COMMENT: '/*' .*? '*/'-> skip;

//INT_LIT
INTLIT: [0-9]+;

//FLOAT_LIT
FLOATLIT: (INT_PART DECI_PART) | (INT_PART DECI_PART? EXP_PART);
fragment INT_PART: [0-9]+;
fragment DECI_PART: '.' [0-9]*;
fragment EXP_PART: [eE] [+-]? [0-9]+;

//STRING_LIT
STRINGLIT: '"' CHAR_LIT* STRINGLIT? '"' { self.text = self.text[1:-1] } ;
fragment CHAR_LIT: ESCSEQ | '\\"' | ~([\n\r] | '"' | '\\');
fragment ESCSEQ: '\\' ([btnfr"\\]);
fragment ILLESC: '\\' ~([btnfr"\\]);

ERROR_CHAR: . { raise ErrorToken(self.text) };
 UNCLOSE_STRING: '"' CHAR_LIT* ('\n' | '\r' | '\r\n' | 'EOF' | ~'"') {
	raise UncloseString(self.text[1:])
};

ILLEGAL_ESCAPE: '"' CHAR_LIT* ILLESC {
	raise IllegalEscape(self.text[1:])
};