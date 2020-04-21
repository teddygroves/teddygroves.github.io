.PHONY: clean

FIGURES = $(shell find img/ -type f -name '*.png')
POSTS_ORG := $(shell find posts_org/ -type f -name '*.org')
POSTS_HTML := $(POSTS_ORG:posts_org/%.org=posts_html/%.html)

PANDOCFLAGS =                          \
  --from=org                           \
  --highlight-style=pygments           \
  --bibliography=bibliography.bib      \
  --mathml                             

all: index.html

posts_html:
	mkdir posts_html

posts_html/%.html: posts_org/%.org $(FIGURES) Makefile posts_html
	pandoc -s $< -o $@ --css=../style.css $(PANDOCFLAGS)

index.html: index.org $(POSTS_HTML)
	pandoc -s $< -o $@ --css=style.css $(PANDOCFLAGS)

clean:
	rm -Rf posts_html
