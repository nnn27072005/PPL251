"""
AST Generation module for OPLang programming language.
This module contains the ASTGeneration class that converts parse trees
into Abstract Syntax Trees using the visitor pattern.
"""

from functools import reduce
from build.OPLangVisitor import OPLangVisitor
from build.OPLangParser import OPLangParser
from src.utils.nodes import *


class ASTGeneration(OPLangVisitor):
    # ------------------- PROGRAM -------------------
    # Visit a parse tree produced by OPLangParser#program.
    # classdecllist EOF;
    def visitProgram(self, ctx:OPLangParser.ProgramContext):
        return Program(self.visit(ctx.classdecllist()))

    # classdecllist: classdecl classdecllist | classdecl;
    def visitClassdecllist(self, ctx:OPLangParser.ClassdecllistContext):
        if ctx.getChildCount() == 1:
            return [self.visit(ctx.classdecl())]
        return [self.visit(ctx.classdecl())] + self.visit(ctx.classdecllist())


    # classdecl: CLASS ID classextends classbody;
    def visitClassdecl(self, ctx:OPLangParser.ClassdeclContext):
        class_name = ctx.ID().getText()
        members = self.visit(ctx.classbody())
        return ClassDecl(class_name, self.visit(ctx.classextends()), members)


    # classextends: EXTENDS ID | ;
    def visitClassextends(self, ctx:OPLangParser.ClassextendsContext):
        return ctx.ID().getText() if ctx.ID() else None


    # classbody: LP classmemlist RP;
    def visitClassbody(self, ctx:OPLangParser.ClassbodyContext):
        return self.visit(ctx.classmemlist())

    # classmemlist: classmem classmemlist | ;
    def visitClassmemlist(self, ctx:OPLangParser.ClassmemlistContext):
        if ctx.getChildCount() == 0:
            return []
        return self.visit(ctx.classmem()) + self.visit(ctx.classmemlist())

    # classmem: attrdecl | methoddecl;
    def visitClassmem(self, ctx:OPLangParser.ClassmemContext):
        if ctx.attrdecl():
            return self.visit(ctx.attrdecl())  # đã là list
        return self.visit(ctx.methoddecl())  # bọc MethodDecl vào list

    # methoddecl: constructor | method | destructor;
    def visitMethoddecl(self, ctx:OPLangParser.MethoddeclContext):
        if ctx.constructor():
            return self.visit(ctx.constructor())
        elif ctx.method():
            return self.visit(ctx.method())
        return self.visit(ctx.destructor())


    # constructor: defaultcon | copycon | user_definedcon;
    def visitConstructor(self, ctx:OPLangParser.ConstructorContext):
        if ctx.defaultcon():
            return self.visit(ctx.defaultcon())
        elif ctx.copycon():
            return self.visit(ctx.copycon())
        return self.visit(ctx.user_definedcon())


    # defaultcon: ID LB RB blockstmt_no_return;
    def visitDefaultcon(self, ctx:OPLangParser.DefaultconContext):
        return [ConstructorDecl(ctx.ID().getText(), [], self.visit(ctx.blockstmt_no_return()))]


    # copycon: ID LB ID AMPERSAND? 'other' RB blockstmt_no_return;
    def visitCopycon(self, ctx:OPLangParser.CopyconContext):
        param_type = ctx.ID(1)
        if ctx.AMPERSAND():
            param_type = ReferenceType(param_type)
        params = [Parameter(param_type, 'other')]
        return [ConstructorDecl(ctx.ID(0).getText(), params, self.visit(ctx.blockstmt_no_return()))]


    # user_definedcon: ID paramdecl blockstmt_no_return;
    def visitUser_definedcon(self, ctx:OPLangParser.User_definedconContext):
        name = ctx.ID().getText()
        params = self.visit(ctx.paramdecl())
        body = self.visit(ctx.blockstmt_no_return())
        return [ConstructorDecl(name, params, body)]


    # method: STATIC? (typ | VOID) AMPERSAND? ID paramdecl blockstmt;
    def visitMethod(self, ctx:OPLangParser.MethodContext):
        is_static = bool(ctx.STATIC())
        typ = self.visit(ctx.typ()) if ctx.typ() else PrimitiveType("void")
        if ctx.AMPERSAND():
            typ = ReferenceType(typ)
        return [MethodDecl(is_static, typ, ctx.ID().getText(), self.visit(ctx.paramdecl()), self.visit(ctx.blockstmt()))]


    # destructor: TILDE ID LB RB blockstmt_no_return;
    def visitDestructor(self, ctx:OPLangParser.DestructorContext):
        return [DestructorDecl(ctx.ID().getText(), self.visit(ctx.blockstmt_no_return()))]


    # typ: primitivetyp | classtyp | arraytyp;
    def visitTyp(self, ctx:OPLangParser.TypContext):
        if ctx.primitivetyp():
            return self.visit(ctx.primitivetyp())
        elif ctx.classtyp():
            return self.visit(ctx.classtyp())
        return self.visit(ctx.arraytyp())


    # paramdecl: LB paramnullist RB;
    def visitParamdecl(self, ctx:OPLangParser.ParamdeclContext):
        return self.visit(ctx.paramnullist())


    # paramnullist: paramprime | ;
    def visitParamnullist(self, ctx:OPLangParser.ParamnullistContext):
        return self.visit(ctx.paramprime()) if ctx.paramprime() else []


    # paramprime: param SEMICOLON paramprime | param;
    def visitParamprime(self, ctx:OPLangParser.ParamprimeContext):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.param())
        return self.visit(ctx.param()) + self.visit(ctx.paramprime())


    # param: typ AMPERSAND? idlist;
    def visitParam(self, ctx:OPLangParser.ParamContext):
        typ = self.visit(ctx.typ())
        ids = self.visit(ctx.idlist())
        if ctx.AMPERSAND():
            typ = ReferenceType(typ)
        return [Parameter(typ, id) for id in ids]


    # idlist: ID COMMA idlist | ID;
    def visitIdlist(self, ctx:OPLangParser.IdlistContext):
        if ctx.getChildCount() == 1:
            return [(ctx.ID().getText())]
        return [(ctx.ID().getText())] + self.visit(ctx.idlist())


    # attrdecllist: attrdecl attrdecllist | attrdecl;
    def visitAttrdecllist(self, ctx:OPLangParser.AttrdecllistContext):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.attrdecl())
        return self.visit(ctx.attrdecl()) + self.visit(ctx.attrdecllist())


    # attrdecl: mutattr | immutattr;
    def visitAttrdecl(self, ctx:OPLangParser.AttrdeclContext):
        return self.visit(ctx.mutattr()) if ctx.mutattr() else self.visit(ctx.immutattr())


    # mutattr: (STATIC? | FINAL STATIC | STATIC FINAL) typ attrlist SEMICOLON;
    def visitMutattr(self, ctx: OPLangParser.MutattrContext):
        is_static = bool(ctx.STATIC())
        is_final = bool(ctx.FINAL())
        typ = self.visit(ctx.typ())
        attr_list = self.visit(ctx.attrlist())

        all_attrs = []
        for ids, init in attr_list:
            for i, id_name in enumerate(ids):
                if init and i == len(ids) - 1:
                    all_attrs.append(Attribute(id_name, init))
                else:
                    all_attrs.append(Attribute(id_name))
        return [AttributeDecl(is_static, is_final, typ, all_attrs)]

    # immutattr: (FINAL STATIC? | STATIC FINAL) typ attrlist SEMICOLON;
    def visitImmutattr(self, ctx: OPLangParser.ImmutattrContext):
        is_static = bool(ctx.STATIC())
        typ = self.visit(ctx.typ())
        attr_list = self.visit(ctx.attrlist())

        all_attrs = []
        for ids, init in attr_list:
            for i, id_name in enumerate(ids):
                if init and i == len(ids) - 1:
                    all_attrs.append(Attribute(id_name, init))
                else:
                    all_attrs.append(Attribute(id_name))
        return [AttributeDecl(is_static, True, typ, all_attrs)]

    # attrlist: attrmem COMMA attrlist | attrmem;
    def visitAttrlist(self, ctx:OPLangParser.AttrlistContext):
        if ctx.getChildCount() > 1:
            return [self.visit(ctx.attrmem())] + self.visit(ctx.attrlist())
        else:
            return [self.visit(ctx.attrmem())]

    # attrmem: idlist attrinit;
    def visitAttrmem(self, ctx:OPLangParser.AttrmemContext):
        ids = self.visit(ctx.idlist())
        init = self.visit(ctx.attrinit()) if ctx.attrinit() else None
        return (ids, init)

    # Visit a parse tree produced by OPLangParser#attrinit.
    # attrinit: ASSIGN expr | ;
    def visitAttrinit(self, ctx:OPLangParser.AttrinitContext):
        return self.visit(ctx.expr()) if ctx.expr() else None

    # vardecllist: vardecl vardecllist | vardecl;
    def visitVardecllist(self, ctx:OPLangParser.VardecllistContext):
        if ctx.getChildCount() > 1:
            return self.visit(ctx.vardecl()) + self.visit(ctx.vardecllist())
        return self.visit(ctx.vardecl())
    
    # vardecl: mutvar | immutvar;
    def visitVardecl(self, ctx:OPLangParser.VardeclContext):
        if ctx.mutvar():
            return self.visit(ctx.mutvar())
        return self.visit(ctx.immutvar())

    # mutvar: typ AMPERSAND? varlist SEMICOLON;
    def visitMutvar(self, ctx: OPLangParser.MutvarContext):
        typ = self.visit(ctx.typ())
        ids_inits = self.visit(ctx.varlist())
        if ctx.AMPERSAND():
            typ = ReferenceType(typ)

        all_vars = []
        for ids, init in ids_inits:
            for i, id_name in enumerate(ids):
                if init and i == len(ids) - 1:
                    all_vars.append(Variable(id_name, init))
                else:
                    all_vars.append(Variable(id_name))
        return [VariableDecl(False, typ, all_vars)]

    
    # immutvar: FINAL typ varlist SEMICOLON;
    def visitImmutvar(self, ctx: OPLangParser.ImmutvarContext):
        typ = self.visit(ctx.typ())
        ids_inits = self.visit(ctx.varlist())
        # if ctx.AMPERSAND():
        #     typ = ReferenceType(typ)

        all_vars = []
        for ids, init in ids_inits:
            # Nếu có init thì chỉ gán cho biến cuối
            for i, id_name in enumerate(ids):
                if init and i == len(ids) - 1:
                    all_vars.append(Variable(id_name, init))
                else:
                    all_vars.append(Variable(id_name))

        return [VariableDecl(True, typ, all_vars)]
    
    # varlist: varmem COMMA varlist | varmem;
    def visitVarlist(self, ctx:OPLangParser.VarlistContext):
        if ctx.getChildCount() > 1:
            return [self.visit(ctx.varmem())] + self.visit(ctx.varlist())
        return [self.visit(ctx.varmem())]

    # varmem: idlist varinit;
    def visitVarmem(self, ctx:OPLangParser.VarmemContext):
        ids = self.visit(ctx.idlist())
        init = self.visit(ctx.varinit()) if ctx.varinit() else None
        return (ids, init)
    
    # varinit: ASSIGN expr | ;
    def visitVarinit(self, ctx:OPLangParser.VarinitContext):
        return self.visit(ctx.expr()) if ctx.expr() else None

    # Visit a parse tree produced by OPLangParser#arraylit.
    # arraylit: LSB arraymemlist RSB;
    def visitArraylit(self, ctx:OPLangParser.ArraylitContext):
        elements = self.visit(ctx.arraymemlist()) if ctx.arraymemlist() else []
        return ArrayLiteral(elements)

    # arraymemlist: arraymem COMMA arraymemlist | arraymem | ;
    def visitArraymemlist(self, ctx: OPLangParser.ArraymemlistContext):
        if ctx.getChildCount() == 0:
            return []
        if ctx.getChildCount() == 1:
            return [self.visit(ctx.arraymem())]
        return [self.visit(ctx.arraymem())] + self.visit(ctx.arraymemlist()) 

    # arraymem: INTLIT | FLOATLIT | STRINGLIT | booleanlit | NEW ID LB argnullist RB;
    def visitArraymem(self, ctx):
        if ctx.INTLIT():
            return IntLiteral(int(ctx.INTLIT().getText()))
        elif ctx.FLOATLIT():
            return FloatLiteral(float(ctx.FLOATLIT().getText()))
        elif ctx.STRINGLIT():
            return StringLiteral(ctx.STRINGLIT().getText())
        elif ctx.booleanlit():
            return self.visit(ctx.booleanlit())
        elif ctx.NEW():
            class_name = ctx.ID().getText()
            args = self.visit(ctx.argnullist()) if ctx.argnullist() else []
            return ObjectCreation(class_name, args)
    # Visit a parse tree produced by OPLangParser#booleanlit.
    # booleanlit: TRUE | FALSE;
    def visitBooleanlit(self, ctx:OPLangParser.BooleanlitContext):
        if ctx.TRUE():
            return BoolLiteral(True)
        return BoolLiteral(False)


    # Visit a parse tree produced by OPLangParser#exprlist.
    # exprlist: expr COMMA exprlist | expr;
    def visitExprlist(self, ctx:OPLangParser.ExprlistContext):
        return [self.visit(ctx.expr())] + self.visit(ctx.exprlist()) if ctx.getChildCount() > 1 else [self.visit(ctx.expr())]


    # Visit a parse tree produced by OPLangParser#expr.
    # expr: expr1 (GREATER_EQ | LESS_EQ | GREATER | LESS) expr1 | expr1;
    def visitExpr(self, ctx:OPLangParser.ExprContext):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.expr1(0))
        left = self.visit(ctx.expr1(0))
        operator = ctx.getChild(1).getText()
        right = self.visit(ctx.expr1(1))
        return BinaryOp(left, operator, right)


    # Visit a parse tree produced by OPLangParser#expr1.
    # expr1: expr2 (EQ | NEQ) expr2 | expr2;
    def visitExpr1(self, ctx:OPLangParser.Expr1Context):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.expr2(0))
        left = self.visit(ctx.expr2(0))
        operator = ctx.getChild(1).getText()
        right = self.visit(ctx.expr2(1))
        return BinaryOp(left, operator, right)


    # Visit a parse tree produced by OPLangParser#expr2.
    # expr2: expr2 (AND | OR) expr3 | expr3;
    def visitExpr2(self, ctx:OPLangParser.Expr2Context):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.expr3())
        left = self.visit(ctx.expr2())
        operator = ctx.getChild(1).getText()
        right = self.visit(ctx.expr3())
        return BinaryOp(left, operator, right)


    # Visit a parse tree produced by OPLangParser#expr3.
    # expr3: expr3 (ADD | SUB) expr4 | expr4;
    def visitExpr3(self, ctx:OPLangParser.Expr3Context):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.expr4())
        left = self.visit(ctx.expr3())
        operator = ctx.getChild(1).getText()
        right = self.visit(ctx.expr4())
        return BinaryOp(left, operator, right)


    # Visit a parse tree produced by OPLangParser#expr4.
    # expr4: expr4 (MUL | DIV_I | DIV_F | MOD) expr5 | expr5;
    def visitExpr4(self, ctx:OPLangParser.Expr4Context):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.expr5())
        left = self.visit(ctx.expr4())
        operator = ctx.getChild(1).getText()
        right = self.visit(ctx.expr5())
        return BinaryOp(left, operator, right)


    # Visit a parse tree produced by OPLangParser#expr5.
    # expr5: expr5 CONCAT expr6 | expr6;
    def visitExpr5(self, ctx:OPLangParser.Expr5Context):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.expr6())
        left = self.visit(ctx.expr5())
        operator = ctx.CONCAT().getText()
        right = self.visit(ctx.expr6())
        return BinaryOp(left, operator, right)


    # Visit a parse tree produced by OPLangParser#expr6.
    # expr6: (NOT) expr6 | expr7;
    def visitExpr6(self, ctx:OPLangParser.Expr6Context):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.expr7())
        operator = ctx.getChild(0).getText()
        operand = self.visit(ctx.expr6())
        return UnaryOp(operator, operand)


    # Visit a parse tree produced by OPLangParser#expr7.
    # expr7: (ADD | SUB) expr7 | expr8;
    def visitExpr7(self, ctx:OPLangParser.Expr7Context):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.expr8())
        operator = ctx.getChild(0).getText()
        operand = self.visit(ctx.expr7())
        return UnaryOp(operator, operand)


    # Visit a parse tree produced by OPLangParser#expr8.
    # expr8: expr9 postfixlist;
    def visitExpr8(self, ctx: OPLangParser.Expr8Context):
        base = self.visit(ctx.expr9())
        postfixes = self.visit(ctx.postfixlist())
        if not postfixes:
            return base
        def apply_postfix(acc, postfix):
            return PostfixExpression(acc, [postfix])

        return reduce(apply_postfix, postfixes, base)

    # Visit a parse tree produced by OPLangParser#postfixlist.
    # postfixlist: postfix postfixlist | ;
    def visitPostfixlist(self, ctx: OPLangParser.PostfixlistContext):
        if ctx.getChildCount() == 0:
            return []
        if ctx.postfix():
            first = self.visit(ctx.postfix())
            rest = self.visit(ctx.postfixlist()) if ctx.postfixlist() else []
            return ([first] if first is not None else []) + [p for p in rest if p is not None]
        return []

    # Visit a parse tree produced by OPLangParser#postfix.
    # postfix : LSB expr RSB | DOT ID | DOT ID LB argnullist RB ;
    def visitPostfix(self, ctx:OPLangParser.PostfixContext):
        if ctx.expr():
            return ArrayAccess(self.visit(ctx.expr()))
        if ctx.LB():
            args = self.visit(ctx.argnullist()) if ctx.argnullist() else []
            return MethodCall(ctx.ID().getText(), args)
        if ctx.ID():
            return MemberAccess(ctx.ID().getText())


    # Visit a parse tree produced by OPLangParser#expr9.
    # expr9: NEW ID LB argnullist RB | expr10 ;
    def visitExpr9(self, ctx:OPLangParser.Expr9Context):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.expr10())
        return ObjectCreation(ctx.ID().getText(), self.visit(ctx.argnullist()) if ctx.argnullist() else [])


    # Visit a parse tree produced by OPLangParser#expr10.
    # expr10: THIS | ID | NIL | primitivelit | arraylit | subexpr;
    def visitExpr10(self, ctx:OPLangParser.Expr10Context):
        if ctx.THIS():
            return ThisExpression()
        elif ctx.ID():
            return Identifier(ctx.ID().getText())
        elif ctx.NIL():
            return NilLiteral()
        elif ctx.primitivelit():
            return self.visit(ctx.primitivelit())
        elif ctx.arraylit():
            return self.visit(ctx.arraylit())
        return self.visit(ctx.subexpr())


    # Visit a parse tree produced by OPLangParser#argnullist.
    # argnullist: argprime | ;
    def visitArgnullist(self, ctx:OPLangParser.ArgnullistContext):
        return self.visit(ctx.argprime()) if ctx.argprime() else []


    # Visit a parse tree produced by OPLangParser#argprime.
    # argprime: expr COMMA argprime | expr;
    def visitArgprime(self, ctx:OPLangParser.ArgprimeContext):
        if ctx.getChildCount() == 1:
            return [self.visit(ctx.expr())]
        return [self.visit(ctx.expr())] + self.visit(ctx.argprime())


    # Visit a parse tree produced by OPLangParser#primitivelit.
    # primitivelit: INTLIT | FLOATLIT | STRINGLIT | booleanlit;
    def visitPrimitivelit(self, ctx:OPLangParser.PrimitivelitContext):
        if ctx.INTLIT():
            return IntLiteral(int(ctx.INTLIT().getText()))
        elif ctx.FLOATLIT():
            return FloatLiteral(float(ctx.FLOATLIT().getText()))
        elif ctx.STRINGLIT():
            return StringLiteral(ctx.STRINGLIT().getText())
        elif ctx.booleanlit():
            return self.visit(ctx.booleanlit())

    # Visit a parse tree produced by OPLangParser#subexpr.
    # subexpr: LB expr RB;
    def visitSubexpr(self, ctx:OPLangParser.SubexprContext):
        inner_expr = self.visit(ctx.expr())
        return ParenthesizedExpression(inner_expr)


    # Visit a parse tree produced by OPLangParser#stmtlist.
    # stmtlist: stmt stmtlist | ;
    def visitStmtlist(self, ctx:OPLangParser.StmtlistContext):
        return [self.visitStmt(ctx.stmt())] + self.visitStmtlist(ctx.stmtlist()) if ctx.stmt() else []


    # Visit a parse tree produced by OPLangParser#stmt.
    # stmt: blockstmt | assignstmt | ifstmt | forstmt | breakstmt | continuestmt | returnstmt | methodinstmt;
    def visitStmt(self, ctx:OPLangParser.StmtContext):
        if ctx.blockstmt():
            return self.visit(ctx.blockstmt())
        elif ctx.assignstmt():
            return self.visit(ctx.assignstmt())
        elif ctx.ifstmt():
            return self.visit(ctx.ifstmt())
        elif ctx.forstmt():
            return self.visit(ctx.forstmt())
        elif ctx.breakstmt():
            return self.visit(ctx.breakstmt())
        elif ctx.continuestmt():
            return self.visit(ctx.continuestmt())
        elif ctx.returnstmt():
            return self.visit(ctx.returnstmt())
        elif ctx.methodinstmt():
            return self.visit(ctx.methodinstmt())


    # Visit a parse tree produced by OPLangParser#blockstmt.
    # blockstmt: LP vardecllist? stmtlist RP;
    def visitBlockstmt(self, ctx:OPLangParser.BlockstmtContext):
        var_decls = self.visit(ctx.vardecllist()) if ctx.vardecllist() else []
        stmts = self.visit(ctx.stmtlist())
        return BlockStatement(var_decls, stmts)


    # Visit a parse tree produced by OPLangParser#blockstmt_no_return.
    # blockstmt_no_return: LP vardecllist? stmtlist_no_return RP;
    def visitBlockstmt_no_return(self, ctx:OPLangParser.Blockstmt_no_returnContext):
        var_decls = self.visit(ctx.vardecllist()) if ctx.vardecllist() else []
        stmts = self.visit(ctx.stmtlist_no_return())
        return BlockStatement(var_decls, stmts)


    # Visit a parse tree produced by OPLangParser#stmtlist_no_return.
    # stmtlist_no_return: stmt_no_return stmtlist_no_return | ;
    def visitStmtlist_no_return(self, ctx:OPLangParser.Stmtlist_no_returnContext):
        return [self.visitStmt_no_return(ctx.stmt_no_return())] + self.visitStmtlist_no_return(ctx.stmtlist_no_return()) if ctx.stmt_no_return() else []


    # Visit a parse tree produced by OPLangParser#stmt_no_return.
    # stmt_no_return: blockstmt_no_return | ifstmt | assignstmt | forstmt | breakstmt | continuestmt | methodinstmt;
    def visitStmt_no_return(self, ctx:OPLangParser.Stmt_no_returnContext):
        if ctx.blockstmt_no_return():
            return self.visit(ctx.blockstmt_no_return())
        elif ctx.ifstmt():
            return self.visit(ctx.ifstmt())
        elif ctx.assignstmt():
            return self.visit(ctx.assignstmt())
        elif ctx.forstmt():
            return self.visit(ctx.forstmt())
        elif ctx.breakstmt():
            return self.visit(ctx.breakstmt())
        elif ctx.continuestmt():
            return self.visit(ctx.continuestmt())
        elif ctx.methodinstmt():
            return self.visit(ctx.methodinstmt())


    # Visit a parse tree produced by OPLangParser#assignstmt.
    # assignstmt: lhs ASSIGN expr SEMICOLON;
    def visitAssignstmt(self, ctx:OPLangParser.AssignstmtContext):
        lhs = self.visit(ctx.lhs())
        expr = self.visit(ctx.expr())
        return AssignmentStatement(lhs, expr)


    # Visit a parse tree produced by OPLangParser#lhs.
    # lhs: ID | expr9 postfix postfixlist;
    def visitLhs(self, ctx: OPLangParser.LhsContext):
        if ctx.ID():
            return IdLHS(ctx.ID().getText())

        base = self.visit(ctx.expr9())
        postfixes = []

        if ctx.postfix():
            postfixes.append(self.visit(ctx.postfix()))
        # cộng thêm postfixlist (có thể rỗng)
        if ctx.postfixlist():
            postfixes += self.visit(ctx.postfixlist())

        postfix_expr = PostfixExpression(base, postfixes)
        return PostfixLHS(postfix_expr)


    # Visit a parse tree produced by OPLangParser#ifstmt.
    # ifstmt: IF expr THEN stmt | IF expr THEN stmt ELSE stmt;
    def visitIfstmt(self, ctx:OPLangParser.IfstmtContext):
        condition = self.visit(ctx.expr())
        then_branch = self.visit(ctx.stmt(0))
        else_branch = self.visit(ctx.stmt(1)) if ctx.ELSE() else None
        return IfStatement(condition, then_branch, else_branch)


    # Visit a parse tree produced by OPLangParser#forstmt.
    # forstmt: FOR ID ASSIGN expr (TO | DOWNTO) expr DO stmt;
    def visitForstmt(self, ctx:OPLangParser.ForstmtContext):
        var_name = ctx.ID().getText()
        init_expr = self.visit(ctx.expr(0))
        end_expr = self.visit(ctx.expr(1))
        direction = ctx.getChild(4).getText()
        body = self.visit(ctx.stmt())
        return ForStatement(var_name, init_expr, direction, end_expr, body)


    # Visit a parse tree produced by OPLangParser#breakstmt.
    # breakstmt: BREAK SEMICOLON;
    def visitBreakstmt(self, ctx:OPLangParser.BreakstmtContext):
        return BreakStatement()


    # Visit a parse tree produced by OPLangParser#continuestmt.
    # continuestmt: CONTINUE SEMICOLON;
    def visitContinuestmt(self, ctx:OPLangParser.ContinuestmtContext):
        return ContinueStatement()


    # Visit a parse tree produced by OPLangParser#returnstmt.
    # returnstmt: RETURN expr SEMICOLON;
    def visitReturnstmt(self, ctx:OPLangParser.ReturnstmtContext):
        return ReturnStatement(self.visit(ctx.expr()))


    def visitMethodinstmt(self, ctx: OPLangParser.MethodinstmtContext):
        primary = self.visit(ctx.expr9())  # ThisExpression, Identifier, ObjectCreation, ...
        postfixes = []
        if ctx.postfix():
            postfixes.append(self.visit(ctx.postfix()))
        if ctx.postfixlist():
            postfixes += self.visit(ctx.postfixlist())

        args = self.visit(ctx.argnullist()) if ctx.argnullist() else []

        if postfixes:
            last = postfixes[-1]
            if isinstance(last, MemberAccess):
                postfixes[-1] = MethodCall(last.member_name, args)
            elif isinstance(last, MethodCall):
                postfixes[-1] = MethodCall(last.method_name, args)
            else:
                postfixes.append(MethodCall("", args))
        else:
            postfixes.append(MethodCall("", args))

        postfix_expr = PostfixExpression(primary, postfixes)
        return MethodInvocationStatement((postfix_expr))


    # Visit a parse tree produced by OPLangParser#primitivetyp.
    # primitivetyp: INT | FLOAT | STRING | BOOLEAN;
    def visitPrimitivetyp(self, ctx:OPLangParser.PrimitivetypContext):
        if ctx.INT():
            return PrimitiveType("int")
        elif ctx.FLOAT():
            return PrimitiveType("float")
        elif ctx.STRING():
            return PrimitiveType("string")
        elif ctx.BOOLEAN():
            return PrimitiveType("boolean")


    # Visit a parse tree produced by OPLangParser#classtyp.
    # classtyp: ID;
    def visitClasstyp(self, ctx:OPLangParser.ClasstypContext):
        return ClassType(ctx.ID().getText())


    # Visit a parse tree produced by OPLangParser#arraytyp.
    # arraytyp: (primitivetyp | classtyp) AMPERSAND? LSB INTLIT RSB;
    def visitArraytyp(self, ctx:OPLangParser.ArraytypContext):
        typ = self.visit(ctx.getChild(0))
        size = int(ctx.INTLIT().getText())
        if ctx.AMPERSAND():
            typ = ReferenceType(typ)
        return ArrayType(typ, size)
