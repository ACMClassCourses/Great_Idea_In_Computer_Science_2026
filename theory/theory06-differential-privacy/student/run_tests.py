#!/usr/bin/env python3
import argparse
import math
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / '.build'
CXX = os.environ.get('CXX', 'g++')


def compile_target(name: str) -> Path:
    src = ROOT / name / 'main.cpp'
    if not src.exists():
        print(f'[ERROR] missing {src.relative_to(ROOT)}')
        print(f'Create {name}/main.cpp first.')
        sys.exit(2)
    BUILD.mkdir(exist_ok=True)
    out = BUILD / name
    cmd = [CXX, '-std=c++17', '-O2', str(src), '-I', str(ROOT / name), '-o', str(out)]
    p = subprocess.run(cmd, text=True, capture_output=True)
    if p.returncode != 0:
        print(f'[COMPILE FAIL] {name}')
        print(p.stderr)
        sys.exit(2)
    print(f'[COMPILE OK] {name}')
    return out


def run_program(exe: Path, text: str, timeout=8):
    try:
        p = subprocess.run([str(exe)], input=text, text=True, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, 'TIMEOUT'
    if p.returncode != 0:
        return None, f'non-zero exit code {p.returncode}\n{p.stderr.strip()}'
    lines = [x.strip() for x in p.stdout.splitlines() if x.strip()]
    return lines, None


def fnum(s):
    try:
        return float(s)
    except Exception:
        return None


def fail(case, line_no, expected, actual):
    print(f'[FAIL] {case}')
    if line_no is not None:
        print(f'line {line_no}')
    print(f'expected: {expected}')
    print(f'actual:   {actual}')


def basic_exact(exe: Path):
    folder = ROOT / 'basic/tests/exact'
    for inp in sorted(folder.glob('*.in')):
        case = inp.stem
        oracle = (folder / f'{case}.out').read_text().splitlines()
        actual, err = run_program(exe, inp.read_text())
        if err:
            fail(case, None, 'program finishes normally', err)
            return False
        if len(actual) != len(oracle):
            fail(case, None, f'{len(oracle)} output lines', f'{len(actual)} output lines')
            return False
        for i, (rule, got) in enumerate(zip(oracle, actual), 1):
            parts = rule.split()
            gp = got.split()
            ok = False
            if parts[0] == 'VALUE_ANY':
                ok = len(gp) == 2 and gp[0] == 'VALUE' and fnum(gp[1]) is not None and math.isfinite(float(gp[1]))
            elif parts[0] == 'VALUE_NEAR':
                if len(gp) == 2 and gp[0] == 'VALUE' and fnum(gp[1]) is not None:
                    ok = abs(float(gp[1]) - float(parts[1])) <= float(parts[2])
            elif parts[0] == 'REMAIN_NEAR':
                if len(gp) == 2 and gp[0] == 'REMAIN' and fnum(gp[1]) is not None:
                    ok = abs(float(gp[1]) - float(parts[1])) <= float(parts[2])
            elif parts[0] == 'REJECTED':
                ok = got == 'REJECTED'
            if not ok:
                fail(case, i, rule, got)
                return False
        print(f'[PASS] {case}')
    return True


def basic_oj(exe: Path):
    """Run the ten deterministic OJ data points with numeric tolerance."""
    folder = ROOT / 'basic/oj'
    for inp in sorted(folder.glob('*.in')):
        case = inp.stem
        expected = (folder / f'{case}.out').read_text().splitlines()
        actual, err = run_program(exe, inp.read_text())
        if err:
            fail(case, None, 'program finishes normally', err)
            return False
        if len(actual) != len(expected):
            fail(case, None, f'{len(expected)} output lines', f'{len(actual)} output lines')
            return False
        for i, (want, got) in enumerate(zip(expected, actual), 1):
            wp, gp = want.split(), got.split()
            ok = wp[0] == gp[0] if gp else False
            if ok and wp[0] in ('VALUE', 'REMAIN'):
                ok = (len(wp) == len(gp) == 2 and fnum(gp[1]) is not None
                      and math.isfinite(float(gp[1]))
                      and abs(float(gp[1]) - float(wp[1])) <= 1e-5)
            elif ok:
                ok = want == got
            if not ok:
                fail(case, i, want, got)
                return False
        print(f'[OJ PASS] {case}')
    return True


def replace_seed(text: str, seed: int, hard=False):
    lines = text.splitlines()
    p = lines[0].split()
    p[-1] = str(seed)
    lines[0] = ' '.join(p)
    return '\n'.join(lines) + '\n'


def basic_quality(exe: Path):
    folder = ROOT / 'basic/tests/quality'
    print('\nBasic quality tests (reported, not exact pass/fail):')
    for inp in sorted(folder.glob('*.in')):
        case = inp.stem
        truths = [float(x.split()[1]) for x in (folder / f'{case}.out').read_text().splitlines() if x.strip()]
        errors=[]; rel=[]; bad=0
        for seed in range(1, 13):
            actual, err = run_program(exe, replace_seed(inp.read_text(), seed))
            if err or len(actual) != len(truths):
                bad += 1; continue
            good=True
            for line, truth in zip(actual, truths):
                p=line.split()
                if len(p)!=2 or p[0] != 'VALUE' or fnum(p[1]) is None:
                    good=False; break
                val=float(p[1]); e=abs(val-truth); errors.append(e)
                if abs(truth)>1e-12: rel.append(e/abs(truth))
            if not good: bad += 1
        if bad:
            print(f'[QUALITY] {case}: {bad}/12 runs malformed or failed')
        if errors:
            mae=sum(errors)/len(errors)
            mre=(sum(rel)/len(rel)*100) if rel else float('nan')
            print(f'[QUALITY] {case}: MAE={mae:.4f}, mean relative error={mre:.2f}%')
        else:
            print(f'[QUALITY] {case}: no valid numeric outputs')


def hard_exact(exe: Path):
    folder = ROOT / 'hard/tests/exact'
    for inp in sorted(folder.glob('*.in')):
        case=inp.stem
        oracle=(folder/f'{case}.out').read_text().splitlines()
        actual,err=run_program(exe,inp.read_text())
        if err:
            fail(case,None,'program finishes normally',err); return False
        if len(actual)!=len(oracle):
            fail(case,None,f'{len(oracle)} output lines',f'{len(actual)} output lines'); return False
        for i,(rule,got) in enumerate(zip(oracle,actual),1):
            rp=rule.split(); gp=got.split(); ok=False
            if rp[0] in ('ALERT','BELOW'):
                ok = len(gp)>=2 and gp[0]==rp[0] and gp[1]==rp[1]
                # Non-numeric ALERT is expected unless oracle says ALERT_NEAR.
                if rp[0]=='ALERT' and len(gp)!=2: ok=False
                if rp[0]=='BELOW' and len(gp)!=2: ok=False
            elif rp[0]=='FINISHED':
                ok = got=='FINISHED'
            elif rp[0]=='ALERT_NEAR':
                if len(gp)==3 and gp[0]=='ALERT' and gp[1]==rp[1] and fnum(gp[2]) is not None:
                    ok=abs(float(gp[2])-float(rp[2])) <= float(rp[3])
            if not ok:
                fail(case,i,rule,got); return False
        print(f'[PASS] {case}')
    return True


def parse_quality_oracle(path: Path):
    seeds=20; signals=set(); counts={}
    for line in path.read_text().splitlines():
        p=line.split()
        if not p: continue
        if p[0]=='SEEDS': seeds=int(p[1])
        elif p[0]=='SIGNALS': signals=set(map(int,p[1:]))
        elif p[0]=='COUNTS':
            for item in p[1:]:
                a,b=item.split(':'); counts[int(a)]=int(b)
    return seeds,signals,counts


def hard_quality(exe: Path):
    folder=ROOT/'hard/tests/quality'
    print('\nHard quality tests (reported, not exact pass/fail):')
    for inp in sorted(folder.glob('*.in')):
        case=inp.stem
        seeds,signals,counts=parse_quality_oracle(folder/f'{case}.out')
        total_signal_hits=0; possible_signal_hits=0; false_alerts=0; alert_total=0; numeric_errors=[]; malformed=0
        for seed in range(1,seeds+1):
            actual,err=run_program(exe,replace_seed(inp.read_text(),seed),timeout=10)
            if err:
                malformed += 1; continue
            alerted=[]; numvals=[]; good=True
            for line in actual:
                p=line.split()
                if not p: continue
                if p[0]=='ALERT' and len(p) in (2,3):
                    try: t=int(p[1])
                    except: good=False; break
                    alerted.append(t)
                    if len(p)==3:
                        try: numvals.append((t,float(p[2])))
                        except: good=False; break
                elif p[0]=='BELOW' and len(p)==2:
                    pass
                elif p[0]=='FINISHED' and len(p)==1:
                    pass
                else:
                    good=False; break
            if not good:
                malformed+=1; continue
            aset=set(alerted)
            total_signal_hits += len(aset & signals)
            possible_signal_hits += len(signals)
            fa=len([t for t in alerted if t not in signals]); false_alerts += fa; alert_total += len(alerted)
            for t,v in numvals:
                if t in counts: numeric_errors.append(abs(v-counts[t]))
        valid=seeds-malformed
        recall=(total_signal_hits/possible_signal_hits*100) if possible_signal_hits else 0
        false_per=(false_alerts/valid) if valid else float('nan')
        msg=f'[QUALITY] {case}: signal recall={recall:.1f}%, false alerts/run={false_per:.2f}'
        if numeric_errors: msg += f', numeric MAE={sum(numeric_errors)/len(numeric_errors):.3f}'
        if malformed: msg += f', malformed/failed runs={malformed}/{seeds}'
        print(msg)


def hard_stress(exe: Path):
    # Online generated: no large .in file is stored in the project.
    topics=300; students=40000
    events=[]
    for s in range(1,students+1):
        t=(s*37)%topics+1
        events.append((s,t))
        if s%5==0: events.append((s,t))  # duplicates
        if s%11==0: events.append((s,(t%topics)+1))
    query=list(range(1,topics+1))
    lines=[f'{len(events)} 12345']+[f'{s} {t}' for s,t in events]
    lines += [f'ALERT 120 8 5.0', str(len(query)), ' '.join(map(str,query))]
    text='\n'.join(lines)+'\n'
    actual,err=run_program(exe,text,timeout=15)
    if err:
        print(f'[STRESS FAIL] {err}'); return False
    if len(actual)!=len(query):
        print(f'[STRESS FAIL] expected {len(query)} output lines, got {len(actual)}'); return False
    print(f'[STRESS OK] generated {len(events)} events and {len(query)} queries in memory')
    return True


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('target', choices=['basic','basic-oj','hard','all'])
    ap.add_argument('--stress', action='store_true')
    args=ap.parse_args()
    ok=True
    if args.target in ('basic','basic-oj','all'):
        b=compile_target('basic')
        if args.target == 'basic-oj':
            print('\n== Basic OJ data points ==')
            if not basic_oj(b): return 1
        else:
            print('\n== Basic exact tests ==')
            if not basic_exact(b): return 1
            basic_quality(b)
            if args.target == 'all':
                print('\n== Basic OJ data points ==')
                if not basic_oj(b): return 1
    if args.target in ('hard','all'):
        h=compile_target('hard')
        print('\n== Hard exact tests ==')
        if not hard_exact(h): return 1
        hard_quality(h)
        if args.stress:
            print('\n== Hard online stress test ==')
            ok = hard_stress(h) and ok
    return 0 if ok else 1

if __name__=='__main__':
    raise SystemExit(main())
