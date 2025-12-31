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
                                                        # [
                                                        #     AssignmentStatement(PostfixExpression(Identifier("this"), [MemberAccess("x")]), IntLiteral(0)),
                                                        #     AssignmentStatement(PostfixExpression(Identifier("this"), [MemberAccess("y")]), IntLiteral(0))
                                                        # ]
                                                        []
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