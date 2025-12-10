"""
Static Semantic Checker for OPLang Programming Language

This module implements a comprehensive static semantic checker using visitor pattern
for the OPLang object-oriented programming language. It performs type checking,
scope management, inheritance validation, and detects all semantic errors as 
specified in the OPLang language specification.
"""

from functools import reduce
from platform import node
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
        global_env = [{"class": "io", "statics": {"attrs": [], "methods": self.global_env}}]
        self.visit_program(ast, global_env)
    global_env = [
        {"name": "readInt",  "params": [], "return_type": "int", "type": "int", "static": True},
        {"name": "writeInt", "params": ["int"], "return_type": "void", "type": "void", "static": True},
        {"name": "writeIntLn", "params": ["int"], "return_type": "void", "type": "void", "static": True},
        {"name": "readFloat",  "params": [], "return_type": "float", "type": "float", "static": True},
        {"name": "writeFloat", "params": ["float"], "return_type": "void", "type": "void", "static": True},
        {"name": "writeFloatLn", "params": ["float"], "return_type": "void", "type": "void", "static": True},
        {"name": "readBool",  "params": [], "return_type": "boolean", "type": "boolean", "static": True},
        {"name": "writeBool", "params": ["boolean"], "return_type": "void", "type": "void", "static": True},
        {"name": "writeBoolLn", "params": ["boolean"], "return_type": "void", "type": "void", "static": True},
        {"name": "readStr",   "params": [], "return_type": "string", "type": "string", "static": True},
        {"name": "writeStr",  "params": ["string"], "return_type": "void", "type": "void", "static": True},
        {"name": "writeStrLn","params": ["string"], "return_type": "void", "type": "void", "static": True},
    ]

        # --- PHASE 1: only register attributes (no init evaluation) ---
    def _collect_attribute_decl(self, node: "AttributeDecl", o: Any = None):
        """
        Ghi nhận tên/kiểu/const/static của các attribute vào class_env
        (không evaluate init_value ở bước này).
        Sử dụng cùng cấu trúc target mà code hiện tại dùng: o[0][kind]['attrs'].
        """
        kind = "statics" if node.is_static else "locals"
        target = o[0][kind]["attrs"]

        declared_type = node.attr_type.accept(self, o)
        declared_type_name = self.get_type_name(declared_type)
        if isinstance(declared_type, ClassType):
            if not self.lookupGlobal(declared_type_name, o)[0]:
                raise UndeclaredClass(declared_type_name)
        for attr in node.attributes:
            # nếu đã có tên tương tự trong target -> Redeclared
            if any(a["name"] == attr.name for a in target):
                raise Redeclared("Attribute", attr.name)
            # tạo entry "light" — chưa ghi value_type vì chưa evaluate init
            target.append({
                "name": attr.name,
                "type": declared_type_name,
                "const": node.is_final or isinstance(node.attr_type, ReferenceType),
                "value_type": None,
                "static": node.is_static
            })

    def _collect_attribute_decl(self, node: "AttributeDecl", o: Any = None):
        kind = "statics" if node.is_static else "locals"
        target = o[0][kind]["attrs"]

        declared_type = node.attr_type.accept(self, o)
        declared_type_name = self.get_type_name(declared_type)
        if isinstance(declared_type, ClassType):
            if not self.lookupGlobal(declared_type_name, o)[0]:
                raise UndeclaredClass(declared_type_name)
        
        for attr in node.attributes:
            # Kiểm tra trùng tên
            if any(a["name"] == attr.name for a in target):
                # FIX: Kiểm tra nếu là final thì báo lỗi Redeclared Constant, ngược lại là Attribute
                raise Redeclared("Constant" if node.is_final else "Attribute", attr.name)
            
            target.append({
                "name": attr.name,
                "type": declared_type_name,
                "const": node.is_final or isinstance(node.attr_type, ReferenceType),
                "value_type": None,
                "static": node.is_static
            })

    def _check_attribute_decl(self, node: "AttributeDecl", o: Any = None):
        kind = "statics" if node.is_static else "locals"
        target = o[0][kind]["attrs"]
        declared_type = node.attr_type.accept(self, o)
        declared_typename = self.get_type_name(declared_type)
        
        # Context scope for init expression evaluation
        init_env = [{
            "current": o[0]["current"],
            "inherit": o[0].get("inherit", []),
            "static_context": node.is_static # Mark context as static or instance
        }] + o

        last_init_expr = None
        for attr in node.attributes[::-1]:
            if attr.init_value:
                last_init_expr = attr.init_value
            sym = next((a for a in target if a["name"] == attr.name), None)
            if sym is None:
                raise UndeclaredAttribute(attr.name)

            # Evaluate init_value in init_env
            init_type = attr.init_value.accept(self, init_env) if attr.init_value else None
            
            is_const = sym["const"]
            type_check = None
            if init_type:
                if isinstance(init_type, list):
                    type_check = init_type[0]
                elif isinstance(init_type, dict):
                    type_check = init_type["type"]

            if is_const:
                print(attr.init_value)
                if isinstance(attr.init_value, NilLiteral):
                    raise IllegalConstantExpression(NilLiteral())
                if attr.init_value is None:
                    raise IllegalConstantExpression(last_init_expr if last_init_expr else NilLiteral())
                # Check constant expression validity
                is_init_const_expr = False
                is_nil = False
                
                if isinstance(init_type, list):
                    is_init_const_expr = init_type[1]
                    is_nil = (init_type[0] == "nil")
                elif isinstance(init_type, dict):
                    is_init_const_expr = init_type.get("const", False)
                    is_nil = (init_type.get("type") == "nil")
                
                # Only ClassType variables can be assigned non-constant expressions (like 'new A()') or 'nil'
                if not is_init_const_expr and not isinstance(node.attr_type, ClassType):
                     raise IllegalConstantExpression(attr.init_value)
                
                if not is_nil:
                     if not self.check_type(type_check, declared_typename, o):
                        raise TypeMismatchInConstant(node)
            else:
                if init_type and not self.check_type(type_check, declared_typename, o):
                    raise TypeMismatchInStatement(node)

            sym["value_type"] = type_check


    def check_type(self, from_type, to_type, env):
        """
        Check for type compatibility (Coercion):
        1. Exact match (same_type)
        2. nil -> any Class type (but not primitive)
        3. int -> float
        4. Subclass -> Superclass (Deep inheritance)
        """
        # 1. Exact match
        if self.same_type(from_type, to_type):
            return True

        # 2. nil -> ClassType
        # 'nil' can be assigned to any object (ClassType), but not primitives (int, float, bool, string)
        if from_type == "nil":
            if isinstance(to_type, str) and to_type not in ["int", "float", "boolean", "string", "void"]:
                # Check if to_type is a declared class
                if self.lookupGlobal(to_type, env)[0]:
                    return True
            return False

        # 3. int -> float
        if from_type == "int" and to_type == "float":
            return True

        # 4. Subclass -> Superclass (Inheritance Check)
        if isinstance(from_type, str) and isinstance(to_type, str):
            # Use lookupGlobal to get class def, ignoring local variable shadowing
            found_class = self.lookupGlobal(from_type, env)
            if found_class[0]:
                # Get immediate parents
                parents = found_class[1].get("inherit", [])
                
                # Check direct inheritance
                if to_type in parents:
                    return True
                
                # Check deep inheritance (Ancestors) using a queue
                queue = list(parents)
                visited = set(parents)
                while queue:
                    curr = queue.pop(0)
                    if curr == to_type:
                        return True
                    
                    # Fetch parent class info
                    curr_cls = self.lookupGlobal(curr, env)
                    if curr_cls[0]:
                        grandparents = curr_cls[1].get("inherit", [])
                        for gp in grandparents:
                            if gp not in visited:
                                visited.add(gp)
                                queue.append(gp)

        return False

    def get_type_name(self, t: Any):
        if isinstance(t, ReferenceType):
            return self.get_type_name(t.referenced_type)
        if isinstance(t, PrimitiveType):
            return t.type_name
        if isinstance(t, ClassType):
            return t.class_name
        if isinstance(t, ArrayType):
            return {"kind": "array", "elem": self.get_type_name(t.element_type), "size": t.size}
        return str(t)

    # ============================================
    # LOOKUP FUNCTIONS
    # ============================================

        # ============================================
    # LOOKUP FUNCTIONS (bản đầy đủ, tường minh)
    # ============================================

    def lookupClass(self, name, env):
        """
        Tra class theo tên, nhưng nếu trong local scope có biến cùng tên,
        xem như class name bị shadow → không được dùng trong ngữ cảnh này.
        """
        # 1) Kiểm tra shadow từ local scope
        if env and isinstance(env, list) and "local" in env[0]:
            for var in env[0]["local"]:
                if var["name"] == name:
                    # Class name bị che khuất bởi biến local
                    return [False, None, None]

        # 2) Không bị shadow → tra class theo env
        for (idx, item) in enumerate(env):
            if item.get("class") == name:
                return [True, item, idx]

        return [False, None, None]


    def lookupVarFromGlobal(self, name, env, current_class):
        """
        Tìm biến/hàm từ môi trường toàn cục (bao gồm class hiện tại, các class khác, và inherited).
        Dùng cho tra cứu symbol trong toàn bộ chương trình.
        """
        # Nếu đang trong method, ta lưu tên method hiện hành
        current_method = env[0].get("method", "")

        # Duyệt qua từng class trong env (trừ phần local stack)
        for classItem in env:
            if "class" not in classItem:
                continue

            # --- Class hiện tại ---
            if classItem["class"] == current_class:
                # Nếu đang trong method, ưu tiên method scope
                if current_method:
                    for m in classItem["statics"]["methods"]:
                        if m["name"] == name:
                            return [True, m, "method", "static", classItem["class"]]
                    for m in classItem["locals"]["methods"]:
                        if m["name"] == name:
                            return [True, m, "method", "local", classItem["class"]]
                # Thuộc tính
                for a in classItem["statics"]["attrs"]:
                    if a["name"] == name:
                        return [True, a, "attribute", "static", classItem["class"]]
                for a in classItem["locals"]["attrs"]:
                    if a["name"] == name:
                        return [True, a, "attribute", "local", classItem["class"]]

            # --- Class khác (có thể là cha) ---
            else:
                if current_method:
                    for m in classItem["statics"]["methods"]:
                        if m["name"] == name:
                            return [True, m, "method", "static", classItem["class"], "inherited"]
                    for m in classItem["locals"]["methods"]:
                        if m["name"] == name:
                            return [True, m, "method", "local", classItem["class"], "inherited"]
                for a in classItem["statics"]["attrs"]:
                    if a["name"] == name:
                        return [True, a, "attribute", "static", classItem["class"], "inherited"]
                for a in classItem["locals"]["attrs"]:
                    if a["name"] == name:
                        return [True, a, "attribute", "local", classItem["class"], "inherited"]

        return [False, None, None]

    def lookupVarFromTail(self, name, env, current_class, parents=None):
        """
        Tìm biến/hàm trong class hiện tại hoặc cha (kế thừa).
        Đã sửa: Luôn tìm kiếm method bất kể ngữ cảnh (bỏ check if current_method).
        """
        # --- Duyệt class hiện tại ---
        for classItem in env:
            if classItem.get("class") == current_class:
                # Tìm trong Methods (Static & Local)
                for m in classItem["statics"]["methods"]:
                    if m["name"] == name:
                        return [True, m, "method", "static", classItem["class"]]
                for m in classItem["locals"]["methods"]:
                    if m["name"] == name:
                        return [True, m, "method", "local", classItem["class"]]
                
                # Tìm trong Attributes
                for a in classItem["statics"]["attrs"]:
                    if a["name"] == name:
                        return [True, a, "attribute", "static", classItem["class"]]
                for a in classItem["locals"]["attrs"]:
                    if a["name"] == name:
                        return [True, a, "attribute", "local", classItem["class"]]

        # --- Duyệt các class cha nếu có ---
        if parents:
            stack = parents.copy()
            while len(stack) > 0:
                parent_class = stack[-1]
                for classItem in env:
                    if classItem.get("class") == parent_class:
                        # Tìm trong Methods (Inherited)
                        for m in classItem["statics"]["methods"]:
                            if m["name"] == name:
                                return [True, m, "method", "static", classItem["class"], "inherited"]
                        for m in classItem["locals"]["methods"]:
                            if m["name"] == name:
                                return [True, m, "method", "local", classItem["class"], "inherited"]
                        
                        # Tìm trong Attributes (Inherited)
                        for a in classItem["statics"]["attrs"]:
                            if a["name"] == name:
                                return [True, a, "attribute", "static", classItem["class"], "inherited"]
                        for a in classItem["locals"]["attrs"]:
                            if a["name"] == name:
                                return [True, a, "attribute", "local", classItem["class"], "inherited"]
                stack.pop()

        return [False, None, None]

    def lookupInside(self, name, env):
        """
        Tìm identifier:
        1. Duyệt ngược các scope cục bộ (Block -> Method).
        2. Nếu không thấy, tìm trong Class Member (hiện tại + kế thừa).
        """
        # --- 1. Tìm trong các scope cục bộ (từ trong ra ngoài) ---
        for scope in env:
            # Nếu gặp scope chứa biến local
            if "local" in scope:
                for x in scope["local"]:
                    if x["name"] == name:
                        return [True, x, "local"]
            
            # Nếu gặp ranh giới Class (scope của ClassDecl), dừng tìm kiếm biến cục bộ
            # Vì biến cục bộ không thể "xuyên" qua ranh giới method/class ra ngoài global theo cách này
            if "class" in scope and "statics" in scope:
                break

        # --- 2. Tìm trong class hiện tại hoặc cha (Members) ---
        current_class = env[0].get("current")
        inherit = env[0].get("inherit", [])
        lookup = self.lookupVarFromTail(name, env, current_class, inherit)
        if lookup[0]:
            return lookup

        # --- 3. Không tìm thấy ---
        return [False, None, None]

    def lookupClassMember(self, name, env, current_class):
        if current_class == "io":
            for m in self.global_env:
                if m["name"] == name:
                    return [True, m, "method", "static", "io"]
            return [False, None, None, None, None]
        
        # 1. Tìm định nghĩa class hiện tại để lấy danh sách cha (inherit)
        # Dùng lookupGlobal để chắc chắn tìm thấy Class Definition (bỏ qua local shadowing)
        found_cls = self.lookupGlobal(current_class, env)
        
        full_parents = []
        if found_cls[0]:
            # Lấy danh sách cha trực tiếp
            parents = found_cls[1].get("inherit", [])
            
            # 2. Thu thập toàn bộ danh sách tổ tiên (Deep Inheritance support)
            # Vì lookupVarFromTail chỉ duyệt qua list parents được truyền vào mà không tự đệ quy
            queue = list(parents)
            while queue:
                p = queue.pop(0)
                if p not in full_parents:
                    full_parents.append(p)
                    # Tìm cha của p để thêm vào queue
                    p_cls = self.lookupGlobal(p, env)
                    if p_cls[0]:
                        queue.extend(p_cls[1].get("inherit", []))
        
        # 3. Gọi lookupVarFromTail với danh sách đầy đủ các class cha
        found = self.lookupVarFromTail(name, env, current_class, full_parents)
        
        if found[0]:
            return found
        return [False, None, None, None, None]

    def lookupGlobal(self, name, env):
        """Tìm class hoặc builtin global function."""
        # Class global
        for cls in env:
            if cls.get("class") == name:
                return [True, cls, "class"]

        # Builtin function
        for f in self.global_env:
            if f["name"] == name:
                return [True, f, "builtin"]

        return [False, None, None]

    def same_type(self, a, b):
        # a và b đều là string → primitive hoặc class
        if isinstance(a, str) and isinstance(b, str):
            return a == b
        # a và b đều là dict kiểu array
        if isinstance(a, dict) and isinstance(b, dict):
            return (
                a["kind"] == "array"
                and b["kind"] == "array"
                and self.same_type(a["elem"], b["elem"])
                and a["size"] == b["size"]
            )
        return False
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
        if self.lookupGlobal(cname, o)[0]:
            raise Redeclared("Class", cname)

        class_env = {
            "class": cname,
            "current": cname,
            "statics": {"attrs": [], "methods": []},
            "locals": {"attrs": [], "methods": []},
            "inherit": [pname] if pname else [],
        }

        if pname:
            found = self.lookupGlobal(pname, o)
            if not found[0]:
                raise UndeclaredClass(pname)

        # Env to use when visiting members (class at head)
        env_with_class = [class_env] + o

        # === PHA 1: collect attribute declarations (only register symbols) ===
        for mem in node.members:
            if isinstance(mem, AttributeDecl):
                self._collect_attribute_decl(mem, env_with_class)

        # === PHA 2: check attributes (init values) and visit methods ===
        for mem in node.members:
            if isinstance(mem, AttributeDecl):
                self._check_attribute_decl(mem, env_with_class)
            else:
                # methods / constructors / etc — reuse existing visitor behaviour
                mem.accept(self, env_with_class)

        # cuối cùng thêm class_env vào global env (như cậu đang làm)
        o.append(class_env)
        return class_env

    
    def visit_attribute_decl(self, node: "AttributeDecl", o: Any = None):
        """
        Kiểm tra khai báo attribute trong class.
        Sửa lỗi: Cho phép biến final kiểu ClassType được khởi tạo bởi non-constant expression (như new Class).
        """
        kind = "statics" if node.is_static else "locals"
        target = o[0][kind]["attrs"]

        declared_type = node.attr_type.accept(self, o)
        declared_typename = self.get_type_name(declared_type)
        
        methods_in_class = o[0]["statics"]["methods"] + o[0]["locals"]["methods"]
        last_init_expr = None
        for attr in node.attributes[::-1]:
            if attr.init_value:
                last_init_expr = attr.init_value
            # --- Redeclaration ---
            if any(a["name"] == attr.name for a in target):
                raise Redeclared("Attribute", attr.name)

            if any(m["name"] == attr.name for m in methods_in_class):
                raise Redeclared("Attribute", attr.name)
            # --- Xác định kiểu gán ban đầu ---
            init_type = attr.init_value.accept(self, o) if attr.init_value else None

            # --- Xác định xem có là constant không ---
            is_const = node.is_final
            if init_type:
                if isinstance(init_type, list):
                    type_check = init_type[0]
                elif isinstance(init_type, dict):
                    type_check = init_type["type"]
                else:
                    type_check = None
            else:
                type_check = None
            
            # --- Kiểm tra constant ---
            if is_const:
                if isinstance(attr.init_value, NilLiteral):
                    raise IllegalConstantExpression(last_init_expr if last_init_expr else NilLiteral())
                
                if type(init_type) is list:
                    type_check = init_type[0]
                    if init_type[0] == "nil":
                         pass # nil gán cho final object OK
                    
                    # Logic cũ: if not init_type[1]: raise IllegalConstantExpression...
                    # Logic mới: Nếu không phải constant expression, chỉ báo lỗi nếu KHÔNG phải là ClassType
                    if not init_type[1]:
                        if not isinstance(node.attr_type, ClassType):
                            raise IllegalConstantExpression(attr.init_value)

                    if init_type[0] != "nil" and not self.check_type(init_type[0], declared_typename, o):
                        raise TypeMismatchInConstant(node)
                    
                    if init_type is None:
                        raise IllegalConstantExpression(attr.init_value)

                elif type(init_type) is dict:
                    type_check = init_type["type"]
                    if init_type["type"] == "nil":
                         pass

                    if not init_type.get("const", False):
                        if not isinstance(node.attr_type, ClassType):
                             raise IllegalConstantExpression(attr.init_value)

                    if init_type["type"] != "nil" and not self.check_type(init_type["type"], declared_typename, o):
                         raise TypeMismatchInConstant(node)

                    if init_type["type"] is None:
                        raise IllegalConstantExpression(attr.init_value)
            else:
                # Kiểm tra type mismatch cho biến thường
                if init_type and not self.check_type(type_check, declared_typename, o):
                    raise TypeMismatchInStatement(node)

            # --- Thêm vào scope ---
            target.append({
                "name": attr.name,
                "type": declared_typename,
                "const": is_const,
                "value_type": init_type[0] if init_type else None,
                "static": node.is_static
            })


    def visit_attribute(self, node: "Attribute", o: Any = None):
        pass

    # Method declarations
     
    def visit_method_decl(self, node: "MethodDecl", o: Any = None):
        kind = "statics" if node.is_static else "locals"
        target = o[0][kind]["methods"]

        # Lấy danh sách kiểu tham số của method hiện tại
        param_types = [self.get_type_name(p.param_type) for p in node.params]
        # Kiểm tra redeclared (chỉ khi cùng tên và cùng danh sách kiểu tham số)
        for m in target:
            if m["name"] == node.name and m["param_types"] == param_types:
                raise Redeclared("Method", node.name)

        # Xác định kiểu trả về
        type_name = self.get_type_name(node.return_type)
        method_info = {
            "kind": "Method",
            "name": node.name,
            "type": type_name if isinstance(node.return_type, PrimitiveType) else str(node.return_type),
            "params": param_types,
            "param_types": param_types,  # lưu để so sánh sau
            "return_type": type_name if isinstance(node.return_type, PrimitiveType) or isinstance(node.return_type, ClassType) else str(node.return_type),
            "static": node.is_static
        }
        # Tạo môi trường local (method scope)
        target.append(method_info)
        local_env = [{
            "current": o[0]["class"],
            "inherit": o[0].get("inherit", []),
            "local": [],
            "return_type": method_info["return_type"],
            "method": node.name,
            "is_static": node.is_static
        }] + o
        # Thêm các tham số vào local scope
        list(map(lambda p: self.visit_parameter(p, local_env), node.params))
        # Duyệt thân hàm
        if node.body:
            # self.visit_block_statement(node.body, local_env)
            self.visit_method_body(node.body, local_env)
        # Lưu vào môi trường class
    def visit_method_body(self, node, o):
        env = o  
        for v in node.var_decls:
            v.accept(self, env)
        for s in node.statements:
            s.accept(self, env)
     
    def visit_constructor_decl(self, node: "ConstructorDecl", o: Any = None):
        cname = o[0]["class"]
        param_types = [self.get_type_name(p.param_type) for p in node.params]
        kind = "locals"
        target = o[0][kind]["methods"]
        if node.name != cname:
            raise TypeMismatchInStatement(node)
        for m in target:
            if m["name"] == node.name and m["param_types"] == param_types:
                raise Redeclared("Method", node.name)
        method_info = {
            "kind": "Constructor",
            "name": node.name,
            "type": cname,
            "params": param_types,
            "param_types": param_types,  # lưu để so sánh sau
            "return_type": cname,
            "static": "locals"
        }
        env = [{
            "current": cname,
            "inherit": o[0].get("inherit", []),
            "local": [],
            "return_type": cname,     # constructor return type = class
            "method": cname           # để lookupInside/lookupClassMember hoạt động đúng
        }] + o
        list(map(lambda p: self.visit_parameter(p, env), node.params))
        if node.body:
            self.visit_block_statement(node.body, env)
        target.append(method_info)

     
    def visit_destructor_decl(self, node: "DestructorDecl", o: Any = None):
          for m in o[0]["locals"]["methods"]:
            if m["name"] == node.name and m["kind"] == "Destructor" and m["param_types"] == []:
                raise Redeclared("Destructor", node.name)
          method_info = {
            "kind": "Destructor",
            "name": node.name,
            "type": o[0]["class"],
            "params": [],
            "param_types": [],  # lưu để so sánh sau
            "return_type": o[0]["class"],
            "static": "locals"
          }
          if node.body:
            self.visit_block_statement(node.body, [{"current": o[0]["class"], "local": []}] + o)
          o[0]["locals"]["methods"].append(method_info)

     
    def visit_parameter(self, node: "Parameter", o: Any = None):
        local_scope = o[0]["local"]
        if any(v["name"] == node.name for v in local_scope):
            raise Redeclared("Parameter", node.name)

        declared_type = node.param_type.accept(self, o)
        type_name = self.get_type_name(declared_type)

        # Nếu là ClassType thì class phải tồn tại
        if isinstance(declared_type, ClassType):
            if not self.lookupGlobal(type_name, o)[0]:
                raise UndeclaredClass(type_name)

        local_scope.append({"name": node.name, "type": type_name, "const": False})

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
        # duyệt các biến và statement
        new_scope = {
            "current": o[0]["current"],
            "inherit": o[0].get("inherit", []),
            "local": [],
            "return_type": o[0].get("return_type", None),
            "method": o[0].get("method", None),
            "in_loop": o[0].get("in_loop", False)
        }
        env = [new_scope] + o
        list(map(lambda v: v.accept(self, env), node.var_decls))
        list(map(lambda s: s.accept(self, env), node.statements))


     
    def visit_variable_decl(self, node: "VariableDecl", o: Any = None):
        declared_type = node.var_type.accept(self, o)
        declared_typename = self.get_type_name(declared_type)
        if isinstance(declared_type, ClassType):
            if not self.lookupGlobal(declared_typename, o)[0]:
                raise UndeclaredClass(declared_typename)
        local_scope = o[0]["local"]
        class_env = o[1] if len(o) > 1 and isinstance(o[1], dict) and "class" in o[1] else None
        last_init_expr = None
        for var in node.variables[::-1]:
            if var.init_value:
                last_init_expr = var.init_value
            if any(s["name"] == var.name for s in local_scope):
                raise Redeclared("Constant" if node.is_final else "Variable", var.name)
            
            init_type = var.init_value.accept(self, o) if var.init_value else None
            is_const = node.is_final
            # Kiểm tra constant
            if init_type:
                if isinstance(init_type, list):
                    type_check = init_type[0]
                elif isinstance(init_type, dict):
                    type_check = init_type["type"]
                else:
                    type_check = None
            else:
                type_check = None
            
            if is_const:
                if isinstance(var.init_value, NilLiteral):
                    raise IllegalConstantExpression(last_init_expr if last_init_expr else NilLiteral())
                if var.init_value is None:
                    raise IllegalConstantExpression(last_init_expr if last_init_expr else NilLiteral())
                if type(init_type) is list:
                    type_check = init_type[0]
                    if init_type[0] == "nil":
                        raise IllegalConstantExpression(var.init_value)
                    
                    # Sửa lỗi logic tương tự attribute_decl
                    if not init_type[1]:
                        if not isinstance(node.var_type, ClassType):
                            raise IllegalConstantExpression(var.init_value)

                    if init_type[0] != declared_typename and not self.check_type(init_type[0], declared_typename, o):
                        raise TypeMismatchInConstant(node)
                    
                    if init_type is None:
                        raise IllegalConstantExpression(var.init_value)
                    
                elif type(init_type) is dict:
                    type_check = init_type["type"]
                    if init_type["type"] == "nil":
                        raise IllegalConstantExpression(var.init_value)
                    
                    if not init_type.get("const", False): # init_type["const"] check
                        if not isinstance(node.var_type, ClassType):
                            raise IllegalConstantExpression(var.init_value)

                    if init_type["type"] != declared_typename and not self.check_type(init_type["type"], declared_typename, o):
                        raise TypeMismatchInConstant(node)
                    
                    if init_type["type"] is None:
                        raise IllegalConstantExpression(var.init_value)
                    
            else:
                # Kiểm tra type mismatch cho biến thường
                if init_type and not self.check_type(type_check, declared_typename, o):
                    if type(type_check) is dict and type_check["kind"] == "array" and declared_typename["kind"] == "array":
                        if type_check["size"] == 0 and declared_typename["size"] == 0:
                            continue
                    raise TypeMismatchInStatement(node)
            # Thêm vào scope
            res = {
                "name": var.name,
                "type": declared_typename,
                "const": is_const,
                "value_type": type_check
            }
            local_scope.append(res)

     
    def visit_variable(self, node: "Variable", o: Any = None):
        pass

    def visit_assignment_statement(self, node: "AssignmentStatement", o: Any = None):
        lhs_info = node.lhs.accept(self, o)

        # ---- chuẩn hóa lhs ----
        # id: string (IdLHS)
        # postfix: dict {"type": ..., "const": ..., "chain": [...]} (PostfixLHS)
        if isinstance(lhs_info, str):
            # simple identifier
            lhs_name = lhs_info
            
            found = self.lookupInside(lhs_name, o)
            
            # --- FIX START: Check static context for assignment LHS ---
            if found[0]:
                is_static_method = o[0].get("is_static", False)
                # found structure: [True, symbol, kind, storage, ...]
                # storage is at index 3 ('local' = instance member, 'static' = static member)
                if len(found) >= 4:
                    storage = found[3]
                    if is_static_method and storage == 'local':
                        # Đang ở method static mà truy cập biến instance -> Xem như không tìm thấy
                        raise UndeclaredIdentifier(lhs_name)
            # --- FIX END ---

            if not found[0]:
                raise UndeclaredIdentifier(lhs_name)
            
            sym = found[1]
            target_type = sym["type"]
        elif isinstance(lhs_info, dict):
            # postfix chain
            chain = lhs_info.get("chain", [])
            if len(chain) == 0:
                raise TypeMismatchInStatement(node)

            # base (ví dụ 'a' trong a.x)
            base = chain[0]
            base_name = base.get("name")
            base_type = base.get("type")

            # nếu base là identifier (chuỗi tên), cần lookup để biết kiểu của base
            # (ví dụ a := new A() => a type = "A")
            if base_name =="this":
                base_sym = {"type": o[0]["current"], "const": False}
                base_type = base_sym["type"]
            else:
                found_base = self.lookupInside(base_name, o)
                if not found_base[0]:
                    # --- FIX START: Kiểm tra nếu base là tên Class ---
                    found_class = self.lookupClass(base_name, o)
                    if found_class[0]:
                        # Nếu là class, tạo một symbol giả để tiếp tục logic check phía dưới
                        base_sym = {"type": base_name, "const": False}
                    else:
                        raise UndeclaredIdentifier(base_name)
                    # --- FIX END ---
                else:
                    base_sym = found_base[1]
                
                base_type = base_sym["type"]

            # attribute/method/array chain: lấy phần tử cuối cùng để xác định mục tiêu gán
            last = chain[-1]

            if last["kind"] == "attr":
                attr_name = last["name"]
                # tìm thuộc tính trong class của base
                found_attr = self.lookupClassMember(attr_name, o, base_type)
                if not found_attr[0]:
                    raise UndeclaredAttribute(attr_name)
                sym = found_attr[1]
                target_type = sym["type"]

            elif last["kind"] == "array":
                # gán vào phần tử mảng, target_type là elem_type
                elem_type = last.get("elem_type")
                if elem_type is None:
                    raise TypeMismatchInStatement(node)
                target_type = elem_type
                # không có symbol const check ở đây (mảng có thể là biến cục bộ hoặc attribute),
                # nếu muốn kiểm tra const cần tìm symbol của mảng base (chain[-2] hoặc base)
                # tìm symbol của mảng (the array variable itself)
                if len(chain) >= 2:
                    # tên biến mảng (nếu chain gồm base + array access)
                    arr_name = chain[-2]["name"] if chain[-2].get("kind") in ("primary","attr") else base_name
                    found_arr = self.lookupInside(arr_name, o)
                    if not found_arr[0]:
                        # nếu arr là attribute
                        found_arr = self.lookupClassMember(arr_name, o, base_type)
                    if found_arr[0]:
                        sym = found_arr[1]
                    else:
                        sym = {"const": False}  # fallback
                else:
                    sym = {"const": False}

            elif last["kind"] == "method":
                # phương thức không thể là LHS
                raise TypeMismatchInStatement(node)
            else:
                # không nhận dạng được kind
                raise TypeMismatchInStatement(node)
        else:
            raise TypeMismatchInStatement(node)

        # ---- kiểm tra const ----
        if sym.get("const", False):
            raise CannotAssignToConstant(node)

        # ---- RHS ----
        rhs = node.rhs.accept(self, o)
        if rhs is None:
            raise TypeMismatchInStatement(node)

        # chuẩn hóa rhs_type (rhs có thể là ["int", True] hoặc dict cho array, v.v.)
        if isinstance(rhs, (list, tuple)):
            rhs_type = rhs[0]
        else:
            rhs_type = rhs["type"] if isinstance(rhs, dict) else str(rhs)
        # ---- so sánh kiểu ----
        # target_type và rhs_type có thể là string (primitive/class) hoặc dict (array)
        if not self.check_type(rhs_type, target_type, o):
            raise TypeMismatchInStatement(node)

     
    def visit_if_statement(self, node: "IfStatement", o: Any = None):
        cond = node.condition.accept(self, o)
        if cond[0] != "boolean":
            raise TypeMismatchInStatement(node)
        node.then_stmt.accept(self, o)
        if node.else_stmt:
            node.else_stmt.accept(self, o)
     
    def visit_for_statement(self, node: "ForStatement", o: Any = None):
        var = node.variable
        lookup = self.lookupInside(var, o)
        if not lookup[0]:
            raise UndeclaredIdentifier(var)
        
        var_info = lookup[1]
        if var_info["const"]:
            # 🚨 Không thể gán lại biến final trong for loop
            raise CannotAssignToConstant(node)

        if var_info["type"] != "int":
            raise TypeMismatchInStatement(node)

        start = node.start_expr.accept(self, o)
        end = node.end_expr.accept(self, o)
        if start[0] != "int" or end[0] != "int":
            raise TypeMismatchInStatement(node)

        loop_scope = [{
            "in_loop": True,
            "local": o[0].get("local", []),    # giữ lại biến local như i, j
            "current": o[0]["current"],
            "inherit": o[0].get("inherit", []),
            "return_type": o[0].get("return_type", None)
        }]
        node.body.accept(self, loop_scope + o)

     
    def visit_break_statement(self, node: "BreakStatement", o: Any = None):
        if not any(scope.get("in_loop", False) for scope in o):
            raise MustInLoop(node)

     
    def visit_continue_statement(self, node: "ContinueStatement", o: Any = None):
        if not any(scope.get("in_loop", False) for scope in o):
            raise MustInLoop(node)

     
    def visit_return_statement(self, node: "ReturnStatement", o: Any = None):
        # Determine expected return type from current method scope
        expected_type = o[0].get("return_type", "void")
        
        if node.value:
            expr_info = node.value.accept(self, o)
            # Normalize expression type info
            if isinstance(expr_info, (list, tuple)):
                actual_type = expr_info[0]
            elif isinstance(expr_info, dict):
                actual_type = expr_info["type"]
            else:
                actual_type = str(expr_info)
        else:
            actual_type = "void"

        # Coercion Check
        if not self.check_type(actual_type, expected_type, o):
            raise TypeMismatchInStatement(node)

     
    def visit_method_invocation_statement(self, node: "MethodInvocationStatement", o: Any = None):
        # Tạo bản sao của scope
        new_scope = o[0].copy()
        
        # 1. Đánh dấu cho phép gọi hàm void
        new_scope["is_proc"] = True
        
        # 2. Gắn node Statement cha vào scope để PostfixExpression nhận biết
        new_scope["parent_stmt"] = node
        
        # Tạo môi trường mới
        new_env = [new_scope] + o[1:]
        
        node.method_call.accept(self, new_env)

    # Left-hand side (LHS)
     
    def visit_id_lhs(self, node: "IdLHS", o: Any = None):
        return node.name

     
    def visit_postfix_lhs(self, node: "PostfixLHS", o: Any = None):
        expr_info = node.postfix_expr.accept(self, o)
        return expr_info

    # Expressions
     
    def visit_binary_op(self, node: "BinaryOp", o: Any = None):
        left = node.left.accept(self, o)
        right = node.right.accept(self, o)
        op = node.operator

        numeric_ops = ["+", "-", "*", "/"]
        divint_mods = ["\\", "%"]
        compare_ops = ["<", "<=", ">", ">="]
        equality_ops = ["==", "!="]
        logical_ops = ["&&", "||"]
        concat_ops = ["^"]
        const_1 = False
        const_2 = False
        lhs_type = None
        rhs_type = None
        if isinstance(left, (list, tuple)):
            const_1 = left[1]
            lhs_type = left[0]
        else:
            const_1 = left.get("const", False)
            lhs_type = left.get("type", str(left))
        if isinstance(right, (list, tuple)):
            const_2 = right[1]
            rhs_type = right[0]
        else:
            const_2 = right.get("const", False)
            rhs_type = right.get("type", str(right))
        # const_1 = left[1] if isinstance(left, (list, tuple)) else left.get("const", False)
        # const_2 = right[1] if isinstance(right, (list, tuple)) else right.get("const", False)
        is_const = const_1 and const_2

        if op in divint_mods:
            if lhs_type != "int" or rhs_type != "int":
                raise TypeMismatchInExpression(node)
            return ["int", is_const]
        # Arithmetic
        if op in numeric_ops:
            if lhs_type not in ["int", "float"] or rhs_type not in ["int", "float"]:
                raise TypeMismatchInExpression(node)
            return ["float" if "float" in (lhs_type, rhs_type) else "int", is_const]

        # Comparison
        if op in compare_ops:
            if lhs_type not in ["int", "float"] or rhs_type not in ["int", "float"]:
                raise TypeMismatchInExpression(node)
            return ["boolean", is_const]

        # Equality
        if op in equality_ops:
            if lhs_type not in ["int", "boolean"] or rhs_type not in ["int", "boolean"] or lhs_type != rhs_type:
                raise TypeMismatchInExpression(node)
            return ["boolean", is_const]

        # Logical
        if op in logical_ops:
            if lhs_type != "boolean" or rhs_type != "boolean":
                raise TypeMismatchInExpression(node)
            return ["boolean", is_const]

        # String concatenation
        if op in concat_ops:
            if lhs_type != "string" or rhs_type != "string":
                raise TypeMismatchInExpression(node)
            return ["string", is_const]

        raise TypeMismatchInExpression(node)

     
    def visit_unary_op(self, node: "UnaryOp", o: Any = None):
        expr = node.operand.accept(self, o)
        op = node.operator
        is_const = False
        type_name = None
        if isinstance(expr, (list, tuple)):
            is_const = expr[1]
            type_name = expr[0]
        else:
            is_const = expr.get("const", False)
            type_name = expr.get("type", str(expr))
        if op == "!":
            if type_name != "boolean":
                raise TypeMismatchInExpression(node)
            return ["boolean", is_const]
        elif op == "-":
            if type_name not in ["int", "float"]:
                raise TypeMismatchInExpression(node)
            return [type_name, is_const]
        raise TypeMismatchInExpression(node)
     
    # def visit_postfix_expression(self, node: "PostfixExpression", o: Any = None):
    #     # --- 1. Lấy thông tin Primary ---
    #     try:
    #         primary_info = node.primary.accept(self, o)
    #     except UndeclaredIdentifier as e:
    #         # FIX: Nếu Identifier không tồn tại và đang được dùng để truy cập thành phần (.field, .method)
    #         # thì coi đây là lỗi UndeclaredClass thay vì UndeclaredIdentifier.
    #         if isinstance(node.primary, Identifier) and node.postfix_ops:
    #             if isinstance(node.postfix_ops[0], (MemberAccess, MethodCall)):
    #                 raise UndeclaredClass(node.primary.name)
    #         # Nếu không phải ngữ cảnh dot access (ví dụ: truy cập mảng hoặc biến đơn lẻ), giữ nguyên lỗi cũ
    #         raise e

    #     # Normalize: Chuẩn hóa thông tin trả về từ primary
    #     primary_type = None
    #     is_const = False
    #     is_class_ref = False
    #     primary_name = None

    #     if isinstance(primary_info, (list, tuple)) and len(primary_info) == 3 and primary_info[2] == "class":
    #         primary_type = primary_info[0]   
    #         is_const = False
    #         is_class_ref = True
    #         primary_name = primary_info[0]
    #     elif isinstance(primary_info, (list, tuple)):
    #         primary_type = primary_info[0]
    #         is_const = primary_info[1]
    #         if isinstance(node.primary, Identifier):
    #             primary_name = node.primary.name
    #         elif isinstance(node.primary, ClassType):
    #             primary_name = node.primary.class_name
    #         else:
    #             primary_name = getattr(node.primary, "name", str(node.primary))
    #     else:
    #         primary_type = primary_info.get("type") if isinstance(primary_info, dict) else str(primary_info)
    #         is_const = primary_info.get("const", False) if isinstance(primary_info, dict) else False
    #         if isinstance(node.primary, Identifier):
    #             primary_name = node.primary.name
    #         elif isinstance(node.primary, ClassType):
    #             primary_name = node.primary.class_name
    #         else:
    #             primary_name = getattr(node.primary, "name", str(node.primary))

    #     if isinstance(node.primary, ThisExpression):
    #         primary_name = "this"
    #         primary_type = o[0].get("current")
    #         is_class_ref = False 

    #     chain = [{"kind": "primary", "name": primary_name, "type": primary_type}]
    #     current_type = primary_type

    #     # --- 2. Duyệt chuỗi Postfix Ops ---
    #     for op in node.postfix_ops:
    #         if isinstance(op, MemberAccess):
    #             # Kiểm tra Type trước
    #             is_valid_class = False
    #             if isinstance(current_type, str):
    #                 if current_type == "io":
    #                     is_valid_class = True
    #                 else:
    #                     found_class = self.lookupClass(current_type, o)
    #                     if found_class[0]:
    #                         is_valid_class = True
                
    #             if not is_valid_class:
    #                 raise TypeMismatchInExpression(node)

    #             # Kiểm tra Attribute tồn tại
    #             member_name = op.member_name
    #             found = self.lookupClassMember(member_name, o, current_type)
                
    #             if not found[0]:
    #                 raise UndeclaredAttribute(member_name)
                
    #             member_type = found[1]["type"]
    #             member_static = found[1].get("static", False)

    #             # Kiểm tra quyền truy cập static/instance
    #             if is_class_ref and not member_static:
    #                 raise IllegalMemberAccess(node)
    #             if (not is_class_ref) and member_static:
    #                 raise IllegalMemberAccess(node)

    #             chain.append({"kind": "attr", "name": member_name, "type": member_type})
    #             current_type = member_type
    #             is_class_ref = False
    #             is_const = found[1].get("const", False)

    #         elif isinstance(op, MethodCall):
    #             is_valid_class = False
    #             if isinstance(current_type, str):
    #                 if current_type == "io": is_valid_class = True
    #                 elif self.lookupClass(current_type, o)[0]: is_valid_class = True
                
    #             if not is_valid_class:
    #                 raise TypeMismatchInExpression(node)

    #             method_name = op.method_name
    #             found = self.lookupClassMember(method_name, o, current_type)
    #             if not found[0]:
    #                 raise UndeclaredMethod(method_name)
                
    #             expected_params = found[1]['params']
    #             actual_args = [a.accept(self, o) for a in op.args]
    #             if len(expected_params) != len(actual_args):
    #                 raise TypeMismatchInExpression(node)
                
    #             for act, exp in zip(actual_args, expected_params):
    #                 # Sửa: kiểm tra cả list và dict cho chắc chắn
    #                 act_type = act[0] if isinstance(act, list) else (act['type'] if isinstance(act, dict) else str(act))
    #                 if not self.check_type(act_type, exp, o):
    #                     raise TypeMismatchInExpression(node)
                            
    #             ret_type = found[1].get("return_type", "void")
    #             method_static = found[1].get("static", False)

    #             if is_class_ref and not method_static:
    #                 raise IllegalMemberAccess(node)
    #             if (not is_class_ref) and method_static:
    #                 raise IllegalMemberAccess(node)
                
    #             args = [a[0] if isinstance(a, list) else a['type'] for a in actual_args]
    #             chain.append({"kind": "method", "name": method_name, "args": args, "ret": ret_type})
    #             current_type = ret_type
    #             is_class_ref = False

    #         elif isinstance(op, ArrayAccess):
    #             if not isinstance(current_type, dict) or current_type.get("kind") != "array":
    #                 raise TypeMismatchInExpression(node)

    #             idx = op.index.accept(self, o)
    #             idx_type = idx[0] if isinstance(idx, list) else idx["type"]
    #             idx_const = idx[1] if isinstance(idx, list) else idx.get("const", False)

    #             if idx_type != "int":
    #                 raise TypeMismatchInExpression(node)
                
    #             elem_type = current_type["elem"]
    #             is_const = is_const and idx_const
    #             chain.append({"kind": "array", "index_type": "int", "elem_type": elem_type})
    #             current_type = elem_type
    #             is_class_ref = False

    #     res = {"type": current_type, "const": is_const, "chain": chain}
    #     return res

    def visit_postfix_expression(self, node: "PostfixExpression", o: Any = None):
        primary_info = None
        # --- 1. RESOLVE PRIMARY (Không dùng try-except) ---
        if isinstance(node.primary, Identifier):
            name = node.primary.name
            
            # A. Tìm trong Local/Variable/Attribute scope
            found = self.lookupInside(name, o)
            if found[0]:
                # Logic kiểm tra ngữ cảnh static/instance (copy từ visit_identifier)
                is_valid = True
                if len(found) >= 4:
                    storage = found[3]
                    in_method = o[0].get("method") is not None
                    is_static_method = o[0].get("is_static", False)
                    in_attr_init = "static_context" in o[0]
                    is_static_ctx = o[0].get("static_context", False)

                    if storage == 'local':
                        if in_method and is_static_method: is_valid = False
                        elif in_attr_init and is_static_ctx: is_valid = False
                        elif not in_method and not in_attr_init: is_valid = False
                
                if is_valid:
                    sym = found[1]
                    primary_info = [sym["type"], sym.get("const", False)]

            # B. Nếu không phải biến, tìm Class (Static base)
            if primary_info is None:
                found_cls = self.lookupClass(name, o)
                if found_cls[0]:
                    primary_info = [name, False, "class"]

            # C. Nếu không phải class, tìm Builtin
            if primary_info is None:
                found_glob = self.lookupGlobal(name, o)
                if found_glob[0] and found_glob[2] == "builtin":
                    primary_info = [found_glob[1]["return_type"], True]

            # D. Nếu vẫn None -> LỖI
            if primary_info is None:
                # Nếu theo sau là MemberAccess/MethodCall -> UndeclaredClass
                if node.postfix_ops and isinstance(node.postfix_ops[0], (MemberAccess, MethodCall)):
                    raise UndeclaredClass(name)
                # Ngược lại -> UndeclaredIdentifier
                raise UndeclaredIdentifier(name)

        else:
            # Primary không phải Identifier (Literal, This, Parenthesized...) -> Accept bình thường
            primary_info = node.primary.accept(self, o)

        # --- NORMALIZE PRIMARY INFO ---
        primary_type = None
        is_const = False
        is_class_ref = False
        primary_name = None

        if isinstance(primary_info, (list, tuple)) and len(primary_info) == 3 and primary_info[2] == "class":
            primary_type = primary_info[0]   
            is_const = False
            is_class_ref = True
            primary_name = primary_info[0]
        elif isinstance(primary_info, (list, tuple)):
            primary_type = primary_info[0]
            is_const = primary_info[1]
            if isinstance(node.primary, Identifier):
                primary_name = node.primary.name
            elif isinstance(node.primary, ClassType):
                primary_name = node.primary.class_name
            else:
                primary_name = getattr(node.primary, "name", str(node.primary))
        else:
            primary_type = primary_info.get("type") if isinstance(primary_info, dict) else str(primary_info)
            is_const = primary_info.get("const", False) if isinstance(primary_info, dict) else False
            if isinstance(node.primary, Identifier):
                primary_name = node.primary.name
            elif isinstance(node.primary, ClassType):
                primary_name = node.primary.class_name
            else:
                primary_name = getattr(node.primary, "name", str(node.primary))
        if isinstance(node.primary, ThisExpression):
            primary_name = "this"
            primary_type = o[0].get("current")
            is_class_ref = False 

        chain = [{"kind": "primary", "name": primary_name, "type": primary_type}]
        current_type = primary_type

        # --- 2. LOOP POSTFIX OPS ---
        for i, op in enumerate(node.postfix_ops):
            if isinstance(op, MemberAccess):
                # 1. Check Type (Không phải class thì không được gọi .attr)
                is_valid_type = False
                if isinstance(current_type, str):
                    if current_type == "io": is_valid_type = True
                    elif self.lookupClass(current_type, o)[0]: is_valid_type = True
                
                if not is_valid_type:
                    raise TypeMismatchInExpression(node)

                # 2. Check Existence (Attribute có tồn tại không)
                member_name = op.member_name
                found = self.lookupClassMember(member_name, o, current_type)
                if not found[0]:
                    raise UndeclaredAttribute(member_name)
                
                member_type = found[1]["type"]
                member_static = found[1].get("static", False)

                # 3. Check Static/Instance Access
                if is_class_ref and not member_static:
                    raise IllegalMemberAccess(node)
                if (not is_class_ref) and member_static:
                    raise IllegalMemberAccess(node)

                chain.append({"kind": "attr", "name": member_name, "type": member_type})
                current_type = member_type
                is_class_ref = False
                is_const = found[1].get("const", False)

            elif isinstance(op, MethodCall):
                # 1. Check Type
                is_valid_type = False
                if isinstance(current_type, str):
                    if current_type == "io": is_valid_type = True
                    elif self.lookupClass(current_type, o)[0]: is_valid_type = True
                
                if not is_valid_type:
                    raise TypeMismatchInExpression(node)

                # 2. Check Existence
                method_name = op.method_name
                found = self.lookupClassMember(method_name, o, current_type)
                if not found[0]:
                    raise UndeclaredMethod(method_name)
                
                # 3. Check Params
                expected_params = found[1]['params']
                
                # Tham số hàm là Expression context -> Tắt is_proc
                arg_scope = o[0].copy()
                arg_scope["is_proc"] = False
                if "parent_stmt" in arg_scope:
                    del arg_scope["parent_stmt"]
                arg_env = [arg_scope] + o[1:]
                
                actual_args = [a.accept(self, arg_env) for a in op.args]

                if len(expected_params) != len(actual_args):
                    raise TypeMismatchInExpression(node)
                
                for act, exp in zip(actual_args, expected_params):
                    act_type = act[0] if isinstance(act, list) else (act['type'] if isinstance(act, dict) else str(act))
                    if not self.check_type(act_type, exp, o):
                        if o[0].get("parent_stmt"):
                            # Nếu đang được gọi trực tiếp từ MethodInvocationStatement
                            raise TypeMismatchInStatement(o[0]["parent_stmt"])
                        else:
                            # Ngữ cảnh expression bình thường
                            raise TypeMismatchInExpression(node)
                            
                ret_type = found[1].get("return_type", "void")
                method_static = found[1].get("static", False)

                # 4. Check Static/Instance
                if is_class_ref and not method_static:
                    raise IllegalMemberAccess(node)
                if (not is_class_ref) and method_static:
                    raise IllegalMemberAccess(node)

                # 5. Check VOID & Context
                if ret_type == "void":
                    is_last_op = (i == len(node.postfix_ops) - 1)
                    if not is_last_op:
                        raise TypeMismatchInExpression(node)
                    
                    # Lấy cờ từ o[0] (lúc này o[0] đã an toàn và chứa đủ thông tin)
                    is_proc = o[0].get("is_proc", False)
                    if not is_proc:
                        raise TypeMismatchInExpression(node)

                args = [a[0] if isinstance(a, list) else a['type'] for a in actual_args]
                chain.append({"kind": "method", "name": method_name, "args": args, "ret": ret_type})
                current_type = ret_type
                is_class_ref = False

            elif isinstance(op, ArrayAccess):
                if not isinstance(current_type, dict) or current_type.get("kind") != "array":
                    raise TypeMismatchInExpression(node)

                # Index context -> Tắt is_proc (mặc định)
                idx = op.index.accept(self, o)
                idx_type = idx[0] if isinstance(idx, list) else idx["type"]
                idx_const = idx[1] if isinstance(idx, list) else idx.get("const", False)

                if idx_type != "int":
                    raise TypeMismatchInExpression(node)
                
                elem_type = current_type["elem"]
                is_const = is_const and idx_const
                chain.append({"kind": "array", "index_type": "int", "elem_type": elem_type})
                current_type = elem_type
                is_class_ref = False

        res = {"type": current_type, "const": is_const, "chain": chain}
        return res

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
        
        class_env = found[1]
        
        # Collect argument types
        arg_types = []
        for arg in node.args:
            arg_info = arg.accept(self, o)
            # Normalize type info
            if isinstance(arg_info, (list, tuple)):
                arg_types.append(arg_info[0])
            elif isinstance(arg_info, dict):
                arg_types.append(arg_info["type"])
            else:
                arg_types.append(str(arg_info))
                
        # Find constructors
        # Constructors are stored in locals["methods"] with kind="Constructor"
        constructors = [
            m for m in class_env["locals"]["methods"] 
            if m.get("kind") == "Constructor"
        ]
        
        # Logic for default constructor
        if len(constructors) == 0:
            # No explicit constructors -> implicit default constructor ()
            if len(arg_types) == 0:
                return [class_name, False]
            else:
                raise TypeMismatchInExpression(node)
        
        # Check against explicit constructors
        for cons in constructors:
            param_types = cons["param_types"]
            if len(param_types) != len(arg_types):
                continue
            
            # Check type compatibility
            match = True
            for i in range(len(param_types)):
                # check_type(from, to, env)
                if not self.check_type(arg_types[i], param_types[i], o):
                    match = False
                    break
            
            if match:
                return [class_name, False]
                
        # No matching constructor found
        raise TypeMismatchInExpression(node)
 
    # def visit_static_method_invocation(
    #     self, node: "StaticMethodInvocation", o: Any = None
    # ):
    #     pass
     
    # def visit_static_member_access(self, node: "StaticMemberAccess", o: Any = None):
    #     pass
     
    # def visit_method_invocation(self, node: "MethodInvocation", o: Any = None):
    #     pass
 
    def visit_identifier(self, node: "Identifier", o: Any = None):
        # 1. Look in local/class scope
        found = self.lookupInside(node.name, o)
        if found[0]:
            is_valid = True
            if len(found) >= 4:
                storage = found[3]
                
                # Context flags
                in_method = o[0].get("method") is not None
                is_static_method = o[0].get("is_static", False)
                
                # Attribute init context
                in_attr_init = "static_context" in o[0]
                is_static_ctx = o[0].get("static_context", False)

                if storage == 'local':
                    if in_method:
                        if is_static_method: is_valid = False
                    elif in_attr_init:
                        if is_static_ctx: is_valid = False
                    else:
                        # Not in method and not in specific attr context -> likely global/class level
                        # without proper context wrapper. 
                        # This should typically be invalid for instance members.
                        is_valid = False

            if is_valid:
                sym = found[1]
                return [sym["type"], sym.get("const", False)]
        
        # 2. Look for Class (Static reference base)
        found_cls = self.lookupClass(node.name, o)
        if found_cls[0]:
            return [node.name, False, "class"]

        # 3. Builtin
        found_glob = self.lookupGlobal(node.name, o)
        if found_glob[0] and found_glob[2] == "builtin":
            return [found_glob[1]["return_type"], True]

        raise UndeclaredIdentifier(node.name)


     
    def visit_this_expression(self, node: "ThisExpression", o: Any = None):
        # Disallow in static method
        if o[0].get("method") and o[0].get("is_static", False):
            raise IllegalMemberAccess(node)
        
        # Disallow in static attribute initialization
        if o[0].get("static_context", False):
             raise IllegalMemberAccess(node)
             
        return [o[0]["current"], False]


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
        return ["boolean", True]

     
    def visit_string_literal(self, node: "StringLiteral", o: Any = None):
        return ["string", True]

     
    def visit_array_literal(self, node: "ArrayLiteral", o: Any = None):
        elems = [x.accept(self, o) for x in node.value]

        # Case 1: empty literal `{}` → hợp lệ
        if len(elems) == 0:
            return [{"kind": "array", "elem": None, "size": 0}, False]

        # Case 2: non-empty literal → kiểm tra type consistency
        elem_types = list(set([t[0] for t in elems]))
        if len(elem_types) > 1:
            raise IllegalArrayLiteral(node)
        is_const = all(t[1] for t in elems)
        return [{"kind": "array", "elem": elem_types[0], "size": len(elems)}, is_const]

     
    def visit_nil_literal(self, node: "NilLiteral", o: Any = None):
        return ["nil", True]