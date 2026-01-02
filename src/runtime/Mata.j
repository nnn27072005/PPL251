.source Mata.java
.class public Mata
.super java/lang/Object
.field value I

.method public setValue(I)V
.var 0 is this LMata; from Label0 to Label1
.var 1 is value I from Label0 to Label1
Label0:
	iload_1
	aload_0
	swap
	putfield Mata/value I
Label1:
	return
.limit stack 2
.limit locals 2
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
