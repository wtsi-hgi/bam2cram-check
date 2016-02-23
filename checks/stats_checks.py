import os
import subprocess
import logging
import re

from checks import utils
import sys

class RunSamtoolsCommands:
    @classmethod
    def _run_subprocess(cls, args_list):
        proc = subprocess.run(args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        utils.log_error(args_list, proc.stderr, proc.returncode)
        if proc.stderr or proc.returncode != 0:
            raise RuntimeError("ERROR running process: %s, error = %s and exit code = %s" % (args_list, proc.stderr, proc.returncode))
        return proc.stdout

    @classmethod
    def run_samtools_quickcheck(cls, fpath):
        return cls._run_subprocess(['samtools', 'quickcheck', '-v', fpath])

    @classmethod
    def get_samtools_flagstat_output(cls, fpath):
        return cls._run_subprocess(['samtools', 'flagstat', fpath])

    @classmethod
    def get_samtools_stats_output(cls, fpath):
        return cls._run_subprocess(['samtools', 'stats', fpath])

    @classmethod
    def get_samtools_version_output(cls):
        return cls._run_subprocess(['samtools', '--version'])


class HandleSamtoolsStats:

    @classmethod
    def _get_stats(cls, stats_fpath):
        if stats_fpath and os.path.isfile(stats_fpath):
            return utils.read_from_file(stats_fpath)
        return None


    @classmethod
    def _generate_stats(cls, data_fpath):
        if not data_fpath or not os.path.isfile(data_fpath):
            raise ValueError("Can't generate stats from a non-existing file: %s" % str(data_fpath))
        return RunSamtoolsCommands.get_samtools_stats_output(data_fpath)


    @classmethod
    def _is_stats_file_older_than_data(cls, data_fpath, stats_fpath):
        if utils.compare_mtimestamp(data_fpath, stats_fpath) >= 0:
            return True
        return False

    @classmethod
    def fetch_stats(cls, fpath, stats_fpath):
        if not fpath or not os.path.isfile(fpath):
            raise ValueError("You need to give a valid file path if you want the stats")
        if os.path.isfile(stats_fpath) and not cls._is_stats_file_older_than_data(fpath, stats_fpath) and \
                utils.can_read_file(stats_fpath):
            stats = HandleSamtoolsStats._get_stats(stats_fpath)
            logging.info("Reading stats from file %s" % stats_fpath)
        else:
            stats = HandleSamtoolsStats._generate_stats(fpath)
            logging.info("Generating stats for file %s" % fpath)
            if os.path.isfile(stats_fpath) and cls._is_stats_file_older_than_data(fpath, stats_fpath):
                logging.warning("The stats file is older than the actual file, you need to remove/update it. "
                                "Regenerating the stats, but without saving.")
        return stats

    @classmethod
    def persist_stats(cls, stats, stats_fpath):
        if not stats or not stats_fpath:
            raise ValueError("You must provide both stats and stats file path for saving the stats to a file."
                         " Received stats = %s and stats fpath = %s" % (str(stats), str(stats_fpath)))
        if not os.path.isfile(stats_fpath):
            logging.info("Persisting the stats to disk")
            return utils.write_to_file(stats_fpath, stats)
        else:
            logging.info("Skipping persist_stats to disk, apparently there is a valid stats file there already.")
        return False

    @classmethod
    def extract_seq_checksum_from_stats(cls, stats: str) -> str:
        for line in stats.split('\n'):
            if re.search('^CHK', line):
                return line
        return None


class HandleSamtoolsVersion:

    @classmethod
    def _get_version_nr_from_samtools_output(cls, output):
        version_line = output.splitlines()[0]
        tokens = version_line.split()
        if len(tokens) < 2:
            raise ValueError("samtools --version output looks different than expected. Can't parse it.")
        return tokens[1]

    @classmethod
    def _extract_major_version_nr(cls, version):
        return version.split('.', 1)[0]

    @classmethod
    def _extract_minor_version_nr(cls, version):
        vers_tokens = version.split('.', 1)
        if len(vers_tokens) < 2:
            raise ValueError("samtools version output looks different than expected.Can't parse it.")
        return vers_tokens[1].split('.', 1)

    @classmethod
    def check_samtools_version(cls, version_output):
        errors = []
        if not version_output:
            errors.append("You need to use at least samtools version 1.3.")
        version = cls._get_version_nr_from_samtools_output(version_output)
        major_nr = cls._extract_major_version_nr(version)
        minor_nr = cls._extract_minor_version_nr(version)
        if not major_nr.isdigit():
            raise ValueError("Can't parse samtools version string")
        if int(major_nr) < 1:
            raise ValueError("You need to use at least samtools version 1.3.")
        else:
            minor_nr_1 = minor_nr.split('.', 1)
            if not minor_nr_1.isdigit():
                raise ValueError("Can't parse samtools version string.")
                return errors
            if int(minor_nr_1[0]) < 3:
                raise ValueError("You need to use at least samtools version 1.3.")


class CompareStatsForFiles:
    @classmethod
    def compare_flagstats(cls, flagstat_b, flagstat_c):
        errors = []
        if not flagstat_c or not flagstat_b:
            errors.append("At least one of the flagstats is missing")
            return errors
        if flagstat_b != flagstat_c:
            logging.error("FLAGSTAT DIFFERENT:\n %s then:\n %s " % (flagstat_b, flagstat_c))
            errors.append("FLAGSTAT DIFFERENT:\n %s then:\n %s " % (flagstat_b, flagstat_c))
        else:
            logging.info("Flagstats are equal.")
        return errors

    @classmethod
    def compare_stats_by_sequence_checksum(cls, stats_b, stats_c):
        errors = []
        if not stats_b or not stats_c:
            errors.append("You need to provide both BAM and CRAM stats for cmparison")
            return errors

        chk_b = HandleSamtoolsStats.extract_seq_checksum_from_stats(stats_b)
        chk_c = HandleSamtoolsStats.extract_seq_checksum_from_stats(stats_c)
        if not chk_b:
            errors.append("For some reason there is no CHK line in the samtools stats")
            logging.error("For some reason there is no CHK line in the samtools stats")
        if not chk_c:
            errors.append("For some reason there is no CHK line in the samtools stats")
            logging.error("For some reason there is no CHK line in the samtools stats")

        if chk_b != chk_c:
            errors.append("STATS SEQUENCE CHECKSUM DIFFERENT: %s and %s" % (chk_b, chk_c))
            logging.error("STATS SEQUENCE CHECKSUM DIFFERENT: %s and %s" % (chk_b, chk_c))
        return errors


    @classmethod
    def compare_bam_and_cram_by_statistics(cls, bam_path, cram_path):
        errors = []
        # Check that it's a valid file path
        if not bam_path or not os.path.isfile(bam_path):
            errors.append("The BAM file path: %s is not valid" % bam_path)
        if not cram_path or not os.path.isfile(cram_path):
            errors.append("The CRAM file path:%s is not valid" % cram_path)
        if errors:
            logging.error("There are errors with the file paths you provided: %s" % errors)
            return errors

        # Check that the files are readable by me
        if not utils.can_read_file(bam_path):
            errors.append("Can't read file %s" % bam_path)
        if not utils.can_read_file(cram_path):
            errors.append("Can't read file %s" % cram_path)
        if errors:
            logging.error("There are problems reading the files: %s" % errors)
            return errors

        # Checking on samtools version:
        version_output = RunSamtoolsCommands.get_samtools_version_output()
        try:
            HandleSamtoolsVersion.check_samtools_version(version_output)
        except ValueError as e:
            errors.append(str(e))
            return errors

        # Quickcheck the files before anything:
        try:
            RunSamtoolsCommands.run_samtools_quickcheck(bam_path)
        except RuntimeError as e:
            errors.append(str(e))

        try:
            RunSamtoolsCommands.run_samtools_quickcheck(cram_path)
        except RuntimeError as e:
            errors.append(str(e))
        if errors:
            logging.error("There are problems running quickcheck on the files you've given: %s" % errors)
            return errors

        # Calculate and compare flagstat:
        try:
            flagstat_b = RunSamtoolsCommands.get_samtools_flagstat_output(bam_path)
        except RuntimeError as e:
            errors.append(str(e))

        try:
            flagstat_c = RunSamtoolsCommands.get_samtools_flagstat_output(cram_path)
        except RuntimeError as e:
            errors.append(str(e))

        if not errors:
            errors.extend(cls.compare_flagstats(flagstat_b, flagstat_c))
        else:
            logging.error("THere are problems running flagstat on the files you've given: %s" % errors)

        # Calculate and compare stats:
        stats_fpath_b = bam_path + ".stats"
        stats_fpath_c = cram_path + ".stats"
        stats_b, stats_c = None, None
        try:
            stats_b = HandleSamtoolsStats.fetch_stats(bam_path, stats_fpath_b)
        except (ValueError, RuntimeError) as e:
            errors.append(str(e))

        try:
            stats_c = HandleSamtoolsStats.fetch_stats(cram_path, stats_fpath_c)
        except (ValueError, RuntimeError) as e:
            errors.append(str(e))

        if not errors and stats_b and stats_c:
            errors.extend(cls.compare_stats_by_sequence_checksum(stats_b, stats_c))
        else:
            errors.append("Can't compare samtools stats.")
            logging.error("For some reason I can't compare samtools stats for your files.")

        # Persist stats:
        try:
            if stats_b:
                HandleSamtoolsStats.persist_stats(stats_b, stats_fpath_b)
        except IOError as e:
            errors.append("Can't save stats to disk for %s file" % bam_path)
            logging.error("Can't save stats to disk for %s file" % bam_path)

        try:
            if stats_c:
                HandleSamtoolsStats.persist_stats(stats_c, stats_fpath_c)
        except IOError as e:
            errors.append("Can't save stats to disk for %s file" % cram_path)
            logging.error("Can't save stats to disk for %s file" % cram_path)
        return errors


