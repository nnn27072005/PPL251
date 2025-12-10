from utils import Checker
from src.utils.nodes import *

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
    expected = "IllegalConstantExpression(UnaryOp(-, ParenthesizedExpression((BinaryOp(BinaryOp(BinaryOp(IntLiteral(2), +, Identifier(x)), +, IntLiteral(7)), +, UnaryOp(-, IntLiteral(9)))))))"
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
            static int a := 6;
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
    expected = "IllegalConstantExpression(UnaryOp(-, ParenthesizedExpression((BinaryOp(BinaryOp(BinaryOp(IntLiteral(2), +, Identifier(x)), +, IntLiteral(7)), +, UnaryOp(-, IntLiteral(9)))))))"
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
    expected = "Static checking passed"
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
                final int MAX_SIZE := 100;
                final int MAX_SIZE := 200;
            }
        }
    """
    expected = "Redeclared(Constant, MAX_SIZE)"
    assert Checker(source).check_from_source() == expected

def test_018():
    source = """
        class Test {
            static void main() {
                final int x := nil;
            }
            }
    """
    expected = "IllegalConstantExpression(NilLiteral(nil))"
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

def test_020():
    source = """
        class ArrayError {
        static void main() {
            int[3] intArray := {1, 2, 3};
            float[3] floatArray := {1.0, 2.0, 3.0};
            int[2] smallArray := {1, 2};
            
            # intArray := floatArray;
            intArray := smallArray;
        }
    }
    """
    expected = "TypeMismatchInStatement(AssignmentStatement(IdLHS(intArray) := Identifier(smallArray)))"
    assert Checker(source).check_from_source() == expected

def test_021():
    source = """
        class Test {
            int add(int a; int b) {
                return a + b;
            }
            int add(int i; int j){
                return i + 1;
            }
            static void main() {
                int[5] arr := {1, 2, 3, 4, 5};
                arr[2] := 10;
            }
        }
    """
    expected = "Redeclared(Method, add)"
    assert Checker(source).check_from_source() == expected

def test_022():
    source = """
        class Test {
            int add(int a; int b; int a) {
                return a + b;
            }
            static void main() {
                int[5] arr := {1, 2, 3, 4, 5};
                arr[2] := 10;
            }
        }
    """
    expected = "Redeclared(Parameter, a)"
    assert Checker(source).check_from_source() == expected

def test_023():
    source = """
        class Animal {
            void makeSound() {
                io.writeStrLn("Some sound");
            }
        }
        class Dog extends Animal {
            void makeSound() { 
                io.writeStrLn("Woof!");
            }
        }
        class Test {
            static void main() {
            }
        }
    """
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected

def test_024():
    source = """
        class Car {
            string brand;
            int year;
            
            void display() {
                io.writeStrLn(model);
            }

        }
        """
    expected = "UndeclaredIdentifier(model)"
    assert Checker(source).check_from_source() == expected

def test_025():
    source = """
        class Calculator {
            int add(int a; int b) {
                return a + b;
            }
            
            void test() {
                return "123";
            }
            static void main() {
            }
        }
    """
    expected = "TypeMismatchInStatement(ReturnStatement(return StringLiteral('123')))"
    assert Checker(source).check_from_source() == expected

def test_026():
    source = """
        class LoopExample {
            final int limit := 10;
            
            static void main() {
                for limit := 0 to 20 do {
                    io.writeIntLn(limit);
                }
            }
        }
    """
    expected = "CannotAssignToConstant(ForStatement(for limit := IntLiteral(0) to IntLiteral(20) do BlockStatement(stmts=[MethodInvocationStatement(PostfixExpression(Identifier(io).writeIntLn(Identifier(limit))))])))"
    assert Checker(source).check_from_source() == expected

def test_027():
    "if with non-boolean condition"
    source = """
        class Test {
            static void main() {
                int x := 5;
                float y := 10.0;
                if x > 5 then {
                    io.writeStrLn("Hello");
                }
            }
        }
    """
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected

def test_028():
    source = """
        class Parent {
            int age := 42;
            string name := "Ngu";
            Parent(int age; string name) {
                this.age := age;
                this.name := name;
            }
        }
        class Child extends Parent {
            string school := "ABC School";
            float age := 18;
            string name := "Child Name";
            Child(float age; string name) {
                this.age := age;
                this.name := name;
            }
        }
        
        class ValidCoercion {
            int x := 10;
            float y := x; # int to float coercion
            Parent p := new Child(15, "John");
            static void main() {
                
            }
        }
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected

def test_029():
    source = """
        class ArraySubscriptError{
            static void main(){
                int[5] numbers := {1, 2, 3, 4, 5};
                string[2] words := {"hello", "world"};
                
                int value1 := numbers["index"];
            }
        }
        """
    expected = "TypeMismatchInExpression(PostfixExpression(Identifier(numbers)[StringLiteral('index')]))"
    assert Checker(source).check_from_source() == expected

def test_030():
    source = """
    class BinaryOpError {
        static void main() {
            int x := 5;
            string text := "hello";
            boolean flag := true;

            int comparison := text < x;
            boolean result := x && flag;
            int sum := x + text;     # Error: TypeMismatchInExpression at binary operation
        }
}
"""
    expected = "TypeMismatchInExpression(BinaryOp(Identifier(text), <, Identifier(x)))"
    assert Checker(source).check_from_source() == expected

def test_031():
    source = """
    class A{}
    class B {}
    class test{
        test(int x,y){}
        test(int a; int b){}
        static void main(){
            A[2] arrA := {new A(), new A()};
        }
    }
"""
    expected = "Redeclared(Method, test)"
    assert Checker(source).check_from_source() == expected

def test_032():
    source = """
    class ValidLoops {
        void forLoopWithBreak() {
            int i;
            for i := 0 to 10 do {
                if i == 5 then {
                    break;    
                }
                if i % 2 == 0 then {
                    continue; 
                }
                io.writeIntLn(i);
            }
        }
        
        void forLoop() {
            int i;
            for i := 0 to 10 do {
                if i == 3 then {
                    continue;  
                }
                if i == 8 then {
                    break;  
                }
                io.writeIntLn(i);
            }
        }
        
        void nestedLoops() {
            int i;
            int j;
            for i := 0 to 5 do {
                for j := 0 to 5 do {
                    if i == j then {
                        continue;
                    }
                    if j > 3 then {
                        break;  
                    }
                }
            }
        }
        static void main() {}
    }
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected

def test_033():
    source = """
    class Test {
        static void main() {
            float x;
            for x := 0.01 to 1.0 do {
                io.writeFloatLn(x);
            }
        }
    }   
    """
    expected = "TypeMismatchInStatement(ForStatement(for x := FloatLiteral(0.01) to FloatLiteral(1.0) do BlockStatement(stmts=[MethodInvocationStatement(PostfixExpression(Identifier(io).writeFloatLn(Identifier(x))))])))"
    assert Checker(source).check_from_source() == expected

def test_034():
    source = """
    class Test{
        float A(){
            return 3;
        }
        static void main(){
            float result := this.A();
        }
    }"""
    expected = "IllegalMemberAccess(ThisExpression(this))"
    assert Checker(source).check_from_source() == expected

def test_035():
    source = """
    class Test {
        static void main() {
            int x := 10;
            float y := 20.5;
            boolean flag := true;
            string message := "Hello, World!";
            
            int sum := x + 5;
            float average := (x + y) / 2.0;
            boolean isAdult := flag && false;
            string greeting := message ^ " Welcome!";
        }
    }
    """
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected

def test_036():
    source = """
    class Animal {
        void makeSound() {
            io.writeStrLn("Some sound");
        }
    }
    class Cat extends Animal {
        void makeSound() {
            io.writeStrLn("Meow!");
        }
    }
    class Test {
        Animal A()  {
            Cat c := new Cat();
            return c;
        }
        static void main() {
            Animal a := new Cat();
            a.makeSound();  
        }
    }
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected

def test_037():
    source = """
    class test {
        int getValue() {
            return 42;
        }
        int testMe (){
            final int value := this.getValue();
        }
        static void main() {
            
        }
    }
""" 
    expected = "IllegalConstantExpression(PostfixExpression(ThisExpression(this).getValue()))"
    assert Checker(source).check_from_source() == expected

def test_038():
    source ="""
    class Student {
        string name;
        int age;
        static int totalStudents := 0;
        string school := "Default School";
        
        static void resetCount() {
            totalStudents := 0;
        }
        
        void setName(string n) {
            name := n;
        }
        
        void secretMethod() {
            io.writeStrLn("Secret");
        }
}
    class ValidAccess {
    void test() {
        int count := Student.totalStudents;
        
        Student s := new Student();
        s.school := "New School";      
        s.setName("Alice");        
        Student.resetCount();             
    }
}

class GraduateStudent extends Student {
    void accessProtected() {
        age := 25;                       
        # setName("Graduate");    
    }
}
    class Test {
        static void main() {
        }
    }
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected

def test_039():
    source ="""
    class Student {
        string name;
        int age;
        static int totalStudents := 0;
        string school := "Default School";
        
        static void resetCount() {
            totalStudents := 0;
        }
        
        void setName(string n) {
            name := n;
        }
        
        void secretMethod() {
            io.writeStrLn("Secret");
        }
}
    class StaticAccessError {
    void test() {
        string school := Student.school;     # Error: IllegalMemberAccess at member access
        Student.setName("John");            # Error: IllegalMemberAccess at method call
    }
}

class GraduateStudent extends Student {
    void accessProtected() {
        age := 25;                       
        # setName("Graduate");    
    }
}
    class Test {
        static void main() {
        }
    }
"""
    expected = "IllegalMemberAccess(PostfixExpression(Identifier(Student).school))"
    assert Checker(source).check_from_source() == expected

from utils import Checker

def test_040():
    # redeclared attribute in same class
    source = """
    class A {
        int x;
        int x;
        static void main() {}
    }
    """
    expected = "Redeclared(Attribute, x)"
    assert Checker(source).check_from_source() == expected

def test_041():
    # undeclared class used in variable
    source = """
    class Test {
        static void main() {
            Unknown u := new Unknown();
        }
    }
    """
    expected = "UndeclaredClass(Unknown)"
    assert Checker(source).check_from_source() == expected

def test_042():
    # undeclared method call on this
    source = """
    class Test {
        int foo() {
            return 1;
        }
        static void main() {
            this.bar();
        }
    }
    """
    expected = "IllegalMemberAccess(ThisExpression(this))"
    assert Checker(source).check_from_source() == expected

def test_043():
    # undeclared attribute access on object
    source = """
    class A { int x; }
    class Test {
        static void main() {
            A a := new A();
            int v := a.y;
        }
    }
    """
    expected = "UndeclaredAttribute(y)"
    assert Checker(source).check_from_source() == expected

def test_044():
    # cannot assign to constant (final local)
    source = """
    class Test {
        static void main() {
            final int z := 3;
            z := 4;
        }
    }
    """
    expected = "CannotAssignToConstant(AssignmentStatement(IdLHS(z) := IntLiteral(4)))"
    assert Checker(source).check_from_source() == expected

def test_045():
    # type mismatch in assignment (string to int)
    source = """
    class Test {
        static void main() {
            int x := "no";
        }
    }
    """
    expected = "TypeMismatchInStatement(VariableDecl(PrimitiveType(int), [Variable(x = StringLiteral('no'))]))"
    assert Checker(source).check_from_source() == expected

def test_046():
    # type mismatch in expression (boolean used in arithmetic)
    source = """
    class Test {
        static void main() {
            int a := true + 1;
        }
    }
    """
    expected = "TypeMismatchInExpression(BinaryOp(BoolLiteral(True), +, IntLiteral(1)))"
    assert Checker(source).check_from_source() == expected

def test_047():
    # type mismatch in constant (const wrong type)
    source = """
    class Test {
        static void main() {
            final float f := 5;
        }
    }
    """
    # int->float coercion may be allowed for vars but for constants spec may require exact type;
    # using TypeMismatchInConstant to include this case (matches sample patterns).
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected

def test_048():
    # must in loop (break outside)
    source = """
    class Test {
        static void main() {
            if true then {
                break;
            }
        }
    }
    """
    expected = "MustInLoop(BreakStatement())"
    assert Checker(source).check_from_source() == expected

def test_049():
    # illegal constant expression: method call in final init
    source = """
    class A {
        int get() { return 2; }
    }
    class Test {
        static void main() {
            A a := new A();
            final int v := a.get();
        }
    }
    """
    expected = "IllegalConstantExpression(PostfixExpression(Identifier(a).get()))"
    assert Checker(source).check_from_source() == expected

def test_050():
    # illegal array literal: mixed types
    source = """
    class Test {
        static void main() {
            int[3] arr := {1, 2, 3.0};
        }
    }
    """
    expected = "IllegalArrayLiteral(ArrayLiteral({IntLiteral(1), IntLiteral(2), FloatLiteral(3.0)}))"
    assert Checker(source).check_from_source() == expected

def test_051():
    # illegal member access: instance access static via object
    source = """
    class A {
        static int s := 0;
    }
    class Test {
        static void main() {
            A a := new A();
            int x := a.s;
        }
    }
    """
    expected = "IllegalMemberAccess(PostfixExpression(Identifier(a).s))"
    assert Checker(source).check_from_source() == expected

def test_052():
    # illegal member access: static access instance via class name (instance method)
    source = """
    class A {
        void m() {}
    }
    class Test {
        static void main() {
            A.m();
        }
    }
    """
    expected = "IllegalMemberAccess(PostfixExpression(Identifier(A).m()))"
    assert Checker(source).check_from_source() == expected

def test_053():
    # redeclared parameter in method signature
    source = """
    class Test {
        int f(int a; int a) { return a; }
        static void main() {}
    }
    """
    expected = "Redeclared(Parameter, a)"
    assert Checker(source).check_from_source() == expected

def test_054():
    # redeclared method (same name and param types)
    source = """
    class Test {
        int f(int a) { return a; }
        int f(int b) { return b+1; }
        static void main() {}
    }
    """
    expected = "Redeclared(Method, f)"
    assert Checker(source).check_from_source() == expected

def test_055():
    # undeclared identifier used as LHS
    source = """
    class Test {
        static void main() {
            x := 5;
        }
    }
    """
    expected = "UndeclaredIdentifier(x)"
    assert Checker(source).check_from_source() == expected

def test_056():
    # type mismatch in for loop: loop var not int
    source = """
    class Test {
        static void main() {
            float i;
            for i := 0 to 10 do {}
        }
    }
    """
    expected = "TypeMismatchInStatement(ForStatement(for i := IntLiteral(0) to IntLiteral(10) do BlockStatement(stmts=[])))"
    assert Checker(source).check_from_source() == expected

def test_057():
    # array index type mismatch (string index)
    source = """
    class Test {
        static void main() {
            int[3] a := {1,2,3};
            int x := a["1"];
        }
    }
    """
    expected = "TypeMismatchInExpression(PostfixExpression(Identifier(a)[StringLiteral('1')]))"
    assert Checker(source).check_from_source() == expected

def test_058():
    # method argument count mismatch
    source = """
    class A {
        void m(int a; int b) {}
    }
    class Test {
        static void main() {
            A a := new A();
            a.m(1);
        }
    }
    """
    expected = "TypeMismatchInExpression(PostfixExpression(Identifier(a).m(IntLiteral(1))))"
    assert Checker(source).check_from_source() == expected

def test_059():
    # method argument type mismatch
    source = """
    class A {
        void m(int a; string s) {}
    }
    class Test {
        static void main() {
            A a := new A();
            a.m("wrong", 123);
        }
    }
    """
    expected = "TypeMismatchInStatement(MethodInvocationStatement(PostfixExpression(Identifier(a).m(StringLiteral('wrong'), IntLiteral(123)))))"
    assert Checker(source).check_from_source() == expected

def test_060():
    # return type mismatch in method
    source = """
    class Test {
        int f() { return "no"; }
        static void main() {}
    }
    """
    expected = "TypeMismatchInStatement(ReturnStatement(return StringLiteral('no')))"
    assert Checker(source).check_from_source() == expected

def test_061():
    # no entry point (no static void main())
    source = """
    class A { void f() {} }
    class B { void g() {} }
    """
    expected = "No Entry Point"
    assert Checker(source).check_from_source() == expected

def test_062():
    # redeclared class
    source = """
    class A {}
    class A {}
    """
    expected = "Redeclared(Class, A)"
    assert Checker(source).check_from_source() == expected

def test_063():
    # attribute initialization type mismatch
    source = """
    class Test {
        int a := 1.5;
    }
    """
    expected = "TypeMismatchInStatement(AttributeDecl(PrimitiveType(int), [Attribute(a = FloatLiteral(1.5))]))"
    assert Checker(source).check_from_source() == expected

def test_064():
    # attribute constant illegal (nil)
    source = """
    class Test {
        final string s := nil;
        static void main() {}
    }
    """
    expected = "IllegalConstantExpression(NilLiteral(nil))"
    assert Checker(source).check_from_source() == expected

def test_065():
    # object creation of undeclared class
    source = """
    class Test {
        static void main() {
            B b := new B();
        }
    }
    """
    expected = "UndeclaredClass(B)"
    assert Checker(source).check_from_source() == expected

def test_066():
    # array assignment with incompatible sizes
    source = """
    class Test {
        static void main() {
            int[3] a := {1,2,3};
            int[2] b := {1,2};
            a := b;
        }
    }
    """
    expected = "TypeMismatchInStatement(AssignmentStatement(IdLHS(a) := Identifier(b)))"
    assert Checker(source).check_from_source() == expected

def test_067():
    # attempt to assign to attribute constant
    source = """
    class A {
        final int x := 1;
    }
    class Test {
        static void main() {
            A a := new A();
            a.x := 2;
        }
    }
    """
    expected = "CannotAssignToConstant(AssignmentStatement(PostfixLHS(PostfixExpression(Identifier(a).x)) := IntLiteral(2)))"
    assert Checker(source).check_from_source() == expected

def test_068():
    # nested illegal constant expression: uses non-const variable
    source = """
    class Test {
        static int v := 3;
        static void main() {
            final int x := v + 2;
        }
    }
    """
    expected = "IllegalConstantExpression(BinaryOp(Identifier(v), +, IntLiteral(2)))"
    assert Checker(source).check_from_source() == expected

def test_069():
    # equality on different types
    source = """
    class Test {
        static void main() {
            boolean b := (1 == "1");
        }
    }
    """
    expected = "TypeMismatchInExpression(BinaryOp(IntLiteral(1), ==, StringLiteral('1')))"
    assert Checker(source).check_from_source() == expected

def test_070():
    # logical operator on non-boolean
    source = """
    class Test {
        static void main() {
            boolean b := 1 && 0;
        }
    }
    """
    expected = "TypeMismatchInExpression(BinaryOp(IntLiteral(1), &&, IntLiteral(0)))"
    assert Checker(source).check_from_source() == expected

def test_071():
    # unary not on non-boolean
    source = """
    class Test {
        static void main() {
            boolean b := !123;
        }
    }
    """
    expected = "TypeMismatchInExpression(UnaryOp(!, IntLiteral(123)))"
    assert Checker(source).check_from_source() == expected

def test_072():
    # array literal empty but typed mismatch when used
    source = """
    class ForLoopError {
    void loop() {
        float f := 1.5;
        int i;
        boolean condition := true;
       
        for f := 0 to 10 do {  
            io.writeFloatLn(f);
        }
       
        for i := condition to 10 do { 
            io.writeIntLn(i);
        }
    }
}
    """
    expected = "TypeMismatchInStatement(ForStatement(for f := IntLiteral(0) to IntLiteral(10) do BlockStatement(stmts=[MethodInvocationStatement(PostfixExpression(Identifier(io).writeFloatLn(Identifier(f))))])))"
    assert Checker(source).check_from_source() == expected

def test_073():
    # access inherited attribute successfully (should pass)
    source = """
    class P { int x := 1; }
    class C extends P { int y := x; }
    class Test { static void main() {} }
    """
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected

def test_074():
    # override method signature incompatible (redeclaration with different params allowed? test redeclare)
    source = """
    class P { int f(int a) { return a; } }
    class C extends P { int f(int a; int b) { return a; } }
    class Test { static void main() {} }
    """
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected

def test_075():
    # using this in static context (IllegalMemberAccess)
    source = """
    class Test {
        static void main() {
            this.x := 1;
        }
    }
    """
    expected = "IllegalMemberAccess(ThisExpression(this))"
    assert Checker(source).check_from_source() == expected

def test_076():
    # calling void-returning method in expression (should be TypeMismatchInExpression)
    source = """
    class A {
        int v() {return 1;}
    }
    class Test {
        static void main() {
            int x := (new A()).v();
        }
    }
    """
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected

def test_077():
    # assignment of void to variable
    source = """
    class Test {
        int A(int x; int y) {
            return 1;
        }
        int A(int a,b) {
            return 2;
        }
        static void main() {
            
        }
    }
    """
    expected = "Redeclared(Method, A)"
    assert Checker(source).check_from_source() == expected

def test_078():
    # redeclared local variable across nested blocks (same-block redeclare)
    source = """
    class Test {
        int x := 2.5;
        static void main() {
        
        }
    }
    """
    expected = "TypeMismatchInStatement(AttributeDecl(PrimitiveType(int), [Attribute(x = FloatLiteral(2.5))]))"
    assert Checker(source).check_from_source() == expected

def test_079():
    # using identifier that shadows class name incorrectly
    source = """
    class A {}
    class Test {
        static void main() {
            int A := 5;
            A a := new A();
        }
    }
    """
    expected = "UndeclaredClass(A)"
    assert Checker(source).check_from_source() == expected

def test_080():
    # illegal access of parent-only attribute via class name
    source = """
    class P { int x := 1; }
    class C extends P {}
    class Test {
        static void main() {
            int v := P.x;
        }
    }
    """
    expected = "IllegalMemberAccess(PostfixExpression(Identifier(P).x))"
    assert Checker(source).check_from_source() == expected

def test_081():
    # assigning array element with wrong type
    source = """
    class Test {
        static void main() {
            int[2] a := {1,2};
            a[0] := 3.5;
        }
    }
    """
    expected = "TypeMismatchInStatement(AssignmentStatement(PostfixLHS(PostfixExpression(Identifier(a)[IntLiteral(0)])) := FloatLiteral(3.5)))"
    assert Checker(source).check_from_source() == expected

def test_082():
    # missing method in inheritance chain
    source = """
    class P {}
    class C extends P {
        void foo() {
            this.bar();
        }
    }
    """
    expected = "UndeclaredMethod(bar)"
    assert Checker(source).check_from_source() == expected

def test_083():
    # constant referencing nil
    source = """
    class Test {
        static void main() {
            final int a := nil;
        }
    }
    """
    expected = "IllegalConstantExpression(NilLiteral(nil))"
    assert Checker(source).check_from_source() == expected

def test_084():
    source = """
    class Test {
        int a := 1;
        int b := 2;
        void sum() {
            return this.a + this.b;
        }
        static void main() {
        }
    }
    """
    expected = "TypeMismatchInStatement(ReturnStatement(return BinaryOp(PostfixExpression(ThisExpression(this).a), +, PostfixExpression(ThisExpression(this).b))))"
    assert Checker(source).check_from_source() == expected

def test_085():
    # using method name as variable
    source = """
    class Test {
        int foo() { return 1; }
        static void main() {
            int foo := 5;
        }
    }
    """
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected

def test_086():
    # assignment to method call (lhs is method)
    source = """
    class Test {
        void calculate() {
        float a := 2.5;
        float b := 4.0;
        int e := 4;
        e := (a ^ b) + 2;
        }
        static void main() {
        }
    }
    """
    expected = "TypeMismatchInExpression(BinaryOp(Identifier(a), ^, Identifier(b)))"
    assert Checker(source).check_from_source() == expected

def test_087():
    # use of parent attribute without inheritance declared (UndeclaredAttribute)
    source = """
    class Child {
        int get(int x, y) {
            return parentAttr;
        }
    }
    """
    expected = "UndeclaredIdentifier(parentAttr)"
    assert Checker(source).check_from_source() == expected

def test_088():
    # break/continue properly nested - should pass
    source = """
    class Test {
        void loop() {
            int i;
            for i := 0 to 3 do {
                if i == 2 then break;
            }
        }
        static void main() {}
    }
    """
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected

def test_089():
    # complex constant expression with only literals and unary/binary ops -> allowed
    source = """
    class Test {
    final int y, z := 123;
        static void main() {
            final int x := (1 + 2) * (3 - 1) + -4;
        }
    }
    """
    expected = "IllegalConstantExpression(IntLiteral(123))"
    assert Checker(source).check_from_source() == expected

def test_090():
    source = """
    class Test{
        void main(){
            int[0] arr := {};
            int a := "string";
        }
    }
"""
    expected = "TypeMismatchInStatement(VariableDecl(PrimitiveType(int), [Variable(a = StringLiteral('string'))]))"
    assert Checker(source).check_from_source() == expected

def test_091():
    source = """
    class A {

    A(int x){
        final int y, z := 123;
    }
    static void main(){}
}
"""
    expected = "IllegalConstantExpression(IntLiteral(123))"
    assert Checker(source).check_from_source() == expected


def test_092():
    "illegal constant expression"
    source = """
        class ArrayAccessInConstant {
    
    static void main() {
    final int[5] NUMBERS := {1, 2, 3, 4, 5};
    final int FIRST := NUMBERS[0];
    }
    }
    
    """
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected

def test_093():
    source = Program(
    class_decls=[
        ClassDecl(
            name="Test",
            superclass=None,
            members=[
                MethodDecl(
                    is_static=True,
                    return_type=PrimitiveType("void"),
                    name="main",
                    params=[],
                    body=BlockStatement(
                        var_decls=[
                            VariableDecl(
                                is_final=False,
                                var_type=PrimitiveType("int"),
                                variables=[
                                    Variable(
                                        name="x", init_value=StringLiteral("hello")
                                    )
                                ],
                            )
                        ],
                        statements=[],
                    ),
                )
            ],
        )
    ]
)
    expected = "TypeMismatchInStatement(VariableDecl(PrimitiveType(int), [Variable(x = StringLiteral('hello'))]))"
    assert Checker(ast=source).check_from_ast() == expected

def test_094():
    source = """
    class Test {
        int a := 1;
        int b := this.a;
        static void main() {
        }
    }
    """
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected

def test_095():
    source = """
    class Test {
        final int[5] NUMBERS := {1, 2, 3, 4, 5};
        final int FIRST := NUMBERS[0];
        static void main() {
        }
    }
"""
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected

def test_096():
    source = """
    class Test{
        int a := 1;
        int b := 3;
        int sum(int a,b){
            return a + b;
        }
        int tinh(){
            int c := this.sum(this.a, this.b);
            return c;
        }
        static void main(){

        }
    }
    """
    expected = "Static checking passed"
    assert Checker(source).check_from_source() == expected

def test_097():
    source = """
    class Test{
        final int a := 1;
        final int b := 3;
        final int c, d := 4;
        int sum(int a,b){
            return a + b;
        }

        static void main(){
        }
    }
    """
    expected = "IllegalConstantExpression(IntLiteral(4))"
    assert Checker(source).check_from_source() == expected


def test_098():
    source = """
    class Test{
        int num := 5;
        int sum1(int a,b){
            return a + b;
        }
        int sum2(int x,y){
            int c;
            c := this.sum1(x, y);
            return c;
        }
        static void main(){
            this.num := 10;
        }
    }
    """
    expected = "IllegalMemberAccess(ThisExpression(this))"
    assert Checker(source).check_from_source() == expected

def test_099():
    source = """
        class Test {
            final int a := 1;
            Test(){
                this.a := 2;
            }
            static void main() {
            }
            ~Test(){
            
            }
        }
    """
    expected = "CannotAssignToConstant(AssignmentStatement(PostfixLHS(PostfixExpression(ThisExpression(this).a)) := IntLiteral(2)))"
    assert Checker(source).check_from_source() == expected

def test_100():
    source = """
        class Test {
            final int a := 1;
            Test(){
            }
            static void main() {
            }
            ~Test(){
                this.a := 2;
            }
        }
    """
    expected = "CannotAssignToConstant(AssignmentStatement(PostfixLHS(PostfixExpression(ThisExpression(this).a)) := IntLiteral(2)))"
    assert Checker(source).check_from_source() == expected


