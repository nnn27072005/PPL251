.source Main.java
.class public Main
.super java/lang/Object

.method public static main([Ljava/lang/String;)V
Label0:
	iconst_1
	ifgt Label4
	iconst_1
	iconst_0
	idiv
	iconst_0
	if_icmpne Label6
	iconst_1
	goto Label7
Label6:
	iconst_0
Label7:
	goto Label5
Label4:
	iconst_1
Label5:
	ifle Label2
	ldc "Safe"
	invokestatic io/writeStr(Ljava/lang/String;)V
	goto Label3
Label2:
	ldc "Crash"
	invokestatic io/writeStr(Ljava/lang/String;)V
Label3:
Label1:
	return
.limit stack 7
.limit locals 1
.end method
