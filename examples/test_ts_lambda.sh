#!/bin/sh

BT2_HOME=$HOME/git/bowtie2/bowtie2

REF=$BT2_HOME/example/reference/lambda_virus.fa
IDX=$BT2_HOME/example/index/lambda_virus

UNP_IN=$BT2_HOME/example/reads/reads_1.fq

SAM_OUT=test_ts.sam

python ../bin/ts.py \
	--ref $REF \
	--U $UNP_IN \
	--S $SAM_OUT \
	--fastq \
	--scoring "1,2,6,1,5,3,5,3" \
	--num-reads 100 \
	--bt2-exe $BT2_HOME/bowtie2 \
	--bt2-args "-x $IDX"