.source ZAnimal.java
.class public ZAnimal
.super java/lang/Object

.method public speak()Ljava/lang/String;
.var 0 is this LZAnimal; from Label0 to Label1
Label0:
	ldc "Some sound"
	areturn
Label1:
	aconst_null
	areturn
.limit stack 1
.limit locals 1
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
