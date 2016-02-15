[![Build Status](https://travis-ci.org/wtsi-hgi/bam2cram-check.svg)](https://travis-ci.org/wtsi-hgi/bam2cram-check)
[![codecov.io](https://codecov.io/github/wtsi-hgi/bam2cram-check/coverage.svg?branch=master)](https://codecov.io/github/wtsi-hgi/bam2cram-check?branch=master)

# bam2cram-check

This package is for checking that the file format convertion between a BAM and a CRAM leaves the data unaffected. The checks rely on the comparison between samtools stats' (CHK field), and on samtools flagstat. In addition to this both files are samtools quickcheck-ed. The stats are generated for both files. However, if there is a .stats or .flagstat file in the directory where each file is, then it will use those.

For running this you need:
```
samtools >=1.3
```

Usage:
```bash
python main.py -b <bam_file> -c <cram_file> -e <err_file> --log <log_file>
```
