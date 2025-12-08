from tests.utils import ASTGenerator


def test_001():
    """Test basic class declaration AST generation"""
    source = """class TestClass {
        void main() {
            final int x := 10;
            x := x + 5;
        }
    }"""
    expected = "Program([ClassDecl(TestClass, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(final PrimitiveType(int), [Variable(x = IntLiteral(10))])], stmts=[AssignmentStatement(IdLHS(x) := BinaryOp(Identifier(x), +, IntLiteral(5)))]))])])"
    # Just check that it doesn't return an error
    assert str(ASTGenerator(source).generate()) == expected


def test_002():
    """Test class with method declaration AST generation"""
    source = """   
    class A{}
    class Test { 
        void main() { 
            A[2] arr := {new A(), new A()};
        }
    }"""
    expected = "Program([ClassDecl(TestClass, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_003():
    """Test class with constructor AST generation"""
    source = """class TestClass {
        int x;
        TestClass(int x) {
            this.x := x;
        }
    }"""
    expected = "Program([ClassDecl(TestClass, [AttributeDecl(PrimitiveType(int), [Attribute(x)]), ConstructorDecl(TestClass([Parameter(PrimitiveType(int) x)]), BlockStatement(stmts=[AssignmentStatement(PostfixLHS(PostfixExpression(ThisExpression(this).x)) := Identifier(x))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_004():
    """Test class with inheritance AST generation"""
    source = """class Child extends Parent {
        int[0] arr := {};
    }"""
    expected = "Program([ClassDecl(Child, extends Parent, [AttributeDecl(PrimitiveType(int), [Attribute(y)])])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_005():
    """Test static and final attributes AST generation"""
    source = """class TestClass {
        static final int MAX_SIZE := 100;
        final float PI := 3.14;
    }"""
    expected = "Program([ClassDecl(TestClass, [AttributeDecl(static final PrimitiveType(int), [Attribute(MAX_SIZE = IntLiteral(100))]), AttributeDecl(final PrimitiveType(float), [Attribute(PI = FloatLiteral(3.14))])])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_006():
    """Test if-else statement AST generation"""
    source = """class TestClass {
        void main() {
            if x > 0 then {
                return x;
            } else {
                return 0;
            }
        }
    }"""
    expected = "Program([ClassDecl(TestClass, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(stmts=[IfStatement(if BinaryOp(Identifier(x), >, IntLiteral(0)) then BlockStatement(stmts=[ReturnStatement(return Identifier(x))]), else BlockStatement(stmts=[ReturnStatement(return IntLiteral(0))]))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_007():
    """Test for loop AST generation"""
    source = """class TestClass {
        void main() {
            int sum := 0;
            for i := 1 to 10 do {
                sum := sum + i;
            }
        }
    }"""
    expected = "Program([ClassDecl(TestClass, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(sum = IntLiteral(0))])], stmts=[ForStatement(for i := IntLiteral(1) to IntLiteral(10) do BlockStatement(stmts=[AssignmentStatement(IdLHS(sum) := BinaryOp(Identifier(sum), +, Identifier(i)))]))]))])])"
    assert str(ASTGenerator(source).generate()) == expected

def test_008():
    """Test array operations AST generation"""
    source = """class TestClass {
        void main() {
            int[5] arr;
            arr[0] := 42;
        }
    }"""
    expected = "Program([ClassDecl(TestClass, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(ArrayType(PrimitiveType(int)[5]), [Variable(arr)])], stmts=[AssignmentStatement(PostfixLHS(PostfixExpression(Identifier(arr)[IntLiteral(0)])) := IntLiteral(42))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_009():
    """Test object creation and method call AST generation"""
    source = """class TestClass {
        void main() {
            Rectangle r := new Rectangle(5.0, 3.0);
            float area := r.getArea();
        }
    }"""
    expected = "Program([ClassDecl(TestClass, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(ClassType(Rectangle), [Variable(r = ObjectCreation(new Rectangle(FloatLiteral(5.0), FloatLiteral(3.0))))]), VariableDecl(PrimitiveType(float), [Variable(area = PostfixExpression(Identifier(r).getArea()))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


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
    assert str(ASTGenerator(source).generate()) == expected


def test_011():
    """Test destructor AST generation"""
    source = """class TestClass {
        ~TestClass() {
            int x := 0;
        }
    }"""
    expected = "Program([ClassDecl(TestClass, [DestructorDecl(~TestClass(), BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(x = IntLiteral(0))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected

def test_012():
    """Class with multiple attributes and methods"""
    source = """class Complex {
        int a;
        float b;
        static int c := 10;
        void main() {
            a := 1;
            b := 2.0;
            c := a + 3;
        }
    }"""
    expected = "Program([ClassDecl(Complex, [AttributeDecl(PrimitiveType(int), [Attribute(a)]), AttributeDecl(PrimitiveType(float), [Attribute(b)]), AttributeDecl(static PrimitiveType(int), [Attribute(c = IntLiteral(10))]), MethodDecl(PrimitiveType(void) main([]), BlockStatement(stmts=[AssignmentStatement(IdLHS(a) := IntLiteral(1)), AssignmentStatement(IdLHS(b) := FloatLiteral(2.0)), AssignmentStatement(IdLHS(c) := BinaryOp(Identifier(a), +, IntLiteral(3)))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_013():
    """Class with overloaded constructors"""
    source = """class Point {
        float x;
        float y;
        Point() {
            x := 0.0;
            y := 0.0;
        }
        Point(float x; float y) {
            this.x := x;
            this.y := y;
        }
    }"""
    print(str(ASTGenerator(source).generate()))
    expected = "Program([ClassDecl(Point, [AttributeDecl(PrimitiveType(float), [Attribute(x)]), AttributeDecl(PrimitiveType(float), [Attribute(y)]), ConstructorDecl(Point([]), BlockStatement(stmts=[AssignmentStatement(IdLHS(x) := FloatLiteral(0.0)), AssignmentStatement(IdLHS(y) := FloatLiteral(0.0))])), ConstructorDecl(Point([Parameter(PrimitiveType(float) x), Parameter(PrimitiveType(float) y)]), BlockStatement(stmts=[AssignmentStatement(PostfixLHS(PostfixExpression(ThisExpression(this).x)) := Identifier(x)), AssignmentStatement(PostfixLHS(PostfixExpression(ThisExpression(this).y)) := Identifier(y))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_014():
    """Class inheritance with methods calling super-like constructor via new"""
    source = """class Base {
        int id;
        Base(int id) {
            this.id := id;
        }
    }
    class Child extends Base {
        Child(int id) {
            Base b := new Base(id);
            this.id := b.id;
        }
    }"""
    expected = "Program([ClassDecl(Base, [AttributeDecl(PrimitiveType(int), [Attribute(id)]), ConstructorDecl(Base([Parameter(PrimitiveType(int) id)]), BlockStatement(stmts=[AssignmentStatement(PostfixLHS(PostfixExpression(ThisExpression(this).id)) := Identifier(id))]))]), ClassDecl(Child, extends Base, [ConstructorDecl(Child([Parameter(PrimitiveType(int) id)]), BlockStatement(vars=[VariableDecl(ClassType(Base), [Variable(b = ObjectCreation(new Base(Identifier(id))))])], stmts=[AssignmentStatement(PostfixLHS(PostfixExpression(ThisExpression(this).id)) := PostfixExpression(Identifier(b).id))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_015():
    """Class with nested for and if using arrays"""
    source = """class Matrix {
        int[3] data;
        void fill() {
            for i := 0 to 2 do {
                for j := 0 to 2 do {
                    data[i] := data[i] + j;
                }
            }
        }
    }"""
    expected = "Program([ClassDecl(Matrix, [AttributeDecl(ArrayType(PrimitiveType(int)[3]), [Attribute(data)]), MethodDecl(PrimitiveType(void) fill([]), BlockStatement(stmts=[ForStatement(for i := IntLiteral(0) to IntLiteral(2) do BlockStatement(stmts=[ForStatement(for j := IntLiteral(0) to IntLiteral(2) do BlockStatement(stmts=[AssignmentStatement(PostfixLHS(PostfixExpression(Identifier(data)[Identifier(i)])) := BinaryOp(PostfixExpression(Identifier(data)[Identifier(i)]), +, Identifier(j)))]))]))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_016():
    """Static final mixed with methods returning expressions"""
    source = """class Consts {
        static final int A := 1;
        final int B := 2;
        int getSum() {
            return A + B;
        }
    }"""
    expected = "Program([ClassDecl(Consts, [AttributeDecl(static final PrimitiveType(int), [Attribute(A = IntLiteral(1))]), AttributeDecl(final PrimitiveType(int), [Attribute(B = IntLiteral(2))]), MethodDecl(PrimitiveType(int) getSum([]), BlockStatement(stmts=[ReturnStatement(return BinaryOp(Identifier(A), +, Identifier(B)))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_017():
    """Method with reference parameters and assignment between references"""
    source = """class RefOps {
        void swap(int & a; int & b) {
            int tmp := a;
            a := b;
            b := tmp;
        }
    }"""
    expected = "Program([ClassDecl(RefOps, [MethodDecl(PrimitiveType(void) swap([Parameter(ReferenceType(PrimitiveType(int) &) a), Parameter(ReferenceType(PrimitiveType(int) &) b)]), BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(tmp = Identifier(a))])], stmts=[AssignmentStatement(IdLHS(a) := Identifier(b)), AssignmentStatement(IdLHS(b) := Identifier(tmp))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_018():
    """Constructor with object creation assigned to attribute"""
    source = """class Container {
        Item it;
        Container(Item i) {
            this.it := i;
        }
        Container() {
            this.it := new Item(1);
        }
    }"""
    expected = "Program([ClassDecl(Container, [AttributeDecl(ClassType(Item), [Attribute(it)]), ConstructorDecl(Container([Parameter(ClassType(Item) i)]), BlockStatement(stmts=[AssignmentStatement(PostfixLHS(PostfixExpression(ThisExpression(this).it)) := Identifier(i))])), ConstructorDecl(Container([]), BlockStatement(stmts=[AssignmentStatement(PostfixLHS(PostfixExpression(ThisExpression(this).it)) := ObjectCreation(new Item(IntLiteral(1))))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_019():
    """Chained method calls and attribute access in expressions"""
    source = """class Node {
        Node next;
        int value;
        int compute() {
            Node n := this.next;
            int v := n.next.value;
            return v + this.value;
        }
    }"""
    expected = "Program([ClassDecl(Node, [AttributeDecl(ClassType(Node), [Attribute(next)]), AttributeDecl(PrimitiveType(int), [Attribute(value)]), MethodDecl(PrimitiveType(int) compute([]), BlockStatement(vars=[VariableDecl(ClassType(Node), [Variable(n = PostfixExpression(ThisExpression(this).next))]), VariableDecl(PrimitiveType(int), [Variable(v = PostfixExpression(PostfixExpression(Identifier(n).next).value))])], stmts=[ReturnStatement(return BinaryOp(Identifier(v), +, PostfixExpression(ThisExpression(this).value)))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_020():
    """Array of objects, assignments and method calls returning floats"""
    source = """class Scene {
        Rectangle[2] rects;
        void init() {
            rects[0] := new Rectangle(1.0, 2.0);
            rects[1] := new Rectangle(3.0, 4.0);
        }
    }"""
    expected = "Program([ClassDecl(Scene, [AttributeDecl(ArrayType(ClassType(Rectangle)[2]), [Attribute(rects)]), MethodDecl(PrimitiveType(void) init([]), BlockStatement(stmts=[AssignmentStatement(PostfixLHS(PostfixExpression(Identifier(rects)[IntLiteral(0)])) := ObjectCreation(new Rectangle(FloatLiteral(1.0), FloatLiteral(2.0)))), AssignmentStatement(PostfixLHS(PostfixExpression(Identifier(rects)[IntLiteral(1)])) := ObjectCreation(new Rectangle(FloatLiteral(3.0), FloatLiteral(4.0))))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_021():
    """Method with complex BinaryOp nesting"""
    source = """class Calc {
        int compute(int a; int b) {
            return (a + b) * (a - b);
        }
    }"""
    expected = "Program([ClassDecl(Calc, [MethodDecl(PrimitiveType(int) compute([Parameter(PrimitiveType(int) a), Parameter(PrimitiveType(int) b)]), BlockStatement(stmts=[ReturnStatement(return BinaryOp(ParenthesizedExpression((BinaryOp(Identifier(a), +, Identifier(b)))), *, ParenthesizedExpression((BinaryOp(Identifier(a), -, Identifier(b))))))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_022():
    """Method with assignment using postfix this and new object fields"""
    source = """class Wrapper {
        Data d;
        void set(int v) {
            this.d := new Data(v);
            this.d.value := v;
        }
    }"""
    expected = "Program([ClassDecl(Wrapper, [AttributeDecl(ClassType(Data), [Attribute(d)]), MethodDecl(PrimitiveType(void) set([Parameter(PrimitiveType(int) v)]), BlockStatement(stmts=[AssignmentStatement(PostfixLHS(PostfixExpression(ThisExpression(this).d)) := ObjectCreation(new Data(Identifier(v)))), AssignmentStatement(PostfixLHS(PostfixExpression(ThisExpression(this).d.value)) := Identifier(v))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_023():
    """Class with multiple constructors and attribute initialization lists"""
    source = """class Multi {
        int a;
        int b;
        static final int C := 5;
        Multi(int a; int b) {
            this.a := a;
            this.b := b;
        }
        Multi() {
            a := C;
            b := C;
        }
    }"""
    expected = "Program([ClassDecl(Multi, [AttributeDecl(PrimitiveType(int), [Attribute(a)]), AttributeDecl(PrimitiveType(int), [Attribute(b)]), AttributeDecl(static final PrimitiveType(int), [Attribute(C = IntLiteral(5))]), ConstructorDecl(Multi([Parameter(PrimitiveType(int) a), Parameter(PrimitiveType(int) b)]), BlockStatement(stmts=[AssignmentStatement(PostfixLHS(PostfixExpression(ThisExpression(this).a)) := Identifier(a)), AssignmentStatement(PostfixLHS(PostfixExpression(ThisExpression(this).b)) := Identifier(b))])), ConstructorDecl(Multi([]), BlockStatement(stmts=[AssignmentStatement(IdLHS(a) := Identifier(C)), AssignmentStatement(IdLHS(b) := Identifier(C))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_024():
    """Method returning object field after object creation"""
    source = """class Factory {
        Product make() {
            Product p := new Product(10);
            return p.id;
        }
    }"""
    expected = "Program([ClassDecl(Factory, [MethodDecl(ClassType(Product) make([]), BlockStatement(vars=[VariableDecl(ClassType(Product), [Variable(p = ObjectCreation(new Product(IntLiteral(10))))])], stmts=[ReturnStatement(return PostfixExpression(Identifier(p).id))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_025():
    """Class with protected-like naming (no semantics change)"""
    source = """class Protected {
        int _x;
        void set(int v) {
            _x := v;
        }
    }"""
    expected = "Program([ClassDecl(Protected, [AttributeDecl(PrimitiveType(int), [Attribute(_x)]), MethodDecl(PrimitiveType(void) set([Parameter(PrimitiveType(int) v)]), BlockStatement(stmts=[AssignmentStatement(IdLHS(_x) := Identifier(v))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_026():
    """Method with nested postfix method calls"""
    source = """class Chain {
        void run() {
            A a := new A();
            float x := a.getB().getC().value;
        }
    }"""
    expected = "Program([ClassDecl(Chain, [MethodDecl(PrimitiveType(void) run([]), BlockStatement(vars=[VariableDecl(ClassType(A), [Variable(a = ObjectCreation(new A()))]), VariableDecl(PrimitiveType(float), [Variable(x = PostfixExpression(PostfixExpression(PostfixExpression(Identifier(a).getB()).getC()).value))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_027():
    """Array variable declaration with initialization in method"""
    source = """class ArrInit {
        void init() {
            int[4] nums;
            nums[1] := 7;
        }
    }"""
    expected = "Program([ClassDecl(ArrInit, [MethodDecl(PrimitiveType(void) init([]), BlockStatement(vars=[VariableDecl(ArrayType(PrimitiveType(int)[4]), [Variable(nums)])], stmts=[AssignmentStatement(PostfixLHS(PostfixExpression(Identifier(nums)[IntLiteral(1)])) := IntLiteral(7))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_028():
    """Method with conditional assignment (if-else) producing class field result"""
    source = """class Cond {
        int choose(int a; int b) {
            if a > b then {
                return a;
            } else {
                return b;
            }
        }
    }"""
    expected = "Program([ClassDecl(Cond, [MethodDecl(PrimitiveType(int) choose([Parameter(PrimitiveType(int) a), Parameter(PrimitiveType(int) b)]), BlockStatement(stmts=[IfStatement(if BinaryOp(Identifier(a), >, Identifier(b)) then BlockStatement(stmts=[ReturnStatement(return Identifier(a))]), else BlockStatement(stmts=[ReturnStatement(return Identifier(b))]))]))])])"
    assert str(ASTGenerator(source).generate()) == expected

def test_029():
    source = """class Ngu_29 {
        int a;
        Ngu_29(int a) {
            this.a := a;
        }
        int getA() {
            return this.a;
        }
        ~Ngu_29() {
            int x := 0;
        }
    }"""
    expected = "Program([ClassDecl(Ngu_29, [AttributeDecl(PrimitiveType(int), [Attribute(a)]), ConstructorDecl(Ngu_29([Parameter(PrimitiveType(int) a)]), BlockStatement(stmts=[AssignmentStatement(PostfixLHS(PostfixExpression(ThisExpression(this).a)) := Identifier(a))])), MethodDecl(PrimitiveType(int) getA([]), BlockStatement(stmts=[ReturnStatement(return PostfixExpression(ThisExpression(this).a))])), DestructorDecl(~Ngu_29(), BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(x = IntLiteral(0))])], stmts=[]))])])"
    """
        Program(
            [ClassDecl(Ngu_29,
                [AttributeDecl(PrimitiveType(int), [Attribute(a)]),
                 ConstructorDecl(Ngu_29([Parameter(PrimitiveType(int) a)]),
                     BlockStatement(stmts=[
                         AssignmentStatement(
                             PostfixLHS(PostfixExpression(ThisExpression(this).a)) := Identifier(a)
                         )
                     ])
                 ),
                 MethodDecl(PrimitiveType(int) getA([]),
                     BlockStatement(stmts=[
                         ReturnStatement(return PostfixExpression(ThisExpression(this).a))
                     ])
                 ),
                 DestructorDecl(~Ngu_29(),
                     BlockStatement(
                         vars=[VariableDecl(PrimitiveType(int), [Variable(x = IntLiteral(0))])],
                         stmts=[]
                     )
                 )
                ]
            )
            ]
        )
    """
    assert str(ASTGenerator(source).generate()) == expected

def test_030():
    source = """class Ngu_30 {
        int ngu;
        void main(){
            int i;
            for i := 1 to 10 do {
                if i % 2 == 0 then {
                    ngu := ngu + i;
                } else {
                    ngu := ngu - i;
                }
            }
        }
    }"""
    expected = "Program([ClassDecl(Ngu_30, [AttributeDecl(PrimitiveType(int), [Attribute(ngu)]), MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(i)])], stmts=[ForStatement(for i := IntLiteral(1) to IntLiteral(10) do BlockStatement(stmts=[IfStatement(if BinaryOp(BinaryOp(Identifier(i), %, IntLiteral(2)), ==, IntLiteral(0)) then BlockStatement(stmts=[AssignmentStatement(IdLHS(ngu) := BinaryOp(Identifier(ngu), +, Identifier(i)))]), else BlockStatement(stmts=[AssignmentStatement(IdLHS(ngu) := BinaryOp(Identifier(ngu), -, Identifier(i)))]))]))]))])])"
    assert str(ASTGenerator(source).generate()) == expected

def test_031():
    source = """class Ngu_31 {
        void bubbleSort(int[5] arr) {
            int i;
            int j;
            for i := 0 to 4 do {
                for j := 0 to 3 do {
                    if arr[j] > arr[j + 1] then {
                        int temp := arr[j];
                        arr[j] := arr[j + 1];
                        arr[j + 1] := temp;
                    }
                }
            }
        }
        void main() {
            int[5] arr := {5, 2, 9, 1, 5};
            int[5] ngu := this.bubbleSort(arr);
        }
    }"""
    expected= "Program([ClassDecl(Ngu_31, [MethodDecl(PrimitiveType(void) bubbleSort([Parameter(ArrayType(PrimitiveType(int)[5]) arr)]), BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(i)]), VariableDecl(PrimitiveType(int), [Variable(j)])], stmts=[ForStatement(for i := IntLiteral(0) to IntLiteral(4) do BlockStatement(stmts=[ForStatement(for j := IntLiteral(0) to IntLiteral(3) do BlockStatement(stmts=[IfStatement(if BinaryOp(PostfixExpression(Identifier(arr)[Identifier(j)]), >, PostfixExpression(Identifier(arr)[BinaryOp(Identifier(j), +, IntLiteral(1))])) then BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(temp = PostfixExpression(Identifier(arr)[Identifier(j)]))])], stmts=[AssignmentStatement(PostfixLHS(PostfixExpression(Identifier(arr)[Identifier(j)])) := PostfixExpression(Identifier(arr)[BinaryOp(Identifier(j), +, IntLiteral(1))])), AssignmentStatement(PostfixLHS(PostfixExpression(Identifier(arr)[BinaryOp(Identifier(j), +, IntLiteral(1))])) := Identifier(temp))]))]))]))])), MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(ArrayType(PrimitiveType(int)[5]), [Variable(arr = ArrayLiteral({IntLiteral(5), IntLiteral(2), IntLiteral(9), IntLiteral(1), IntLiteral(5)}))]), VariableDecl(ArrayType(PrimitiveType(int)[5]), [Variable(ngu = PostfixExpression(ThisExpression(this).bubbleSort(Identifier(arr))))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected

def test_032():
    source = """class Ngu_32 {
        int factorial(int n) {
            if n == 0 then {
                return 1;
            } else {
                return n * this.factorial(n - 1);
            }
        }
        void main() {
            int result := this.factorial(5);
        }
    }"""
    expected = "Program([ClassDecl(Ngu_32, [MethodDecl(PrimitiveType(int) factorial([Parameter(PrimitiveType(int) n)]), BlockStatement(stmts=[IfStatement(if BinaryOp(Identifier(n), ==, IntLiteral(0)) then BlockStatement(stmts=[ReturnStatement(return IntLiteral(1))]), else BlockStatement(stmts=[ReturnStatement(return BinaryOp(Identifier(n), *, PostfixExpression(ThisExpression(this).factorial(BinaryOp(Identifier(n), -, IntLiteral(1))))))]))])), MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(result = PostfixExpression(ThisExpression(this).factorial(IntLiteral(5))))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected

def test_033():
    source = """class Ngu_33 {
        void main() {
            int[3] arr := {1, 2, 3};
            int sum := 0;
            int i;
            for i := 0 to 2 do {
                sum := sum + arr[i];
            }
        }
    }"""
    expected = "Program([ClassDecl(Ngu_33, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(ArrayType(PrimitiveType(int)[3]), [Variable(arr = ArrayLiteral({IntLiteral(1), IntLiteral(2), IntLiteral(3)}))]), VariableDecl(PrimitiveType(int), [Variable(sum = IntLiteral(0))]), VariableDecl(PrimitiveType(int), [Variable(i)])], stmts=[ForStatement(for i := IntLiteral(0) to IntLiteral(2) do BlockStatement(stmts=[AssignmentStatement(IdLHS(sum) := BinaryOp(Identifier(sum), +, PostfixExpression(Identifier(arr)[Identifier(i)])))]))]))])])"
    assert str(ASTGenerator(source).generate()) == expected

def test_034():
    source = """class Ngu_34{
        void swap(int & x; int & y) {
            int temp := x;
            x := y;
            y := temp;
        }
        void main() {
            int x := 10;
            int y := 20;
            this.swap(x, y);
        }
    }"""
    expected = "Program([ClassDecl(Ngu_34, [MethodDecl(PrimitiveType(void) swap([Parameter(ReferenceType(PrimitiveType(int) &) x), Parameter(ReferenceType(PrimitiveType(int) &) y)]), BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(temp = Identifier(x))])], stmts=[AssignmentStatement(IdLHS(x) := Identifier(y)), AssignmentStatement(IdLHS(y) := Identifier(temp))])), MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(x = IntLiteral(10))]), VariableDecl(PrimitiveType(int), [Variable(y = IntLiteral(20))])], stmts=[MethodInvocationStatement(PostfixExpression(ThisExpression(this).swap(Identifier(x), Identifier(y))))]))])])"
    assert str(ASTGenerator(source).generate()) == expected

def test_035():
    source = """ class Ngu_35 {
        void main() {
            int[3] arr := {3, 1, 2};
            int i;
            for i := 0 to 2 do {
                int j;
                for j := 0 to 1 do {
                    if arr[j] > arr[j + 1] then {
                        int temp := arr[j];
                        arr[j] := arr[j + 1];
                        arr[j + 1] := temp;
                    }
                }
            }
        }    
    }"""
    expected= "Program([ClassDecl(Ngu_35, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(ArrayType(PrimitiveType(int)[3]), [Variable(arr = ArrayLiteral({IntLiteral(3), IntLiteral(1), IntLiteral(2)}))]), VariableDecl(PrimitiveType(int), [Variable(i)])], stmts=[ForStatement(for i := IntLiteral(0) to IntLiteral(2) do BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(j)])], stmts=[ForStatement(for j := IntLiteral(0) to IntLiteral(1) do BlockStatement(stmts=[IfStatement(if BinaryOp(PostfixExpression(Identifier(arr)[Identifier(j)]), >, PostfixExpression(Identifier(arr)[BinaryOp(Identifier(j), +, IntLiteral(1))])) then BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(temp = PostfixExpression(Identifier(arr)[Identifier(j)]))])], stmts=[AssignmentStatement(PostfixLHS(PostfixExpression(Identifier(arr)[Identifier(j)])) := PostfixExpression(Identifier(arr)[BinaryOp(Identifier(j), +, IntLiteral(1))])), AssignmentStatement(PostfixLHS(PostfixExpression(Identifier(arr)[BinaryOp(Identifier(j), +, IntLiteral(1))])) := Identifier(temp))]))]))]))]))])])"
    assert str(ASTGenerator(source).generate()) == expected

def test_036():
    source = """ class Ngu_36 {
                   final int a,b, c := 3;
        void main(){
        
        }
    }"""
    expected = "Program([ClassDecl(Ngu_36, [AttributeDecl(final PrimitiveType(int), [Attribute(a), Attribute(b), Attribute(c = IntLiteral(3))]), MethodDecl(PrimitiveType(void) main([]), BlockStatement(stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected

def test_037():
    source = """ class Ngu_37 {
        static final int a, b,c := 3;
        void main(){
        }
    }"""
    expected = "Program([ClassDecl(Ngu_37, [AttributeDecl(static final PrimitiveType(int), [Attribute(a), Attribute(b), Attribute(c = IntLiteral(3))]), MethodDecl(PrimitiveType(void) main([]), BlockStatement(stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected

def test_038():
    """Test unary minus operator"""
    source = """class Test {
        void main() {
            int x := -5;
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(x = UnaryOp(-, IntLiteral(5)))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_039():
    """Test logical NOT operator"""
    source = """class Test {
        void main() {
            boolean y := !true;
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(boolean), [Variable(y = UnaryOp(!, BoolLiteral(True)))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_040():
    """Test string concatenation"""
    source = """class Test {
        void main() {
            string s := "Hello" + "World";
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(string), [Variable(s = BinaryOp(StringLiteral('Hello'), +, StringLiteral('World')))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_041():
    """Test string comparison"""
    source = """class Test {
        void main() {
            boolean b := "a" == "b";
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(boolean), [Variable(b = BinaryOp(StringLiteral('a'), ==, StringLiteral('b')))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_042():
    """Test logical AND operator"""
    source = """class Test {
        void main() {
            boolean r := true && false;
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(boolean), [Variable(r = BinaryOp(BoolLiteral(True), &&, BoolLiteral(False)))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_043():
    """Test modulo operator"""
    source = """class Test {
        void main() {
            int rem := 10 % 3;
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(rem = BinaryOp(IntLiteral(10), %, IntLiteral(3)))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_044():
    """Test an empty block statement inside a method"""
    source = """class Test {
        void main() {
            {}
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(stmts=[BlockStatement(stmts=[])]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_045():
    """Test break statement in a for loop"""
    source = """class Test {
        void main() {
            for i := 1 to 10 do {
                break;
            }
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(stmts=[ForStatement(for i := IntLiteral(1) to IntLiteral(10) do BlockStatement(stmts=[BreakStatement()]))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_046():
    """Test continue statement in a for loop"""
    source = """class Test {
        void main() {
            for i := 1 to 10 do {
                continue;
            }
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(stmts=[ForStatement(for i := IntLiteral(1) to IntLiteral(10) do BlockStatement(stmts=[ContinueStatement()]))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_047():
    """Test return statement with no value"""
    source = """class Test {
        void main() {
            return 2;
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(stmts=[ReturnStatement(return IntLiteral(2))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_048():
    """Test string attribute declaration"""
    source = """class Test {
        string greeting := "Hello";
    }"""
    expected = "Program([ClassDecl(Test, [AttributeDecl(PrimitiveType(string), [Attribute(greeting = StringLiteral('Hello'))])])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_049():
    """Test boolean attribute declaration"""
    source = """class Test {
        boolean isReady := true;
    }"""
    expected = "Program([ClassDecl(Test, [AttributeDecl(PrimitiveType(boolean), [Attribute(isReady = BoolLiteral(True))])])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_050():
    """Test float attribute declaration"""
    source = """class Test {
        float pi := 3.14;
    }"""
    expected = "Program([ClassDecl(Test, [AttributeDecl(PrimitiveType(float), [Attribute(pi = FloatLiteral(3.14))])])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_051():
    """Test method invocation as a statement"""
    source = """class Test {
        void doSomething() {}
        void main() {
            this.doSomething();
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) doSomething([]), BlockStatement(stmts=[])), MethodDecl(PrimitiveType(void) main([]), BlockStatement(stmts=[MethodInvocationStatement(PostfixExpression(ThisExpression(this).doSomething()))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_052():
    """Test static method call on another class"""
    source = """class Test {
        void main() {
            OtherClass.staticMethod();
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(stmts=[MethodInvocationStatement(PostfixExpression(Identifier(OtherClass).staticMethod()))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_053():
    """Test parenthesized expression"""
    source = """class Test {
        void main() {
            int x := (5 + 3);
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(x = ParenthesizedExpression((BinaryOp(IntLiteral(5), +, IntLiteral(3)))))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_054():
    """Test if statement without an else part"""
    source = """class Test {
        void main() {
            if true then {
                int x := 1;
            }
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(stmts=[IfStatement(if BoolLiteral(True) then BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(x = IntLiteral(1))])], stmts=[]))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_055():
    """Test empty class declaration"""
    source = """class Empty {}"""
    expected = "Program([ClassDecl(Empty, [])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_056():
    """Test multiple variable declarations in one statement"""
    source = """class Test {
        void main() {
            int a, b := 2, c;
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(a), Variable(b = IntLiteral(2)), Variable(c)])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_057():
    """Test multiple attribute declarations in one statement"""
    source = """class Test {
        int x, y := 10, z;
    }"""
    expected = "Program([ClassDecl(Test, [AttributeDecl(PrimitiveType(int), [Attribute(x), Attribute(y = IntLiteral(10)), Attribute(z)])])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_058():
    """Test a class with only a destructor"""
    source = """class Test {
        ~Test() {}
    }"""
    expected = "Program([ClassDecl(Test, [DestructorDecl(~Test(), BlockStatement(stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_059():
    """Test method returning an array literal"""
    source = """class Test {
        int[3] getArray() {
            return {1, 2, 3};
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(ArrayType(PrimitiveType(int)[3]) getArray([]), BlockStatement(stmts=[ReturnStatement(return ArrayLiteral({IntLiteral(1), IntLiteral(2), IntLiteral(3)}))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_060():
    """Test for loop with downto"""
    source = """class Test {
        void main() {
            for i := 10 downto 1 do {
            }
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(stmts=[ForStatement(for i := IntLiteral(10) downto IntLiteral(1) do BlockStatement(stmts=[]))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_061():
    """Test accessing a static attribute from another class"""
    source = """class Test {
        void main() {
            int val := Constants.MAX_VALUE;
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(val = PostfixExpression(Identifier(Constants).MAX_VALUE))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_062():
    """Test a method with no parameters returning a value"""
    source = """class Test {
        int getZero() {
            return 0;
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(int) getZero([]), BlockStatement(stmts=[ReturnStatement(return IntLiteral(0))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_063():
    """Test a simple 'this' expression"""
    source = """class Test {
        Test getSelf() {
            return this;
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(ClassType(Test) getSelf([]), BlockStatement(stmts=[ReturnStatement(return ThisExpression(this))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_064():
    """Test simple assignment to an existing variable"""
    source = """class Test {
        void main() {
            int x;
            x := 10;
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(x)])], stmts=[AssignmentStatement(IdLHS(x) := IntLiteral(10))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_065():
    """Test array access using an expression as index"""
    source = """class Test {
        void main() {
            int[5] a;
            int i := 2;
            int v := a[i + 1];
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(ArrayType(PrimitiveType(int)[5]), [Variable(a)]), VariableDecl(PrimitiveType(int), [Variable(i = IntLiteral(2))]), VariableDecl(PrimitiveType(int), [Variable(v = PostfixExpression(Identifier(a)[BinaryOp(Identifier(i), +, IntLiteral(1))]))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_066():
    """Test a class with a final attribute"""
    source = """class Test {
        final int IMMUTABLE := 5;
    }"""
    expected = "Program([ClassDecl(Test, [AttributeDecl(final PrimitiveType(int), [Attribute(IMMUTABLE = IntLiteral(5))])])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_067():
    """Test a class with a static attribute"""
    source = """class Test {
        static int counter;
    }"""
    expected = "Program([ClassDecl(Test, [AttributeDecl(static PrimitiveType(int), [Attribute(counter)])])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_068():
    """Test 'new' expression with no parameters"""
    source = """class Test {
        void main() {
            Other obj := new Other();
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(ClassType(Other), [Variable(obj = ObjectCreation(new Other()))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_069():
    """Test less than operator"""
    source = """class Test {
        void main() {
            boolean b := 1 < 2;
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(boolean), [Variable(b = BinaryOp(IntLiteral(1), <, IntLiteral(2)))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_070():
    """Test greater than or equal operator"""
    source = """class Test {
        void main() {
            boolean b := 3 >= 3;
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(boolean), [Variable(b = BinaryOp(IntLiteral(3), >=, IntLiteral(3)))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_071():
    """Test not equal operator"""
    source = """class Test {
        void main() {
            boolean b := "a" != "a";
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(boolean), [Variable(b = BinaryOp(StringLiteral('a'), !=, StringLiteral('a')))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_072():
    """Test division operator"""
    source = """class Test {
        void main() {
            float f := 10.0 / 2.0;
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(float), [Variable(f = BinaryOp(FloatLiteral(10.0), /, FloatLiteral(2.0)))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_073():
    """Test nested if statement"""
    source = """class Test {
        void main() {
            if true then {
                if false then {}
            }
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(stmts=[IfStatement(if BoolLiteral(True) then BlockStatement(stmts=[IfStatement(if BoolLiteral(False) then BlockStatement(stmts=[]))]))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_074():
    """Test method with a single parameter"""
    source = """class Test {
        void print(int x) {}
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) print([Parameter(PrimitiveType(int) x)]), BlockStatement(stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_075():
    """Test constructor with a single parameter"""
    source = """class Test {
        Test(int x) {}
    }"""
    expected = "Program([ClassDecl(Test, [ConstructorDecl(Test([Parameter(PrimitiveType(int) x)]), BlockStatement(stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_076():
    """Test empty constructor"""
    source = """class Test {
        Test() {}
    }"""
    expected = "Program([ClassDecl(Test, [ConstructorDecl(Test([]), BlockStatement(stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_077():
    """Test empty method"""
    source = """class Test {
        void doNothing() {}
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) doNothing([]), BlockStatement(stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_078():
    """Test multiple class declarations in one program"""
    source = """class A {} class B {}"""
    expected = "Program([ClassDecl(A, []), ClassDecl(B, [])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_079():
    """Test assigning 'this.x' to a local variable"""
    source = """class Test {
        int x;
        void main() {
            int y := this.x;
        }
    }"""
    expected = "Program([ClassDecl(Test, [AttributeDecl(PrimitiveType(int), [Attribute(x)]), MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(y = PostfixExpression(ThisExpression(this).x))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_080():
    """Test simple boolean expression in an if statement"""
    source = """class Test {
        void main() {
            if (a && b) then {}
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(stmts=[IfStatement(if ParenthesizedExpression((BinaryOp(Identifier(a), &&, Identifier(b)))) then BlockStatement(stmts=[]))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_081():
    """Test local variable declaration of type float"""
    source = """class Test {
        void main() {
            float f := 1.0;
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(float), [Variable(f = FloatLiteral(1.0))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_082():
    """Test local variable declaration of type string"""
    source = """class Test {
        void main() {
            string s := "test";
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(string), [Variable(s = StringLiteral('test'))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_083():
    """Test local variable declaration of type boolean"""
    source = """class Test {
        void main() {
            boolean b := false;
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(boolean), [Variable(b = BoolLiteral(False))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_084():
    """Test a for loop with a single statement in the body"""
    source = """class Test {
        void main() {
            for i := 1 to 5 do {
                a := a + 1;
            }
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(stmts=[ForStatement(for i := IntLiteral(1) to IntLiteral(5) do BlockStatement(stmts=[AssignmentStatement(IdLHS(a) := BinaryOp(Identifier(a), +, IntLiteral(1)))]))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_085():
    """Test if-else-if structure"""
    source = """class Test {
        void main() {
            if a > 0 then {
                return 1;
            } else {
                if a < 0 then {
                    return -1;
                }
            }
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(stmts=[IfStatement(if BinaryOp(Identifier(a), >, IntLiteral(0)) then BlockStatement(stmts=[ReturnStatement(return IntLiteral(1))]), else BlockStatement(stmts=[IfStatement(if BinaryOp(Identifier(a), <, IntLiteral(0)) then BlockStatement(stmts=[ReturnStatement(return UnaryOp(-, IntLiteral(1)))]))]))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_086():
    """Test an array literal with floats"""
    source = """class Test {
        void main() {
            float[2] f := {1.0, 2.5};
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(ArrayType(PrimitiveType(float)[2]), [Variable(f = ArrayLiteral({FloatLiteral(1.0), FloatLiteral(2.5)}))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_087():
    """Test an array literal with strings"""
    source = """class Test {
        void main() {
            string[2] s := {"a", "b"};
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(ArrayType(PrimitiveType(string)[2]), [Variable(s = ArrayLiteral({StringLiteral('a'), StringLiteral('b')}))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_088():
    """Test method call with arguments"""
    source = """class Test {
        void main() {
            obj.method(1, "str");
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(stmts=[MethodInvocationStatement(PostfixExpression(Identifier(obj).method(IntLiteral(1), StringLiteral('str'))))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_089():
    """Test an empty main method"""
    source = """class Test {
        void main() {}
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_090():
    """Test chained attribute access"""
    source = """class Test {
        void main() {
            int v := a.b.c;
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(v = PostfixExpression(PostfixExpression(Identifier(a).b).c))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_091():
    """Test class inheritance with an empty child class"""
    source = """class Child extends Parent {}"""
    expected = "Program([ClassDecl(Child, extends Parent, [])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_092():
    """Test assigning the result of a method call to a variable"""
    source = """class Test {
        void main() {
            int x := obj.getInt();
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(x = PostfixExpression(Identifier(obj).getInt()))])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_093():
    """Test variable declaration without initialization"""
    source = """class Test {
        void main() {
            int x;
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(x)])], stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_094():
    """Test attribute declaration without initialization"""
    source = """class Test {
        float f;
    }"""
    expected = "Program([ClassDecl(Test, [AttributeDecl(PrimitiveType(float), [Attribute(f)])])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_095():
    """Test for loop with an expression in the range"""
    source = """class Test {
        void main() {
            int n := 10;
            for i := 1 to n * 2 do {}
        }
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) main([]), BlockStatement(vars=[VariableDecl(PrimitiveType(int), [Variable(n = IntLiteral(10))])], stmts=[ForStatement(for i := IntLiteral(1) to BinaryOp(Identifier(n), *, IntLiteral(2)) do BlockStatement(stmts=[]))]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_096():
    """Test array attribute declaration"""
    source = """class Test {
        int[5] arr := {};
    }"""
    expected = "Program([ClassDecl(Test, [AttributeDecl(ArrayType(PrimitiveType(int)[5]), [Attribute(arr)])])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_097():
    """Test simple class type for an attribute"""
    source = """class Test {
        Other o;
    }"""
    expected = "Program([ClassDecl(Test, [AttributeDecl(ClassType(Other), [Attribute(o)])])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_098():
    """Test reference type for an attribute"""
    source = """class Test {
        int & ref;
    }"""
    expected = "Program([ClassDecl(Test, [AttributeDecl(PrimitiveType(int), [Attribute(ref)])])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_099():
    """Test method with multiple parameters of different types"""
    source = """class Test {
        void set(int x; float y; string z) {}
    }"""
    expected = "Program([ClassDecl(Test, [MethodDecl(PrimitiveType(void) set([Parameter(PrimitiveType(int) x), Parameter(PrimitiveType(float) y), Parameter(PrimitiveType(string) z)]), BlockStatement(stmts=[]))])])"
    assert str(ASTGenerator(source).generate()) == expected


def test_100():
    """Test a final simple combination of features"""
    source = """
    class Animal {
    }
    class Cat extends Animal {
    }
    class Test {
        Animal A() {
            Cat c := new Cat();
            return c;
        }
        static void main() { 
        }
    }
"""
    expected = "Program([ClassDecl(FinalTest, [AttributeDecl(PrimitiveType(int), [Attribute(x)]), MethodDecl(PrimitiveType(void) setX([Parameter(PrimitiveType(int) val)]), BlockStatement(stmts=[IfStatement(if BinaryOp(Identifier(val), >, IntLiteral(0)) then BlockStatement(stmts=[AssignmentStatement(PostfixLHS(PostfixExpression(ThisExpression(this).x)) := Identifier(val))]))]))])])"
    assert str(ASTGenerator(source).generate()) == expected
