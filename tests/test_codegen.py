# # TODO: Add more test cases here
# # Students should implement at least 100 test cases covering:
# # - All literal types (int, float, boolean, string, array, nil)
# # - Variable declarations and assignments
# # - Binary operations (+, -, *, /, %, ==, !=, <, >, <=, >=, &&, ||)
# # - Unary operations (-, +, !)
# # - Control flow (if, for, break, continue)
# # - Return statements
# # - Method calls (static and instance)
# # - Member access
# # - Array access
# # - Object creation
# # - This expression
# # - Constructors and destructors
# # - Inheritance and polymorphism

# """
# Test cases for OPLang code generation.
# This file contains test cases for the code generator.
# """

from src.utils.nodes import *
from utils import CodeGenerator
# ==========================================
# HELPER FUNCTION (Giảm bớt việc khai báo Class Main lặp lại)
# ==========================================
def wrap_in_main(var_decls_statements: List[VariableDecl], statements: List[Statement]) -> Program:
    """Wraps a list of statements into a Main class with a static main method."""
    return Program([
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement(var_decls_statements, statements)
            )
        ])
    ])


# 1. Basic Output Tests
def test_001():
    """Test string output"""
    input_ast = Program([
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([], [
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("Hello World")])]))
                ])
            )
        ])
    ])
    expect = "Hello World"
    assert CodeGenerator().generate_and_run(input_ast) == expect

def test_002():
    """Test integer output"""
    input_ast = Program([
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([], [
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [IntLiteral(42)])]))
                ])
            )
        ])
    ])
    expect = "42"
    assert CodeGenerator().generate_and_run(input_ast) == expect

def test_003():
    """Test float output"""
    input_ast = Program([
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([], [
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeFloat", [FloatLiteral(3.14)])]))
                ])
            )
        ])
    ])
    # Note: Output format depends on emitter implementation. Standard Java float often prints .0
    # Adjusted check to strictly match emitter behavior (assuming 4 decimal places from previous context or standard)
    # If emitter uses specific formatting, adjust expectation. Assuming standard String.valueOf(float):
    expect = "3.14" 
    assert CodeGenerator().generate_and_run(input_ast) == expect

# 2. Arithmetic Expression Tests
def test_004():
    """Test complex arithmetic: (10 + 20) * 2 - 5 / 2"""
    # 10 + 20 = 30; 30 * 2 = 60; 5/2 = 2.5 (float div); 60 - 2.5 = 57.5
    input_ast = Program([
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([], [
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeFloat", [
                            BinaryOp(
                                BinaryOp(
                                    ParenthesizedExpression(BinaryOp(IntLiteral(10), "+", IntLiteral(20))),
                                    "*",
                                    IntLiteral(2)
                                ),
                                "-",
                                BinaryOp(IntLiteral(5), "/", IntLiteral(2))
                            )
                        ])
                    ]))
                ])
            )
        ])
    ])
    expect = "57.5"
    assert CodeGenerator().generate_and_run(input_ast) == expect

# 3. Variable Declaration & Assignment
def test_005():
    """Test variable declaration and assignment"""
    input_ast = Program([
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([
                    VariableDecl(False, PrimitiveType("int"), [Variable("x", IntLiteral(10))]),
                    VariableDecl(False, PrimitiveType("int"), [Variable("y")])
                ], [
                    AssignmentStatement(IdLHS("y"), BinaryOp(Identifier("x"), "+", IntLiteral(5))),
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [Identifier("y")])]))
                ])
            )
        ])
    ])
    expect = "15"
    assert CodeGenerator().generate_and_run(input_ast) == expect

# 4. Control Flow (If/Else)
def test_006():
    """Test If-Else statement"""
    input_ast = Program([
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([
                    VariableDecl(False, PrimitiveType("int"), [Variable("a", IntLiteral(5))])
                ], [
                    IfStatement(
                        BinaryOp(Identifier("a"), ">", IntLiteral(10)),
                        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("Big")])])),
                        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("Small")])]))
                    )
                ])
            )
        ])
    ])
    expect = "Small"
    assert CodeGenerator().generate_and_run(input_ast) == expect

# 5. Control Flow (For Loop)
def test_007():
    """Test For loop: sum from 1 to 5"""
    input_ast = Program([
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([
                    VariableDecl(False, PrimitiveType("int"), [Variable("i")]),
                    VariableDecl(False, PrimitiveType("int"), [Variable("sum", IntLiteral(0))])
                ], [
                    ForStatement("i", IntLiteral(1), "to", IntLiteral(5),
                        AssignmentStatement(IdLHS("sum"), BinaryOp(Identifier("sum"), "+", Identifier("i")))
                    ),
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [Identifier("sum")])]))
                ])
            )
        ])
    ])
    expect = "15" # 1+2+3+4+5
    assert CodeGenerator().generate_and_run(input_ast) == expect

# 6. Arrays
def test_008():
    """Test Array creation and access"""
    input_ast = Program([
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([
                    VariableDecl(False, ArrayType(PrimitiveType("int"), 3), [
                        Variable("arr", ArrayLiteral([IntLiteral(10), IntLiteral(20), IntLiteral(30)]))
                    ])
                ], [
                    # arr[1] = 50
                    AssignmentStatement(
                        PostfixLHS(PostfixExpression(Identifier("arr"), [ArrayAccess(IntLiteral(1))])),
                        IntLiteral(50)
                    ),
                    # print(arr[1] + arr[2]) -> 50 + 30 = 80
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeInt", [
                            BinaryOp(
                                PostfixExpression(Identifier("arr"), [ArrayAccess(IntLiteral(1))]),
                                "+",
                                PostfixExpression(Identifier("arr"), [ArrayAccess(IntLiteral(2))])
                            )
                        ])
                    ]))
                ])
            )
        ])
    ])
    expect = "80"
    assert CodeGenerator().generate_and_run(input_ast) == expect

# 7. Recursion (Factorial)
def test_009():
    """Test Recursion: Factorial(5)"""
    input_ast = Program([
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("int"), "fact", [Parameter(PrimitiveType("int"), "n")],
                BlockStatement([], [
                    IfStatement(
                        BinaryOp(Identifier("n"), "<=", IntLiteral(1)),
                        ReturnStatement(IntLiteral(1)),
                        ReturnStatement(BinaryOp(
                            Identifier("n"), 
                            "*", 
                            PostfixExpression(Identifier("Main"), [MethodCall("fact", [BinaryOp(Identifier("n"), "-", IntLiteral(1))])])
                        ))
                    )
                ])
            ),
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([], [
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeInt", [
                            PostfixExpression(Identifier("Main"), [MethodCall("fact", [IntLiteral(5)])])
                        ])
                    ]))
                ])
            )
        ])
    ])
    expect = "120"
    assert CodeGenerator().generate_and_run(input_ast) == expect

# 8. Class & Object
def test_010():
    """Test Class instantiation and field access"""
    input_ast = Program([
        ClassDecl("Point", None, [
            AttributeDecl(False, False, PrimitiveType("int"), [Attribute("x"), Attribute("y")]),
            ConstructorDecl('Point', [], BlockStatement([],
                                                        [
                                                            AssignmentStatement(PostfixExpression(Identifier("this"), [MemberAccess("x")]), IntLiteral(0)),
                                                            AssignmentStatement(PostfixExpression(Identifier("this"), [MemberAccess("y")]), IntLiteral(0))
                                                        ]
                                                        # []
            ))
        ]),
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([
                    VariableDecl(False, ClassType("Point"), [
                        Variable("p", ObjectCreation("Point", [])),
                    ]),
                    VariableDecl(False, PrimitiveType("int"), [
                        Variable("x")
                    ])
                ], [
                    AssignmentStatement(
                        PostfixLHS(PostfixExpression(Identifier("p"), [MemberAccess("x")])),
                        IntLiteral(99)
                    ),
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeInt", [
                            PostfixExpression(Identifier("p"), [MemberAccess("x")])
                        ])
                    ])),
                    AssignmentStatement(
                        # x = p.x
                        IdLHS("x"),
                        PostfixExpression(Identifier("p"), [MemberAccess("x")])

                        # IntLiteral(99)
                    ),
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeInt", [Identifier("x")])
                    ]))
                ])
            )
        ])
    ])
    expect = "9999"
    assert CodeGenerator().generate_and_run(input_ast) == expect

# 9. Short-circuit Logic
def test_011():
    """Test Short-circuit AND (&&)"""
    # if (false && (1/0 == 0)) ... should NOT divide by zero
    input_ast = Program([
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([], [
                    IfStatement(
                        BinaryOp(BoolLiteral(False), "&&", BinaryOp(BinaryOp(IntLiteral(1), "\\", IntLiteral(0)), "==", IntLiteral(0))),
                        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("Crash")])])),
                        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("Safe")])]))
                    )
                ])
            )
        ])
    ])
    expect = "Safe"
    assert CodeGenerator().generate_and_run(input_ast) == expect

def test_012():
    """Test Short-circuit OR (||)"""
    # if (true || (1/0 == 0)) ... should NOT divide by zero
    input_ast = Program([
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([], [
                    IfStatement(
                        BinaryOp(BoolLiteral(True), "||", BinaryOp(BinaryOp(IntLiteral(1), "\\", IntLiteral(0)), "==", IntLiteral(0))),
                        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("Safe")])])),
                        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("Crash")])]))
                    )
                ])
            )
        ])
    ])
    expect = "Safe"
    assert CodeGenerator().generate_and_run(input_ast) == expect

def test_013():
    """Test mixed arithmetic operator precedence"""
    # source = """
    # class Main {
    #     static void main() {
    #         int a := 2 + 3 * 4 + 5;
    #         int b := 10 - 2 * 3;
    #         io.writeIntLn(a);
    #         io.writeIntLn(b);
    #     }
    # }
    # """
    source = Program([
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([
                    VariableDecl(False, PrimitiveType("int"), [
                        Variable("a", BinaryOp(
                            BinaryOp(IntLiteral(2), "+", BinaryOp(IntLiteral(3), "*", IntLiteral(4))),
                            "+",
                            IntLiteral(5)
                        ))
                    ]),
                    VariableDecl(False, PrimitiveType("int"), [
                        Variable("b", BinaryOp(
                            IntLiteral(10),
                            "-",
                            BinaryOp(IntLiteral(2), "*", IntLiteral(3))
                        ))
                    ])
                ], [
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeIntLn", [Identifier("a")])
                    ])),
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeIntLn", [Identifier("b")])
                    ]))
                ])
            )
        ])
    ])
    expect = "19\n4"
    assert CodeGenerator().generate_and_run(source) == expect



# # ==========================================
# # GROUP 2: OPERATORS & EXPRESSIONS (Tiếp tục từ test_013)
# # ==========================================

def test_014():
    """test coercion (subclass to superclass & int to float)"""
    ast = Program([
        ClassDecl("ZA", None, [
            ConstructorDecl("ZA", [], BlockStatement([], []))
        ]),
        ClassDecl("ZB", "ZA", [
            ConstructorDecl("ZB", [], BlockStatement([], []))
        ]),
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([
                    VariableDecl(False, ClassType("ZA"), [Variable("a", ObjectCreation("ZB", []))]),
                    VariableDecl(False, PrimitiveType("float"), [Variable("f", IntLiteral(5))])
                ], [
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeFloat", [Identifier("f")])
                    ]))
                ])
            )
        ])
    ])
    assert CodeGenerator().generate_and_run(ast) == "5.0"

def test_015():
    """Unary Operator: Boolean NOT"""
    # print(!true)
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeBool", [UnaryOp("!", BoolLiteral(True))])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([],[stmt])) == "false"

def test_016():
    """Binary Op: Modulo"""
    # print(10 % 3)
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [BinaryOp(IntLiteral(10), "%", IntLiteral(3))])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([],[stmt])) == "1"

def test_017():
    """Binary Op: String Concatenation"""
    # print("Hello" ^ " " ^ "World")
    expr = BinaryOp(BinaryOp(StringLiteral("Hello"), "^", StringLiteral(" ")), "^", StringLiteral("World"))
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [expr])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([],[stmt])) == "Hello World"

def test_018():
    """Comparison: Less Than Equal"""
    # print(5 <= 5)
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeBool", [BinaryOp(IntLiteral(5), "<=", IntLiteral(5))])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([],[stmt])) == "true"

def test_019():
    """Comparison: Not Equal (Float)"""
    # print(5.1 != 5.0)
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeBool", [BinaryOp(FloatLiteral(5.1), "!=", FloatLiteral(5.0))])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([],[stmt])) == "true"

def test_020():
    """Type Coercion: Int + Float"""
    # print(2 + 3.5) -> 5.5
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeFloat", [BinaryOp(IntLiteral(2), "+", FloatLiteral(3.5))])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([],[stmt])) == "5.5"

def test_021():
    """Precedence: * over +"""
    # print(2 + 3 * 4) -> 14
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [BinaryOp(IntLiteral(2), "+", BinaryOp(IntLiteral(3), "*", IntLiteral(4)))])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([],[stmt])) == "14"

def test_022():
    """Precedence: Parentheses"""
    # print((2 + 3) * 4) -> 20
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [BinaryOp(ParenthesizedExpression(BinaryOp(IntLiteral(2), "+", IntLiteral(3))), "*", IntLiteral(4))])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([],[stmt])) == "20"

def test_023():
    """Integer Division (Backslash)"""
    # print(7 \ 2) -> 3
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [BinaryOp(IntLiteral(7), "\\", IntLiteral(2))])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([],[stmt])) == "3"

def test_024():
    """Float Division (Slash)"""
    # print(7 / 2) -> 3.5
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeFloat", [BinaryOp(IntLiteral(7), "/", IntLiteral(2))])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([],[stmt])) == "3.5"

def test_025():
    """Complex Boolean Logic"""
    # print((true && false) || true) -> true
    expr = BinaryOp(BinaryOp(BoolLiteral(True), "&&", BoolLiteral(False)), "||", BoolLiteral(True))
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeBool", [expr])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([],[stmt])) == "true"

def test_026():
    """Variable: Uninitialized Int (Default 0?) or Just Decl"""
    # int x := 10; x := x * x; print(x)
    var_decls = [VariableDecl(False, PrimitiveType("int"), [Variable("x", IntLiteral(10))])]
    stmts = [
        AssignmentStatement(IdLHS("x"), BinaryOp(Identifier("x"), "*", Identifier("x"))),
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [Identifier("x")])]))
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls_statements=var_decls, statements=stmts)) == "100"


def test_027():
    """Variable: Multiple Declaration"""
    # int a := 1, b := 2; print(a+b)
    var_decls = [VariableDecl(False, PrimitiveType("int"), [Variable("a", IntLiteral(1)), Variable("b", IntLiteral(2))])]
    stmts = [
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [BinaryOp(Identifier("a"), "+", Identifier("b"))])]))
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls,stmts)) == "3"

def test_028():
    """Float Scientific Notation"""
    # float f := 1.5e2; print(f) -> 150.0
    var_decls = [VariableDecl(False, PrimitiveType("float"), [Variable("f", FloatLiteral(1.5e2))])]
    stmts = [
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeFloat", [Identifier("f")])]))
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls,stmts)) == "150.0"

def test_029():
    """String Escape Sequences"""
    # print("A\nB")
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("A\nB")])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([],[stmt])) == "A\nB"

def test_030():
    """Nested Expressions"""
    # print((10 - 2) * (3 + 1) / 2) -> 8 * 4 / 2 = 16.0 (float div)
    expr = BinaryOp(BinaryOp(ParenthesizedExpression(BinaryOp(IntLiteral(10), "-", IntLiteral(2))), "*", ParenthesizedExpression(BinaryOp(IntLiteral(3), "+", IntLiteral(1)))), "/", IntLiteral(2))
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeFloat", [expr])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([],[stmt])) == "16.0"

# # ==========================================
# # GROUP 3: CONTROL FLOW (31 - 50)
# # ==========================================

def test_031():
    """If without Else (False condition)"""
    stmts = [
        IfStatement(BoolLiteral(False), 
            MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("ShouldNotPrint")])])),
            None
        ),
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("Done")])]))
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main([],stmts)) == "Done"

def test_032():
    """Nested If Statements"""
    var_decls = [VariableDecl(False, PrimitiveType("int"), [Variable("x", IntLiteral(10))])]
    stmts = [
        IfStatement(BinaryOp(Identifier("x"), ">", IntLiteral(5)),
            BlockStatement([], [
                IfStatement(BinaryOp(Identifier("x"), "<", IntLiteral(20)),
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("Target")])])),
                    None
                )
            ]),
            None
        )
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls,stmts)) == "Target"

def test_033():
    """For Loop: Downto"""
    # for i := 3 downto 1 do print(i)
    var_decls = [VariableDecl(False, PrimitiveType("int"), [Variable("i")])]
    stmts = [
        ForStatement("i", IntLiteral(3), "downto", IntLiteral(1),
            MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [Identifier("i")])]))
        )
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls,stmts)) == "321"
def test_034():
    """For Loop with Break"""
    var_decls = [VariableDecl(False, PrimitiveType("int"), [Variable("i")])]
    stmts = [
        ForStatement("i", IntLiteral(1), "to", IntLiteral(5),
            BlockStatement([], [
                IfStatement(BinaryOp(Identifier("i"), "==", IntLiteral(3)), BreakStatement(), None),
                MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [Identifier("i")])]))
            ])
        )
    ]
    # Should print 1, 2 then break
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls,stmts)) == "12"

def test_035():
    """For Loop with Continue"""
    var_decls = [VariableDecl(False, PrimitiveType("int"), [Variable("i")])]
    stmts = [
        ForStatement("i", IntLiteral(1), "to", IntLiteral(4),
            BlockStatement([], [
                IfStatement(BinaryOp(Identifier("i"), "==", IntLiteral(2)), ContinueStatement(), None),
                MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [Identifier("i")])]))
            ])
        )
    ]
    # Should print 1, 3, 4 (skip 2)
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls,stmts)) == "134"

def test_036():
    """While Loop Simulation (using For with Break)"""
    # OPLang doesn't have 'while', simulate with for and break
    var_decls = [VariableDecl(False, PrimitiveType("int"), [Variable("k", IntLiteral(0))]),
        VariableDecl(False, PrimitiveType("int"), [Variable("dummy")])] # For loop needs a var
    stmts = [
        ForStatement("dummy", IntLiteral(1), "to", IntLiteral(100),
            BlockStatement([], [
                IfStatement(BinaryOp(Identifier("k"), ">=", IntLiteral(3)), BreakStatement(), None),
                MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [Identifier("k")])])),
                AssignmentStatement(IdLHS("k"), BinaryOp(Identifier("k"), "+", IntLiteral(1)))
            ])
        )
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls,stmts)) == "012"
def test_037():
    """Nested Loops (Multiplication Table small)"""
    var_decls = [VariableDecl(False, PrimitiveType("int"), [Variable("i")]),
        VariableDecl(False, PrimitiveType("int"), [Variable("j")])]
    stmts = [
        ForStatement("i", IntLiteral(1), "to", IntLiteral(2),
            ForStatement("j", IntLiteral(1), "to", IntLiteral(2),
                MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [BinaryOp(Identifier("i"), "*", Identifier("j"))])]))
            )
        )
    ]
    # 1*1=1, 1*2=2, 2*1=2, 2*2=4 -> 1224
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls,stmts)) == "1224"

def test_038():
    """Loop modifying outer variable"""
    var_decls = [VariableDecl(False, PrimitiveType("int"), [Variable("sum", IntLiteral(0))]),
        VariableDecl(False, PrimitiveType("int"), [Variable("i")])]
    stmts = [
        ForStatement("i", IntLiteral(1), "to", IntLiteral(4),
            AssignmentStatement(IdLHS("sum"), BinaryOp(Identifier("sum"), "+", Identifier("i")))
        ),
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [Identifier("sum")])]))
    ]
    # 1+2+3+4 = 10
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls,stmts)) == "10"

def test_039():
    """Condition with function call (simulated by expression)"""
    stmts = [
         IfStatement(BinaryOp(BinaryOp(IntLiteral(1), "+", IntLiteral(1)), "==", IntLiteral(2)),
            MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("Yes")])])),
            None
         )
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main([],stmts)) == "Yes"

def test_040():
    """Empty Block"""
    stmts = [
        BlockStatement([], []),
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("End")])]))
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main([],stmts)) == "End"

def test_041():
    """If with complex condition"""
    stmts = [
        IfStatement(
            BinaryOp(
                BinaryOp(IntLiteral(5), ">", IntLiteral(3)),
                "&&",
                BinaryOp(IntLiteral(2), "<", IntLiteral(4))
            ),
            MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("True")])])),
            None
        )
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main([],stmts)) == "True"

def test_042():
    # Destructor method
    source = Program([
        ClassDecl(
            "Main", None, [
                MethodDecl(True, PrimitiveType("void"), "main", [],
                    BlockStatement([], [
                        VariableDecl(False, ClassType("Main"), [
                            Variable("obj", ObjectCreation("Main", []))
                        ])
                    ])),
                ConstructorDecl('Main', [], BlockStatement([], [
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("Main Constructor")])])),
                ]))
            ]
        )])
    expect = "Main Constructor"
    assert CodeGenerator().generate_and_run(source) == expect

# ==========================================
# ADDITIONAL TESTS (43-100) - 58 tests
# ==========================================

# GROUP 4: LITERALS & TYPES (43-49)
def test_043():
    """Constant variable"""
    var_decls = [VariableDecl(True, PrimitiveType("int"), [Variable("a", IntLiteral(1))])]
    stmts = [
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [Identifier("a")])])),
        AssignmentStatement(IdLHS("a"), IntLiteral(2))
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls,stmts)) == "1"

def test_044():
    """Test Boolean True/False"""
    stmts = [
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeBool", [BoolLiteral(True)])])),
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeBool", [BoolLiteral(False)])])),
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main([], stmts)) == "truefalse"

def test_045():
    """Test Large Integer"""
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [IntLiteral(999999)])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([], [stmt])) == "999999"

def test_046():
    """Test Small Float"""
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeFloat", [FloatLiteral(0.001)])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([], [stmt])) == "0.001"

def test_047():
    """Test Empty String"""
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("")])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([], [stmt])) == ""

def test_048():
    """Test String with Tab"""
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("A\\tB")])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([], [stmt])) == "A\tB"

def test_049():
    """Test Array of Floats"""
    var_decls = [VariableDecl(False, ArrayType(PrimitiveType("float"), 2), [
        Variable("arr", ArrayLiteral([FloatLiteral(1.5), FloatLiteral(2.5)]))
    ])]
    stmts = [
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [
            MethodCall("writeFloat", [PostfixExpression(Identifier("arr"), [ArrayAccess(IntLiteral(0))])])
        ])),
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [
            MethodCall("writeFloat", [PostfixExpression(Identifier("arr"), [ArrayAccess(IntLiteral(1))])])
        ]))
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "1.52.5"

# GROUP 5: OPERATORS (50-59)
def test_050():
    """Test Greater Than"""
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeBool", [BinaryOp(IntLiteral(10), ">", IntLiteral(5))])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([], [stmt])) == "true"

def test_051():
    """Test Less Than"""
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeBool", [BinaryOp(IntLiteral(3), "<", IntLiteral(7))])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([], [stmt])) == "true"

def test_052():
    """Test Greater or Equal (Equal case)"""
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeBool", [BinaryOp(IntLiteral(5), ">=", IntLiteral(5))])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([], [stmt])) == "true"

def test_053():
    """Test Modulo with variables"""
    var_decls = [VariableDecl(False, PrimitiveType("int"), [Variable("a", IntLiteral(17)), Variable("b", IntLiteral(5))])]
    stmts = [
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [
            MethodCall("writeInt", [BinaryOp(Identifier("a"), "%", Identifier("b"))])
        ]))
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "2"

def test_054():
    """Test Unary Plus"""
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [UnaryOp("+", IntLiteral(42))])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([], [stmt])) == "42"

def test_055():
    """Test Chained String Concatenation"""
    expr = BinaryOp(BinaryOp(BinaryOp(StringLiteral("A"), "^", StringLiteral("B")), "^", StringLiteral("C")), "^", StringLiteral("D"))
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [expr])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([], [stmt])) == "ABCD"

def test_056():
    """Test AND operator with false result"""
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [
        MethodCall("writeBool", [BinaryOp(BoolLiteral(True), "&&", BoolLiteral(False))])
    ]))
    assert CodeGenerator().generate_and_run(wrap_in_main([], [stmt])) == "false"

def test_057():
    """Test OR operator with true result"""
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [
        MethodCall("writeBool", [BinaryOp(BoolLiteral(False), "||", BoolLiteral(True))])
    ]))
    assert CodeGenerator().generate_and_run(wrap_in_main([], [stmt])) == "true"

def test_058():
    """Test Equality with strings"""
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [
        MethodCall("writeBool", [BinaryOp(StringLiteral("test"), "==", StringLiteral("test"))])
    ]))
    assert CodeGenerator().generate_and_run(wrap_in_main([], [stmt])) == "true"

def test_059():
    """Test Inequality with integers"""
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [
        MethodCall("writeBool", [BinaryOp(IntLiteral(5), "!=", IntLiteral(10))])
    ]))
    assert CodeGenerator().generate_and_run(wrap_in_main([], [stmt])) == "true"

# GROUP 6: VARIABLES & ASSIGNMENT (60-67)
def test_060():
    """Test Multiple Variables Same Line"""
    var_decls = [VariableDecl(False, PrimitiveType("int"), [
        Variable("x", IntLiteral(1)),
        Variable("y", IntLiteral(2)),
        Variable("z", IntLiteral(3))
    ])]
    stmts = [
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [
            MethodCall("writeInt", [BinaryOp(BinaryOp(Identifier("x"), "+", Identifier("y")), "+", Identifier("z"))])
        ]))
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "6"

def test_061():
    """Test Variable Reassignment"""
    var_decls = [VariableDecl(False, PrimitiveType("int"), [Variable("x", IntLiteral(10))])]
    stmts = [
        AssignmentStatement(IdLHS("x"), IntLiteral(20)),
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [Identifier("x")])]))
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "20"

def test_062():
    """Test Variable with Expression"""
    var_decls = [VariableDecl(False, PrimitiveType("int"), [Variable("result", BinaryOp(IntLiteral(5), "*", IntLiteral(4)))])]
    stmts = [
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [Identifier("result")])]))
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "20"

def test_063():
    """Test Float Variable"""
    var_decls = [VariableDecl(False, PrimitiveType("float"), [Variable("pi", FloatLiteral(3.14159))])]
    stmts = [
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeFloat", [Identifier("pi")])]))
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "3.1416"

def test_064():
    """Test String Variable"""
    var_decls = [VariableDecl(False, PrimitiveType("string"), [Variable("msg", StringLiteral("Test"))])]
    stmts = [
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [Identifier("msg")])]))
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "Test"

def test_065():
    """Test Boolean Variable"""
    var_decls = [VariableDecl(False, PrimitiveType("boolean"), [Variable("f", BoolLiteral(True))])]
    stmts = [
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeBool", [Identifier("f")])]))
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "true"

def test_066():
    """Test Assignment Chain"""
    var_decls = [
        VariableDecl(False, PrimitiveType("int"), [Variable("a", IntLiteral(5))]),
        VariableDecl(False, PrimitiveType("int"), [Variable("b")]),
        VariableDecl(False, PrimitiveType("int"), [Variable("c")])
    ]
    stmts = [
        AssignmentStatement(IdLHS("b"), Identifier("a")),
        AssignmentStatement(IdLHS("c"), Identifier("b")),
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [Identifier("c")])]))
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "5"

def test_067():
    """Test Variable Uninitialized then Assigned"""
    var_decls = [VariableDecl(False, PrimitiveType("int"), [Variable("x")])]
    stmts = [
        AssignmentStatement(IdLHS("x"), IntLiteral(100)),
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [Identifier("x")])]))
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "100"

# GROUP 7: CONTROL FLOW (68-77)
def test_068():
    """Test If without Else (True condition)"""
    stmts = [
        IfStatement(BoolLiteral(True),
            MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("Yes")])])),
            None
        )
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main([], stmts)) == "Yes"

def test_069():
    """Test If-Else with complex boolean"""
    var_decls = [VariableDecl(False, PrimitiveType("int"), [Variable("age", IntLiteral(18))])]
    stmts = [
        IfStatement(BinaryOp(Identifier("age"), ">=", IntLiteral(18)),
            MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("Adult")])])),
            MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("Minor")])]))
        )
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "Adult"

def test_070():
    """Test For Loop 1 to 3"""
    var_decls = [VariableDecl(False, PrimitiveType("int"), [Variable("i")])]
    stmts = [
        ForStatement("i", IntLiteral(1), "to", IntLiteral(3),
            MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [Identifier("i")])]))
        )
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "123"

def test_071():
    """Test For Loop 5 downto 3"""
    var_decls = [VariableDecl(False, PrimitiveType("int"), [Variable("i")])]
    stmts = [
        ForStatement("i", IntLiteral(5), "downto", IntLiteral(3),
            MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [Identifier("i")])]))
        )
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "543"

def test_072():
    """Test Break in Loop"""
    var_decls = [VariableDecl(False, PrimitiveType("int"), [Variable("i")])]
    stmts = [
        ForStatement("i", IntLiteral(1), "to", IntLiteral(10),
            BlockStatement([], [
                IfStatement(BinaryOp(Identifier("i"), ">", IntLiteral(3)), BreakStatement(), None),
                MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [Identifier("i")])]))
            ])
        )
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "123"

def test_073():
    """Test Continue in Loop"""
    var_decls = [VariableDecl(False, PrimitiveType("int"), [Variable("i")])]
    stmts = [
        ForStatement("i", IntLiteral(1), "to", IntLiteral(5),
            BlockStatement([], [
                IfStatement(BinaryOp(Identifier("i"), "==", IntLiteral(3)), ContinueStatement(), None),
                MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [Identifier("i")])]))
            ])
        )
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "1245"

def test_074():
    """Test Nested If-Else"""
    var_decls = [VariableDecl(False, PrimitiveType("int"), [Variable("x", IntLiteral(15))])]
    stmts = [
        IfStatement(BinaryOp(Identifier("x"), ">", IntLiteral(10)),
            IfStatement(BinaryOp(Identifier("x"), ">", IntLiteral(20)),
                MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("Large")])])),
                MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("Medium")])]))
            ),
            MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("Small")])]))
        )
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "Medium"

def test_075():
    """Test For Loop with Accumulator"""
    var_decls = [
        VariableDecl(False, PrimitiveType("int"), [Variable("i")]),
        VariableDecl(False, PrimitiveType("int"), [Variable("product", IntLiteral(1))])
    ]
    stmts = [
        ForStatement("i", IntLiteral(1), "to", IntLiteral(4),
            AssignmentStatement(IdLHS("product"), BinaryOp(Identifier("product"), "*", Identifier("i")))
        ),
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [Identifier("product")])]))
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "24"  # 1*2*3*4

def test_076():
    """Test Loop with Empty Body via Block"""
    var_decls = [VariableDecl(False, PrimitiveType("int"), [Variable("i")])]
    stmts = [
        ForStatement("i", IntLiteral(1), "to", IntLiteral(3), BlockStatement([], [])),
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("Done")])]))
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "Done"

def test_077():
    """Test Multiple If Statements Sequential"""
    var_decls = [VariableDecl(False, PrimitiveType("int"), [Variable("x", IntLiteral(5))])]
    stmts = [
        IfStatement(BinaryOp(Identifier("x"), ">", IntLiteral(0)),
            MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("Positive")])])),
            None
        ),
        IfStatement(BinaryOp(Identifier("x"), "<", IntLiteral(10)),
            MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("Small")])])),
            None
        )
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "PositiveSmall"

# GROUP 8: METHODS & FUNCTIONS (78-85)
def test_078():
    """Test Static Method with Return"""
    input_ast = Program([
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("int"), "add", [
                Parameter(PrimitiveType("int"), "a"),
                Parameter(PrimitiveType("int"), "b")
            ], BlockStatement([], [
                ReturnStatement(BinaryOp(Identifier("a"), "+", Identifier("b")))
            ])),
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([], [
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeInt", [PostfixExpression(Identifier("Main"), [MethodCall("add", [IntLiteral(3), IntLiteral(7)])])])
                    ]))
                ])
            )
        ])
    ])
    assert CodeGenerator().generate_and_run(input_ast) == "10"

def test_079():
    """Test Method with No Parameters"""
    input_ast = Program([
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("int"), "getNumber", [],
                BlockStatement([], [ReturnStatement(IntLiteral(42))])
            ),
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([], [
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeInt", [PostfixExpression(Identifier("Main"), [MethodCall("getNumber", [])])])
                    ]))
                ])
            )
        ])
    ])
    assert CodeGenerator().generate_and_run(input_ast) == "42"

def test_080():
    """Test Method Returning Float"""
    input_ast = Program([
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("float"), "half", [Parameter(PrimitiveType("int"), "n")],
                BlockStatement([], [
                    ReturnStatement(BinaryOp(Identifier("n"), "/", IntLiteral(2)))
                ])
            ),
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([], [
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeFloat", [PostfixExpression(Identifier("Main"), [MethodCall("half", [IntLiteral(5)])])])
                    ]))
                ])
            )
        ])
    ])
    assert CodeGenerator().generate_and_run(input_ast) == "2.5"

def test_081():
    """Test Method Returning Boolean"""
    input_ast = Program([
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("boolean"), "isPositive", [Parameter(PrimitiveType("int"), "n")],
                BlockStatement([], [
                    ReturnStatement(BinaryOp(Identifier("n"), ">", IntLiteral(0)))
                ])
            ),
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([], [
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeBool", [PostfixExpression(Identifier("Main"), [MethodCall("isPositive", [IntLiteral(5)])])])
                    ]))
                ])
            )
        ])
    ])
    assert CodeGenerator().generate_and_run(input_ast) == "true"

def test_082():
    """Test Method Returning String"""
    input_ast = Program([
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("string"), "greet", [Parameter(PrimitiveType("string"), "name")],
                BlockStatement([], [
                    ReturnStatement(BinaryOp(StringLiteral("Hello "), "^", Identifier("name")))
                ])
            ),
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([], [
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeStr", [PostfixExpression(Identifier("Main"), [MethodCall("greet", [StringLiteral("World")])])])
                    ]))
                ])
            )
        ])
    ])
    assert CodeGenerator().generate_and_run(input_ast) == "Hello World"

def test_083():
    """Test Recursive Fibonacci"""
    input_ast = Program([
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("int"), "fib", [Parameter(PrimitiveType("int"), "n")],
                BlockStatement([], [
                    IfStatement(BinaryOp(Identifier("n"), "<=", IntLiteral(1)),
                        ReturnStatement(Identifier("n")),
                        ReturnStatement(BinaryOp(
                            PostfixExpression(Identifier("Main"), [MethodCall("fib", [BinaryOp(Identifier("n"), "-", IntLiteral(1))])]),
                            "+",
                            PostfixExpression(Identifier("Main"), [MethodCall("fib", [BinaryOp(Identifier("n"), "-", IntLiteral(2))])])
                        ))
                    )
                ])
            ),
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([], [
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeInt", [PostfixExpression(Identifier("Main"), [MethodCall("fib", [IntLiteral(6)])])])
                    ]))
                ])
            )
        ])
    ])
    assert CodeGenerator().generate_and_run(input_ast) == "8"  # fib(6) = 8

def test_084():
    """Test Method with Multiple Parameters"""
    input_ast = Program([
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("int"), "max3", [
                Parameter(PrimitiveType("int"), "a"),
                Parameter(PrimitiveType("int"), "b"),
                Parameter(PrimitiveType("int"), "c")
            ], BlockStatement([], [
                IfStatement(BinaryOp(BinaryOp(Identifier("a"), ">=", Identifier("b")), "&&", BinaryOp(Identifier("a"), ">=", Identifier("c"))),
                    ReturnStatement(Identifier("a")),
                    IfStatement(BinaryOp(Identifier("b"), ">=", Identifier("c")),
                        ReturnStatement(Identifier("b")),
                        ReturnStatement(Identifier("c"))
                    )
                )
            ])),
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([], [
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeInt", [PostfixExpression(Identifier("Main"), [MethodCall("max3", [IntLiteral(3), IntLiteral(7), IntLiteral(5)])])])
                    ]))
                ])
            )
        ])
    ])
    assert CodeGenerator().generate_and_run(input_ast) == "7"

def test_085():
    """Test Void Method (No Return)"""
    input_ast = Program([
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "printHello", [],
                BlockStatement([], [
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeStr", [StringLiteral("Hello")])]))
                ])
            ),
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([], [
                    MethodInvocationStatement(PostfixExpression(Identifier("Main"), [MethodCall("printHello", [])]))
                ])
            )
        ])
    ])
    assert CodeGenerator().generate_and_run(input_ast) == "Hello"

# GROUP 9: CLASSES & OBJECTS (86-93)
def test_086():
    """Test Class with Fields"""
    input_ast = Program([
        ClassDecl("Person", None, [
            AttributeDecl(False, False, PrimitiveType("string"), [Attribute("name")]),
            AttributeDecl(False, False, PrimitiveType("int"), [Attribute("age")])
        ]),
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([
                    VariableDecl(False, ClassType("Person"), [Variable("p", ObjectCreation("Person", []))])
                ], [
                    AssignmentStatement(PostfixLHS(PostfixExpression(Identifier("p"), [MemberAccess("age")])), IntLiteral(25)),
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeInt", [PostfixExpression(Identifier("p"), [MemberAccess("age")])])
                    ]))
                ])
            )
        ])
    ])
    assert CodeGenerator().generate_and_run(input_ast) == "25"

def test_087():
    """Test Constructor with Parameters"""
    input_ast = Program([
        ClassDecl("Mox", None, [
            AttributeDecl(False, False, PrimitiveType("int"), [Attribute("width"), Attribute("height")]),
            ConstructorDecl("Mox", [Parameter(PrimitiveType("int"), "w"), Parameter(PrimitiveType("int"), "h")],
                BlockStatement([], [
                    AssignmentStatement(PostfixLHS(PostfixExpression(Identifier("this"), [MemberAccess("width")])), Identifier("w")),
                    AssignmentStatement(PostfixLHS(PostfixExpression(Identifier("this"), [MemberAccess("height")])), Identifier("h"))
                ])
            )
        ]),
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([
                    VariableDecl(False, ClassType("Mox"), [Variable("b", ObjectCreation("Mox", [IntLiteral(10), IntLiteral(20)]))])
                ], [
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeInt", [PostfixExpression(Identifier("b"), [MemberAccess("width")])])
                    ])),
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeInt", [PostfixExpression(Identifier("b"), [MemberAccess("height")])])
                    ]))
                ])
            )
        ])
    ])
    assert CodeGenerator().generate_and_run(input_ast) == "1020"

def test_088():
    """Test Instance Method"""
    input_ast = Program([
        ClassDecl("Mox", None, [
            AttributeDecl(False, False, PrimitiveType("int"), [Attribute("count")]),
            ConstructorDecl("Mox", [], BlockStatement([], [
                AssignmentStatement(PostfixLHS(PostfixExpression(Identifier("this"), [MemberAccess("count")])), IntLiteral(0))
            ])),
            MethodDecl(False, PrimitiveType("void"), "increment", [],
                BlockStatement([], [
                    AssignmentStatement(
                        PostfixLHS(PostfixExpression(Identifier("this"), [MemberAccess("count")])),
                        BinaryOp(PostfixExpression(Identifier("this"), [MemberAccess("count")]), "+", IntLiteral(1))
                    )
                ])
            ),
            MethodDecl(False, PrimitiveType("int"), "getCount", [],
                BlockStatement([], [
                    ReturnStatement(PostfixExpression(Identifier("this"), [MemberAccess("count")]))
                ])
            )
        ]),
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([
                    VariableDecl(False, ClassType("Mox"), [Variable("c", ObjectCreation("Mox", []))])
                ], [
                    MethodInvocationStatement(PostfixExpression(Identifier("c"), [MethodCall("increment", [])])),
                    MethodInvocationStatement(PostfixExpression(Identifier("c"), [MethodCall("increment", [])])),
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeInt", [PostfixExpression(Identifier("c"), [MethodCall("getCount", [])])])
                    ]))
                ])
            )
        ])
    ])
    assert CodeGenerator().generate_and_run(input_ast) == "2"

def test_089():
    """Test This Keyword"""
    input_ast = Program([
        ClassDecl("Mata", None, [
            AttributeDecl(False, False, PrimitiveType("int"), [Attribute("value")]),
            MethodDecl(False, PrimitiveType("void"), "setValue", [Parameter(PrimitiveType("int"), "value")],
                BlockStatement([], [
                    AssignmentStatement(
                        PostfixLHS(PostfixExpression(Identifier("this"), [MemberAccess("value")])),
                        Identifier("value")
                    )
                ])
            )
        ]),
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([
                    VariableDecl(False, ClassType("Mata"), [Variable("d", ObjectCreation("Mata", []))])
                ], [
                    MethodInvocationStatement(PostfixExpression(Identifier("d"), [MethodCall("setValue", [IntLiteral(99)])])),
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeInt", [PostfixExpression(Identifier("d"), [MemberAccess("value")])])
                    ]))
                ])
            )
        ])
    ])
    assert CodeGenerator().generate_and_run(input_ast) == "99"

def test_090():
    """Test Multiple Objects"""
    input_ast = Program([
        ClassDecl("Point", None, [
            AttributeDecl(False, False, PrimitiveType("int"), [Attribute("x"), Attribute("y")]),
            ConstructorDecl("Point", [Parameter(PrimitiveType("int"), "x"), Parameter(PrimitiveType("int"), "y")],
                BlockStatement([], [
                    AssignmentStatement(PostfixLHS(PostfixExpression(Identifier("this"), [MemberAccess("x")])), Identifier("x")),
                    AssignmentStatement(PostfixLHS(PostfixExpression(Identifier("this"), [MemberAccess("y")])), Identifier("y"))
                ])
            )
        ]),
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([
                    VariableDecl(False, ClassType("Point"), [Variable("p1", ObjectCreation("Point", [IntLiteral(1), IntLiteral(2)]))]),
                    VariableDecl(False, ClassType("Point"), [Variable("p2", ObjectCreation("Point", [IntLiteral(3), IntLiteral(4)]))])
                ], [
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeInt", [PostfixExpression(Identifier("p1"), [MemberAccess("x")])])
                    ])),
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeInt", [PostfixExpression(Identifier("p2"), [MemberAccess("y")])])
                    ]))
                ])
            )
        ])
    ])
    assert CodeGenerator().generate_and_run(input_ast) == "14"

def test_091():
    """Test Static Field"""
    input_ast = Program([
        ClassDecl("Monfig", None, [
            AttributeDecl(True, False, PrimitiveType("int"), [Attribute("version", IntLiteral(1))])
        ]),
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([], [
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeInt", [PostfixExpression(Identifier("Monfig"), [MemberAccess("version")])])
                    ]))
                ])
            )
        ])
    ])
    assert CodeGenerator().generate_and_run(input_ast) == "1"

def test_092():
    """Test Object Field Assignment via Method"""
    input_ast = Program([
        ClassDecl("Mell", None, [
            AttributeDecl(False, False, PrimitiveType("int"), [Attribute("data")]),
            MethodDecl(False, PrimitiveType("int"), "getData", [],
                BlockStatement([], [ReturnStatement(PostfixExpression(Identifier("this"), [MemberAccess("data")]))])
            )
        ]),
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([
                    VariableDecl(False, ClassType("Mell"), [Variable("c", ObjectCreation("Mell", []))])
                ], [
                    AssignmentStatement(PostfixLHS(PostfixExpression(Identifier("c"), [MemberAccess("data")])), IntLiteral(77)),
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeInt", [PostfixExpression(Identifier("c"), [MethodCall("getData", [])])])
                    ]))
                ])
            )
        ])
    ])
    assert CodeGenerator().generate_and_run(input_ast) == "77"

def test_093():
    """Test Default Constructor (No params)"""
    input_ast = Program([
        ClassDecl("Simple", None, [
            AttributeDecl(False, False, PrimitiveType("int"), [Attribute("num")]),
            ConstructorDecl("Simple", [], BlockStatement([], [
                AssignmentStatement(PostfixLHS(PostfixExpression(Identifier("this"), [MemberAccess("num")])), IntLiteral(123))
            ]))
        ]),
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([
                    VariableDecl(False, ClassType("Simple"), [Variable("s", ObjectCreation("Simple", []))])
                ], [
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeInt", [PostfixExpression(Identifier("s"), [MemberAccess("num")])])
                    ]))
                ])
            )
        ])
    ])
    assert CodeGenerator().generate_and_run(input_ast) == "123"

# # GROUP 10: ARRAYS (94-97)
def test_094():
    """Test Array Access Multiple Elements"""
    var_decls = [VariableDecl(False, ArrayType(PrimitiveType("int"), 4), [
        Variable("nums", ArrayLiteral([IntLiteral(10), IntLiteral(20), IntLiteral(30), IntLiteral(40)]))
    ])]
    stmts = [
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [
            MethodCall("writeInt", [PostfixExpression(Identifier("nums"), [ArrayAccess(IntLiteral(0))])])
        ])),
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [
            MethodCall("writeInt", [PostfixExpression(Identifier("nums"), [ArrayAccess(IntLiteral(3))])])
        ]))
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "1040"

def test_095():
    """Test Array Element Modification"""
    var_decls = [VariableDecl(False, ArrayType(PrimitiveType("int"), 3), [
        Variable("arr", ArrayLiteral([IntLiteral(1), IntLiteral(2), IntLiteral(3)]))
    ])]
    stmts = [
        AssignmentStatement(PostfixLHS(PostfixExpression(Identifier("arr"), [ArrayAccess(IntLiteral(1))])), IntLiteral(99)),
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [
            MethodCall("writeInt", [PostfixExpression(Identifier("arr"), [ArrayAccess(IntLiteral(1))])])
        ]))
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "99"

def test_096():
    """Test Array with Boolean Elements"""
    var_decls = [VariableDecl(False, ArrayType(PrimitiveType("boolean"), 2), [
        Variable("flags", ArrayLiteral([BoolLiteral(True), BoolLiteral(False)]))
    ])]
    stmts = [
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [
            MethodCall("writeBool", [PostfixExpression(Identifier("flags"), [ArrayAccess(IntLiteral(0))])])
        ])),
        MethodInvocationStatement(PostfixExpression(Identifier("io"), [
            MethodCall("writeBool", [PostfixExpression(Identifier("flags"), [ArrayAccess(IntLiteral(1))])])
        ]))
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "truefalse"

def test_097():
    """Test Array Iteration with For Loop"""
    var_decls = [
        VariableDecl(False, ArrayType(PrimitiveType("int"), 3), [
            Variable("arr", ArrayLiteral([IntLiteral(5), IntLiteral(10), IntLiteral(15)]))
        ]),
        VariableDecl(False, PrimitiveType("int"), [Variable("i")])
    ]
    stmts = [
        ForStatement("i", IntLiteral(0), "to", IntLiteral(2),
            MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                MethodCall("writeInt", [PostfixExpression(Identifier("arr"), [ArrayAccess(Identifier("i"))])])
            ]))
        )
    ]
    assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "51015"

# GROUP 11: EDGE CASES & COMPLEX SCENARIOS (98-100)
def test_098():
    """Test Complex Expression with Mixed Operations"""
    # ((10 + 5) * 2 - 8) / 2 + 3 = (15 * 2 - 8) / 2 + 3 = (30 - 8) / 2 + 3 = 22 / 2 + 3 = 11 + 3 = 14
    expr = BinaryOp(
        BinaryOp(
            BinaryOp(
                BinaryOp(ParenthesizedExpression(BinaryOp(IntLiteral(10), "+", IntLiteral(5))), "*", IntLiteral(2)),
                "-",
                IntLiteral(8)
            ),
            "\\",
            IntLiteral(2)
        ),
        "+",
        IntLiteral(3)
    )
    stmt = MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [expr])]))
    assert CodeGenerator().generate_and_run(wrap_in_main([], [stmt])) == "14"

def test_099():
    """Test Combining Classes, Arrays, and Loops"""
    input_ast = Program([
        ClassDecl("ZItem", None, [
            AttributeDecl(False, False, PrimitiveType("int"), [Attribute("id")]),
            ConstructorDecl("ZItem", [Parameter(PrimitiveType("int"), "id")],
                BlockStatement([], [
                    AssignmentStatement(PostfixLHS(PostfixExpression(Identifier("this"), [MemberAccess("id")])), Identifier("id"))
                ])
            )
        ]),
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([
                    VariableDecl(False, ArrayType(ClassType("ZItem"), 3), [Variable("items")]),
                    VariableDecl(False, PrimitiveType("int"), [Variable("i")])
                ], [
                    AssignmentStatement(PostfixLHS(PostfixExpression(Identifier("items"), [ArrayAccess(IntLiteral(0))])), ObjectCreation("ZItem", [IntLiteral(1)])),
                    AssignmentStatement(PostfixLHS(PostfixExpression(Identifier("items"), [ArrayAccess(IntLiteral(1))])), ObjectCreation("ZItem", [IntLiteral(2)])),
                    AssignmentStatement(PostfixLHS(PostfixExpression(Identifier("items"), [ArrayAccess(IntLiteral(2))])), ObjectCreation("ZItem", [IntLiteral(3)])),
                    ForStatement("i", IntLiteral(0), "to", IntLiteral(2),
                        MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                            MethodCall("writeInt", [PostfixExpression(PostfixExpression(Identifier("items"), [ArrayAccess(Identifier("i"))]), [MemberAccess("id")])])
                        ]))
                    )
                ])
            )
        ])
    ])
    assert CodeGenerator().generate_and_run(input_ast) == "123"

def test_100():
    """Test Deep Nesting of All Features"""
    input_ast = Program([
        ClassDecl("ZCalculator", None, [
            MethodDecl(True, PrimitiveType("int"), "compute", [Parameter(PrimitiveType("int"), "x")],
                BlockStatement([
                    VariableDecl(False, PrimitiveType("int"), [Variable("result", IntLiteral(0))]),
                    VariableDecl(False, PrimitiveType("int"), [Variable("i")])
                ], [
                    ForStatement("i", IntLiteral(1), "to", Identifier("x"),
                        BlockStatement([], [
                            IfStatement(BinaryOp(BinaryOp(Identifier("i"), "%", IntLiteral(2)), "==", IntLiteral(0)),
                                AssignmentStatement(IdLHS("result"), BinaryOp(Identifier("result"), "+", Identifier("i"))),
                                None
                            )
                        ])
                    ),
                    ReturnStatement(Identifier("result"))
                ])
            )
        ]),
        ClassDecl("Main", None, [
            MethodDecl(True, PrimitiveType("void"), "main", [],
                BlockStatement([], [
                    MethodInvocationStatement(PostfixExpression(Identifier("io"), [
                        MethodCall("writeInt", [PostfixExpression(Identifier("ZCalculator"), [MethodCall("compute", [IntLiteral(10)])])])
                    ]))
                ])
            )
        ])
    ])
    # Sum of even numbers from 1 to 10: 2+4+6+8+10 = 30
    assert CodeGenerator().generate_and_run(input_ast) == "30"

# def test_101():
#     """test inheritance with animal class with method speak"""
#     ast = Program([
#         ClassDecl("ZAnimal", None, [
#             MethodDecl(False, PrimitiveType("string"), "speak", [],
#                 BlockStatement([], [
#                     ReturnStatement(StringLiteral("Some sound"))
#                 ])
#             )
#         ]),
#         ClassDecl("ZDog", "Animal", [
#             MethodDecl(False, PrimitiveType("string"), "speak", [],
#                 BlockStatement([], [
#                     ReturnStatement(StringLiteral("Woof"))
#                 ])
#             )
#         ]),
#         ClassDecl("ZCat", "Animal", [
#             MethodDecl(False, PrimitiveType("string"), "speak", [],
#                 BlockStatement([], [
#                     ReturnStatement(StringLiteral("Meow"))
#                 ])
#             )
#         ]),
#         ClassDecl("Main", None, [
#             MethodDecl(True, PrimitiveType("void"), "main", [],
#                 BlockStatement([
#                     VariableDecl(False, ClassType("ZAnimal"), [Variable("a1", ObjectCreation("ZDog", []))]),
#                     VariableDecl(False, ClassType("ZAnimal"), [Variable("a2", ObjectCreation("ZCat", []))])
#                 ], [
#                     MethodInvocationStatement(PostfixExpression(Identifier("io"), [
#                         MethodCall("writeStr", [PostfixExpression(Identifier("a1"), [MethodCall("speak", [])])])
#                     ])),
#                     MethodInvocationStatement(PostfixExpression(Identifier("io"), [
#                         MethodCall("writeStr", [PostfixExpression(Identifier("a2"), [MethodCall("speak", [])])])
#                     ]))
#                 ])
#             )
#         ])
#     ])
#     assert CodeGenerator().generate_and_run(ast) == "WoofMeow"

# def test_102():
#     """assign constants elements of an array to a variable and print them"""
#     var_decls = [
#         VariableDecl(True, ArrayType(PrimitiveType("int"), 4), [
#             Variable("arr", ArrayLiteral([IntLiteral(11), IntLiteral(22), IntLiteral(33), IntLiteral(44)]))
#         ]),
#         VariableDecl(True, PrimitiveType("int"), [Variable("a"), Variable("b"), Variable("c"), Variable("d")])
#     ]
#     stmts = [
#         AssignmentStatement(IdLHS("a"), PostfixExpression(Identifier("arr"), [ArrayAccess(IntLiteral(0))])),
#         AssignmentStatement(IdLHS("b"), PostfixExpression(Identifier("arr"), [ArrayAccess(IntLiteral(1))])),
#         AssignmentStatement(IdLHS("c"), PostfixExpression(Identifier("arr"), [ArrayAccess(IntLiteral(2))])),
#         AssignmentStatement(IdLHS("d"), PostfixExpression(Identifier("arr"), [ArrayAccess(IntLiteral(3))])),
#         MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [Identifier("a")])])),
#         MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [Identifier("b")])])),
#         MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [Identifier("c")])])),
#         MethodInvocationStatement(PostfixExpression(Identifier("io"), [MethodCall("writeInt", [Identifier("d")])]))
#     ]
#     assert CodeGenerator().generate_and_run(wrap_in_main(var_decls, stmts)) == "11223344"