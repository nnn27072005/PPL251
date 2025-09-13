from src.astgen import ASTGeneration


def test_001():
    """Test basic class declaration AST generation"""
    source = """class TestClass {
        int x;
    }"""
    expected = "Program([ClassDecl(TestClass, [AttributeDecl(PrimitiveType(int), [Attribute(x)])])])"
    # Just check that it doesn't return an error
    assert str(ASTGeneration().visitProgram(source)) == expected


def test_002():
    """Test class with method declaration AST generation"""
    source = """class TestClass {
        void main() {
            return;
        }
    }"""
    expected = "Program([ClassDecl(TestClass, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(stmts=[ReturnStatement(return NilLiteral(nil))]))])])"
    assert str(ASTGeneration().visitProgram(source)) == expected


def test_003():
    """Test class with constructor AST generation"""
    source = """class TestClass {
        int x;
        TestClass(int x) {
            this.x := x;
        }
    }"""
    expected = "Program([ClassDecl(TestClass, [AttributeDecl(PrimitiveType(int), [Attribute(x)]), ConstructorDecl(TestClass([Parameter(PrimitiveType(int) x)]), BlockStatement(stmts=[AssignmentStatement(PostfixLHS(PostfixExpression(ThisExpression(this).x)) := Identifier(x))]))])])"
    assert str(ASTGeneration().visitProgram(source)) == expected


def test_004():
    """Test class with inheritance AST generation"""
    source = """class Child extends Parent {
        int y;
    }"""
    expected = "Program([ClassDecl(Child, extends Parent, [AttributeDecl(PrimitiveType(int), [Attribute(y)])])])"
    assert str(ASTGeneration().visitProgram(source)) == expected


def test_005():
    """Test static and final attributes AST generation"""
    source = """class TestClass {
        static final int MAX_SIZE := 100;
        final float PI := 3.14;
    }"""
    expected = "Program([ClassDecl(TestClass, [AttributeDecl(static final PrimitiveType(int), [Attribute(MAX_SIZE = IntLiteral(100))]), AttributeDecl(final PrimitiveType(float), [Attribute(PI = FloatLiteral(3.14))])])])"
    assert str(ASTGeneration().visitProgram(source)) == expected


def test_006():
    """Test if-else statement AST generation"""
    source = """class TestClass {
        void main() {
            if (x > 0) then {
                return x;
            } else {
                return 0;
            }
        }
    }"""
    expected = "Program([ClassDecl(TestClass, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(stmts=[IfStatement(BinaryOp(Identifier(x) > IntLiteral(0)), BlockStatement(stmts=[ReturnStatement(return Identifier(x))]), BlockStatement(stmts=[ReturnStatement(return IntLiteral(0))]))]))])])"
    assert str(ASTGeneration().visitProgram(source)) == expected


def test_007():
    """Test for loop AST generation"""
    source = """class TestClass {
        void main() {
            for i := 1 to 10 do {
                io.writeIntLn(i);
            }
        }
    }"""
    expected = "Program([ClassDecl(TestClass, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(stmts=[ForStatement(i, IntLiteral(1), to, IntLiteral(10), BlockStatement(stmts=[MethodInvocationStatement(PostfixExpression(Identifier(io).writeIntLn([Identifier(i)]))]))]))])])"
    assert str(ASTGeneration().visitProgram(source)) == expected


def test_008():
    """Test array operations AST generation"""
    source = """class TestClass {
        void main() {
            int[5] arr;
            arr[0] := 42;
        }
    }"""
    expected = "Program([ClassDecl(TestClass, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(ArrayType(PrimitiveType(int)[IntLiteral(5)]), [Variable(arr)])], stmts=[AssignmentStatement(PostfixLHS(PostfixExpression(Identifier(arr), [ArrayAccess(IntLiteral(0))])) := IntLiteral(42))]))])])"
    assert str(ASTGeneration().visitProgram(source)) == expected


def test_009():
    """Test object creation and method call AST generation"""
    source = """class TestClass {
        void main() {
            Rectangle r := new Rectangle(5.0, 3.0);
            float area := r.getArea();
        }
    }"""
    expected = "Program([ClassDecl(TestClass, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(ClassType(Rectangle), [Variable(r = ObjectCreation(new Rectangle([FloatLiteral(5.0), FloatLiteral(3.0)])))]), VariableDecl(PrimitiveType(float), [Variable(area = PostfixExpression(Identifier(r), [MethodCall(getArea, [])]))])], stmts=[]))])])"
    assert str(ASTGeneration().visitProgram(source)) == expected


def test_010():
    """Test reference type AST generation"""
    source = """class TestClass {
        void swap(int & a; int & b) {
            int temp := a;
            a := b;
            b := temp;
        }
    }"""
    expected = "Program([ClassDecl(TestClass, [MethodDecl(PrimitiveType(void) swap([Parameter(ReferenceType(PrimitiveType(int) &) a), Parameter(ReferenceType(PrimitiveType(int) &) b)]), BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(temp = Identifier(a))])], stmts=[AssignmentStatement(IdLHS(a) := Identifier(b)), AssignmentStatement(IdLHS(b) := Identifier(temp))]))])])"
    assert str(ASTGeneration().visitProgram(source)) == expected


def test_011():
    """Test destructor AST generation"""
    source = """class TestClass {
        ~TestClass() {
            io.writeStrLn("Object destroyed");
        }
    }"""
    expected = "Program([ClassDecl(TestClass, [DestructorDecl(~TestClass(), BlockStatement(stmts=[MethodInvocationStatement(PostfixExpression(Identifier(io), [MethodCall(writeStrLn, [StringLiteral('Object destroyed')])]))]))])])"
    assert str(ASTGeneration().visitProgram(source)) == expected


def test_012():
    """Test static method invocation AST generation"""
    source = """class TestClass {
        void main() {
            int count := Shape.getCount();
        }
    }"""
    expected = "Program([ClassDecl(TestClass, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(count = PostfixExpression(Identifier(Shape), [MethodCall(getCount, [])]))])], stmts=[]))])])"
    assert str(ASTGeneration().visitProgram(source)) == expected
