#!gmake

NM=freebayes
USER=ekg
VER=1.1.0

.PHONY: all
all: $(NM)

$(NM): $(NM)-git/bin/freebayes
	ln -s -f $< $@

$(NM)-git/bin/freebayes: $(NM)-git
	$(MAKE) -C $<

$(NM)-git:
	git clone -b v$(VER) --recursive https://github.com/$(USER)/$(NM).git $@

.PHONY: clean
clean:
	rm -rf $(NM)-git $(NM)
