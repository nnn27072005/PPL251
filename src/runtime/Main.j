.source Main.java
.class public Main
.super java/lang/Object

.method public static main([Ljava/lang/String;)V
Label0:
.var 1 is arr [I from Label0 to Label1
	iconst_4
	newarray int
	dup
	iconst_0
	bipush 11
	iastore
	dup
	iconst_1
	bipush 22
	iastore
	dup
	iconst_2
	bipush 33
	iastore
	dup
	iconst_3
	bipush 44
	iastore
	astore_1
.var 2 is a I from Label0 to Label1
	iconst_0
	istore_2
.var 3 is b I from Label0 to Label1
	iconst_0
	istore_3
.var 4 is c I from Label0 to Label1
	iconst_0
	istore 4
.var 5 is d I from Label0 to Label1
	iconst_0
	istore 5
	aload_1
	iconst_0
	iaload
	istore_2
	aload_1
	iconst_1
	iaload
	istore_3
	aload_1
	iconst_2
	iaload
	istore 4
	aload_1
	iconst_3
	iaload
	istore 5
	iload_2
	invokestatic io/writeInt(I)V
	iload_3
	invokestatic io/writeInt(I)V
	iload 4
	invokestatic io/writeInt(I)V
	iload 5
	invokestatic io/writeInt(I)V
Label1:
	return
.limit stack 5
.limit locals 6
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
