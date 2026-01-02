.source Simple.java
.class public Simple
.super java/lang/Object
.field num I

.method public <init>()V
.var 0 is this LSimple; from Label0 to Label1
Label0:
	aload_0
	invokespecial java/lang/Object/<init>()V
	bipush 123
	aload_0
	swap
	putfield Simple/num I
	return
Label1:
.limit stack 2
.limit locals 1
.end method
