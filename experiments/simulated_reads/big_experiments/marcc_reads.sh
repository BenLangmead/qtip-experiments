#!/bin/sh

AMT=50M
MEM="256G"
PARTITION=lrgmem
NHOURS=16

for PAIRED in 0 1 ; do
for LEN in 100 250 ; do

if [ "$PAIRED" == "1" ] ; then
for REP in 1 2 3 4 5 ; do
cat >.mason_reads_${PAIRED}_${REP}_${LEN}.sh <<EOF
#!/bin/bash -l
#SBATCH
#SBATCH --nodes=1
#SBATCH --mem=${MEM}
#SBATCH --partition=${PARTITION}
#SBATCH --time=${NHOURS}:00:00
make r${PAIRED}_mason_ill_${LEN}_${REP}_${AMT}.fq.gz
EOF
echo "sbatch .mason_reads_${PAIRED}_${REP}_${LEN}.sh"
done
else
cat >.mason_reads_${PAIRED}_${LEN}.sh <<EOF
#!/bin/bash -l
#SBATCH
#SBATCH --nodes=1
#SBATCH --mem=${MEM}
#SBATCH --partition=${PARTITION}
#SBATCH --time=${NHOURS}:00:00
make r${PAIRED}_mason_ill_${LEN}_${AMT}.fq.gz
EOF
echo "sbatch .mason_reads_${PAIRED}_${LEN}.sh"
fi

done
done
