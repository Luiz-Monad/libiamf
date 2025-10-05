#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

# Resolve paths relative to the project root (two levels up from this script)
ROOT = Path(__file__).resolve().parents[3]
UPSTREAM = str(ROOT / "source")
ORIGIN = str(ROOT / "target")
TMP = str(ROOT / "workdir")

def logrun(cmd, cwd=None):
    wd=("" if cwd is None else str(cwd))
    rwd=wd.replace(str(ROOT), "")
    print("+", rwd, (" ".join(cmd)))

def run(cmd, cwd=None):
    logrun(cmd, cwd=cwd)
    subprocess.run(cmd, cwd=cwd, check=True)

def runout(cmd, cwd=None):
    logrun(cmd, cwd=cwd)
    return subprocess.check_output(cmd, cwd=cwd).decode()

def clean_dir(path):
    if os.path.exists(path):
        run(["rm", "-rf", path])
    os.makedirs(path)

def get_upstream_worktree():
    return Path(TMP) / "upstream_worktree"

def ensure_upstream_worktree():
    """Ensure we have a non-bare clone to checkout commits from."""
    worktree = get_upstream_worktree()
    if worktree.exists():
        run(["rm", "-rf", str(worktree)])
    run(["cp", "-fR", UPSTREAM, str(worktree)])
    return str(worktree)

def normalize_workdir(workdir, branch):
    """Call normalize.py with the upstream SHA for tracking."""
    sha = runout(cwd=str(workdir), cmd=[
        "git", "rev-parse", "HEAD"
    ]).splitlines()[0]
    run(cwd=str(workdir), cmd=[
        "python3",
        str(Path(ORIGIN) / ".github" / "workflows" / "normalize.py"),
        "--until-sha", sha
    ])
    run(cwd=str(workdir), cmd=[
        "git", "branch", branch
    ])

def get_commits(workdir, branch):
    """Get commit list from upstream."""
    output = runout(cwd=str(workdir), cmd=[
        "git", "rev-list", 
        "--reverse", 
        "--branches", branch
    ])
    return output.splitlines()

def prepare_worktree():
    os.chdir(ORIGIN)

    # Clean workspace and export upstream commit
    clean_dir(TMP)
    upstream_tree = ensure_upstream_worktree()

    # Apply normalization to TMP
    normalize_workdir(upstream_tree, "tree")

def replay_commits():

    # Read all commits
    upstream_tree = get_upstream_worktree()
    commits = get_commits(upstream_tree, "tree")

    for sha in commits:
        info = runout(cwd=upstream_tree, cmd=[
            "git", "show", 
            "-s", "--format=%an|%ae|%at|%s", 
            sha
        ]).strip().split("|")
        author_name, author_email, author_time, subject = info

        print(f"Replaying commit {sha[:7]}: {subject}")

        # Clean workspace and export upstream commit
        run(cwd=upstream_tree, cmd=[
            "git", "checkout", sha
        ])

        # Copy normalized content to normalized repo
        run([
            "rsync", "-a", 
            "--delete", 
            "--exclude=/.git", 
            "--exclude=/.github", 
            f"{upstream_tree}/",
            ORIGIN
        ])

        # Commit it
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = author_name
        env["GIT_AUTHOR_EMAIL"] = author_email
        env["GIT_AUTHOR_DATE"] = author_time
        env["GIT_COMMITTER_NAME"] = author_name
        env["GIT_COMMITTER_EMAIL"] = author_email
        env["GIT_COMMITTER_DATE"] = author_time
        run(cwd=ORIGIN, cmd=[
            "git", "add", "*"
        ])
        run(cwd=ORIGIN, cmd=[
            "git", "commit", 
            "--allow-empty",
            "-m", f"{subject}"
        ])

def config_git():
    run(["git", "config", "--global", "advice.detachedHead", "false"])
    run(["git", "config", "--global", "user.name", "GitHub Actions Bot"])
    run(["git", "config", "--global", "user.email", "actions@github.com"])

if __name__ == "__main__":
    config_git()
    prepare_worktree()
    replay_commits()
