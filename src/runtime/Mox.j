.source Mox.java
.class public Mox
.super java/lang/Object
.field count I

.method public <init>()V
.var 0 is this LMox; from Label0 to Label1
Label0:
	aload_0
	invokespecial java/lang/Object/<init>()V
	iconst_0
	aload_0
	swap
	putfield Mox/count I
	return
Label1:
.limit stack 2
.limit locals 1
.end method

.method public increment()V
.var 0 is this LMox; from Label0 to Label1
Label0:
	aload_0
	getfield Mox/count I
	iconst_1
	iadd
	aload_0
	swap
	putfield Mox/count I
Label1:
	return
.limit stack 2
.limit locals 1
.end method

.method public getCount()I
.var 0 is this LMox; from Label0 to Label1
Label0:
	aload_0
	getfield Mox/count I
	ireturn
Label1:
	iconst_0
	ireturn
.limit stack 1
.limit locals 1
.end method
