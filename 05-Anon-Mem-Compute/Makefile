all: testcase.out 

testcase.out: testcase.c
	clang $< -o $@ -Wno-return-type


clean:
	rm -f testcase.out 
