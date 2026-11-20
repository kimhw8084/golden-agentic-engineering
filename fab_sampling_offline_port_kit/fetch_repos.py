#!/usr/bin/env python3
"""Fetch public repositories on an internet-connected staging machine only.
Never downloads inside the isolated work environment. No third-party code execution.
"""
import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path

HOME = Path(__file__).resolve().parent
CANDIDATES = json.loads((HOME / 'repos.json').read_text(encoding='utf-8'))['repositories']

def git(*args, cwd=None):
    return subprocess.run(['git', *args], cwd=cwd, capture_output=True, text=True)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--stage', choices=['core','fab','extended','all'], default='all')
    p.add_argument('--output', default=str(HOME / 'sources'))
    args = p.parse_args()
    target = Path(args.output).resolve()
    target.mkdir(parents=True, exist_ok=True)
    selected = [r for r in CANDIDATES if args.stage == 'all' or (args.stage == 'core' and r['stage'] == 'core') or (args.stage == 'fab' and r['stage'].startswith('fab')) or (args.stage == 'extended' and r['stage'].startswith('extended'))]
    output = []
    for r in selected:
        dest = target / r['repo'].replace('/','__')
        state = {'repo':r['repo'],'stage':r['stage'],'expected_license':r['license_expected'],'path':str(dest.relative_to(HOME)) if dest.is_relative_to(HOME) else str(dest),'url':r['url']}
        print(f"[{r['rank']:02}] {r['repo']} ...", flush=True)
        if not dest.exists():
            result = git('clone','--depth','1','--single-branch','--no-tags','--',r['url'],str(dest))
            if result.returncode != 0:
                state.update(status='CLONE_FAILED',error=result.stderr[-1800:]);output.append(state); print('FAILED');continue
        if not (dest / '.git').exists():
            state.update(status='INVALID_EXISTING_DIR');output.append(state);print('FAILED');continue
        sha = git('-C',str(dest),'rev-parse','HEAD')
        origin = git('-C',str(dest),'remote','get-url','origin')
        if sha.returncode or origin.returncode or origin.stdout.strip().rstrip('/').removesuffix('.git').lower() != r['url'].rstrip('/').removesuffix('.git').lower():
            state.update(status='GIT_MISMATCH_OR_ERROR');output.append(state);print('FAILED');continue
        license_files = [str(x.relative_to(dest)) for x in dest.iterdir() if x.is_file() and x.name.lower().startswith(('license','licence','copying'))]
        state.update(status='CLONED_PENDING_AUDIT',sha=sha.stdout.strip(),license_files=license_files,has_submodules=(dest/'.gitmodules').exists(),has_lfs_pointers='not_checked')
        output.append(state)
        print('OK '+state['sha'][:12])
    prior_path=HOME/'repos.lock.json'
    prior=[]
    if prior_path.exists():
        prior=json.loads(prior_path.read_text(encoding='utf-8')).get('entries',[])
    by_repo={x['repo']:x for x in prior}
    by_repo.update({x['repo']:x for x in output})
    lock={'generated_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'entries':[by_repo[r['repo']] for r in CANDIDATES if r['repo'] in by_repo]}
    prior_path.write_text(json.dumps(lock,indent=2)+'\n',encoding='utf-8')
    failures=[x for x in output if x['status'] != 'CLONED_PENDING_AUDIT']
    print(f'Finished: {len(output)-len(failures)}/{len(output)} cloned; lock: {prior_path}')
    if failures: raise SystemExit(2)

if __name__=='__main__':main()
