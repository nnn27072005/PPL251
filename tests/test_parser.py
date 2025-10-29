# tests/test_parser_by_category.py
import pytest
from utils import Parser

def test_001():
    """Test basic class with main method"""
    source = """class Program { static void main() {} }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_002():
    """Test method with parameters"""
    source = """class Math { int add(int a; int b) { return a + b; } }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_003():
    """Test class with attribute declaration"""
    source = """class Test { int x; static void main() { x := 42; } }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_004():
    """Test class with string attribute"""
    source = """class Test { string name; static void main() { name := "Alice"; } }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_005():
    """Test final attribute declaration"""
    source = """class Constants { final float PI := 3.14159; static void main() {} }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_006():
    """Test if-else statement"""
    source = """class Test { 
        static void main() { 
            if (x > 0) then { 
                io.writeStrLn("positive"); 
            } else { 
                io.writeStrLn("negative"); 
            }
        }
    }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_007():
    """Test for loop with to keyword"""
    source = """class Test { 
        static void main() { 
            int i;
            for i := 1 to 10 do { 
                i := i + 1; 
            }
        }
    }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_008():
    """Test for loop with downto keyword"""
    source = """class Test { 
        static void main() { 
            int i;
            for i := 10 downto 1 do { 
                io.writeInt(i); 
            }
        }
    }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_009():
    """Test array declaration and access"""
    source = """class Test { 
        static void main() { 
            int[3] arr := {1, 2, 3};
            int first;
            first := arr[0];
            arr[1] := 42;
        }
    }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_010():
    """Test string concatenation and object creation"""
    source = """class Test { 
        static void main() { 
            string result;
            Test obj;
            result := "Hello" ^ " " ^ "World";
            obj := new Test();
        }
    }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_011():
    """Test parser error: missing closing brace in class declaration"""
    source = """class Test { int x := 1; """  # Thiếu dấu }
    expected = "Error on line 1 col 25: <EOF>"
    assert Parser(source).parse() == expected

def test_012():
    """Test parser error: missing closing brace in class declaration"""
    source = """class Shape {
    static final int numOfShape := 0;
    final int immuAttribute := 0;

    float length, width;
    static int getNumOfShape() {
        return numOfShape;
    }
}

class Rectangle extends Shape {
    float getArea() {
        return this.length * this.width;
    }
}
 """  # Thiếu dấu }
    expected = "success"
    assert Parser(source).parse() == expected

def test_013():
    """Test parser error: missing closing brace in class declaration"""
    source = """class A {final int My1stCons := 1 + 5, My2ndCons := 2;
static int x, y := 0;}
"""  # Thiếu dấu }
    expected = "success"
    assert Parser(source).parse() == expected

def test_014():
    """Test parser error: missing closing brace in class declaration"""
    source = """class A {final int My1stCons := 1 + 5, My2ndCons := 2;
static int x, y := 0;}
"""  # Thiếu dấu }
    expected = "success"
    assert Parser(source).parse() == expected

def test_015():
    """Test parser error: missing closing brace in class declaration"""
    source = """class A {
        int main(){
            int x := 10;
            int & ref := x;        # ref is an alias for x
            Rectangle r := new Rectangle(5.0, 3.0);
            Rectangle & rectRef := r;  # rectRef is an alias for r
            int x := 10;
        int & ref := x;
            ref := 20;             # x also becomes 20
        rectRef.length := 10.0;    # r.length also becomes 10.0

        a[3+x.foo(2)] := a[b[2]] + 3;
        x.b[2] := x.m()[3];

        
        ref := 20;  # x becomes 20, ref still refers to x
    }}
""" 
    expected = "success"
    assert Parser(source).parse() == expected

def test_016():
    """Test parser error: missing closing brace in class declaration"""
    source = """class A {
        int hey(){
            int x := 10;
            int & ref := x;
            ref := 20;  # x becomes 20, ref still refers to x
            this.aPI := 3.14;
value := x.foo(5);
l[3] := value * 2;
ref := newValue;  # Assignment to reference
if flag then
    io.writeStrLn("Expression is true");
else
    io.writeStrLn("Expression is false");
for i := 1 to 100 do {
    io.writeIntLn(i);
    Intarray[i] := i + 1;
    break;
    continue;
}

for x := 5 downto 2 do
    io.writeIntLn(x);
    continue;
    break;

    return this.Hello();
        }
}
"""
    expected = "success"
    assert Parser(source).parse() == expected

# ----------------------------
# Class Declaration
# ----------------------------
class Test_ClassDeclaration:
    def test_001(self):
        """Basic class with main"""
        source = """class Program { static void main() {} }"""
        expected = "success"
        assert Parser(source).parse() == expected

    def test_002(self):
        """Inheritance and instance method with return"""
        source = """
        class Rectangle extends Shape {
            float getArea() { return this.length * this.width; }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_003(self):
        """Multi-class file: classes declared multiple times"""
        source = """
        class A { void m() {} }
        class B extends A { void n() {} }
        class C { static void main() {} }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_004(self):
        """Complex program using many features together"""
        source = """
        class Point { float x, y; Point(float x; float y) { this.x := x; this.y := y; } }
        class Shape { Point p; float area() { return 0.0; } }
        class Circle extends Shape { float r; Circle(float r) { this.r := r; } float area() { return 3.14 * this.r * this.r; } }
        class Main { static void main() { Shape s := new Circle(2.0); io.writeFloatLn(s.area()); } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_005(self):
        """Empty class with no members"""
        source = """class EmptyClass { }"""
        expected = "success"
        assert Parser(source).parse() == expected

    def test_006(self):
        """Complex example combining inheritance, override and polymorphic call"""
        source = """
        class Shape { float getArea() { return 0.0; } }
        class Rect extends Shape { float w, h; Rect(float w; int h) { this.w := w; this.h := h; } float getArea() { return this.w * this.h; } }
        class Main { void main() { Shape s := new Rect(3.0,4.0); io.writeFloatLn(s.getArea()); } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_007(self):
        """Multiple classes referencing each other in attributes"""
        source = """
        class A { B b; }
        class B { A a; }
        class Main { static void main() {} }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_008(self):
        """Example 1"""
        source = """
class Example1 {
    int factorial(int n){
        if n == 0 then return 1; else return n * this.factorial(n - 1);
    }

    void main(){
        int x;
        x := io.readInt();
        io.writeIntLn(this.factorial(x));
    }
}
""" 
        expected = "success"
        assert Parser(source).parse() == expected

    def test_009(self):
        """Example 2"""
        source = """
class Shape {
    float length, width;
    float getArea() {}
    Shape(float length; float width){
        this.length := length;
        this.width := width;
    }
}

class Rectangle extends Shape {
    float getArea(){
        return this.length * this.width;
    }
}

class Triangle extends Shape {
    float getArea(){
        return this.length * this.width / 2;
    }
}

class Example2 {
    void main(){
        Shape s;
        s := new Rectangle(3;4);
        io.writeFloatLn(s.getArea());
        s := new Triangle(3;4);
        io.writeFloatLn(s.getArea());
    }
}
""" 
        expected = "Error on line 26 col 28: ;"
        assert Parser(source).parse() == expected

    def test_010(self):
        """Example 3"""
        source = """
class Rectangle {
    float length, width;
    static int count;
    
    ## Default constructor
    Rectangle() {
        this.length := 1.0;
        this.width := 1.0;
        Rectangle.count := Rectangle.count + 1;
    }
    
    ## Copy constructor
    Rectangle(Rectangle other) {
        this.length := other.length;
        this.width := other.width;
        Rectangle.count := Rectangle.count + 1;
    }
    
    ## User-defined constructor
    Rectangle(float length; float width) {
        this.length := length;
        this.width := width;
        Rectangle.count := Rectangle.count + 1;
    }
    
    ## Destructor
    ~Rectangle() {
        Rectangle.count := Rectangle.count - 1;
        io.writeStrLn("Rectangle destroyed");
    }
    
    float getArea() {
        return this.length * this.width;
    }
    
    static int getCount() {
        return Rectangle.count;
    }
}

class Example3 {
    void main() {
        ## Using different constructors
        Rectangle r1 := new Rectangle();           ## Default constructor
        Rectangle r2 := new Rectangle(5.0, 3.0);  ## User-defined constructor
        Rectangle r3 := new Rectangle(r2);        ## Copy constructor
        
        io.writeFloatLn(r1.getArea());  ## 1.0
        io.writeFloatLn(r2.getArea());  ## 15.0
        io.writeFloatLn(r3.getArea());  ## 15.0
        io.writeIntLn(Rectangle.getCount());  ## 3
        
        ## Destructors will be called automatically when objects go out of scope
    }
}
""" 
        expected = "success"
        assert Parser(source).parse() == expected

    def test_011(self):
        """Example 4"""
        source = """
class MathUtils {
    static void swap(int & a; int & b) {
        int temp := a;
        a := b;
        b := temp;
    }
    
    static void modifyArray(int[5] & arr; int index; int value) {
        arr[index] := value;
    }
    
    static int & findMax(int[5] & arr) {
        int & max := arr[0];
        for i := 1 to 4 do {
            if (arr[i] > max) then {
                max := arr[i];
            }
        }
        return max;
    }
}

class StringBuilder {
    string & content;
    
    StringBuilder(string & content) {
        this.content := content;
    }
    
    StringBuilder & append(string & text) {
        this.content := this.content ^ text;
        return this;
    }
    
    StringBuilder & appendLine(string & text) {
        this.content := this.content ^ text ^ "\\n";
        return this;
    }
    
    string & toString() {
        return this.content;
    }
}

class Example4 {
    void main() {
        ## Reference variables
        int x := 10, y := 20;
        int & xRef := x;
        int & yRef := y;
        
        io.writeIntLn(xRef);  ## 10
        io.writeIntLn(yRef);  ## 20
        
        ## Pass by reference
        MathUtils.swap(x; y);
        io.writeIntLn(x);  ## 20
        io.writeIntLn(y);  ## 10
        
        ## Array references
        int[5] numbers := {1, 2, 3, 4, 5};
        MathUtils.modifyArray(numbers; 2; 99);
        io.writeIntLn(numbers[2]);  ## 99
        
        ## Reference return
        int & maxRef := MathUtils.findMax(numbers);
        maxRef := 100;
        io.writeIntLn(numbers[2]);  ## 100
        
        ## Method chaining with references
        string text := "Hello";
        StringBuilder & builder := new StringBuilder(text);
        builder.append(" ").append("World").appendLine("!");
        io.writeStrLn(builder.toString());  ## "Hello World!\\n"
    }
}
""" 
        expected = "Error on line 57 col 24: ;"
        assert Parser(source).parse() == expected

    def test_012(self):
        """Final complex main example tying many features together"""
        source = """
    class Example {
        float length, width;
        Example(float length; string width) { this.length := length; this.width := width; }
        float getArea() { return this.length * this.width; }
    }
    class Main {
        static void main() {
            Example s := new Example(3.0, 4.0);
            io.writeFloatLn(s.getArea());
        }
    }
    """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_013(self):
        """Duplicate basic class with main (test duplicates in file)"""
        source = """class Program { static void main() {} }"""
        expected = "success"
        assert Parser(source).parse() == expected

    def test_014(self):
        """Parser error: missing closing brace"""
        source = """class Test { int x := 1; """  # Thiếu dấu }
        expected = "Error on line 1 col 25: <EOF>"
        assert Parser(source).parse() == expected

    def test_015(self):
        """Parser error: missing closing brace (duplicate)"""
        source = """class Test { int x := 1; """  # Thiếu dấu }
        expected = "Error on line 1 col 25: <EOF>"
        assert Parser(source).parse() == expected

# ----------------------------
# Attribute declaration
# ----------------------------
class Test_AttributeDeclaration:
    def test_001(self):
        """Class with attributes and a static method"""
        source = """
        class Shape {
            static final int numOfShape := 0;
            final int immuAttribute := 0;
            float length, width;
            static int getNumOfShape() { return numOfShape; }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_002(self):
        """Multiple attributes declared in one line, mixing initialization"""
        source = """
        class A {
            int a, b := 2, c;
            static final string s := "hello";
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_003(self):
        """Static attribute access via Class.attr and static method call (attr present)"""
        source = """
        class S { static int cnt; static int get() { return cnt; } }
        class Use { void main() { S.cnt := 5; io.writeIntLn(S.get()); } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_004(self):
        """Use of '=' initialization in attribute declarations"""
        source = """
        class AttrInit {
            int a := 1, b := 2;
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_005(self):
        """Test class with attribute declaration"""
        source = """class Test { int x; static void main() { x := 42; } }"""
        expected = "success"
        assert Parser(source).parse() == expected

    def test_006(self):
        """Test class with string attribute"""
        source = """class Test { string name; static void main() { name := "Alice"; } }"""
        expected = "success"
        assert Parser(source).parse() == expected

    def test_007(self):
        """Final attribute declaration"""
        source = """class Constants { final float PI := 3.14159; static void main() {} }"""
        expected = "success"
        assert Parser(source).parse() == expected

    def test_008(self):
        """Attribute list with no initializers (edge case)"""
        source = """
        class Attrs { int a, b, c; }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_009(self):
        """Declaration of multiple array variables together"""
        source = """
        class MultiArr {
            void main() {
                int[3] a, b := {1,2,3};
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_010(self):
        """Large class with mixed static/final keywords ordering"""
        source = """
        class MixOrder {
            static final int A := 1;
            final static float B := 2.0;
            void main() {}
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_011(self):
        """Duplicate attribute declaration tests"""
        source = """class Test { int x; static void main() { x := 42; } }"""
        expected = "success"
        assert Parser(source).parse() == expected

    def test_012(self):
        """Duplicate string attribute test"""
        source = """class Test { string name; static void main() { name := "Alice"; } }"""
        expected = "success"
        assert Parser(source).parse() == expected

# ----------------------------
# Method declaration
# ----------------------------
class Test_MethodDeclaration:
    def test_001(self):
        """Method invocation: static and instance calls"""
        source = """class A { static void s() {} void m() {} }
        class B {
            void main() {
                A a := new A();
                A.s();
                a.m();
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_002(self):
        """Method with reference parameter (single group of ids)"""
        source = """
        class M {
            static void swap(int & a; double b) {}  # note: parsed as one param group typ & idList
            void main() {}
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_003(self):
        """Reference parameter with semicolon-separated param groups"""
        source = """
        class MathUtils {
            static void swap(int & a; int & b) {
                int temp := a;
                a := b;
                b := temp;
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_004(self):
        """Method without parameters and with empty body"""
        source = """
        class Empty { void doNothing() {} }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_005(self):
        """Method parameter groups with semicolon separating different types"""
        source = """
        class ParamTest {
            void foo(float a; char & b; int c) { io.writeIntLn(c); }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_006(self):
        """Method that returns a reference to class attribute"""
        source = """
        class C {
            int v;
            int & getVRef() { return v; }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_007(self):
        """Method with no parameters but with return type"""
        source = """
        class NoParam { int get() { return 42; } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_008(self):
        """Method declaration order doesn't matter; parser accepts many members"""
        source = """
        class Many {
            int a;
            void f() {}
            static void main() {}
            final int c := 3;
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_009(self):
        """Method invocation with complex argument expressions"""
        source = """
        class ComplexArg {
            int sum(int a; int b) { return a + b; }
            void main() { io.writeIntLn(this.sum(1 + 2, 3 * 4)); }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_010(self):
        """Method with multiple grouped params (same type)"""
        source = """
        class GroupParam {
            void foo(int a;int b;int & c) { io.writeIntLn(a + b + c); }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_011(self):
        """Method with reference parameter and array param grouping"""
        source = """
        class MixRef { static void proc(int & arr; int idx) { arr[idx] := 0; } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_012(self):
        """Method that returns array type"""
        source = """
        class ARR {
            int[2] make() { int[2] x := {1,2}; return x; }
            void main() { io.writeIntLn(this.make()[0]); }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_013(self):
        """Method call statement where method returns void"""
        source = """
        class A { static void s() {} }
        class B { void main() { A.s(); } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_014(self):
        """Method returning array reference via value (array returned as expression)"""
        source = """
        class ARet { int[2] m() { int[2] a := {1,2}; return a; } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_015(self):
        """Method with no parameters and empty body duplicate"""
        source = """
        class Empty { void doNothing() {} }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_016(self):
        """Method with parameters (simple)"""
        source = """class Math { int add(int a; int b) { return a + b; } }"""
        expected = "success"
        assert Parser(source).parse() == expected

    def test_017(self):
        """Method with parameters (duplicate test)"""
        source = """class Math { int add(int a; int b) { return a + b; } }"""
        expected = "success"
        assert Parser(source).parse() == expected

# ----------------------------
# Constructor declaration
# ----------------------------
class Test_ConstructorDeclaration:
    def test_001(self):
        """Constructor (user-defined) and usage in main"""
        source = """
        class Rectangle {
            float length, width;
            Rectangle(float length; float width) {
                this.length := length;
                this.width := width;
            }
        }
        class Main {
            static void main() {
                Rectangle r := new Rectangle(3, 4);
                io.writeFloatLn(r.getArea());
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_002(self):
        """Default and copy constructors plus destructor present"""
        source = """
        class Rectangle {
            float length, width; int a, b;
            static int count;
            Rectangle() { this.length := 1.0; this.width := 1.0; Rectangle.count := Rectangle.count + 1; }
            Rectangle(Rectangle other) { this.length := other.length; this.width := other.width; Rectangle.count := Rectangle.count + 1; }
            Rectangle(float length, width) { this.length := length; this.width := width; Rectangle.count := Rectangle.count + 1; }
            ~Rectangle() { Rectangle.count := Rectangle.count - 1; io.writeStrLn("Destroyed"); }
            float getArea() { return this.length * this.width; }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_003(self):
        """Use of multiple constructors and new selection (constructor selection)"""
        source = """
        class C {
            C() {}
            C(C other) {}
        }
        class Main { void main() { C a := new C(); C b := new C(a); } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_004(self):
        """Constructor referencing this to init attributes"""
        source = """
        class P {
            int x;
            P(int x) { this.x := x; }
            int get() { return this.x; }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_005(self):
        """Constructor: use of this in constructor to refer to attributes (CtorThis)"""
        source = """
        class CtorThis {
            int a;
            CtorThis(int a) { this.a := a; }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

# ----------------------------
# Destructor declaration
# ----------------------------
class Test_DestructorDeclaration:
    def test_001(self):
        """Destructor declaration present"""
        source = """
        class Rectangle {
            ~Rectangle() {
                Rectangle.count := Rectangle.count - 1;
                io.writeStrLn("Rectangle destroyed");
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_002(self):
        """Default and copy constructors plus destructor (Example 3 contained destructor)"""
        source = """
        class Rectangle {
            float length, width;
            static int count;
            Rectangle() { this.length := 1.0; this.width := 1.0; Rectangle.count := Rectangle.count + 1; }
            ~Rectangle() { this.count := this.count - 1; io.writeStrLn("Rectangle destroyed"); }
            float getArea() { return this.length * this.width; }
            static int getCount() { return this.count; }
        }
        class Example3 {
            void main() {
                Rectangle r1 := new Rectangle();
                io.writeFloatLn(r1.getArea());
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

# ----------------------------
# Primitive Type (int/float/boolean/string related)
# ----------------------------
class Test_PrimitiveType:
    def test_001(self):
        """Boolean operators and short-circuit expressions"""
        source = """
        class BoolOps {
            boolean foo() { return true; }
            void main() {
                boolean a;
                a := true && (false || this.foo());
                if a then io.writeStrLn("ok");
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_002(self):
        """Arithmetic precedence and mixed int/float coercion"""
        source = """
        class Math {
            float compute() { return 1 + 2.0 * 3; }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_003(self):
        """Relational operators with integers and floats"""
        source = """
        class Rel {
            boolean cmp() { return 1 < 2 && 3.0 >= 2; }
        }
        """
        expected = "Error on line 3 col 48: >="
        assert Parser(source).parse() == expected

    def test_004(self):
        """Modulo and integer division operators"""
        source = """
        class DivMod { int f() { return 10 \\ 3 + 10 % 3; } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_005(self):
        """Logical not and combined boolean expressions"""
        source = """
        class Logic { boolean neg() { return ! (true && false); } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_006(self):
        """Using various relational operators in series"""
        source = """
        class ROps { boolean test() { return 1 <= 2 && 3 || 1 && !(1 == 0); } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_007(self):
        """Use of boolean literals directly in expressions"""
        source = """
        class BoolLit { void main() { boolean b := true; if b == false then io.writeStrLn("no"); } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_008(self):
        """Boolean return from relational of floats"""
        source = """
        class FR {
            boolean cmp(float a; float b) { return a > b; }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_009(self):
        """Use of E operator forms in float literals (exponent)"""
        source = """
        class FloExp { float x() { return 1.2E3; } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_010(self):
        """NEG and NOT unary together"""
        source = """
        class Unary { int f() { return -1; } boolean g() { return !true; } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

# ----------------------------
# Array Type
# ----------------------------
class Test_ArrayType:
    def test_001(self):
        """Array declaration, literal and indexing"""
        source = """
        class Example {
            void main() {
                int[5] arr := {1,2,3,4,5};
                int x;
                x := arr[2];
                io.writeIntLn(x);
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_002(self):
        """Indexing an expression result and nested indexing"""
        source = """
        class Idx {
            void main() {
                int[3] a := {1,2,3};
                int[3] b := {4,5,6};
                int x;
                x := a[b[1]];
                io.writeIntLn(x);
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_003(self):
        """Array of floats and float literals with exponent"""
        source = """
        class Floats {
            void main() {
                float[3] a := {1.0, 2., 3e2};
                io.writeFloatLn(a[2]);
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_004(self):
        """Array as parameter (array type in param) and modification"""
        source = """
        class ArrUtil {
            static void modify(int[5] & arr; int idx; int val) { arr[idx] := val; }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_005(self):
        """Array literal of floats and usage in expression"""
        source = """
        class AL {
            void main() { float[3] a := {1.0, 2.0, 3.0}; io.writeFloatLn(a[0] + a[1]); }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_006(self):
        """Indexing on method return that gives an array"""
        source = """
        class A { int[3] arr() { int[3] x := {1,2,3}; return x; } }
        class Use { void main() { A a := new A(); io.writeIntLn(a.arr()[1]); } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_007(self):
        """Declaration of multiple array variables together and indexing results"""
        source = """
        class MultiArr {
            void main() {
                int[3] a, b := {1,2,3};
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_008(self):
        """Array literal and braces usage in general"""
        source = """class Test { static void main() { int[3] arr := {1, 2, 3}; } }"""
        expected = "success"
        assert Parser(source).parse() == expected

    def test_009(self):
        """Method returning array type and using indexing on returned array"""
        source = """
        class ARR {
            int[2] make() { int[2] x := {1,2}; return x; }
            void main() { io.writeIntLn(this.make()[0]); }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_010(self):
        """Returned array assigned to variable and indexed"""
        source = """
        class AR {
            int[2] m() { int[2] a := {7,8}; return a; }
            void main() { int[2] b := this.m(); io.writeIntLn(b[1]); }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

# ----------------------------
# Class Type (nil/new/class usage)
# ----------------------------
class Test_ClassType:
    def test_001(self):
        """Nil literal usage for class type variables"""
        source = """
        class Node { Node next; Node() {} }
        class Main {
            void main() {
                Node n;
                n := nil;
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_002(self):
        """Use of NIL assignment to class variable inside method"""
        source = """
        class RefTest {
            Node n;
            void clear() { n := nil; }
        }
        class Node { Node next; }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_003(self):
        """Object creation and new selection tests"""
        source = """
        class C { C() {} C(C other) {} }
        class Main { void main() { C a := new C(); C b := new C(a); } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_004(self):
        """String concatenation and object creation (test mixing new)"""
        source = """class Test { 
            static void main() { 
                string result;
                Test obj;
                result := "Hello" ^ " " ^ "World";
                obj := new Test();
            }
        }"""
        expected = "success"
        assert Parser(source).parse() == expected

    def test_005(self):
        """Multiple nested comments mixed with code and class usage"""
        source = """
        /* top comment */
        class C {
            # inline comment
            void main() { /* inner block */ io.writeStrLn("ok"); }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

# ----------------------------
# Reference Type
# ----------------------------
class Test_ReferenceType:
    def test_001(self):
        """Reference return type and chaining (Builder example)"""
        source = """
        class Builder {
            string & content;
            Builder(string & content) { this.content := content; }
            Builder & append(string & t) { this.content := this.content ^ t; return this; }
            string & toString() { return this.content; }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_002(self):
        """Method declarations with ampersand return type (reference)"""
        source = """
        class C {
            int v;
            int & getRef() { return v; }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_003(self):
        """Reference return (findMax)"""
        source = """
        class Utils {
            static int & findMax(int[5] & arr) {
                int & max := arr[0];
                for i := 1 to 4 do {
                    if arr[i] > max then max := arr[i];
                }
                return max;
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_004(self):
        """Complex program combining references, arrays, loops, and IO"""
        source = """
        class Utils {
            static int & findMax(int[5] & arr) {
                int & max := arr[0];
                for i := 1 to 4 do {
                    if arr[i] > max then max := arr[i];
                }
                return max;
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_005(self):
        """Reference variable initialization and use in Example4"""
        source = """
        class Example4 {
            void main() {
                int x := 10, y := 20;
                int & xRef := x;
                int & yRef := y;
                io.writeIntLn(xRef);
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_006(self):
        """Chaining method calls and returns (reference chaining example)"""
        source = """
        class S {
            S & set() { return this; }
            S & next() { return this; }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

# ----------------------------
# Expression
# ----------------------------
class Test_Expression:
    def test_001(self):
        """String literal with escapes and concatenation"""
        source = r'''
        class S {
            void main() {
                string s := "Hello\tWorld\n";
                io.writeStrLn(s ^ "!");
            }
        }
        '''
        expected = "success"
        assert Parser(source).parse() == expected

    def test_002(self):
        """Complex expression with parentheses and unary operators"""
        source = """
        class Expr {
            int f() { return - (1 + 2) * (3 - -4); }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_003(self):
        """Member access chains with dot and method call"""
        source = """
        class C { int v; int getV() { return v; } }
        class Use {
            void main() {
                C c := new C();
                c.v := 10;
                io.writeIntLn(c.getV());
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_004(self):
        """Concatenation of multiple strings"""
        source = """
        class Concat { void main() { string s := "a" ^ "b" ^ "c"; io.writeStrLn(s); } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_005(self):
        """Complex nested expressions with method calls and indexing"""
        source = """
        class Complex {
            int[3] arr() { int[3] x := {1,2,3}; return x; }
            void main() { io.writeIntLn(this.arr()[1] + (2 * 3)); }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_006(self):
        """Method call with expression arguments evaluated left-to-right"""
        source = """
        class Eval {
            int a;
            int f(int x) { this.a := x; return x; }
            void main() { int x := this.f(1) + this.f(2); }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_007(self):
        """Expression using modulo, multiplication, addition precedence"""
        source = """
        class ExprPrec { int f() { return 1 + 2 * 3 % 4; } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_008(self):
        """Complex expression mixing boolean and arithmetic via precedence"""
        source = """
        class Mix { int f() { return (1 + 2) * (3 - 4) / 2; } boolean b() { return (1 < 2) && (2 < 3); } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_009(self):
        """Operators chain with both boolean and arithmetic mixing via precedence"""
        source = """
        class Mix { int f() { return (1 + 2) * (3 - 4) / 2; } boolean b() { return (1 < 2) && (2 < 3); } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_010(self):
        """Expression with member access + indexing chain"""
        source = """
        class C { int[2] a; }
        class D { C c; void main() { io.writeIntLn(this.c.a[0]); } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_011(self):
        """Large expression used as assignment RHS"""
        source = """
        class LongExpr {
            void main() {
                int x;
                x := ((1+2) * (3+4) - 5) \\ 2 % 3;
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_012(self):
        """Expression involving new and method calls on RHS"""
        source = """
        class A { A() {} int f() { return 1; } }
        class Use { void main() { A a := new A(); int x := a.f(); io.writeIntLn(x); } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_013(self):
        """String literal escapes complex"""
        source = r'''
        class Esc { void main() { string s := "Line1\nLine2\tTabbed\\Backslash\"Quote\""; io.writeStrLn(s); } }
        '''
        expected = "success"
        assert Parser(source).parse() == expected

    def test_014(self):
        """String concatenation and writeStrLn usage"""
        source = """
        class SConcat { void main() { io.writeStrLn("a" ^ "b" ^ "\\n"); } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_015(self):
        """String literal edgecases with escaped quotes"""
        source = r'''
        class S { void main() { string s := "He said: \"Hi\""; io.writeStrLn(s); } }
        '''
        expected = "success"
        assert Parser(source).parse() == expected

    def test_016(self):
        """Use of colon in separators inside expressions"""
        source = """
        class Col { void main() { io.writeStr(":"); } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_017(self):
        """Member access within class"""
        source = """class Col {
            int calSum(int a; b) {
                return a + b;
            }
            void main() { 
                io.writeIntLn(this.calSum(3,5)); 
            } 
        }
        """
        expected = "Error on line 2 col 31: )"
        assert Parser(source).parse() == expected

# ----------------------------
# Statement
# ----------------------------
class Test_Statement:
    def test_001(self):
        """For loop with to and assignment inside"""
        source = """
        class LoopTest {
            void main() {
                int i;
                for i := 1 to 3 do {
                    io.writeIntLn(i);
                }
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_002(self):
        """For loop with downto and single-statement body"""
        source = """
        class LoopDown {
            void main() {
                for k := 5 downto 2 do io.writeIntLn(k);
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_003(self):
        """If then else statement with boolean expression"""
        source = """
        class IfElse {
            void main() {
                boolean flag;
                flag := true;
                if flag then io.writeStrLn("yes"); else io.writeStrLn("no");
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_004(self):
        """Break and continue inside for loop"""
        source = """
        class BreakCont {
            void main() {
                int i;
                for i := 1 to 5 do {
                    if i == 3 then break;
                    if i == 2 then continue;
                    io.writeIntLn(i);
                }
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected



    def test_007(self):
        """Multiple var declarations in a block and later assignments"""
        source = """
        class Vars {
            void main() {
                int[5] ngu := {};
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_008(self):
        """Break/Continue nested for loops"""
        source = """
        class ComplexLoop {
            void main() {
                int i;
                for i := 1 to 3 do {
                    for i := 1 to 2 do {
                        continue;
                    }
                    break;
                }
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_009(self):
        """Use of boolean read/write IO methods in io class"""
        source = """
        class IOTest {
            void main() {
                boolean b;
                b := io.readBool();
                io.writeBoolLn(b);
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_010(self):
        """Method returning void used as statement"""
        source = """
        class VoidUse { void p() {} void main() { this.p(); } }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_011(self):
        """Nested blocks with variable shadowing (block scope) used as statements"""
        source = """
        class Shadow {
            void main() {
                int x := 1;
                {
                    int x := 2;
                    io.writeIntLn(x);
                }
                io.writeIntLn(x);
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_012(self):
        """Method that returns array type and using indexing on returned array as statements"""
        source = """
        class ARR {
            int[2] make() { int[2] x := {1,2}; return x; }
            void main() { io.writeIntLn(this.make()[0]); }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_013(self):
        """If-else statement (duplicate tests)"""
        source = """class Test { 
            static void main() { 
                if (x > 0) then { 
                    io.writeStrLn("positive"); 
                } else { 
                    io.writeStrLn("negative"); 
                }
            }
        }"""
        expected = "success"
        assert Parser(source).parse() == expected

    def test_014(self):
        """For loop with to keyword (duplicate)"""
        source = """class Test { 
            static void main() { 
                int i;
                for i := 1 to 10 do { 
                    i := i + 1; 
                }
            }
        }"""
        expected = "success"
        assert Parser(source).parse() == expected

    def test_015(self):
        """For loop with downto keyword (duplicate)"""
        source = """class Test { 
            static void main() { 
                int i;
                for i := 10 downto 1 do { 
                    io.writeInt(i); 
                }
            }
        }"""
        expected = "success"
        assert Parser(source).parse() == expected

# ----------------------------
# Scope
# ----------------------------
class Test_Scope:
    def test_001(self):
        """Nested blocks and block variable declarations"""
        source = """
        class Blocks {
            void main() {
                {
                    int x := 1;
                    {
                        float y := 2.0;
                        io.writeFloatLn(y);
                    }
                    io.writeIntLn(x);
                }
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_002(self):
        """Use of 'this' inside methods and constructor init (class scope)"""
        source = """
        class P {
            int x;
            P(int x) { this.x := x; }
            int get() { return this.x; }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_003(self):
        """Variable shadowing in nested blocks"""
        source = """
        class Shadow {
            void main() {
                int x := 1;
                {
                    int x := 2;
                    io.writeIntLn(x);
                }
                io.writeIntLn(x);
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_004(self):
        """Method scope: parameters and locals visible inside method only"""
        source = """
        class LocalMany {
            void main() {
                float a, b, c;
                int i, j := 0;
                a := 1.0;
            }
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

    def test_005(self):
        """Method declaration order and member visibility"""
        source = """
        class Many {
            int a;
            void f() {}
            static void main() {}
            final int c := 3;
        }
        """
        expected = "success"
        assert Parser(source).parse() == expected

# End of file
def test_001():
    """Test basic class with main method"""
    source = """class Program { static void main() {} }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_002():
    """Test method with parameters"""
    source = """class Math { int add(int a; int b) { return a + b; } }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_003():
    """Test class with attribute declaration"""
    source = """class Test { int x; static void main() { x := 42; } }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_004():
    """Test class with string attribute"""
    source = """class Test { string name; static void main() { name := "Alice"; } }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_005():
    """Test final attribute declaration"""
    source = """class Constants { final float PI := 3.14159; static void main() {} }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_006():
    """Test if-else statement"""
    source = """class Test { 
        static void main() { 
            if (x > 0) then { 
                io.writeStrLn("positive"); 
            } else { 
                io.writeStrLn("negative"); 
            }
        }
    }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_007():
    """Test for loop with to keyword"""
    source = """class Test { 
        static void main() { 
            int i;
            for i := 1 to 10 do { 
                i := i + 1; 
            }
        }
    }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_008():
    """Test for loop with downto keyword"""
    source = """class Test { 
        static void main() { 
            int i;
            for i := 10 downto 1 do { 
                io.writeInt(i); 
            }
        }
    }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_009():
    """Test array declaration and access"""
    source = """class Test { 
        static void main() { 
            int[3] arr := {1, 2, 3};
            int first;
            first := arr[0];
            arr[1] := 42;
        }
    }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_010():
    """Test string concatenation and object creation"""
    source = """class Test { 
        static void main() { 
            string result;
            Test obj;
            result := "Hello" ^ " " ^ "World";
            obj := new Test();
        }
    }"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_011():
    """Test parser error: missing closing brace in class declaration"""
    source = """class Test { int x := 1; """  # Thiếu dấu }
    expected = "Error on line 1 col 25: <EOF>"
    assert Parser(source).parse() == expected

def test_012():
    """Example 1"""
    source = """
class Example1 {
    int factorial(int n){
        if n == 0 then return 1; else return n * this.factorial(n - 1);
    }

    void main(){
        int x;
        x := io.readInt();
        io.writeIntLn(this.factorial(x));
    }
}
""" 
    expected = "success"
    assert Parser(source).parse() == expected

def test_013():
    """Example 2"""
    source = """
class Shape {
    float length, width;
    float getArea() {}
    Shape(float length, width){
        this.length := length;
        this.width := width;
    }
}

class Rectangle extends Shape {
    float getArea(){
        return this.length * this.width;
    }
}

class Triangle extends Shape {
    float getArea(){
        return this.length * this.width / 2;
    }
}

class Example2 {
    void main(){
        Shape s;
        s := new Rectangle(3,4);
        io.writeFloatLn(s.getArea());
        s := new Triangle(3,4);
        io.writeFloatLn(s.getArea());
    }
}
""" 
    expected = "success"
    assert Parser(source).parse() == expected

def test_014():
    """Example 3"""
    source = """
class Rectangle {
    float length, width;
    static int count;
    
    ## Default constructor
    Rectangle() {
        this.length := 1.0;
        this.width := 1.0;
        Rectangle.count := Rectangle.count + 1;
    }
    
    ## Copy constructor
    Rectangle(Rectangle other) {
        this.length := other.length;
        this.width := other.width;
        Rectangle.count := Rectangle.count + 1;
    }
    
    ## User-defined constructor
    Rectangle(float length, width) {
        this.length := length;
        this.width := width;
        Rectangle.count := Rectangle.count + 1;
    }
    
    ## Destructor
    ~Rectangle() {
        Rectangle.count := Rectangle.count - 1;
        io.writeStrLn("Rectangle destroyed");
    }
    
    float getArea() {
        return this.length * this.width;
    }
    
    static int getCount() {
        return Rectangle.count;
    }
}

class Example3 {
    void main() {
        ## Using different constructors
        Rectangle r1 := new Rectangle();           ## Default constructor
        Rectangle r2 := new Rectangle(5.0, 3.0);  ## User-defined constructor
        Rectangle r3 := new Rectangle(r2);        ## Copy constructor
        
        io.writeFloatLn(r1.getArea());  ## 1.0
        io.writeFloatLn(r2.getArea());  ## 15.0
        io.writeFloatLn(r3.getArea());  ## 15.0
        io.writeIntLn(Rectangle.getCount());  ## 3
        
        ## Destructors will be called automatically when objects go out of scope
    }
}
""" 
    expected = "success"
    assert Parser(source).parse() == expected

def test_015():
    """Example 4"""
    source = """class MathUtils {
    static void swap(int & a; int & b) {
        int temp := a;
        a := b;
        b := temp;
    }
    
    static void modifyArray(int[5] & arr; int index; int value) {
        arr[index] := value;
    }
    
    static int & findMax(int[5] & arr) {
        int & max := arr[0];
        for i := 1 to 4 do {
            if (arr[i] > max) then {
                max := arr[i];
            }
        }
        return max;
    }
}

class StringBuilder {
    string & content;
    
    StringBuilder(string & content) {
        this.content := content;
    }
    
    StringBuilder & append(string & text) {
        this.content := this.content ^ text;
        return this;
    }
    
    StringBuilder & appendLine(string & text) {
        this.content := this.content ^ text ^ "\\n";
        return this;
    }
    
    string & toString() {
        return this.content;
    }
}

class Example4 {
    void main() {
        ## Reference variables
        int x := 10, y := 20;
        int & xRef := x;
        int & yRef := y;
        int[5] numbers := {1, 2, 3, 4, 5};
        int & maxRef := MathUtils.findMax(numbers);
        string text := "Hello";
        StringBuilder & builder := new StringBuilder(text);
        
        io.writeIntLn(xRef);  ## 10
        io.writeIntLn(yRef);  ## 20
        
        ## Pass by reference
        MathUtils.swap(x, y);
        io.writeIntLn(x);  ## 20
        io.writeIntLn(y);  ## 10
        
        ## Array references
        MathUtils.modifyArray(numbers, 2, 99);
        io.writeIntLn(numbers[2]);  ## 99
        
        ## Reference return
        maxRef := 100;
        io.writeIntLn(numbers[2]);  ## 100
        
        ## Method chaining with references
        builder.append(" ").append("World").appendLine("!");
        io.writeStrLn(builder.toString());  ## "Hello World!\\n"
    }
}
""" 
    expected = "success"
    assert Parser(source).parse() == expected
def test_016():
    source = """class VOTIEN {int[5] arr := {1+2};int cal(){## Array references
        int[5] numbers := {1, 2, 3, 4, 5};}}"""
    expected = "Error on line 1 col 30: +"
    assert Parser(source).parse() == expected
def test_025():
    source = """class VOTIEN {int arr := {1+2};}"""
    expected = "Error on line 1 col 27: +"
    assert Parser(source).parse() == expected
def test_037():
    source = """class A {int z := a.true.b;}"""
    expected = "Error on line 1 col 20: true"
    assert Parser(source).parse() == expected
def test_042():
    source = """class A {int z := (new a() + 1).foo(a, );}"""
    expected = "Error on line 1 col 39: )"
    assert Parser(source).parse() == expected
def test_044():
    source = """class A {int z := a[2+3] + a.f().c[b][2] + a[true + 1.0][a.a()][c] + a[a[2] >= 2];}"""
    expected = "success"
    assert Parser(source).parse() == expected
def test_045():
        source = """class A {int z := a[b].c;}"""
        expected = "success"
        assert Parser(source).parse() == expected
def test_048():
    source = """class A {int z := +-+--++a + +a - -a[2];}"""
    expected = "success"
    assert Parser(source).parse() == expected
def test_049():
        source = """class A {int z := !!nil + !a + !!!+-+-a;}"""
        expected = "success"
        assert Parser(source).parse() == expected
def test_050():
    source = """class A {int z := -!a;}"""
    expected = "Error on line 1 col 19: !"
    assert Parser(source).parse() == expected
def test_054():
    source = """class A {int z := 1.0 && true || this;}"""
    expected = "success"
    assert Parser(source).parse() == expected
def test_057():
    source = """class A {int z := 1.0 != a * 3 != c ;}"""
    expected = "Error on line 1 col 31: !="
    assert Parser(source).parse() == expected
def test_063():
    source = """class A {int z := a <= 2 > {a, b};}"""
    expected = "Error on line 1 col 25: >"
    assert Parser(source).parse() == expected
def test_065():
        source = """class A {int z := a == 2 > c == this;}"""
        expected = "success"
        assert Parser(source).parse() == expected
def test_073():
        source = """class B {
            final int a, b;
            static float a, b, c := 2;
            final boolean a := 1, b, c := 2;
            static string a := 1, b, c := 2;
            int& a := 2, c;
            int[2] a := 2;
            ID c := 1;
        }"""
        expected = "success"
        assert Parser(source).parse() == expected
def test_076():
        source = """class B {
        void a := 2;
        }"""
        expected = "Error on line 2 col 15: :="
        assert Parser(source).parse() == expected
def test_078():
    source = """class B {
        A& a := 2;
        int[3]& a ;
        A & & c;
    }"""
    expected = "Error on line 4 col 12: &"
    assert Parser(source).parse() == expected
def test_079():
        source = """class B {
            ID[2] a;
        }"""
        expected = "success"
        assert Parser(source).parse() == expected
def test_086():
    source = """class B {
        final void foo(){}
        }"""
    expected = "Error on line 2 col 14: void"
    assert Parser(source).parse() == expected
def test_084():
        source = """class B {
            final int a := 2;
            static int[2]& foo(){}
            void foo(int a, b; int& c){}
            static int a := 2;
            static void foo(int a, b){return 1;}
        }"""
        expected = "success"
        assert Parser(source).parse() == expected
def test_089():
    source = """class B {
        void foo(int a, int b){}
        }"""
    expected = "Error on line 2 col 24: int"
    assert Parser(source).parse() == expected
def test_099():
        source = """class B {
            void B(){
            int a := 2;
            }
        }"""
        expected = "success"
        assert Parser(source).parse() == expected
def test_100():
        source = """class B {
            void B(){
                a := 2;
                a.b[2] := 3 + 3 *4;
                this.a[2] := 3 + 3;
                a[2][a.fo()] := a.b.c();
            }
        }"""
        expected = "success"
        assert Parser(source).parse() == expected
def test_102():
        source = """class B {
            void B(){
            a[2].c := 1;
            }
        }"""
        expected = "success"
        assert Parser(source).parse() == expected
def test_301():
    source = """class B {
            void B(){
                int & x := nil;
            }
        }"""
    expected = "success"
    assert Parser(source).parse() == expected
def test_103():
    source = """class B {
            void B(){
                a.fo().c := 2;
                {2,3}.a := 2;
                a := 3;
                a[2+a[2]][3] := 2;
                this.a.c := 3;
            this := 2;
            }
        }"""
    expected = "Error on line 8 col 17: :="
    assert Parser(source).parse() == expected
def test_105():
    source = """class B {
            void B(){
                break;
                continue;
                return 2;
                a.foo(3, 4, a.foo());
                (new ID()).b.c.k(2, 3).foo();
            }
        }"""
    expected = "success"
    assert Parser(source).parse() == expected
def test_111():
    source = """class B {
            void B(){
            a.foo() := 2;
            }
        }"""
    expected = "success"
    assert Parser(source).parse() == expected
def test_123():
        source = """class B {
            void B(){
            {};
            }
        }"""
        expected = "Error on line 3 col 14: ;"
        assert Parser(source).parse() == expected
def test_160():
    source = """class A {
            int a;
            float b;
            string c;
            void foo(int x; float y) {
                a := x;
                b := y;
                c := "done";
            }
        }
        class B extends A {
            void bar() {
                this.foo(1, 2.0);
            }
        }"""
    expected = "success"
    assert Parser(source).parse() == expected
def test_185():
        source = """class A {
            void main() {
            while (x < ) {
                    x := x + 1;
                }
            }
        }"""
        expected = "Error on line 3 col 18: ("
        assert Parser(source).parse() == expected
def test_208():
        source = """
    class Main {
        void main() {
        writeStr();
        }
    }
    """
        expected = "Error on line 4 col 16: ("
        assert Parser(source).parse() == expected
def test_223():
        source = """
    class Main {
        final static int a;
        static final int b;
    }
    """
        expected = "success"
        assert Parser(source).parse() == expected
def test_224():
    source = """
    class Main {
    static static int a;
    }
    """
    expected = "Error on line 3 col 11: static"
    assert Parser(source).parse() == expected
def test_227():
        source = """
    class Main {
        void main() {
            final int a := 2;
            final int a, b;
        }
    }
    """
        expected = "success"
        assert Parser(source).parse() == expected
def test_233():
    source = """
    class Main {
        void main() {
            a := 2;
        int a := 2;
        }
    }
    """
    expected = "Error on line 5 col 8: int"
    assert Parser(source).parse() == expected

def test_234():
    source = """
    class Main {
        void main() {
        int[5] a := {3,5,5,6,{8}};
        }
    }
    """
    expected = "Error on line 4 col 29: {"
    assert Parser(source).parse() == expected

def test_235():
    source = """
    class Main {
        void main() {
            a[5].getInstance().a := 5;
        }
    }
    """
    expected = "success"
    assert Parser(source).parse() == expected

def test_236():
    source = """
    class TestClass {
        void main() {
            int x := 5;
            x := x + getValue();
            arr[x] := process(x, getValue());
            obj.method(arr[x], x + 1);
            if (x > threshold) then
                break;
            else
                continue;
        }
    }
    """
    expected = "Error on line 5 col 29: ("
    assert Parser(source).parse() == expected

def test_expr_relational():
    """Test relational expressions"""
    source = """class Test { 
        static void main() {
            a.b.c.method()[5].hello() := real.f().hello()[a.hello.world() + arr[7*2+1]].f(7);
        } 
    }"""
    expected = "success"
    assert Parser(source).parse() == expected