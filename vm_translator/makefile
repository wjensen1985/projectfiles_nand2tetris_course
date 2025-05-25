# # give VMTranslator.py execute permission
# SCRIPT = VMTranslator.py

# .PHONY: all chmod_script

# all: chmod_script

# chmod_script:
# 	chmod +x $(SCRIPT)


# # find all .vm files in current directory
# INPUTS := $(wildcard *.vm)

# # create corresponding .asm files
# OUTPUTS := $(INPUTS:.vm=.asm)

# # default target
# all: $(OUTPUTS)

# # rule to process each .vm ie call VMTranslator.py on each
# %.asm: %.vm
# 	python3 VMTranslator.py $<

# # Clean target
# clean:
# 	rm -f *.asm


SCRIPT = VMTranslator.py
WRAPPER = VMTranslator

.PHONY: all clean

# default target
all: $(WRAPPER) $(OUTPUTS)

# find all .vm files in current directory
INPUTS := $(wildcard *.vm)
OUTPUTS := $(INPUTS:.vm=.asm)

# create corresponding .asm files
%.asm: %.vm
	./$(WRAPPER) $<

# Create a wrapper script to run the Python file like an alias
$(WRAPPER): $(SCRIPT)
	echo '#!/bin/bash' > $(WRAPPER)
	echo 'python3 $(SCRIPT) "$$@"' >> $(WRAPPER)
	chmod +x $(WRAPPER)

# Clean target
clean:
	rm -f *.asm $(WRAPPER)
