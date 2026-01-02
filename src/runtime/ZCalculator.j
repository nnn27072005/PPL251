.source ZCalculator.java
.class public ZCalculator
.super java/lang/Object

.method public static compute(I)I
.var 0 is x I from Label0 to Label1
Label0:
.var 1 is result I from Label0 to Label1
	iconst_0
	istore_1
.var 2 is i I from Label0 to Label1
	iconst_0
	istore_2
	iconst_1
	istore_2
Label4:
	iload_2
	iload_0
	if_icmpgt Label3
	iload_2
	iconst_2
	irem
	iconst_0
	if_icmpne Label7
	iconst_1
	goto Label8
Label7:
	iconst_0
Label8:
	ifle Label5
	iload_1
	iload_2
	iadd
	istore_1
	goto Label6
Label5:
Label6:
Label2:
	iload_2
	iconst_1
	iadd
	istore_2
	goto Label4
Label3:
	iload_1
	ireturn
Label1:
	iconst_0
	ireturn
.limit stack 9
.limit locals 3
.end method

.method public <init>()V
Label0:
	aload_0
	invokespecial java/lang/Object/<init>()V
	return
Label1:
.limit stack 1
.limit locals 1
.end method
