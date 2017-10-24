loop1:
	add   $s0, $s1, $s2
	beq   $t0, $t1, loop1
loop2:
	nor   $s6, $s7, $v0
loop3:
	sub   $s3, $s4, $s5
	bne   $t2, $t3, loop2
