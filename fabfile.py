from fabpolish import polish, sniff, local, info
import os
from fabpolish.contrib import (
    find_merge_conflict_leftovers,
    find_pep8_violations
)

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


@sniff(severity='major', timing='fast')
def remove_compiled_classes():
    # Remove compiled python classes
    info('Removing compiled python classes...')
    return local("find -name '*.py[co]' -print0 | xargs -0 rm -f")


@sniff(severity='major', timing='fast')
def fix_file_permission():
    """Fixing permissions for files"""
    # Have to look for script files
    info('Fixing permissions for files')
    return local(
        "git ls-files -z | "
        "xargs -0 chmod -c 0664 > /dev/null 2>&1"
    )


@sniff(severity='major', timing='fast')
def code_analyzer():
    """Running static code analyzer"""
    info('Running static code analyzer')
    return local(
        "git ls-files -z | "
        "grep -PZz '\.py$' | "
        "grep -PZvz 'fabfile.py' | "
        "xargs -0 pyflakes"
    )


@sniff(severity='major', timing='fast')
def remove_debug_info():
    """Check and remove debugging print statements"""
    # Have to remove scripts and test file
    info('Checking for debug print statements')
    return local(
        "! git ls-files -z | "
        "grep -PZvz 'fabfile.py' | "
        "grep -PZz \.py$ | "
        "xargs -0 grep -Pn \'(?<![Bb]lue|>>> )print\' | "
        "grep -v NOCHECK"
    )


@sniff(severity='major', timing='fast')
def servername_compatibility():
    """Checking for no servername compatibility"""
    # exclude fabfile
    info('Checking for no servername compatibility')
    return local(
        "! git ls-files -z | "
        "grep -PZz \.py$ | "
        "grep -PZvz 'config.py' | "
        "grep -PZvz 'fabfile.py' | "
    )


@sniff(severity='major', timing='fast')
def check_migration_branch():
    info('Checking migration branches...')
    return local(
        "! alembic branches | "
        "grep branchpoint "
    )


if __name__ == "__main__":
    polish()