import sys
import re
import subprocess
import shlex


if not sys.version_info >= (3, 8):
    print('Requires python 3.8 or later.')
    sys.exit(1)


def git_describe():
    args = shlex.split('git describe')
    result = subprocess.run(args, capture_output=True)
    return result.stdout.decode('UTF-8').strip()


def main():
    desc = git_describe()
    if m := re.match(r'^\d+\.\d+\.\d+$', desc):
        version = desc
    elif m := re.match(r'^\d+\.\d+\.\d+-rc\d+$', desc):
        version = desc
    elif m := re.match(r'^(\d+\.\d+\.\d+)-(\d+)-g([0-9a-fA-F]+)$', desc):
        version_core = m.group(1)
        changes = m.group(2)
        commit = m.group(3)
        version = f'{version_core}-dev.{changes}+{commit}'
    elif m := re.match(r'^(\d+\.\d+\.\d+)-(\d+)-g([0-9a-fA-F]+)-dirty$', desc):
        version_core = m.group(1)
        changes = m.group(2)
        commit = m.group(3)
        version = f'{version_core}-dev.{changes}+{commit}.dirty'
    else:
        version = '0.0.0'  # Fallback
    print(version)


if __name__ == '__main__':
    main()
