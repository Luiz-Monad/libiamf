#!/usr/bin/env python3
import os
from pathlib import Path

from normalize import normalize_tree
from util import set_logroot, run, runout

# -----------------------------
# Configuration
# -----------------------------

# Resolve paths relative to the project root (two levels up from this script)
ROOT = Path(__file__).resolve().parents[3]
UPSTREAM = str(ROOT / "source")
ORIGIN = str(ROOT / "target")
TMP = str(ROOT / "workdir")

PATHS_TO_REMOVE = [
    "tests/",
    "code/dep_codecs/lib/",
    "code/dep_codecs/include/",
    "code/dep_external/lib/",
    "code/win32/VS2015/.vs/",
    "code/win32/VS2015/iamf.opensdf",
    "code/win32/VS2015/iamf.sdf",
    "code/win32/VS2022/.vs/",
    "code/win32/VS2022/iamf.opensdf",
    "code/win32/VS2022/iamf.sdf",
    "code/win64/VS2022/.vs/",
    "code/win64/VS2022/iamf.opensdf",
    "code/win64/VS2022/iamf.sdf",
]

# -----------------------------
# Helpers
# -----------------------------

set_logroot(ROOT)

def clean_dir(path):
    if os.path.exists(path):
        run(["rm", "-rf", path])
    os.makedirs(path)

def get_upstream_worktree():
    return Path(TMP) / "upstream_worktree"

def ensure_upstream_worktree(branch = "tree"):
    """Ensure we have a non-bare clone to checkout commits from."""
    worktree = get_upstream_worktree()
    if worktree.exists():
        run(["rm", "-rf", str(worktree)])
    run(["cp", "-fR", UPSTREAM, str(worktree)])
    run(["git", "branch", branch], str(worktree))

def is_upstream_commit_applied(sha):
    """Return True if this upstream commit SHA already exists in target history."""
    try:
        output = runout(cwd=ORIGIN, cmd=[
            "git", "log", "--grep", f"Upstream: {sha}", "--format=%H"
        ]).strip()
        return len(output) > 0
    except Exception:
        return False

# -----------------------------
# Normalization utilities
# -----------------------------

def normalize_workdir_tree(workdir):
    normalize_tree(Path(workdir), remove=PATHS_TO_REMOVE)

# -----------------------------
# Replay logic
# -----------------------------

def get_commits(workdir, branch):
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
    ensure_upstream_worktree()

def replay_commits():
    upstream_tree = get_upstream_worktree()
    commits = get_commits(upstream_tree, "HEAD")

    for sha in commits:
        info = runout(cwd=upstream_tree, cmd=[
            "git", "show",
            "-s", "--format=%an|%ae|%at|%s",
            sha
        ]).strip().split("|")
        author_name, author_email, author_time, subject = info
        msg = f"{subject}\n\nUpstream: {sha}"

        # Skip if already applied
        if is_upstream_commit_applied(sha):
            print(f"Skipping already applied commit {sha[:7]}: {subject}")
            continue
        
        print(f"Replaying commit {sha[:7]}: {subject}")

        # Checkout commit
        run(cwd=upstream_tree, cmd=[
            "git", "checkout", "--quiet", sha
        ])

        # Copy normalized content
        run([
            "rsync", "-a",
            "--delete",
            "--exclude=/.git",
            "--exclude=/.github",
            f"{upstream_tree}/",
            ORIGIN
        ])

        # Normalize in-place before rsync
        normalize_workdir_tree(ORIGIN)

        # Commit with same author
        env = os.environ.copy()
        env.update({
            "GIT_AUTHOR_NAME": author_name,
            "GIT_AUTHOR_EMAIL": author_email,
            "GIT_AUTHOR_DATE": author_time,
            "GIT_COMMITTER_NAME": author_name,
            "GIT_COMMITTER_EMAIL": author_email,
            "GIT_COMMITTER_DATE": author_time,
        })
        run(cwd=ORIGIN, cmd=[
            "git", "add", "-A"
        ])
        run(cwd=ORIGIN, cmd=[
            "git", "commit", 
            "--allow-empty",
            "-m", f"{msg}"
        ])

def config_git():
    run(["git", "config", "--global", "advice.detachedHead", "false"])
    run(["git", "config", "--global", "user.name", "GitHub Actions Bot"])
    run(["git", "config", "--global", "user.email", "actions@github.com"])
    run(["git", "config", "--global", "core.autocrlf", "false"])
    run(["git", "config", "--global", "core.safecrlf", "false"])

# -----------------------------
# Main
# -----------------------------

if __name__ == "__main__":
    config_git()
    prepare_worktree()
    replay_commits()
