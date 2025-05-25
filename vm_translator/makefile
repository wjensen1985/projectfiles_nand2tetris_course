# find all .vm files in current directory
INPUTS := $(wildcard *.vm)

# create corresponding .asm files
OUTPUTS := $(INPUTS:.vm=.asm)

# default target
all: $(OUTPUTS)

# rule to process each .vm ie call VMTranslator.py on each
%.asm: %.vm
	python3 VMTranslator.py $<

# Clean target
clean:
	rm -f *.asm