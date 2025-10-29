"""
AST Generation module for OPLang programming language.
This module re-exports AST utilities from the utils package.
"""
from .ast_generation import ASTGeneration
from ..utils import *

__all__ = [
    # Base classes
    "ASTNode",
    "ASTVisitor",
    # Program structure
    "Program",
    "ClassDecl",
    "ClassMember",
    # Attribute declarations
    "AttributeDecl",
    "Attribute",
    # Method declarations
    "MethodDecl",
    "ConstructorDecl",
    "DestructorDecl",
    "Parameter",
    # Type system
    "Type",
    "PrimitiveType",
    "ArrayType",
    "ClassType",
    "ReferenceType",
    # Statements
    "Statement",
    "BlockStatement",
    "VariableDecl",
    "Variable",
    "AssignmentStatement",
    "IfStatement",
    "ForStatement",
    "BreakStatement",
    "ContinueStatement",
    "ReturnStatement",
    "MethodInvocationStatement",
    # Left-hand side (LHS)
    "LHS",
    "IdLHS",
    "PostfixLHS",
    # Expressions
    "Expr",
    "BinaryOp",
    "UnaryOp",
    "PostfixExpression",
    "PostfixOp",
    "MethodCall",
    "MemberAccess",
    "ArrayAccess",
    "ObjectCreation",
    "MemberAccess",
    "Identifier",
    "ThisExpression",
    "ParenthesizedExpression",
    # Literals
    "Literal",
    "IntLiteral",
    "FloatLiteral",
    "BoolLiteral",
    "StringLiteral",
    "ArrayLiteral",
    "NilLiteral",
    # Visitor
    "ASTVisitor",
]
