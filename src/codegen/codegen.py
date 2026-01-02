"""
Code Generator for OPLang programming language.
This module implements a code generator that traverses AST nodes and generates
Java bytecode using the Emitter and Frame classes.
"""

from typing import Any, List, Optional
from ..utils.visitor import ASTVisitor
from ..utils.nodes import *
from .emitter import Emitter
from .frame import Frame
from .error import IllegalOperandException, IllegalRuntimeException
from .io import IO_SYMBOL_LIST
from .utils import *
from functools import *


class CodeGenerator(ASTVisitor):
    """
    Code generator for OPLang.
    Traverses AST and generates JVM bytecode.
    """
    
    def __init__(self):
        self.current_class = None
        self.emit = None
        self.current_superclass = None
        # Global Symbol Tables to track Class Definitions
        self.class_fields = {}
        self.class_methods = {}

    def sanitize_type(self, t):
        """
        Reconstruct type objects to ensure they match the classes imported 
        in this module/emitter, avoiding 'isinstance' failures due to import paths.
        """
        if t is None: return None
        type_name = t.__class__.__name__
        
        if type_name == "PrimitiveType":
            return PrimitiveType(t.type_name)
        elif type_name == "ClassType":
            return ClassType(t.class_name)
        elif type_name == "ArrayType":
            return ArrayType(self.sanitize_type(t.element_type), t.size)
        elif type_name == "ReferenceType":
            return ReferenceType(self.sanitize_type(t.referenced_type))
        return t

    # --- Safe Type Checkers (Avoid reliance on emitter's strict type() checks) ---
    def is_int(self, t):
        return hasattr(t, "type_name") and t.type_name == "int"

    def is_float(self, t):
        return hasattr(t, "type_name") and t.type_name == "float"

    def is_bool(self, t):
        return hasattr(t, "type_name") and t.type_name == "boolean"

    def is_string(self, t):
        return hasattr(t, "type_name") and t.type_name == "string"

    def is_void(self, t):
        return hasattr(t, "type_name") and t.type_name == "void"
    # --------------------------------------------------------------------------------

    # ============================================================================
    # Program and Class Declarations
    # ============================================================================

    def visit_program(self, node: "Program", o: Any = None):
        # Phase 1: Pre-scan all classes to build Symbol Tables
        for class_decl in node.class_decls:
            c_name = class_decl.name
            self.class_fields[c_name] = {}
            self.class_methods[c_name] = {}
            
            for member in class_decl.members:
                if isinstance(member, AttributeDecl):
                    for attr in member.attributes:
                        self.class_fields[c_name][attr.name] = self.sanitize_type(member.attr_type)
                elif isinstance(member, MethodDecl):
                    self.class_methods[c_name][member.name] = self.sanitize_type(member.return_type)

        # Phase 2: Generate Code
        for class_decl in node.class_decls:
            self.visit(class_decl, o)
        

    def visit_class_decl(self, node: "ClassDecl", o: Any = None):
        self.current_class = node.name
        self.current_superclass = node.superclass if node.superclass else "java/lang/Object"
        class_file = node.name + ".j"
        self.emit = Emitter(class_file)
        
        # Cache static methods for return type inference within current class
        self.user_static_methods = {}
        has_constructor = False  # Flag to check if constructor exists
        
        for member in node.members:
            if isinstance(member, MethodDecl) and member.is_static:
                self.user_static_methods[member.name] = member.return_type
            if isinstance(member, ConstructorDecl):
                has_constructor = True

        self.emit.print_out(self.emit.emit_prolog(node.name, self.current_superclass))
        
        for member in node.members:
            self.visit(member, o)

        static_init_stmts = []
        for member in node.members:
            if isinstance(member, AttributeDecl) and member.is_static:
                for attr in member.attributes:
                    if attr.init_value is not None:
                        static_init_stmts.append((attr, member.attr_type))

        if len(static_init_stmts) > 0:
            # Generate static initializer method
            self.emit.print_out(self.emit.emit_method("<clinit>", FunctionType([], PrimitiveType("void")), True))
            
            frame = Frame("<clinit>", PrimitiveType("void"))
            frame.enter_scope(True)
            self.emit.print_out(self.emit.emit_label(frame.get_start_label(), frame))

            for attr, attr_type in static_init_stmts:
                # Compile init expression
                # Note: Static context does not have 'this', use IO_SYMBOL_LIST for globals
                code, typ = self.visit(attr.init_value, Access(frame, IO_SYMBOL_LIST))
                self.emit.print_out(code)

                # Type coercion (e.g., int -> float)
                safe_type = self.sanitize_type(attr_type)
                if self.is_float(safe_type) and self.is_int(typ):
                    self.emit.print_out(self.emit.emit_i2f(frame))
                
                # Assign to static field
                lexeme = self.current_class + "/" + attr.name
                self.emit.print_out(self.emit.emit_put_static(lexeme, safe_type, frame))

            self.emit.print_out(self.emit.emit_return(PrimitiveType("void"), frame))
            self.emit.print_out(self.emit.emit_label(frame.get_end_label(), frame))
            self.emit.print_out(self.emit.emit_end_method(frame))
            frame.exit_scope()
        
        # --- AUTO-GENERATE DEFAULT CONSTRUCTOR IF MISSING ---
        if not has_constructor:
            # Generate: public <init>() { super(); }
            self.emit.print_out(self.emit.emit_method("<init>", FunctionType([], PrimitiveType("void")), False))
            
            frame = Frame("<init>", PrimitiveType("void"))
            frame.enter_scope(True)
            this_idx = frame.get_new_index() # Index 0 for 'this'
            
            self.emit.print_out(self.emit.emit_label(frame.get_start_label(), frame))
            
            # Load 'this'
            self.emit.print_out(self.emit.emit_read_var("this", ClassType(node.name), this_idx, frame))
            self.emit.print_out(self.emit.emit_invoke_special(
                frame, 
                self.current_superclass + "/<init>", 
                FunctionType([], PrimitiveType("void"))
            ))
            
            self.emit.print_out(self.emit.emit_return(PrimitiveType("void"), frame))
            self.emit.print_out(self.emit.emit_label(frame.get_end_label(), frame))
            self.emit.print_out(self.emit.emit_end_method(frame))
            frame.exit_scope()
        # ----------------------------------------------------
        
        self.emit.emit_epilog()

    # ============================================================================
    # Attribute Declarations
    # ============================================================================

    def visit_attribute_decl(self, node: "AttributeDecl", o: Any = None):
        for attr in node.attributes:
            self.visit(attr, node)

    def visit_attribute(self, node: "Attribute", o: Any = None):
        attr_decl = o
        field_name = node.name 
        safe_type = self.sanitize_type(attr_decl.attr_type)
        
        if attr_decl.is_static:
            self.emit.print_out(
                self.emit.emit_attribute(
                    field_name,
                    safe_type,
                    attr_decl.is_final
                )
            )
        else:
            self.emit.print_out(
                self.emit.jvm.emitINSTANCEFIELD(
                    field_name,
                    self.emit.get_jvm_type(safe_type)
                )
            )

    # ============================================================================
    # Method Declarations
    # ============================================================================

    def visit_method_decl(self, node: "MethodDecl", o: Any = None):
        frame = Frame(node.name, self.sanitize_type(node.return_type))
        self.generate_method(node, frame, node.is_static)

    def visit_constructor_decl(self, node: "ConstructorDecl", o: Any = None):
        frame = Frame("<init>", PrimitiveType("void"))
        param_types = [self.sanitize_type(p.param_type) for p in node.params]
        func_type = FunctionType(param_types, PrimitiveType("void"))
        
        self.emit.print_out(self.emit.emit_method("<init>", func_type, False))
        
        frame.enter_scope(True)
        from_label = frame.get_start_label()
        to_label = frame.get_end_label()
        
        this_idx = frame.get_new_index()
        self.emit.print_out(self.emit.emit_var(this_idx, "this", ClassType(self.current_class), from_label, to_label))
        
        sym_list = [Symbol("this", ClassType(self.current_class), Index(this_idx))]
        
        for param in node.params:
            idx = frame.get_new_index()
            safe_type = self.sanitize_type(param.param_type)
            self.emit.print_out(self.emit.emit_var(idx, param.name, safe_type, from_label, to_label))
            sym_list.append(Symbol(param.name, safe_type, Index(idx)))
            
        sym_list = IO_SYMBOL_LIST + sym_list
        
        self.emit.print_out(self.emit.emit_label(from_label, frame))
        
        # Super()
        self.emit.print_out(self.emit.emit_read_var("this", ClassType(self.current_class), this_idx, frame))
        self.emit.print_out(self.emit.emit_invoke_special(
            frame, 
            self.current_superclass + "/<init>", 
            FunctionType([], PrimitiveType("void"))
        ))
        
        o = SubBody(frame, sym_list)
        self.visit(node.body, o)
        
        self.emit.print_out(self.emit.emit_return(PrimitiveType("void"), frame))
        self.emit.print_out(self.emit.emit_label(to_label, frame))
        self.emit.print_out(self.emit.emit_end_method(frame))
        frame.exit_scope()

    def visit_destructor_decl(self, node: "DestructorDecl", o: Any = None):
        frame = Frame("finalize", PrimitiveType("void"))
        func_type = FunctionType([], PrimitiveType("void"))
        
        self.emit.print_out(self.emit.emit_method("finalize", func_type, False))
        
        frame.enter_scope(True)
        from_label = frame.get_start_label()
        to_label = frame.get_end_label()
        
        this_idx = frame.get_new_index()
        self.emit.print_out(self.emit.emit_var(this_idx, "this", ClassType(self.current_class), from_label, to_label))
        sym_list = [Symbol("this", ClassType(self.current_class), Index(this_idx))]
        sym_list = IO_SYMBOL_LIST + sym_list
        
        self.emit.print_out(self.emit.emit_label(from_label, frame))
        
        o = SubBody(frame, sym_list)
        self.visit(node.body, o)
        
        self.emit.print_out(self.emit.emit_return(PrimitiveType("void"), frame))
        self.emit.print_out(self.emit.emit_label(to_label, frame))
        self.emit.print_out(self.emit.emit_end_method(frame))
        frame.exit_scope()

    def visit_parameter(self, node: "Parameter", o: Any = None):
        pass

    def generate_method(self, node: "MethodDecl", frame: Frame, is_static: bool):
        class_name = self.current_class
        method_name = node.name
        param_types = [self.sanitize_type(p.param_type) for p in node.params]
        return_type = self.sanitize_type(node.return_type)
        func_type = FunctionType(param_types, return_type)
        
        # Handle main method signature for JVM (String[] args)
        is_main = (method_name == "main" and len(node.params) == 0 and is_static and self.is_void(return_type))
        
        if is_main:
            str_arr_type = ArrayType(PrimitiveType("string"), 0)
            main_func_type = FunctionType([str_arr_type], return_type)
            self.emit.print_out(self.emit.emit_method(method_name, main_func_type, is_static))
        else:
            self.emit.print_out(self.emit.emit_method(method_name, func_type, is_static))
        
        frame.enter_scope(True)
        from_label = frame.get_start_label()
        to_label = frame.get_end_label()
        
        if is_main:
            frame.get_new_index() 
        
        sym_list = []
        if not is_static:
            this_idx = frame.get_new_index()
            self.emit.print_out(self.emit.emit_var(this_idx, "this", ClassType(class_name), from_label, to_label))
            sym_list.append(Symbol("this", ClassType(class_name), Index(this_idx)))
        
        for param in node.params:
            idx = frame.get_new_index()
            safe_type = self.sanitize_type(param.param_type)
            self.emit.print_out(self.emit.emit_var(idx, param.name, safe_type, from_label, to_label))
            sym_list.append(Symbol(param.name, safe_type, Index(idx)))
        
        sym_list = IO_SYMBOL_LIST + sym_list
        self.emit.print_out(self.emit.emit_label(from_label, frame))
        
        o = SubBody(frame, sym_list)
        self.visit(node.body, o)
        
        # Ensure return
        self.emit.print_out(self.emit.emit_label(to_label, frame))
        
        if self.is_void(return_type):
            self.emit.print_out(self.emit.emit_return(return_type, frame))
        else:
            if self.is_int(return_type) or self.is_bool(return_type):
                self.emit.print_out(self.emit.emit_push_iconst(0, frame))
            elif self.is_float(return_type):
                self.emit.print_out(self.emit.emit_push_fconst("0.0", frame))
            else:
                self.emit.print_out(self.emit.jvm.emitPUSHNULL())
                frame.push()
            self.emit.print_out(self.emit.emit_return(return_type, frame))

        self.emit.print_out(self.emit.emit_end_method(frame))
        frame.exit_scope()

    # ============================================================================
    # Type System
    # ============================================================================

    def visit_primitive_type(self, node: "PrimitiveType", o: Any = None):
        return self.sanitize_type(node)

    def visit_array_type(self, node: "ArrayType", o: Any = None):
        return self.sanitize_type(node)

    def visit_class_type(self, node: "ClassType", o: Any = None):
        return self.sanitize_type(node)

    def visit_reference_type(self, node: "ReferenceType", o: Any = None):
        return self.sanitize_type(node)

    # ============================================================================
    # Statements
    # ============================================================================

    def visit_block_statement(self, node: "BlockStatement", o: SubBody = None):
        if o is None: return
        for var_decl in node.var_decls:
            o = self.visit(var_decl, o)
        for stmt in node.statements:
            self.visit(stmt, o)

    def visit_variable_decl(self, node: "VariableDecl", o: SubBody = None):
        if o is None: return o
        frame = o.frame
        from_label = frame.get_start_label()
        to_label = frame.get_end_label()
        new_sym = []
        safe_var_type = self.sanitize_type(node.var_type)
        
        for var in node.variables:
            idx = frame.get_new_index()
            self.emit.print_out(self.emit.emit_var(idx, var.name, safe_var_type, from_label, to_label))
            new_sym.append(Symbol(var.name, safe_var_type, Index(idx)))
            
            if var.init_value is not None:
                code, typ = self.visit(var.init_value, Access(frame, o.sym))
                self.emit.print_out(code)
                if self.is_float(safe_var_type) and self.is_int(typ):
                    self.emit.print_out(self.emit.emit_i2f(frame))
                self.emit.print_out(self.emit.emit_write_var(var.name, safe_var_type, idx, frame))
            else:
                # [FIX START] Default Initialization
                if self.is_int(safe_var_type) or self.is_bool(safe_var_type):
                    self.emit.print_out(self.emit.emit_push_iconst(0, frame))
                    self.emit.print_out(self.emit.emit_write_var(var.name, safe_var_type, idx, frame))
                elif self.is_float(safe_var_type):
                    self.emit.print_out(self.emit.emit_push_fconst("0.0", frame))
                    self.emit.print_out(self.emit.emit_write_var(var.name, safe_var_type, idx, frame))
                elif isinstance(safe_var_type, ArrayType):
                    self.emit.print_out(self.emit.emit_push_iconst(safe_var_type.size, frame))
                    elem_type = self.sanitize_type(safe_var_type.element_type)
                    if self.is_int(elem_type): self.emit.print_out(self.emit.jvm.emitNEWARRAY("int"))
                    elif self.is_float(elem_type): self.emit.print_out(self.emit.jvm.emitNEWARRAY("float"))
                    elif self.is_bool(elem_type): self.emit.print_out(self.emit.jvm.emitNEWARRAY("boolean"))
                    elif self.is_string(elem_type): self.emit.print_out(self.emit.jvm.emitANEWARRAY("java/lang/String"))
                    elif isinstance(elem_type, ClassType): self.emit.print_out(self.emit.jvm.emitANEWARRAY(elem_type.class_name))
                    else: self.emit.print_out(self.emit.jvm.emitANEWARRAY("java/lang/Object"))
                    self.emit.print_out(self.emit.emit_write_var(var.name, safe_var_type, idx, frame))
                else:
                    self.emit.print_out(self.emit.jvm.emitPUSHNULL())
                    frame.push() # [Important] Update frame tracking for null
                    self.emit.print_out(self.emit.emit_write_var(var.name, safe_var_type, idx, frame))
                # [FIX END]
        
        return SubBody(frame, new_sym + o.sym)

    def visit_variable(self, node: "Variable", o: Any = None):
        pass

    def visit_assignment_statement(self, node: "AssignmentStatement", o: SubBody = None):
        if o is None: return
        rhs_code, rhs_type = self.visit(node.rhs, Access(o.frame, o.sym))
        self.emit.print_out(rhs_code)
        
        if isinstance(node.lhs, IdLHS):
             sym = next(filter(lambda x: x.name == node.lhs.name, o.sym), None)
             if sym and self.is_float(sym.type) and self.is_int(rhs_type):
                 self.emit.print_out(self.emit.emit_i2f(o.frame))
        
        lhs_code, _ = self.visit(node.lhs, Access(o.frame, o.sym, is_left=True))
        self.emit.print_out(lhs_code)

    def visit_if_statement(self, node: "IfStatement", o: SubBody = None):
        if o is None: return
        frame = o.frame
        label_else = frame.get_new_label()
        label_exit = frame.get_new_label()

        cond_code, _ = self.visit(node.condition, Access(frame, o.sym))
        self.emit.print_out(cond_code)
        self.emit.print_out(self.emit.emit_if_false(label_else, frame))

        self.visit(node.then_stmt, o)
        self.emit.print_out(self.emit.emit_goto(label_exit, frame))

        self.emit.print_out(self.emit.emit_label(label_else, frame))
        if node.else_stmt:
            self.visit(node.else_stmt, o)
        
        self.emit.print_out(self.emit.emit_label(label_exit, frame))

    def visit_for_statement(self, node: "ForStatement", o: SubBody = None):
        if o is None: return
        frame = o.frame
        sym = next(filter(lambda x: x.name == node.variable, o.sym), None)
        
        start_code, _ = self.visit(node.start_expr, Access(frame, o.sym))
        self.emit.print_out(start_code)
        self.emit.print_out(self.emit.emit_write_var(sym.name, sym.type, sym.value.value, frame))

        frame.enter_loop()
        label_start = frame.get_new_label()
        label_continue = frame.get_continue_label()
        label_break = frame.get_break_label()
        
        self.emit.print_out(self.emit.emit_label(label_start, frame))
        
        self.emit.print_out(self.emit.emit_read_var(sym.name, sym.type, sym.value.value, frame))
        end_code, _ = self.visit(node.end_expr, Access(frame, o.sym))
        self.emit.print_out(end_code)
        
        if node.direction == "to":
            self.emit.print_out(self.emit.emit_ificmpgt(label_break, frame))
        else:
            self.emit.print_out(self.emit.emit_ificmplt(label_break, frame))
            
        self.visit(node.body, o)
        
        self.emit.print_out(self.emit.emit_label(label_continue, frame))
        
        self.emit.print_out(self.emit.emit_read_var(sym.name, sym.type, sym.value.value, frame))
        self.emit.print_out(self.emit.emit_push_iconst(1, frame))
        if node.direction == "to":
            self.emit.print_out(self.emit.emit_add_op("+", PrimitiveType("int"), frame))
        else:
            self.emit.print_out(self.emit.emit_add_op("-", PrimitiveType("int"), frame))
        self.emit.print_out(self.emit.emit_write_var(sym.name, sym.type, sym.value.value, frame))
        
        self.emit.print_out(self.emit.emit_goto(label_start, frame))
        self.emit.print_out(self.emit.emit_label(label_break, frame))
        frame.exit_loop()

    def visit_break_statement(self, node: "BreakStatement", o: SubBody = None):
        if o is None: return
        self.emit.print_out(self.emit.emit_goto(o.frame.get_break_label(), o.frame))

    def visit_continue_statement(self, node: "ContinueStatement", o: SubBody = None):
        if o is None: return
        self.emit.print_out(self.emit.emit_goto(o.frame.get_continue_label(), o.frame))

    def visit_return_statement(self, node: "ReturnStatement", o: SubBody = None):
        if o is None: return
        code, typ = self.visit(node.value, Access(o.frame, o.sym))
        self.emit.print_out(code)
        
        if self.is_float(o.frame.return_type) and self.is_int(typ):
            self.emit.print_out(self.emit.emit_i2f(o.frame))
            typ = PrimitiveType("float")
            
        self.emit.print_out(self.emit.emit_return(typ, o.frame))

    def visit_method_invocation_statement(self, node: "MethodInvocationStatement", o: SubBody = None):
        if o is None: return
        code, typ = self.visit(node.method_call, Access(o.frame, o.sym))
        self.emit.print_out(code)
        if typ is not None and not self.is_void(typ):
            self.emit.print_out(self.emit.emit_pop(o.frame))

    # ============================================================================
    # Left-hand Side (LHS)
    # ============================================================================

    def visit_id_lhs(self, node: "IdLHS", o: Access = None):
        if o is None: return "", None
        sym = next(filter(lambda x: x.name == node.name, o.sym), None)
        
        if type(sym.value) is Index:
            code = self.emit.emit_write_var(sym.name, sym.type, sym.value.value, o.frame)
            return code, sym.type
        else:
            raise IllegalOperandException(f"Cannot assign to: {node.name}")

    def visit_postfix_lhs(self, node: "PostfixLHS", o: Access = None):
        if o is None: return "", None
        code, current_type = self.visit(node.postfix_expr.primary, o)
        self.emit.print_out(code)
        
        for op in node.postfix_expr.postfix_ops[:-1]:
            if isinstance(op, MemberAccess):
                self.emit.print_out(self.emit.emit_get_field(op.member_name, current_type, o.frame))
                if isinstance(current_type, ClassType) and current_type.class_name in self.class_fields:
                    current_type = self.class_fields[current_type.class_name].get(op.member_name, current_type)
            elif isinstance(op, ArrayAccess):
                idx_code, _ = self.visit(op.index, o)
                self.emit.print_out(idx_code)
                self.emit.print_out(self.emit.emit_aload(current_type.element_type, o.frame))
                current_type = current_type.element_type

        last_op = node.postfix_expr.postfix_ops[-1]
        if isinstance(last_op, MemberAccess):
            field_type = PrimitiveType("int")
            if isinstance(current_type, ClassType) and current_type.class_name in self.class_fields:
                field_type = self.class_fields[current_type.class_name].get(last_op.member_name, field_type)
            field_lexeme = current_type.class_name + "/" + last_op.member_name
            self.emit.print_out(self.emit.jvm.INDENT + "swap" + self.emit.jvm.END)
            self.emit.print_out(self.emit.emit_put_field(field_lexeme, field_type, o.frame))
            
        elif isinstance(last_op, ArrayAccess):
            idx_code, _ = self.visit(last_op.index, o)
            self.emit.print_out(idx_code) 
            
            # [FIX START] Manual Frame update for dup2_x1
            self.emit.print_out(self.emit.jvm.INDENT + "dup2_x1" + self.emit.jvm.END)
            o.frame.push(); o.frame.push() # Báo frame biết stack tăng 2
            self.emit.print_out(self.emit.jvm.INDENT + "pop2" + self.emit.jvm.END)
            o.frame.pop(); o.frame.pop()   # Báo frame biết stack giảm 2
            # [FIX END]
            
            self.emit.print_out(self.emit.emit_astore(current_type.element_type, o.frame))
            
        return "", None

    # ============================================================================
    # Expressions
    # ============================================================================

    def visit_binary_op(self, node: "BinaryOp", o: Access = None):
        op = node.operator
        left_code, left_type = self.visit(node.left, o)
        self.emit.print_out(left_code)
        
        if op == '/' and self.is_int(left_type):
            self.emit.print_out(self.emit.emit_i2f(o.frame))
            left_type = PrimitiveType("float")

        if op == "&&":
            label_false = o.frame.get_new_label()
            label_end = o.frame.get_new_label()
            self.emit.print_out(self.emit.emit_if_false(label_false, o.frame))
            right_code, _ = self.visit(node.right, o)
            self.emit.print_out(right_code)
            self.emit.print_out(self.emit.emit_goto(label_end, o.frame))
            self.emit.print_out(self.emit.emit_label(label_false, o.frame))
            self.emit.print_out(self.emit.emit_push_iconst(0, o.frame))
            self.emit.print_out(self.emit.emit_label(label_end, o.frame))
            return "", PrimitiveType("boolean")

        elif op == "||":
            label_true = o.frame.get_new_label()
            label_end = o.frame.get_new_label()
            self.emit.print_out(self.emit.emit_if_true(label_true, o.frame))
            right_code, _ = self.visit(node.right, o)
            self.emit.print_out(right_code)
            self.emit.print_out(self.emit.emit_goto(label_end, o.frame))
            self.emit.print_out(self.emit.emit_label(label_true, o.frame))
            self.emit.print_out(self.emit.emit_push_iconst(1, o.frame))
            self.emit.print_out(self.emit.emit_label(label_end, o.frame))
            return "", PrimitiveType("boolean")

        right_code, right_type = self.visit(node.right, o)
        self.emit.print_out(right_code)
        
        if op == '/' and self.is_int(right_type):
             self.emit.print_out(self.emit.emit_i2f(o.frame))
             right_type = PrimitiveType("float")

        if self.is_float(left_type) and self.is_int(right_type):
            self.emit.print_out(self.emit.emit_i2f(o.frame))
            right_type = PrimitiveType("float")
        elif self.is_float(right_type) and self.is_int(left_type):
            self.emit.print_out(self.emit.jvm.INDENT + "swap" + self.emit.jvm.END)
            self.emit.print_out(self.emit.emit_i2f(o.frame))
            self.emit.print_out(self.emit.jvm.INDENT + "swap" + self.emit.jvm.END)
            left_type = PrimitiveType("float")

        if self.is_string(left_type) and self.is_string(right_type):
            if op == "==":
                self.emit.print_out(self.emit.emit_invoke_virtual("java/lang/String/equals", FunctionType([ClassType("java/lang/Object")], PrimitiveType("boolean")), o.frame))
                return "", PrimitiveType("boolean")
            elif op == "!=":
                self.emit.print_out(self.emit.emit_invoke_virtual("java/lang/String/equals", FunctionType([ClassType("java/lang/Object")], PrimitiveType("boolean")), o.frame))
                self.emit.print_out(self.emit.emit_push_iconst(1, o.frame))
                self.emit.print_out(self.emit.jvm.emitIXOR())
                o.frame.pop(); o.frame.pop(); o.frame.push()
                return "", PrimitiveType("boolean")
            elif op == "^":
                self.emit.print_out(self.emit.jvm.emitINVOKEVIRTUAL("java/lang/String/concat", "(Ljava/lang/String;)Ljava/lang/String;"))
                o.frame.pop(); o.frame.pop(); o.frame.push()
                return "", PrimitiveType("string")

        res_type = left_type
        if self.is_float(left_type) or self.is_float(right_type) or op == '/':
            res_type = PrimitiveType("float")
        
        if op in ['+', '-']: return self.emit.emit_add_op(op, res_type, o.frame), res_type
        elif op in ['*', '/']: return self.emit.emit_mul_op(op, res_type, o.frame), res_type
        
        # [FIX HERE] Thủ công push vào frame cho phép chia nguyên và chia dư
        elif op == '\\': 
             code = self.emit.emit_div(o.frame)
             o.frame.push() 
             return code, PrimitiveType("int")
        elif op == '%': 
             code = self.emit.emit_mod(o.frame)
             o.frame.push() 
             return code, PrimitiveType("int")
        
        # [FIX HERE] Thủ công push vào frame cho phép so sánh
        elif op in ['>', '<', '>=', '<=', '!=', '==']: 
            code = self.emit.emit_re_op(op, res_type, o.frame)
            o.frame.push() # Giả định kết quả là boolean (1 phần tử trên stack)
            return code, PrimitiveType("boolean")
        
        return "", res_type

    def visit_unary_op(self, node: "UnaryOp", o: Access = None):
        body_code, typ = self.visit(node.operand, o)
        self.emit.print_out(body_code)
        if node.operator == '-': return self.emit.emit_neg_op(typ, o.frame), typ
        elif node.operator == '!': return self.emit.emit_not(typ, o.frame), typ
        return "", typ

    def visit_postfix_expression(self, node: "PostfixExpression", o: Access = None):
        # 1. Visit primary (Identifier, Array, etc.)
        code, current_type = self.visit(node.primary, o)
        
        is_static_access = False
        class_name_for_static = ""
        
        # Nếu primary là Identifier nhưng không tìm thấy trong biến -> Khả năng là Class Name (Static Access)
        if current_type is None and isinstance(node.primary, Identifier):
            is_static_access = True
            class_name_for_static = node.primary.name
        else:
            self.emit.print_out(code)

        # 2. Process Ops
        for op in node.postfix_ops:
            if isinstance(op, MethodCall):
                arg_types = []
                for arg in op.args:
                    arg_code, arg_type = self.visit(arg, o)
                    self.emit.print_out(arg_code)
                    arg_types.append(arg_type)
                
                if is_static_access:
                    found_sym = next((s for s in IO_SYMBOL_LIST if s.name == op.method_name), None)
                    if found_sym:
                        ret_type = found_sym.type.return_type
                    else:
                        ret_type = self.class_methods.get(class_name_for_static, {}).get(op.method_name, PrimitiveType("void"))
                    
                    self.emit.print_out(self.emit.emit_invoke_static(
                        class_name_for_static + "/" + op.method_name, 
                        FunctionType(arg_types, ret_type), 
                        o.frame
                    ))
                    
                    current_type = ret_type
                    is_static_access = False 
                else:
                    # Instance Method Call
                    ret_type = PrimitiveType("void")
                    c_name = "" 
                    if isinstance(current_type, ClassType):
                        c_name = current_type.class_name
                        ret_type = self.class_methods.get(current_type.class_name, {}).get(op.method_name, ret_type)
                    
                    full_method_name = c_name + "/" + op.method_name
                    
                    self.emit.print_out(self.emit.emit_invoke_virtual(
                        full_method_name,
                        FunctionType(arg_types, ret_type), 
                        o.frame
                    ))
                    current_type = ret_type

            elif isinstance(op, MemberAccess):
                if is_static_access:
                     field_type = PrimitiveType("int")
                     # Tra cứu field static
                     if class_name_for_static in self.class_fields:
                         field_type = self.class_fields[class_name_for_static].get(op.member_name, field_type)
                     
                     self.emit.print_out(self.emit.emit_get_static(class_name_for_static + "/" + op.member_name, field_type, o.frame))
                     is_static_access = False
                     current_type = field_type
                else:
                    field_type = PrimitiveType("int")
                    if isinstance(current_type, ClassType):
                        field_type = self.class_fields.get(current_type.class_name, {}).get(op.member_name, field_type)
                    
                    class_name = current_type.class_name if isinstance(current_type, ClassType) else ""
                    full_field_name = class_name + "/" + op.member_name
                        
                    self.emit.print_out(self.emit.emit_get_field(full_field_name, field_type, o.frame))
                    current_type = field_type
                
            elif isinstance(op, ArrayAccess):
                idx_code, _ = self.visit(op.index, o)
                self.emit.print_out(idx_code)
                self.emit.print_out(self.emit.emit_aload(current_type.element_type, o.frame))
                current_type = current_type.element_type
                
        return "", current_type

    def visit_method_call(self, node: "MethodCall", o: Access = None): pass
    def visit_member_access(self, node: "MemberAccess", o: Access = None): pass
    def visit_array_access(self, node: "ArrayAccess", o: Access = None): pass

    def visit_object_creation(self, node: "ObjectCreation", o: Access = None):
        self.emit.print_out(self.emit.jvm.emitNEW(node.class_name))
        o.frame.push() 
        self.emit.print_out(self.emit.emit_dup(o.frame))
        
        param_types = []
        for arg in node.args:
            code, typ = self.visit(arg, o)
            self.emit.print_out(code)
            param_types.append(typ)
        func_type = FunctionType(param_types, PrimitiveType("void"))
        self.emit.print_out(self.emit.emit_invoke_special(o.frame, node.class_name + "/<init>", func_type))
        return "", ClassType(node.class_name)

    def visit_identifier(self, node: "Identifier", o: Access = None):
        if o is None: return "", None
        sym = next(filter(lambda x: x.name == node.name, o.sym), None)
        if sym:
            code = self.emit.emit_read_var(sym.name, sym.type, sym.value.value, o.frame)
            return code, sym.type
        else:
            return "", None

    def visit_this_expression(self, node: "ThisExpression", o: Access = None):
        if o is None: return "", None
        this_sym = next(filter(lambda x: x.name == "this", o.sym), None)
        code = self.emit.emit_read_var("this", this_sym.type, this_sym.value.value, o.frame)
        return code, this_sym.type

    def visit_parenthesized_expression(self, node: "ParenthesizedExpression", o: Access = None):
        return self.visit(node.expr, o)

    # ============================================================================
    # Literals
    # ============================================================================

    def visit_int_literal(self, node: "IntLiteral", o: Access = None):
        return self.emit.emit_push_iconst(node.value, o.frame), PrimitiveType("int")

    def visit_float_literal(self, node: "FloatLiteral", o: Access = None):
        return self.emit.emit_push_fconst(str(node.value), o.frame), PrimitiveType("float")

    def visit_bool_literal(self, node: "BoolLiteral", o: Access = None):
        val = "1" if node.value else "0"
        return self.emit.emit_push_iconst(val, o.frame), PrimitiveType("boolean")

    def visit_string_literal(self, node: "StringLiteral", o: Access = None):
        return self.emit.emit_push_const('"' + node.value + '"', PrimitiveType("string"), o.frame), PrimitiveType("string")

    def visit_array_literal(self, node: "ArrayLiteral", o: Access = None):
        size = len(node.value)
        if size == 0:
             self.emit.print_out(self.emit.emit_push_iconst(0, o.frame))
             self.emit.print_out(self.emit.jvm.emitNEWARRAY("int"))
             o.frame.pop(); o.frame.push()
             return "", ArrayType(PrimitiveType("int"), 0)

        first_elem_code, first_type = self.visit(node.value[0], o)
        self.emit.print_out(self.emit.emit_push_iconst(size, o.frame))
        
        safe_first_type = self.sanitize_type(first_type)
        
        if self.is_int(safe_first_type):
            self.emit.print_out(self.emit.jvm.emitNEWARRAY("int"))
        elif self.is_float(safe_first_type):
             self.emit.print_out(self.emit.jvm.emitNEWARRAY("float"))
        elif self.is_bool(safe_first_type):
             self.emit.print_out(self.emit.jvm.emitNEWARRAY("boolean"))
        elif self.is_string(safe_first_type):
             self.emit.print_out(self.emit.jvm.emitANEWARRAY("java/lang/String"))
        elif isinstance(safe_first_type, ClassType):
             self.emit.print_out(self.emit.jvm.emitANEWARRAY(safe_first_type.class_name))
        else:
             self.emit.print_out(self.emit.jvm.emitANEWARRAY("java/lang/Object"))
        
        o.frame.pop(); o.frame.push()

        for i, elem in enumerate(node.value):
            self.emit.print_out(self.emit.emit_dup(o.frame))
            self.emit.print_out(self.emit.emit_push_iconst(i, o.frame))
            elem_code, elem_type = self.visit(elem, o)
            self.emit.print_out(elem_code)
            
            safe_elem_type = self.sanitize_type(elem_type)
            if self.is_float(safe_first_type) and self.is_int(safe_elem_type):
                 self.emit.print_out(self.emit.emit_i2f(o.frame))
            self.emit.print_out(self.emit.emit_astore(safe_first_type, o.frame))
            
        return "", ArrayType(safe_first_type, size)

    def visit_nil_literal(self, node: "NilLiteral", o: Access = None):
        o.frame.push()
        return self.emit.jvm.emitPUSHNULL(), None