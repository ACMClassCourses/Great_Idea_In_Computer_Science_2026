#!/usr/bin/env python3
"""Compile a C++ submission (or run an executable) against paired .in/.out files."""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def positive_seconds(value):
    number = float(value)
    if not 0 < number < float('inf'):
        raise argparse.ArgumentTypeError('timeout must be a finite positive number')
    return number


def first_difference(expected, actual):
    offset = next((i for i, (a, b) in enumerate(zip(expected, actual)) if a != b),
                  min(len(expected), len(actual)))
    line_number = expected[:offset].count(b'\n') + 1
    column = offset - expected.rfind(b'\n', 0, offset)
    start = expected.rfind(b'\n', 0, offset) + 1
    actual_start = actual.rfind(b'\n', 0, offset) + 1

    def preview(data, begin):
        if begin >= len(data):
            return '<EOF>'
        end = data.find(b'\n', begin)
        if end < 0:
            end = len(data)
        fragment = data[begin:end + 1]
        return repr(fragment[:160]) + (' ...' if len(fragment) > 160 else '')

    return (f'line {line_number}, byte column {column}\n'
            f'    expected: {preview(expected, start)}\n'
            f'    actual:   {preview(actual, actual_start)}\n'
            f'    bytes: expected {len(expected)}, actual {len(actual)}')


def run(args, work_dir):
    inputs = sorted(args.data.resolve().glob(args.pattern))
    inputs = [path for path in inputs if path.is_file() and path.suffix == '.in']
    if not inputs:
        raise ValueError('No matching .in files found')
    for path in inputs:
        if not path.with_suffix('.out').is_file():
            raise ValueError(f'Missing expected output: {path.with_suffix(".out")}')

    if args.exe:
        executable = args.exe.resolve()
        if not executable.is_file():
            raise ValueError(f'Executable does not exist: {executable}')
    else:
        if not args.sources:
            raise ValueError('Provide C++ source files, or use --exe PATH')
        sources = [path.resolve() for path in args.sources]
        for source in sources:
            if not source.is_file():
                raise ValueError(f'Source file does not exist: {source}')
        executable = work_dir / ('submission.exe' if sys.platform == 'win32' else 'submission')
        compiler = shutil.which(args.compiler)
        if compiler is None:
            raise ValueError(f'Compiler not found: {args.compiler}')
        command = [compiler, '-std=c++11', '-O2', '-Wall', '-Wextra',
                   *map(str, sources), '-o', str(executable)]
        print('Compiling...', flush=True)
        build = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               timeout=120)
        if build.stdout:
            print(build.stdout.decode('utf-8', errors='replace'), end='')
        if build.returncode:
            print('Compilation failed.')
            return 1

    passed = 0
    for case in inputs:
        actual_path = work_dir / 'actual.out'
        error_path = work_dir / 'stderr.txt'
        reason = None
        with case.open('rb') as stdin, actual_path.open('wb') as stdout, error_path.open('wb') as stderr:
            try:
                result = subprocess.run([str(executable)], stdin=stdin, stdout=stdout,
                                        stderr=stderr, timeout=args.timeout, cwd=work_dir)
                if result.returncode:
                    reason = f'nonzero exit code {result.returncode}'
            except subprocess.TimeoutExpired:
                reason = f'timeout ({args.timeout:g}s)'
        if reason is None:
            expected = case.with_suffix('.out').read_bytes()
            actual = actual_path.read_bytes()
            if expected != actual:
                reason = first_difference(expected, actual)
        if reason:
            print(f'[FAIL] {case.stem}: {reason}')
            with error_path.open('rb') as stderr:
                diagnostic = stderr.read(1000)
            if diagnostic:
                print('    stderr:', repr(diagnostic))
        else:
            passed += 1
            print(f'[PASS] {case.stem}')
    print(f'\n{passed}/{len(inputs)} passed; {len(inputs) - passed} failed.')
    return 0 if passed == len(inputs) else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sources', nargs='*', type=Path, help='C++ source files to compile')
    parser.add_argument('--exe', type=Path, help='Test an existing executable instead of compiling')
    parser.add_argument('--compiler', default='g++', help='Compiler command or path (default: g++)')
    parser.add_argument('--data', type=Path, default=Path(__file__).resolve().parent / 'data',
                        help='Directory containing .in/.out pairs')
    parser.add_argument('--pattern', default='*.in', help='Input glob, e.g. "03_*.in"')
    parser.add_argument('--timeout', type=positive_seconds, default=5.0,
                        help='Timeout in seconds per case (default: 5)')
    args = parser.parse_args()
    if args.exe and args.sources:
        parser.error('Use source files or --exe, not both')
    try:
        with tempfile.TemporaryDirectory(prefix='page-replacement-tests-') as directory:
            return run(args, Path(directory))
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
