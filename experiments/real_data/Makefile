BWA_HOME=$(QTIP_EXPERIMENTS_HOME)/software/bwa
SNAP_HOME=$(QTIP_EXPERIMENTS_HOME)/software/snap
BT2_HOME=$(QTIP_EXPERIMENTS_HOME)/software/bowtie2
INDEXES=$(QTIP_EXPERIMENTS_HOME)/experiments/refs
HG_FA=$(INDEXES)/hg38.fa
PYTHON=python -O
QTIP=$(QTIP_HOME)/qtip

BT2_QTIP_ARGS=--aligner bowtie2 --bt2-exe $(BT2_HOME)/bowtie2 --index $(HG_FA)
BT2_ARGS=
BT2_PAIR_ARGS=-X 750
BWA_QTIP_ARGS=--aligner bwa-mem --bwa-exe $(BWA_HOME)/bwa --index $(HG_FA)
BWA_ARGS=
BWA_PAIR_ARGS=
SNAP_QTIP_ARGS=--aligner snap --snap-exe $(SNAP_HOME)/snap-aligner --index $(HG_FA).snap
SNAP_ARGS=
SNAP_PAIR_ARGS=

NTHREADS=1
NTHREADS_VS=16

$(shell mkdir -p temp)
ARGS=--ref $(HG_FA) --write-orig-mapq --write-precise-mapq --seed 346 --temp-directory temp
EXTRA_ARGS=

#
# These CSV files contain the ultimate output from multi_aligner.py when
# analyzing SAMs from various aligners (bt2 --very-sensitive,
# bt2 --very-sensitive-local, bwa-mem, bt2 --sensitive, and SNAP).
#

.PHONY: all
all: ERR050082_1.unp.csv ERR050082_1.pair.csv \
     ERR050083_1.unp.csv ERR050083_1.pair.csv

.PHONY: all_new
all_new: new_ERR050082_1.unp.csv ERR050083_1.unp.csv

%.unp.csv: %.bt2vs.unp.sam %.bt2vsl.unp.sam %.bwa.unp.sam %.bt2.unp.sam %.snap.unp.sam
	pypy multi_aligner.py \
	    --sam $^ \
	    --prefix $(<:bt2vs.unp.sam=) \
	    --suffix ".unp" \
	    --name bt2vs bt2vsl bwamem-qtip bt2-qtip snap-qtip \
	    --tier 1 1 2 2 2 > $@

%.pair.csv: %.bt2vs.pair.sam %.bt2vsl.pair.sam %.bwa.pair.sam %.bt2.pair.sam %.snap.pair.sam
	pypy multi_aligner.py \
	    --sam $^ \
	    --prefix $(<:bt2vs.pair.sam=) \
	    --suffix ".pair" \
	    --name bt2vs bt2vsl bwamem-qtip bt2-qtip snap-qtip \
	    --tier 1 1 2 2 2 > $@

# #######
# BWA-MEM
# #######

new_%.bwa.unp.sam: new_%.fastq
	$(PYTHON) $(QTIP) \
		$(BWA_QTIP_ARGS) $(ARGS) $(EXTRA_ARGS) \
		--U $< \
		--keep-intermediates \
		--write-orig-mapq \
		--write-precise-mapq \
		--keep-ztz \
		--assess-accuracy \
		--predict-for-training \
		--output-directory $@ \
		--trials 10 \
		--skip-rewrite \
		-- -t $(NTHREADS_VS) $(BWA_ARGS)

%.bwa.unp.sam: %.fastq
	$(PYTHON) $(QTIP) \
		$(BWA_QTIP_ARGS) $(ARGS) $(EXTRA_ARGS) \
		--U $< \
		--vanilla-output $@ \
		-- -t $(NTHREADS) $(BWA_ARGS)

%.ext_bwa.unp.sam: %.fastq
	$(PYTHON) $(QTIP) \
		$(BWA_QTIP_ARGS) $(ARGS) $(EXTRA_ARGS) \
		--U $< \
		--keep-intermediates \
		--write-orig-mapq \
		--write-precise-mapq \
		--keep-ztz \
		--assess-accuracy \
		--predict-for-training \
		--output-directory $@ \
		-- -t $(NTHREADS_VS) $(BWA_ARGS)

%.bwa.pair.sam: %.fastq
	$(PYTHON) $(QTIP) \
		$(BWA_QTIP_ARGS) $(ARGS) $(EXTRA_ARGS) \
		--m1 $< \
		--m2 $(<:_1.fastq=_2.fastq) \
		--vanilla-output $@ \
		-- -t $(NTHREADS) $(BWA_ARGS) $(BWA_PAIR_ARGS)

# #######
# Bowtie2
# #######

new_%.bt2.unp.sam: new_%.fastq
	$(PYTHON) $(QTIP) \
		$(BT2_QTIP_ARGS) $(ARGS) $(EXTRA_ARGS) \
		--U $< \
		--keep-intermediates \
		--write-orig-mapq \
		--write-precise-mapq \
		--keep-ztz \
		--assess-accuracy \
		--predict-for-training \
		--output-directory $@ \
		--trials 10 \
		--skip-rewrite \
		-- -p $(NTHREADS) $(BT2_ARGS)

%.bt2.unp.sam: %.fastq
	$(PYTHON) $(QTIP) \
		$(BT2_QTIP_ARGS) $(ARGS) $(EXTRA_ARGS) \
		--U $< \
		--vanilla-output $@ \
		-- -p $(NTHREADS) $(BT2_ARGS)

%.bt2.pair.sam: %.fastq
	$(PYTHON) $(QTIP) \
		$(BT2_QTIP_ARGS) $(ARGS) $(EXTRA_ARGS) \
		--m1 $< \
		--m2 $(<:_1.fastq=_2.fastq) \
		--vanilla-output $@ \
		-- -p $(NTHREADS) $(BT2_ARGS) $(BT2_PAIR_ARGS)

# #######
# SNAP
# #######

new_%.snap.unp.sam: new_%.fastq
	$(PYTHON) $(QTIP) \
		$(SNAP_QTIP_ARGS) $(ARGS) $(EXTRA_ARGS) \
		--U $< \
		--keep-intermediates \
		--write-orig-mapq \
		--write-precise-mapq \
		--keep-ztz \
		--assess-accuracy \
		--predict-for-training \
		--output-directory $@ \
		--trials 10 \
		--skip-rewrite \
		-- -t $(NTHREADS) $(SNAP_ARGS)

%.snap.unp.sam: %.fastq
	$(PYTHON) $(QTIP) \
		$(SNAP_QTIP_ARGS) $(ARGS) $(EXTRA_ARGS) \
		--U $< \
		--vanilla-output $@ \
		-- -t $(NTHREADS) $(SNAP_ARGS)

%.snap.pair.sam: %.fastq
	$(PYTHON) $(QTIP) \
		$(SNAP_QTIP_ARGS) $(ARGS) $(EXTRA_ARGS) \
		--m1 $< \
		--m2 $(<:_1.fastq=_2.fastq) \
		--vanilla-output $@ \
		-- -t $(NTHREADS) $(SNAP_ARGS) $(SNAP_PAIR_ARGS)

# ###############
# Extra sensitive
# ###############

%.bt2vs.unp.sam: %.fastq
	$(BT2_HOME)/bowtie2 \
		-x $(INDEXES)/hg38.fa \
		-p $(NTHREADS_VS) \
		-U $< \
		--very-sensitive \
		$(BT2_ARGS) \
		-S $@

%.bt2vs.pair.sam: %.fastq
	$(BT2_HOME)/bowtie2 \
		-x $(INDEXES)/hg38.fa \
		-p $(NTHREADS_VS) \
		-1 $< -2 $(<:_1.fastq=_2.fastq) \
		--very-sensitive \
		$(BT2_ARGS) \
		$(BT2_PAIR_ARGS) \
		-S $@

# #####################
# Extra sensitive local
# #####################

%.bt2vsl.unp.sam: %.fastq
	$(BT2_HOME)/bowtie2 \
		-x $(HG_FA) \
		-p $(NTHREADS_VS) \
		-U $< \
		--very-sensitive-local \
		$(BT2_ARGS) \
		-S $@

%.bt2vsl.pair.sam: %.fastq
	$(BT2_HOME)/bowtie2 \
		-x $(HG_FA) \
		-p $(NTHREADS_VS) \
		-1 $< -2 $(<:_1.fastq=_2.fastq) \
		--very-sensitive-local \
		$(BT2_ARGS) \
		$(BT2_PAIR_ARGS) \
		-S $@
