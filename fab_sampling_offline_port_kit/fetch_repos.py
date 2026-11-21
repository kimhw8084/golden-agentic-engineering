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


def select_repositories(stage=None, repo_names=None):
    """Select an explicit candidate subset; never default to all public sources."""
    if stage and repo_names:
        raise ValueError('Choose one --stage or one or more exact --repo values, not both.')
    if stage is None and not repo_names:
        raise ValueError('Choose an explicit --stage or at least one exact --repo value.')
    if repo_names:
        if len(repo_names) != len(set(repo_names)):
            raise ValueError('Duplicate --repo values are not allowed.')
        known = {item['repo'] for item in CANDIDATES}
        unknown = sorted(set(repo_names) - known)
        if unknown:
            raise ValueError('Unknown repository candidate(s): ' + ', '.join(unknown))
        requested = set(repo_names)
        return [item for item in CANDIDATES if item['repo'] in requested]
    if stage == 'all':
        return list(CANDIDATES)
    if stage == 'core':
        return [item for item in CANDIDATES if item['stage'] == 'core']
    if stage == 'fab':
        return [item for item in CANDIDATES if item['stage'].startswith('fab')]
    if stage == 'extended':
        return [item for item in CANDIDATES if item['stage'].startswith('extended')]
    raise ValueError('Unsupported repository selection.')


def git(*args, cwd=None):
    return subprocess.run(['git', *args], cwd=cwd, capture_output=True, text=True)

def main():
    p = argparse.ArgumentParser()
    selection = p.add_mutually_exclusive_group(required=True)
    selection.add_argument('--stage', choices=['core','fab','extended','all'],
                           help='Select a named candidate group; "all" requires explicit full-scope review.')
    selection.add_argument('--repo', action='append', metavar='OWNER/REPO',
                           help='Select one exact candidate from repos.json; repeat for additional approved candidates.')
    p.add_argument('--output', default=str(HOME / 'sources'))
    args = p.parse_args()
    try:
        selected = select_repositories(args.stage, args.repo)
    except ValueError as exc:
        p.error(str(exc))
    target = Path(args.output).resolve()
    try:
        target.relative_to(HOME.resolve())
    except ValueError:
        p.error('--output must remain inside the kit so its lock can be verified without recording host paths')
    prior_path = HOME / 'repos.lock.json'
    if prior_path.is_symlink():
        p.error('refusing symlinked repos.lock.json')
    target.mkdir(parents=True, exist_ok=True)
    output = []
    for r in selected:
        dest = target / r['repo'].replace('/','__')
        state = {'repo':r['repo'],'stage':r['stage'],'expected_license':r['license_expected'],'path':dest.relative_to(HOME).as_posix(),'url':r['url']}
        print(f"[{r['rank']:02}] {r['repo']} ...", flush=True)
        if dest.is_symlink():
            state.update(status='INVALID_EXISTING_DIR');output.append(state);print('FAILED');continue
        if not dest.exists():
            result = git('clone','--depth','1','--single-branch','--no-tags','--',r['url'],str(dest))
            if result.returncode != 0:
                state.update(status='CLONE_FAILED',error=result.stderr[-1800:]);output.append(state); print('FAILED');continue
        if not (dest / '.git').is_dir() or (dest / '.git').is_symlink():
            state.update(status='INVALID_EXISTING_DIR');output.append(state);print('FAILED');continue
        sha = git('-C',str(dest),'rev-parse','HEAD')
        origin = git('-C',str(dest),'remote','get-url','origin')
        if sha.returncode or origin.returncode or origin.stdout.strip().rstrip('/').removesuffix('.git').lower() != r['url'].rstrip('/').removesuffix('.git').lower():
            state.update(status='GIT_MISMATCH_OR_ERROR');output.append(state);print('FAILED');continue
        license_files = [str(x.relative_to(dest)) for x in dest.iterdir() if x.is_file() and x.name.lower().startswith(('license','licence','copying'))]
        state.update(status='CLONED_PENDING_AUDIT',sha=sha.stdout.strip(),license_files=license_files,has_submodules=(dest/'.gitmodules').exists(),has_lfs_pointers='not_checked')
        output.append(state)
        print('OK '+state['sha'][:12])
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
