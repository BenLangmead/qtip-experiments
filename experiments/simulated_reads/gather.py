#!/usr/bin/env python

"""
Gathers results from simulation experiments.  Run this from the
simulated_reads subdirectory of the qsim-experiments repo.  It descends into
the various experimental subdirectories and parses the Makefiles it finds.

Outputs:
 - "overall.csv" with one big table of summary measures
 - "summary" subdirectory with lots of raw results compiled into a directory
   structure
   + Subdirectories correspond to simulation experiments and contain:
     - for each sampling rate:
       + for each trial:
         - featimport_*.csv -- feature importances for each alignment type
         - params.csv -- feature importances for each model
         - Subdirectories for training/test, each with:
           + roc.csv -- ROC table
           + summary.csv -- summarizes data, model fit
"""

from __future__ import print_function
import sys
import os
import re
import glob
import logging
from os.path import join

# We identify the experiments by fishing through the Makefiles for output
# targets.  When this regex matches a line of a Makefile, we know the
# following lines are giving us the names of targets.
target_re = re.compile('^outs_[_a-zA-Z01-9]*:.*')


def parse_aligner_local(target):
    """ Based on Makefile target name, parse which aligner is involved """
    toks = target.split('_')
    aligner, local = 'bt2', False
    if 'bwamem' in toks[1]:
        aligner = 'bwamem'
        local = True
    if 'snap' in toks[1]:
        aligner = 'snap'
        local = True
    if aligner == 'bt2':
        local = 'l' in toks[1]
    return aligner, local


def parse_species(target):
    """ Based on Makefile target name, parse which species is involved """
    genome = 'hg'
    toks = target.split('_')
    # Parsing reference species info
    if toks[2] == 'mm':
        genome = 'mm'
    if toks[2] == 'zm':
        genome = 'zm'
    return genome


def parse_sim(target):
    """ Based on Makefile target name, parse which read simulator is involved """
    sim = 'mason'
    toks = target.split('_')
    # Parsing simulator info:
    if toks[2] == 'wgsim':
        sim = 'wgsim'
    if toks[2] == 'art':
        sim = 'art'
    return sim


def parse_sensitivity(target, aligner):
    """ Based on Makefile target name, parse which sensitivity level is involved """
    toks = target.split('_')
    sensitivity = 's'
    if aligner == 'bt2':
        sensitivity = toks[1][3:]
    return sensitivity


def parse_paired(target):
    """ Based on Makefile target name, parse whether the data is paired-end """
    return target.startswith('r12')


def parse_readlen(target):
    """ Based on Makefile target name, parse the read length """
    readlen = target.split('_')[-1]
    return 500 if readlen == '50to500' else int(readlen)


def parse_name_and_target(combined):
    """ Based on Makefile target name, parse the read length """
    toks = combined.split('_')
    roff = 3
    if toks[2] == 'r0' or toks[2] == 'r12':
        roff = 2
    assert toks[roff] == 'r0' or toks[roff] == 'r12'
    return '_'.join(toks[:roff]), '_'.join(toks[roff:])


def mkdir_quiet(dr):
    """ Create directories if needed, quietly """
    import errno
    if not os.path.isdir(dr):
        try:
            os.makedirs(dr)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise


def has_done(dr):
    """ Return true if directory contains DONE file, indicating qsim finished
        running. """
    done_fn = join(dr, 'DONE')
    if not os.path.exists(done_fn):
        raise RuntimeError('Directory "%s" does not contain DONE file' % dr)


def copyfiles(fglob, dest, prefix=''):
    """ Copy files (indicated by the file glob fglob) to the destination
        directory (indicated by dest). """
    assert os.path.isdir(dest) and os.path.exists(dest)
    for fn in glob.glob(fglob):
        os.system('cp -f %s %s' % (fn, join(dest, prefix + os.path.basename(fn))))


def roc_file_to_string(roc_fn, inner_sep=':', outer_sep=';'):
    """ Convert a file with a ROC table into a string with one line per ROC row """
    fields = []
    with open(roc_fn) as fh:
        for ln in fh:
            cor, _, _, incor, mapq, _, _, _, _, _ = ln.rstrip().split(',')
            if mapq == "mapq":
                continue
            fields.append(inner_sep.join([mapq, cor, incor]))
    return outer_sep.join(fields)


def compile_line(ofh, combined_target_name, mapq_incl, tt, trial, params_fn, summ_fn, roc_round_fn, roc_orig_fn, first):
    """ Put together one line of output and write to ofh (overall.csv)
        """
    name, target = parse_name_and_target(combined_target_name)
    aligner, local = parse_aligner_local(target)
    paired = parse_paired(target)
    sim = parse_sim(target)
    readlen = parse_readlen(target)
    sensitivity = parse_sensitivity(target, aligner)
    species = parse_species(target)
    headers = ['name', 'mapq_included', 'training', 'trial_no', 'aligner', 'local',
               'paired', 'sim', 'readlen', 'sensitivity', 'species']
    values = [name, 'T' if mapq_incl else 'F', 'T' if tt == 'training' else 'F',
              trial, aligner, 'T' if local else 'F', 'T' if paired else 'F', sim,
              str(readlen), sensitivity, species]
    for fn in [params_fn, summ_fn]:
        with open(fn, 'r') as fh:
            header = fh.readline().rstrip()
            headers += header.split(',')
            body = fh.readline().rstrip()
            values += body.split(',')
    # Add ROCs; these are big long strings
    headers.extend(['roc_round', 'roc_orig'])
    values.extend([roc_file_to_string(roc_round_fn),
                   roc_file_to_string(roc_orig_fn)])
    if first:
        ofh.write(','.join(map(str, headers)) + '\n')
    ofh.write(','.join(map(str, values)) + '\n')


def get_immediate_subdirectories(a_dir):
    """ Return list of subdirectories immediately under the given dir """
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


def handle_dir(dirname, dest_dirname, ofh, first, makefile_fn='Makefile'):
    # ofh is a writable file for overall.csv
    name = os.path.basename(dirname)

    if os.path.exists(join(name, 'IGNORE')):
        return

    with open(join(dirname, makefile_fn)) as fh:

        in_target = False
        for ln in fh:
            if target_re.match(ln):
                in_target = True
            elif in_target:
                if len(ln.rstrip()) == 0:
                    in_target = False
                else:
                    # Parsing a target from the list of targets in the Makefile
                    target = ln.split()[0]
                    if target.endswith('/DONE'):
                        target = target[:-5]
                    target_full = join(dirname, target)
                    has_done(target_full)

                    combined_target_name = name + '_' + target[:-4]
                    logging.info('  Found target: %s' % combined_target_name)
                    odir = join(dest_dirname, combined_target_name)

                    for dir_samp in get_immediate_subdirectories(target_full):

                        assert dir_samp.startswith('sample')
                        rate = dir_samp[6:]
                        odir_r = join(odir, 'sample' + rate)
                        logging.info('    Found sampling rate: %s' % rate)
                        target_full_s = join(target_full, 'sample' + rate)
                        if not os.path.isdir(target_full_s):
                            raise RuntimeError('Directory "%s" does not exist' % target_full_s)

                        for dir_mapq in get_immediate_subdirectories(target_full_s):

                            if dir_mapq in ['mapq_excluded', 'mapq_included']:
                                mapq_included = dir_mapq == 'mapq_included'
                                odir_rm = join(odir_r, dir_mapq)
                                logging.info('      Found %s' % dir_mapq)
                                target_full_sm = join(target_full_s, dir_mapq)
                                if not os.path.isdir(target_full_sm):
                                    raise RuntimeError('Directory "%s" does not exist' % target_full_sm)
                                next_subdirs = get_immediate_subdirectories(target_full_sm)
                            else:
                                assert dir_mapq.startswith('trial')
                                target_full_sm = target_full_s
                                odir_rm = odir_r
                                mapq_included = False
                                next_subdirs = [dir_mapq]

                            for dir_trial in next_subdirs:

                                assert dir_trial.startswith('trial')
                                trial = dir_trial[5:]
                                odir_rmt = join(odir_rm, 'trial' + trial)
                                logging.info('        Found trial: %s' % trial)
                                target_full_smt = join(target_full_sm, 'trial' + trial)
                                if not os.path.isdir(target_full_smt):
                                    raise RuntimeError('Directory "%s" does not exist' % target_full_smt)

                                mkdir_quiet(odir_rmt)

                                os.system('cp -f %s %s' % (join(target_full_smt, 'featimport_*.csv'), odir_rmt))
                                params_fn = join(odir_rmt, 'params.csv')
                                os.system('cp -f %s %s' % (join(target_full_smt, 'params.csv'), params_fn))

                                for tt in ['test', 'training']:

                                    target_full_smtt = join(target_full_smt, tt)
                                    if not os.path.isdir(target_full_smtt):
                                        raise RuntimeError('Directory "%s" does not exist' % target_full_smtt)

                                    mapqst = 'incl' if mapq_included else 'excl'
                                    summ_fn = join(odir_rmt, tt + '_' + mapqst + '_summary.csv')
                                    roc_fn = join(odir_rmt, tt + '_' + mapqst + '_roc.csv')
                                    roc_orig_fn = join(odir_rmt, tt + '_' + mapqst + '_roc_orig.csv')
                                    roc_round_fn = join(odir_rmt, tt + '_' + mapqst + '_roc_round.csv')
                                    os.system('cp -f %s %s' % (join(target_full_smtt, 'summary.csv'), summ_fn))
                                    os.system('cp -f %s %s' % (join(target_full_smtt, 'roc.csv'), roc_fn))
                                    os.system('cp -f %s %s' % (join(target_full_smtt, 'roc_orig.csv'), roc_orig_fn))
                                    os.system('cp -f %s %s' % (join(target_full_smtt, 'roc_round.csv'), roc_round_fn))
                                    compile_line(ofh, combined_target_name, mapq_included, tt, trial, params_fn,
                                                 summ_fn, roc_round_fn, roc_orig_fn, first)
                                    first = False


def go():

    # Set up logger
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                        datefmt='%m/%d/%y-%H:%M:%S', level=logging.DEBUG)

    # Open output overall.csv file
    first = True
    makefile_fn = 'Makefile'
    out_fn = 'overall.csv'
    summary_fn = 'summary'
    experiment = False

    if '--experiment' in sys.argv:
        exp_name = sys.argv[sys.argv.index('--experiment')+1]
        makefile_fn = 'Makefile.' + exp_name
        out_fn = 'overall.' + exp_name + '.csv'
        summary_fn = 'summary_%s' % exp_name
        experiment = True

    # Set up output directory
    if os.path.exists(summary_fn):
        raise RuntimeError('%s directory exists' % summary_fn)
    mkdir_quiet(summary_fn)

    with open(join(summary_fn, out_fn), 'w') as fh:
        # Descend into subdirectories looking for Makefiles
        for dirname, dirs, files in os.walk('.'):
            for fn in files:
                if fn == makefile_fn or (experiment and fn.startswith(makefile_fn)):
                    logging.info('Found a Makefile: %s' % join(dirname, fn))
                    handle_dir(dirname, summary_fn, fh, first, makefile_fn=fn)
                    first = False

    # Compress the output directory, which is large because of the CID and CSE curves
    os.system('tar -cvzf %s.tar.gz %s' % (summary_fn, summary_fn))

if '--slurm' in sys.argv:
    my_hours = 24
    with open('.gather.sh', 'w') as ofh:
        print("#!/bin/bash -l", file=ofh)
        print("#SBATCH", file=ofh)
        print("#SBATCH --nodes=1", file=ofh)
        print("#SBATCH --mem=4G", file=ofh)
        if '--scavenger' in sys.argv:
            print('#SBATCH --partition=scavenger', file=ofh)
            print('#SBATCH --qos=scavenger', file=ofh)
        else:
            print('#SBATCH --partition=shared', file=ofh)
        print('#SBATCH --time=%d:00:00' % my_hours, file=ofh)
        print('#SBATCH --output=.gather.sh.o', file=ofh)
        print('#SBATCH --error=.gather.sh.e', file=ofh)
        print('python gather.py', file=ofh)
    print('sbatch .gather.sh')
else:
    go()
