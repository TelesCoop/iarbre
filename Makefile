# Makefile for building documentation with MkDocs

# Default variables
MKDOCS = mkdocs
DOCS_DIR = docs
BUILD_DIR = site

.PHONY: all build serve clean

# Default target
all: build

# Build the documentation
build:
	$(MKDOCS) build --clean

# Serve the documentation locally
serve:
	$(MKDOCS) serve

# Clean the generated site
clean:
	$(MKDOCS) clean
	@rm -rf $(BUILD_DIR)

# Initialize MkDocs if not already initialized
init:
	$(MKDOCS) new .

# Validate the mkdocs.yml configuration
validate:
	$(MKDOCS) build --strict --verbose
