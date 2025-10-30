from utils import Checker


def test_001():
    """Test a valid program that should pass all checks"""
    source = """
class Test {
    static void main() {
        int x := 5;
        int y := x + 1;
    }
}
"""
    expected = "Static checking passed"
    # Just check that it doesn't return an error
    assert Checker(source).check_from_source() == expected

def test_002():
    """Test redeclared variable error"""
    source = """
class Test {
    static void main() {
        int x := 5;
        int x := 10;
    }
}
"""
    expected = "Redeclared(Variable, x)"
    assert Checker(source).check_from_source() == expected

def test_003():
    """Test undeclared identifier error"""
    source = """
class Test {
    static void main() {
        int x := y + 1;
    }
}
"""
    expected = "UndeclaredIdentifier(y)"
    assert Checker(source).check_from_source() == expected

def test_004():
    """Test type mismatch error"""
    source = """
class Test {
    static void main() {
        int x := "hello";
    }
}
"""
    expected = "TypeMismatchInStatement(VariableDecl(PrimitiveType(int), [Variable(x = StringLiteral('hello'))]))"
    assert Checker(source).check_from_source() == expected

def test_005():
    """Test break not in loop error"""
    source = """
class Test {
    static void main() {
        break;
    }
}
"""
    expected = "MustInLoop(BreakStatement())"
    assert Checker(source).check_from_source() == expected

def test_006():
    """Test cannot assign to constant error"""
    source = """
class Test {
    static void main() {
        final int x := 5;
        x := 10;
    }
}
"""
    expected = "CannotAssignToConstant(AssignmentStatement(IdLHS(x) := IntLiteral(10)))"
    assert Checker(source).check_from_source() == expected

def test_007():
    """Test illegal array literal error - alternative case"""
    source = """
class Test {
    static void main() {
        boolean[2] flags := {true, 42};
    }
}
"""
    expected = "IllegalArrayLiteral(ArrayLiteral({BoolLiteral(True), IntLiteral(42)}))"
    assert Checker(source).check_from_source() == expected

def test_008():
    """redeclared class"""
    source = """
        class Test {
            static void main() {
            }
        }
        class Test {
            static void main() {
            }
        }
    """
    expected = "Redeclared(Class, Test)"
    assert Checker(source).check_from_source() == expected

def test_009():
    """no entry point"""
    source = """
        class Test {
            static void func() {
            }
        }
    """
    expected = "No Entry Point"
    assert Checker(source).check_from_source() == expected

def test_010():
    """redeclared method"""
    source = """
        class Test {
            static void main() {
            }
            static int main() {
                return 0;
            }
        }
    """
    expected = "Redeclared(Method, main)"
    assert Checker(source).check_from_source() == expected

def test_011():
    "redeclared const"
    source = """
        class Test {
            static void main() {
                final int x := 5;
                final int x := 10;
            }
        }
    """
    expected = "Redeclared(Constant, x)"
    assert Checker(source).check_from_source() == expected

def test_012():
    "illegal constant expression"
    source = """
        class A
        {
            int x := 6;
        }
        class Test extends A
        {   
            static void main()
            {
                int x := 3;
                final int y := -(2 + x + 7 + -9);
            }
        }
        """
    expected = "IllegalConstantExpression(Variable(y = UnaryOp(-, ParenthesizedExpression((BinaryOp(BinaryOp(BinaryOp(IntLiteral(2), +, Identifier(x)), +, IntLiteral(7)), +, UnaryOp(-, IntLiteral(9))))))))"
    assert Checker(source).check_from_source() == expected

def test_013():
    source = """
        class Test {
            static void main() {
                x := y + 8;   
            }
        }
    """
    expected = "UndeclaredIdentifier(x)"
    assert Checker(source).check_from_source() == expected

def test_014():
    "illegal constant expression"
    source = """
        class A
        {
            int a := 6;
        }
        class Test extends A
        {   
            int calcX() {
                return 3;
            }
            static void main()
            {
                int x := a;
                final int y := -(2 + x + 7 + -9);
            }
        }
        """
    expected = "IllegalConstantExpression(Variable(y = UnaryOp(-, ParenthesizedExpression((BinaryOp(BinaryOp(BinaryOp(IntLiteral(2), +, Identifier(x)), +, IntLiteral(7)), +, UnaryOp(-, IntLiteral(9))))))))"
    assert Checker(source).check_from_source() == expected

def test_015():
    "reference reassign"
    source = """
        class Test {
            static void main() {
                int & a := 5;
                a := 10;
            }
        }
    """
    expected = "CannotAssignToConstant(AssignmentStatement(IdLHS(a) := IntLiteral(10)))"
    assert Checker(source).check_from_source() == expected

def test_016():
    source = """
        class A {int x := 2;}
        class Test {
            
            static void main() {
                A a := new A();
                a.x := 5;
            }
        }
        """
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected


def test_017():
    "test array"
    source = """
        class Test {
            static void main() {
                int[3] arr := {1, 2, 3};
            }
        }
    """
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected

def test_018():
    source = """
        class Test {
            static void main() {
                final int x := nil;
            }
            }
    """
    expected = "IllegalConstantExpression(Variable(x = NilLiteral(nil)))"
    assert Checker(source).check_from_source() == expected

def test_019():
    source = """
        class Test {
            int a := 3;
            int getA() {
                return this.a;
            }
            static void main() {
                int x;
            }
        }
    """
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected