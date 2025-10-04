#!/usr/bin/env python3
import git_filter_repo as fr

# Paths to be removed entirely from history
PATHS_TO_REMOVE = [
    b"tests/",
    b"code/dep_codecs/lib/",
    b"code/dep_codecs/include/",
    b"code/dep_external/lib/",
    b"code/win32/VS2015/.vs/",
    b"code/win32/VS2015/iamf.opensdf",
    b"code/win32/VS2015/iamf.sdf",
    b"code/win32/VS2022/.vs/",
    b"code/win32/VS2022/iamf.opensdf",
    b"code/win32/VS2022/iamf.sdf",
    b"code/win64/VS2022/.vs/",
    b"code/win64/VS2022/iamf.opensdf",
    b"code/win64/VS2022/iamf.sdf",
]

# Track blob ID to filename mapping
blob_to_filename = {}

def should_use_crlf(filename: bytes) -> bool:
    """Determine if file should use CRLF line endings."""
    path = filename.decode("utf-8", errors="ignore")
    name = path.split("/")[-1]

    if name == "CMakeLists.txt":
        return True

    crlf_extensions = [".sln", ".vcxproj", ".vcxproj.filters", ".props"]
    return any(path.endswith(ext) for ext in crlf_extensions)

def normalize_line_endings(data: bytes, use_crlf: bool) -> bytes:
    """Normalize all line endings to LF, then optionally convert to CRLF."""
    data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return data.replace(b"\n", b"\r\n") if use_crlf else data

def commit_callback(commit, metadata):
    """Remove unwanted paths and build blob-to-filename map."""
    # Filter out unwanted paths entirely
    commit.file_changes = [
        change
        for change in commit.file_changes
        if not any(change.filename.startswith(p) for p in PATHS_TO_REMOVE)
    ]

    # Track blob IDs for line-ending normalization
    for change in commit.file_changes:
        if change.type in (b"A", b"M") and change.blob_id:
            blob_to_filename[change.blob_id] = change.filename

def blob_callback(blob, metadata):
    """Normalize line endings in text blobs based on filename."""
    if not blob.data:
        return

    # Skip binary blobs
    if b"\x00" in blob.data[:8192]:
        return

    filename = blob_to_filename.get(blob.original_id)
    use_crlf = should_use_crlf(filename) if filename else False
    blob.data = normalize_line_endings(blob.data, use_crlf)

if __name__ == "__main__":
    args = fr.FilteringOptions.parse_args(["--force"])
    filter = fr.RepoFilter(
        args,
        commit_callback=commit_callback,
        blob_callback=blob_callback
    )
    filter.run()
