"""
Static Semantic Checker for OPLang Programming Language

This module implements a comprehensive static semantic checker using visitor pattern
for the OPLang object-oriented programming language. It performs type checking,
scope management, inheritance validation, and detects all semantic errors as 
specified in the OPLang language specification.
"""

from functools import reduce
from threading import local
from typing import Dict, List, Set, Optional, Any, Tuple, Union, NamedTuple
from ..utils.visitor import ASTVisitor
from ..utils.nodes import (
    ASTNode, Program, ClassDecl, AttributeDecl, Attribute, MethodDecl,
    ConstructorDecl, DestructorDecl, Parameter, VariableDecl, Variable,
    AssignmentStatement, IfStatement, ForStatement, BreakStatement,
    ContinueStatement, ReturnStatement, MethodInvocationStatement,
    BlockStatement, PrimitiveType, ArrayType, ClassType, ReferenceType,
    IdLHS, PostfixLHS, BinaryOp, UnaryOp, PostfixExpression, PostfixOp,
    MethodCall, MemberAccess, ArrayAccess, ObjectCreation, Identifier,
    ThisExpression, ParenthesizedExpression, IntLiteral, FloatLiteral,
    BoolLiteral, StringLiteral, ArrayLiteral, NilLiteral
)
from .static_error import (
    StaticError, Redeclared, UndeclaredIdentifier, UndeclaredClass,
    UndeclaredAttribute, UndeclaredMethod, CannotAssignToConstant,
    TypeMismatchInStatement, TypeMismatchInExpression, TypeMismatchInConstant,
    MustInLoop, IllegalConstantExpression, IllegalArrayLiteral,
    IllegalMemberAccess, NoEntryPoint
)

class MeType:
    def __init__(self, paramtype, rettype):
        self.paramtype = paramtype
        self.rettype = rettype
    def __str__(self):
        return "MType("+str(self.paramtype)+","+str(self.rettype)+")"


class Symbol:
    def __init__(self, name, mtype, value=None):
        self.name = name
        self.mtype = mtype
        self.value = value
    def __str__(self):
        return "Symbol("+str(self.name)+","+str(self.mtype)+","+str(self.value)+")"

class Stack:
    def __init__(self):
        self.stack = []

    def isEmpty(self):
        return True if len(self.stack) == 0 else False

    def length(self):
        return len(self.stack)

    def top(self):
        return self.stack[-1]

    def push(self, x):
        self.stack.append(x)

    def pop(self):
        try:
            self.stack.pop()
            return True
        except IndexError:
            return False

class StaticChecker(ASTVisitor):
    """
    Stateless static semantic checker for OPLang using visitor pattern.
    
    Checks for all 10 error types specified in OPLang semantic constraints:
    1. Redeclared - Variables, constants, attributes, classes, methods, parameters
    2. Undeclared - Identifiers, classes, attributes, methods  
    3. CannotAssignToConstant - Assignment to final variables/attributes
    4. TypeMismatchInStatement - Type incompatibilities in statements
    5. TypeMismatchInExpression - Type incompatibilities in expressions
    6. TypeMismatchInConstant - Type incompatibilities in constant declarations
    7. MustInLoop - Break/continue outside loop contexts
    8. IllegalConstantExpression - Invalid expressions in constant initialization
    9. IllegalArrayLiteral - Inconsistent types in array literals
    10. IllegalMemberAccess - Improper access to static/instance members

    Also checks for valid entry point: static void main() with no parameters.
    """
    def check_program(self, ast):
        """Convenience method to run checker on AST."""
        try:
            global_env = [{"class": "io", "statics": {"attrs": [], "methods": self.global_env}}]
            self.visit_program(ast, global_env)
            return "Static checking passed"
        except StaticError as e:
            return str(e)
    global_env = [
        Symbol("readInt", MeType([], PrimitiveType("int"))),
        Symbol("writeInt", MeType([PrimitiveType("int")], PrimitiveType("void"))),
        Symbol("writeIntLn", MeType([PrimitiveType("int")], PrimitiveType("void"))),
        Symbol("readFloat", MeType([], PrimitiveType("float"))),
        Symbol("writeFloat", MeType([PrimitiveType("float")], PrimitiveType("void"))),
        Symbol("writeFloatLn", MeType([PrimitiveType("float")], PrimitiveType("void"))),
        Symbol("readBool", MeType([], PrimitiveType("bool"))),
        Symbol("writeBool", MeType([PrimitiveType("bool")], PrimitiveType("void"))),
        Symbol("writeBoolLn", MeType([PrimitiveType("bool")], PrimitiveType("void"))),
        Symbol("readStr", MeType([], PrimitiveType("string"))),
        Symbol("writeStr", MeType([PrimitiveType("string")], PrimitiveType("void"))),
        Symbol("writeStrLn", MeType([PrimitiveType("string")], PrimitiveType("void"))),
    ]

    # ============================================
    # LOOKUP FUNCTIONS
    # ============================================

    def lookupClass(self, name, env):
        """Tìm class theo tên (global scope)."""
        found = next(
            (cls for cls in reversed(env) if cls.get("class") == name),
            None,
        )
        return [bool(found), found, None if not found else env.index(found)]

    def lookupVarFromGlobal(self, name, env, current_class):
        """Tìm symbol trong toàn bộ môi trường, từ local → global."""
        # Duyệt từ local nhất (c[0]) đến global (c[-1])
        def find_in_env(acc, e):
            if acc:
                return acc
            # kiểm tra biến / method trong env
            for scope_type in ["local", "statics", "locals"]:
                scopes = e.get(scope_type, {})
                for kind in ["attrs", "methods"]:
                    items = scopes.get(kind, [])
                    match = next((x for x in items if x["name"] == name), None)
                    if match:
                        return [True, match, kind[:-1], e.get("class", None)]
            return None

        result = reduce(find_in_env, env, None)
        return result if result else [False, None, None]

    def lookupVarFromTail(self, name, env, current_class, parents=None):
        """
        Tìm biến trong current_class hoặc lớp cha, theo hướng local → global.
        `parents` là danh sách các lớp cha.
        """
        # duyệt c từ local → global
        def find_in_env(acc, e):
            if acc:
                return acc
            if e.get("class") == current_class:
                for scope_type in ["locals", "statics"]:
                    for kind in ["attrs", "methods"]:
                        items = e[scope_type].get(kind, [])
                        match = next((x for x in items if x["name"] == name), None)
                        if match:
                            return [True, match, kind[:-1], current_class]
            return None

        result = reduce(find_in_env, env, None)
        if result:
            return result

        # nếu không thấy, tìm trong lớp cha (kế thừa)
        if parents:
            for p in parents:
                parent_found = self.lookupVarFromTail(name, env, p)
                if parent_found[0]:
                    return parent_found + ["inherited"]
        return [False, None, None]

    def lookupInside(self, name, env):
        """Tìm identifier theo ngữ cảnh local → nonlocal → global."""
        # kiểm tra cục bộ
        local_scope = env[0].get("local", [])
        match = next((x for x in local_scope if x["name"] == name), None)
        if match:
            return [True, match, "local"]

        # kiểm tra trong class hiện tại và cha
        current = env[0].get("current", None)
        inherit = env[0].get("inherit", [])
        found = self.lookupVarFromTail(name, env, current, inherit)
        if found[0]:
            return found

        # không tìm thấy
        return [False, None, None]

    def declare_entities(self, entities, declared_type, env, is_final=False, kind="Variable"):
        """
        Hàm high-order để khai báo biến/attribute.
        Hạn chế dùng vòng lặp, tuân thủ functional.
        """
        current_scope = env[0]["local"]
        def add_entity(acc, ent):
            # Kiểm tra trong scope hiện tại + danh sách đang thêm
            all_names = [e["name"] for e in current_scope] + [e["name"] for e in acc]
            if ent.name in all_names:
                raise Redeclared(kind, ent.name)

            init_type = ent.init_value.accept(self, env) if getattr(ent, "init_value", None) else None

            if is_final and not init_type:
                raise IllegalConstantExpression(ent)
            if is_final and init_type and init_type[0] != declared_type.type_name:
                raise TypeMismatchInConstant(ent)

            return acc + [{
                "name": ent.name,
                "type": declared_type.type_name,
                "const": is_final,
                "value_type": init_type[0] if init_type else None
            }]
        return reduce(add_entity, entities, [])

    # ============================================
    # ============================================
    # ============================================
    # ============================================
    # ============================================
    # ============================================
    # ============================================
         
    def visit_program(self, node: "Program", o: Any = None):
        base_env = [{"class": "io", "statics": {"attrs": [], "methods": self.global_env}}]
        env = reduce(lambda acc, c: acc + [c.accept(self, acc)], node.class_decls, base_env)

        has_main = any(
            isinstance(m, MethodDecl)
            and m.name == "main"
            and m.is_static
            and isinstance(m.return_type, PrimitiveType)
            and m.return_type.type_name == "void"
            and len(m.params) == 0
            for d in node.class_decls
            for m in d.members
        )
        if not has_main:
            raise NoEntryPoint()

     
    def visit_class_decl(self, node: "ClassDecl", o: Any = None):
        cname = node.name
        pname = node.superclass
        # Redeclared class check
        if self.lookupClass(cname, o)[0]:
            raise Redeclared("Class", cname)

        # Build class environment
        class_env = {
            "class": cname,
            "statics": {"attrs": [], "methods": []},
            "locals": {"attrs": [], "methods": []},
            "inherit": [pname] if pname else [],
        }

        # Validate parent
        if pname:
            found = self.lookupClass(pname, o)
            if not found[0]:
                raise UndeclaredClass(pname)
            class_env["inherit"] += found[1].get("inherit", [])

        # Traverse members (functional)
        list(map(lambda m: m.accept(self, [class_env] + o), node.members))
        o.append(class_env)
        return class_env
    
    def visit_attribute_decl(self, node: "AttributeDecl", o: Any = None):
        """
        Handle both static/instance and const attributes.
        Checks:
        - Redeclared(Attribute)
        - IllegalConstantExpression (missing init for const)
        - TypeMismatchInConstant (init type != declared type)
        """
        kind = "statics" if node.is_static else "locals"
        declared_type = node.attr_type.accept(self, o)
        o[kind]["attrs"] += self.declare_entities(node.attributes, declared_type, o, node.is_final, "Attribute")



    def visit_attribute(self, node: "Attribute", o: Any = None):
        pass

    # Method declarations
     
    def visit_method_decl(self, node: "MethodDecl", o: Any = None):
        kind = "statics" if node.is_static else "locals"
        target = o[0][kind]["methods"]
        if any(m["name"] == node.name for m in target):
            raise Redeclared("Method", node.name)

        method_info = {
            "name": node.name,
            "type": node.return_type.type_name if isinstance(node.return_type, PrimitiveType) else str(node.return_type),
            "params": [],
            "return_type": node.return_type.type_name if isinstance(node.return_type, PrimitiveType) else None,
            "static": node.is_static,
        }

        local_env = [{"current": o[0]["class"], "inherit": o[0].get("inherit", []), "local": [], "return_type": method_info["return_type"]}] + o
        list(map(lambda p: self.visit_parameter(p, local_env), node.params))
        if node.body:
            self.visit_block_statement(node.body, local_env)

        target.append(method_info)
     
    def visit_constructor_decl(self, node: "ConstructorDecl", o: Any = None):
        env = [{"current": o[0]["class"], "local": []}] + o
        list(map(lambda p: self.visit_parameter(p, env), node.params))
        if node.body:
            self.visit_block_statement(node.body, env)

     
    def visit_destructor_decl(self, node: "DestructorDecl", o: Any = None):
          if node.body:
            self.visit_block_statement(node.body, [{"current": o[0]["class"], "local": []}] + o)

     
    def visit_parameter(self, node: "Parameter", o: Any = None):
        local_scope = o[0]["local"]
        if any(v["name"] == node.name for v in local_scope):
            raise Redeclared("Parameter", node.name)
        local_scope.append({"name": node.name, "type": node.param_type.type_name, "const": False})

    # Type system
     
    def visit_primitive_type(self, node: "PrimitiveType", o: Any = None):
        return node

     
    def visit_array_type(self, node: "ArrayType", o: Any = None):
        return node

     
    def visit_class_type(self, node: "ClassType", o: Any = None):
        return node

     
    def visit_reference_type(self, node: "ReferenceType", o: Any = None):
        return node

    # Statements
     
    def visit_block_statement(self, node: "BlockStatement", o: Any = None):
        # nếu block là root của method (không có local nào trước đó) thì giữ nguyên scope
        new_scope = [{"local": [], "current": o[0].get("current"), "inherit": o[0].get("inherit", []),
                  "return_type": o[0].get("return_type", None)}] + o
        # new_scope = o  # KHÔNG tạo thêm scope mới ở đây

        # duyệt các biến và statement
        list(map(lambda v: v.accept(self, new_scope), node.var_decls))
        list(map(lambda s: s.accept(self, new_scope), node.statements))


     
    def visit_variable_decl(self, node: "VariableDecl", o: Any = None):
        declared_type = node.var_type.accept(self, o)
        local_scope = o[0]["local"]

        for var in node.variables:
            # Kiểm tra redeclaration
            if any(s["name"] == var.name for s in local_scope):
                raise Redeclared("Constant" if node.is_final else "Variable", var.name)

            init_type = var.init_value.accept(self, o) if var.init_value else None

            # Kiểm tra constant
            if node.is_final:
                if not init_type:
                    raise IllegalConstantExpression(var)
                if init_type[0] != declared_type.type_name:
                    raise TypeMismatchInConstant(var)
            else:
                # Kiểm tra type mismatch cho biến thường
                if init_type and init_type[0] != declared_type.type_name:
                    raise TypeMismatchInStatement(node)

            # Thêm vào scope
            local_scope.append({
                "name": var.name,
                "type": declared_type.type_name,
                "const": node.is_final,
                "value_type": init_type[0] if init_type else None
            })


     
    def visit_variable(self, node: "Variable", o: Any = None):
        pass

    # chưa xử lý postfix lhs
    def visit_assignment_statement(self, node: "AssignmentStatement", o: Any = None):
        lhs = node.lhs.accept(self, o)
        if isinstance(lhs, list):  # nếu lỡ trả về kiểu [type, const]
            lhs = lhs[0]
        elif lhs is None:
            # fallback: lấy trực tiếp tên nếu node.lhs là IdLHS
            lhs = getattr(node.lhs, "name", None)

        rhs = node.rhs.accept(self, o)
        if rhs is None:
            raise TypeMismatchInStatement(node)

        lookup = self.lookupInside(lhs, o)
        if not lookup[0]:
            raise UndeclaredIdentifier(lhs)
        sym = lookup[1]

        if sym.get("const", False):
            raise CannotAssignToConstant(node)

        if sym["type"] != rhs[0]:
            raise TypeMismatchInStatement(node)


     
    def visit_if_statement(self, node: "IfStatement", o: Any = None):
        cond = node.condition.accept(self, o)
        if cond[0] != "bool":
            raise TypeMismatchInStatement(node)
        node.then_stmt.accept(self, o)
        if node.else_stmt:
            node.else_stmt.accept(self, o)
     
    def visit_for_statement(self, node: "ForStatement", o: Any = None):
        var = node.variable
        lookup = self.lookupInside(var, o)
        if not lookup[0] or lookup[1]["type"] != "int":
            raise TypeMismatchInStatement(node)
        start = node.start_expr.accept(self, o)
        end = node.end_expr.accept(self, o)
        if start[0] != "int" or end[0] != "int":
            raise TypeMismatchInStatement(node)
        loop_scope = [{"in_loop": True, "current": o[0]["current"], "inherit": o[0]["inherit"], "return_type": o[0].get("return_type")}]
        node.body.accept(self, loop_scope + o)
     
    def visit_break_statement(self, node: "BreakStatement", o: Any = None):
        if not any(scope.get("in_loop", False) for scope in o):
            raise MustInLoop(node)

     
    def visit_continue_statement(self, node: "ContinueStatement", o: Any = None):
        if not any(scope.get("in_loop", False) for scope in o):
            raise MustInLoop(node)

     
    def visit_return_statement(self, node: "ReturnStatement", o: Any = None):
        expr_type = node.value.accept(self, o) if node.value else ["void", True]
        expected_type = o[0].get("return_type", "void")
        if expr_type[0] != expected_type:
            raise TypeMismatchInStatement(node)

     
    def visit_method_invocation_statement(
        self, node: "MethodInvocationStatement", o: Any = None
    ):
        node.method_call.accept(self, o)

    # Left-hand side (LHS)
     
    def visit_id_lhs(self, node: "IdLHS", o: Any = None):
        return node.name

     
    def visit_postfix_lhs(self, node: "PostfixLHS", o: Any = None):
        expr_type = node.postfix_expr.accept(self, o)
        return expr_type[0]

    # Expressions
     
    def visit_binary_op(self, node: "BinaryOp", o: Any = None):
        left = node.left.accept(self, o)
        right = node.right.accept(self, o)
        op = node.operator

        numeric_ops = ["+", "-", "*", "/"]
        compare_ops = ["<", "<=", ">", ">="]
        equality_ops = ["==", "!="]
        logical_ops = ["&&", "||"]
        concat_ops = ["^"]

        # Arithmetic
        if op in numeric_ops:
            if left[0] not in ["int", "float"] or right[0] not in ["int", "float"]:
                raise TypeMismatchInExpression(node)
            return ["float" if "float" in (left[0], right[0]) else "int", False]

        # Comparison
        if op in compare_ops:
            if left[0] not in ["int", "float"] or right[0] not in ["int", "float"]:
                raise TypeMismatchInExpression(node)
            return ["bool", False]

        # Equality
        if op in equality_ops:
            if left[0] != right[0]:
                raise TypeMismatchInExpression(node)
            return ["bool", False]

        # Logical
        if op in logical_ops:
            if left[0] != "bool" or right[0] != "bool":
                raise TypeMismatchInExpression(node)
            return ["bool", False]

        # String concatenation
        if op in concat_ops:
            if left[0] != "string" or right[0] != "string":
                raise TypeMismatchInExpression(node)
            return ["string", False]

        raise TypeMismatchInExpression(node)

     
    def visit_unary_op(self, node: "UnaryOp", o: Any = None):
        expr = node.operand.accept(self, o)
        op = node.operator
        if op == "!":
            if expr[0] != "bool":
                raise TypeMismatchInExpression(node)
            return ["bool", False]
        elif op == "-":
            if expr[0] not in ["int", "float"]:
                raise TypeMismatchInExpression(node)
            return [expr[0], False]
        raise TypeMismatchInExpression(node)

     
    def visit_postfix_expression(self, node: "PostfixExpression", o: Any = None):
        primary_type = node.primary.accept(self, o)  # [type_name, is_const_expr]
        current_type = primary_type[0]

        for op in node.postfix_ops:
            if isinstance(op, MemberAccess):
                member_name = op.member_name
                found = self.lookupVarFromTail(member_name, o, current_type)
                if not found[0]:
                    raise UndeclaredAttribute(member_name)
                current_type = found[1]["type"]

            elif isinstance(op, MethodCall):
                method_name = op.method_name
                found = self.lookupVarFromTail(method_name, o, current_type)
                if not found[0]:
                    raise UndeclaredMethod(method_name)
                # Kiểm tra args
                expected_params = found[1].get("params", [])
                actual_args = [a.accept(self, o) for a in op.args]
                if len(actual_args) != len(expected_params):
                    raise TypeMismatchInExpression(op)
                for act, exp in zip(actual_args, expected_params):
                    if act[0] != exp:
                        raise TypeMismatchInExpression(op)
                current_type = found[1]["return_type"]

            elif isinstance(op, ArrayAccess):
                idx = op.index.accept(self, o)
                if idx[0] != "int":
                    raise TypeMismatchInExpression(op)
                # Giả sử array type đã được xử lý ở đâu đó
                current_type = "element"

        return [current_type, False]

     
    def visit_method_call(self, node: "MethodCall", o: Any = None):
        return {"method": node.method_name, "args": node.args}

     
    def visit_member_access(self, node: "MemberAccess", o: Any = None):
        return {"member": node.member_name}

     
    def visit_array_access(self, node: "ArrayAccess", o: Any = None):
        return {"index": node.index}

     
    def visit_object_creation(self, node: "ObjectCreation", o: Any = None):
        class_name = node.class_name
        found = self.lookupClass(class_name, o)
        if not found[0]:
            raise UndeclaredClass(class_name)
        return [class_name, False]

     
    # def visit_static_method_invocation(
    #     self, node: "StaticMethodInvocation", o: Any = None
    # ):
    #     pass

     
    # def visit_static_member_access(self, node: "StaticMemberAccess", o: Any = None):
    #     pass

     
    # def visit_method_invocation(self, node: "MethodInvocation", o: Any = None):
    #     pass

     
    def visit_identifier(self, node: "Identifier", o: Any = None):
        found = self.lookupInside(node.name, o)
        if not found[0]:
            raise UndeclaredIdentifier(node.name)
        symbol = found[1]
        return [symbol["type"], symbol.get("const", False)]

     
    def visit_this_expression(self, node: "ThisExpression", o: Any = None):
        return ["this", False]

     
    def visit_parenthesized_expression(
        self, node: "ParenthesizedExpression", o: Any = None
    ):
        return node.expr.accept(self, o)

    # Literals
    def visit_int_literal(self, node: "IntLiteral", o: Any = None):
        return ["int", True]

     
    def visit_float_literal(self, node: "FloatLiteral", o: Any = None):
        return ["float", True]

     
    def visit_bool_literal(self, node: "BoolLiteral", o: Any = None):
        return ["bool", True]

     
    def visit_string_literal(self, node: "StringLiteral", o: Any = None):
        return ["string", True]

     
    def visit_array_literal(self, node: "ArrayLiteral", o: Any = None):
        list = [x.accept(self, o) for x in node.value]
        res = all(map(lambda x: x[0] == list[0][0] and x[1] == True, list))
        if not res:
            raise IllegalArrayLiteral(node)
        return [list[0][0], False]

     
    def visit_nil_literal(self, node: "NilLiteral", o: Any = None):
        return ["nil", True]