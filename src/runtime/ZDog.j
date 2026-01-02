.source ZDog.java
.class public ZDog
.super ZAnimal

.method public speak()Ljava/lang/String;
.var 0 is this LZDog; from Label0 to Label1
Label0:
	ldc "Woof"
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
	invokespecial ZAnimal/<init>()V
	return
Label1:
.limit stack 1
.limit locals 1
.end method
