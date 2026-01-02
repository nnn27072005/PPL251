.source ZCat.java
.class public ZCat
.super ZAnimal

.method public speak()Ljava/lang/String;
.var 0 is this LZCat; from Label0 to Label1
Label0:
	ldc "Meow"
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
