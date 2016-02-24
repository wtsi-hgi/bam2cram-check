#!/usr/bin/env bash
set -euf

wget https://github.com/samtools/samtools/releases/download/1.3/samtools-1.3.tar.bz2
tar -xvjf samtools-1.3.tar.bz2
rm samtools-1.3.tar.bz2
cd samtools-1.3
make
make prefix=$SAMTOOLS_INSTALL install
cd ..
rm -rf samtools-1.3

