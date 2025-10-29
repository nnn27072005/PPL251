from utils import Tokenizer


def test_001():
    """Test basic identifier tokenization"""
    source = "abc"
    expected = "abc,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_002():
    """Test keywords recognition"""
    source = "class extends static final if else for do then to downto new this void boolean int float string true false nil break continue return"
    expected = "class,extends,static,final,if,else,for,do,then,to,downto,new,this,void,boolean,int,float,string,true,false,nil,break,continue,return,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_003():
    """Test integer literals"""
    source = "42 0 255 2500"
    expected = "42,0,255,2500,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_004():
    """Test float literals"""
    source = "9.0 12e8 1. 0.33E-3 128e+42"
    expected = "9.0,12e8,1.,0.33E-3,128e+42,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_005():
    """Test boolean literals"""
    source = "true false"
    expected = "true,false,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_006():
    """Test unclosed string literal error"""
    source = '"Hello World'
    expected = "Unclosed String: Hello World"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_007():
    """Test illegal escape sequence error"""
    source = '"Hello \\x World"'
    expected = "Illegal Escape In String: Hello \\x"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_008():
    """Test error character (non-ASCII or invalid character)"""
    source = "int x := 5; @ invalid"
    expected = "int,x,:=,5,;,Error Token @"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_009():
    """Test valid string literals with escape sequences"""
    source = '"This is a string containing tab \\t" "He asked me: \\"Where is John?\\""'
    expected = "This is a string containing tab \\t,He asked me: \\\"Where is John?\\\",EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_010():
    """Test string literals return content without quotes"""
    source = '"Hello World"'
    expected = "Hello World,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_011():
    """Test empty string literal"""
    source = '""'
    expected = ",EOF"  # Empty string content
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_012():
    """Test operators and separators"""
    source = "+ - * / \\ % == != < <= > >= && || ! := ^ new . ( ) [ ] { } , ; :"
    expected = "+,-,*,/,\\,%,==,!=,<,<=,>,>=,&&,||,!,:=,^,new,.,(,),[,],{,},,,;,:,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_013():
    """Identifier starting with underscore"""
    source = "_var"
    expected = "_var,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_014():
    source = "-42"
    expected = "-,42,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_015():
    source = "+99"
    expected = "+,99,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_016():
    source = "000123"
    expected = "000123,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_017():
    source = ".5"
    expected = ".,5,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_018():
    source = "1_000"
    expected = "1,_000,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_019():
    source = "1000000000000000000000000"
    expected = "1000000000000000000000000,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_020():
    source = "-0"
    expected = "-,0,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_021():
    source = '""'
    expected = ",EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_022():
    source = '"Line1\\nLine2"'
    expected = "Line1\\nLine2,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_023():
    source = '"Tab\\tSeparated"'
    expected = "Tab\\tSeparated,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_024():
    source = '"Quote: \\\"Inside\\\""'
    expected = "Quote: \\\"Inside\\\",EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_025():
    source = '"Backslash: \\\\"'
    expected = "Backslash: \\\\,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_026():
    source = '"Hello'
    expected = "Unclosed String: Hello"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_027():
    source = '"Hello \\x World"'
    expected = "Illegal Escape In String: Hello \\x"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_028():
    source = '"Hello\\nWorld"'
    expected = "Hello\\nWorld,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_029():
    source = '"Line with newline\\ninside"'
    expected = "Line with newline\\ninside,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected


def test_030():
    source = """class TestClass {
            void main() {
                return;
            }
    }"""
    expected = "class,TestClass,{,void,main,(,),{,return,;,},},EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_031():
    """Empty input should only return EOF"""
    source = ""
    expected = "EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_032():
    """Identifier with digits inside"""
    source = "abc123"
    expected = "abc123,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_033():
    """Identifier with multiple underscores"""
    source = "__my_var__1"
    expected = "__my_var__1,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_034():
    """Case sensitivity of keywords"""
    source = "Class CLASS class"
    expected = "Class,CLASS,class,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_035():
    """Multiple keywords mixed with identifiers"""
    source = "intX floatValue stringY booleanFlag"
    expected = "intX,floatValue,stringY,booleanFlag,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_036():
    """Valid integer literal large number"""
    source = "999999999999"
    expected = "999999999999,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_037():
    """Float without decimal part but with exponent"""
    source = "12e10"
    expected = "12e10,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_038():
    """Float with decimal but no exponent"""
    source = "3.14159"
    expected = "3.14159,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_039():
    """Float with exponent and decimal"""
    source = "6.02e23"
    expected = "6.02e23,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_040():
    """Invalid float literal (.12)"""
    source = ".12"
    expected = ".,12,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_041():
    """Invalid float literal (143e)"""
    source = "143e"
    expected = "143,e,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_042():
    """Boolean literals mixed"""
    source = "true false true"
    expected = "true,false,true,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_043():
    """String with escape newline"""
    source = '"Line1\\nLine2"'
    expected = "Line1\\nLine2,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_044():
    """String with escaped quote"""
    source = '"He said: \\"Hello\\""'
    expected = "He said: \\\"Hello\\\",EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_045():
    """String with backslash"""
    source = '"C:\\\\path"'
    expected = "C:\\\\path,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_046():
    """Illegal escape inside string"""
    source = '"abc\\y"'
    expected = "Illegal Escape In String: abc\\y"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_047():
    """Unclosed string literal at EOF"""
    source = '"unterminated'
    expected = "Unclosed String: unterminated"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_048():
    """Unclosed string literal with newline"""
    source = '"Hello\nWorld"'
    expected = "Unclosed String: Hello\n"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_049():
    """Array literal of ints"""
    source = "{1,2,3}"
    expected = "{,1,,,2,,,3,},EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_050():
    """Array literal of floats"""
    source = "{1.1,2.2,3.3}"
    expected = "{,1.1,,,2.2,,,3.3,},EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_051():
    """Operators sequence"""
    source = "++--**//\\%"
    expected = "+,+,-,-,*,*,/,/,\\,%,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_052():
    """Comparison operators"""
    source = "== != < <= > >="
    expected = "==,!=,<,<=,>,>=,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_053():
    """Logical operators"""
    source = "&& || !"
    expected = "&&,||,!,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_054():
    """Assignment operators"""
    source = ":="
    expected = ":=,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_055():
    """Concatenation operator"""
    source = '"abc" ^ "def"'
    expected = "abc,^,def,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_056():
    """Dot and method call tokens"""
    source = "obj.method()"
    expected = "obj,.,method,(,),EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_057():
    """Square brackets indexing"""
    source = "arr[10]"
    expected = "arr,[,10,],EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_058():
    """Curly braces block"""
    source = "{ int x; }"
    expected = "{,int,x,;,},EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_059():
    """Colon and semicolon"""
    source = ": ;"
    expected = ":,;,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_060():
    """Line comment should be skipped"""
    source = "int x; # this is a comment"
    expected = "int,x,;,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_061():
    """Block comment should be skipped"""
    source = "int y; /* comment inside */ float z;"
    expected = "int,y,;,float,z,;,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_062():
    """Nested comment not allowed"""
    source = "/* outer /* inner */ still */"
    expected = "still,*,/,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_063():
    """Unexpected character $"""
    source = "int $a;"
    expected = "int,Error Token $"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_064():
    """Unicode character not allowed"""
    source = "π"
    expected = "Error Token π"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_065():
    """Multiple statements"""
    source = "int x; float y;"
    expected = "int,x,;,float,y,;,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_066():
    """Chained member access"""
    source = "a.b.c.d"
    expected = "a,.,b,.,c,.,d,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_067():
    """New object creation"""
    source = "new Rectangle(3,4)"
    expected = "new,Rectangle,(,3,,,4,),EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_068():
    """Destructor symbol"""
    source = "~Rectangle()"
    expected = "~,Rectangle,(,),EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_069():
    """Reference symbol &"""
    source = "int & ref := x;"
    expected = "int,&,ref,:=,x,;,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_070():
    """Nil literal"""
    source = "nil"
    expected = "nil,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_071():
    """This keyword"""
    source = "this"
    expected = "this,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_072():
    """Main method declaration"""
    source = "void main() { return; }"
    expected = "void,main,(,),{,return,;,},EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_073():
    """Final and static attribute"""
    source = "static final int x := 5;"
    expected = "static,final,int,x,:=,5,;,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_074():
    """Float with exponent and sign"""
    source = "1.23e-10"
    expected = "1.23e-10,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_075():
    source = "12e+"
    expected = "12,e,+,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_076():
    """Empty array literal"""
    source = "{}"
    expected = "{,},EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_077():
    """Array literal of booleans"""
    source = "{true,false,true}"
    expected = "{,true,,,false,,,true,},EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_078():
    """String concatenation expression"""
    source = '"Hello" ^ "World"'
    expected = "Hello,^,World,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_079():
    """Complex expression"""
    source = "(a + b) * c[2].foo(3)"
    expected = "(,a,+,b,),*,c,[,2,],.,foo,(,3,),EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_080():
    """Break and continue"""
    source = "break; continue;"
    expected = "break,;,continue,;,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_081():
    """For loop structure"""
    source = "for i := 1 to 10 do x := x + 1;"
    expected = "for,i,:=,1,to,10,do,x,:=,x,+,1,;,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_082():
    """If statement"""
    source = "if x < 10 then return x; else return 0;"
    expected = "if,x,<,10,then,return,x,;,else,return,0,;,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_083():
    source = "1.2.3"
    expected = "1.2,.,3,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_084():
    source = "-3.14"
    expected = "-,3.14,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_085():
    """Plus sign float literal as tokens"""
    source = "+2.71"
    expected = "+,2.71,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_086():
    """Invalid escape inside string"""
    source = '"abc\\q"'
    expected = "Illegal Escape In String: abc\\q"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_087():
    """String with formfeed escape"""
    source = '"Line\\fBreak"'
    expected = "Line\\fBreak,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_088():
    """String with carriage return escape"""
    source = '"Line\\rEnd"'
    expected = "Line\\rEnd,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_089():
    """Nested method calls"""
    source = "obj.foo(bar.baz(1,2))"
    expected = "obj,.,foo,(,bar,.,baz,(,1,,,2,),),EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_090():
    """Class with inheritance header tokens"""
    source = "class Rectangle extends Shape { }"
    expected = "class,Rectangle,extends,Shape,{,},EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_091():
    """Nil usage in assignment"""
    source = "MyClass obj := nil;"
    expected = "MyClass,obj,:=,nil,;,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_092():
    """Static method invocation"""
    source = "IO.writeInt(5);"
    expected = "IO,.,writeInt,(,5,),;,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_093():
    """Reference parameter declaration"""
    source = "void swap(int & a; int & b) { }"
    expected = "void,swap,(,int,&,a,;,int,&,b,),{,},EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_094():
    """Multiple variables declared"""
    source = "int a, b, c := 5;"
    expected = "int,a,,,b,,,c,:=,5,;,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_095():
    """Complex boolean expression"""
    source = "if (a && b) || !c then return;"
    expected = "if,(,a,&&,b,),||,!,c,then,return,;,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_096():
    """Error token at end"""
    source = "int x; $"
    expected = "int,x,;,Error Token $"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_097():
    """Escaped double quote string"""
    source = '"She said: \\"Hi\\""'
    expected = "She said: \\\"Hi\\\",EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_098():
    """String with tab escape"""
    source = '"Column1\\tColumn2"'
    expected = "Column1\\tColumn2,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_099():
    """Reference assignment"""
    source = "int & ref := x;"
    expected = "int,&,ref,:=,x,;,EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected

def test_100():
    """Complex program header"""
    source = "class Program { static void main() { return; } }"
    expected = "class,Program,{,static,void,main,(,),{,return,;,},},EOF"
    assert Tokenizer(source).get_tokens_as_string() == expected
