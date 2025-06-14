# Makefile ─ build pipeline for turning a public ChatGPT *Share* link into
# ≤ 20 Markdown container files that can be uploaded to a Custom GPT.
#
# Required environment variable
#   DEEP_RESEARCH_URL  – the public share URL, e.g.
#                        https://chat.openai.com/share/abc123
# Optional variables (may be overridden on command‑line or as env vars)
#   SLUG = deep_research    # used in chunk headers & filenames
#   OUT  = containers       # output directory for generated .md files
#
# Example usage ─ in your shell:
#   export DEEP_RESEARCH_URL=https://chat.openai.com/share/abc123
#   make containers                # produces ./containers/*.md
#
#   # Override defaults on the fly
#   make containers SLUG=humana OUT=humana_files
#
# Targets
#   containers – run share2containers.py with the chosen parameters
#   clean      – remove the output directory

# ---------------- configurable variables ----------------
SLUG ?= deep_research
OUT  ?= containers
# --------------------------------------------------------

ifndef DEEP_RESEARCH_URL
$(error DEEP_RESEARCH_URL environment variable not set. Export it before running make)
endif

.PHONY: containers clean

containers:
	@echo "Installing required Python packages..."
	@pip install --upgrade pip
	@pip install tiktoken html2text
	@echo "Using DEEP_RESEARCH_URL: $(DEEP_RESEARCH_URL)"
	@echo "Using SLUG: $(SLUG)"
	@echo "Output directory: $(OUT)"
	@echo "Running share2containers.py to generate Markdown files..."
	@mkdir -p $(OUT)
	@echo "Generating containers in $(OUT) for share URL: $(DEEP_RESEARCH_URL)"
	@echo "Using slug: $(SLUG)"
	@echo "Output will be saved in: $(OUT)"
	@echo "Running the script..."
	python src/share2containers.py \
	    --url  "$(DEEP_RESEARCH_URL)" \
	    --slug $(SLUG) \
	    --out  $(OUT)

clean:
	rm -rf $(OUT)

install-tiktoken:

