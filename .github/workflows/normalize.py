import re
import sys

def should_use_crlf(filename):
    """Determine if file should use CRLF based on .gitattributes rules"""
    path = filename.decode('utf-8', errors='ignore')
    name = path.split('/')[-1]
    
    # CMakeLists.txt uses CRLF
    if name == 'CMakeLists.txt':
        return True
    
    # Visual Studio files use CRLF
    crlf_extensions = ['.sln', '.vcxproj', '.vcxproj.filters', '.props']
    for ext in crlf_extensions:
        if path.endswith(ext):
            return True
    
    # Everything else uses LF
    return False

# Store metadata across callbacks
blob_metadata = {}

def process_filename(filename, callback_metadata):
    """Store filename information for blob processing"""
    # This won't work well because blobs are processed before filenames
    pass

def process_blob(blob, callback_metadata):
    """Normalize line endings in blob data"""
    if not blob.data:
        return
    
    # Skip binary files (heuristic: contains null bytes in first 8KB)
    if b'\x00' in blob.data[:8192]:
        return
    
    # Since we can't reliably get filename in blob callback,
    # we'll store original blob data and process in commit callback
    blob_metadata[blob.original_id] = blob.data

def process_commit(commit, callback_metadata):
    """Process commits and their file changes"""
    for change in commit.file_changes:
        if change.type == b'D':  # Deletion
            continue
            
        if not change.blob_id:
            continue
        
        # Determine line ending based on filename
        needs_crlf = should_use_crlf(change.filename)
        
        # We can't easily modify blob data here, so we set mode instead
        # This is a limitation - we need a different approach
        pass

SCRIPT

echo "================================================================"
echo "ERROR: git-filter-repo blob callbacks cannot access filenames!"
echo "================================================================"
echo ""
echo "Use this alternative approach with a Python script instead:"
echo ""

cat > normalize_lineendings.py << 'PYTHONSCRIPT'
#!/usr/bin/env python3
import git_filter_repo as fr
import sys

# Track blob ID to filename mapping
blob_to_filename = {}

def should_use_crlf(filename):
    """Determine if file should use CRLF"""
    path = filename.decode('utf-8', errors='ignore')
    name = path.split('/')[-1]
    
    if name == 'CMakeLists.txt':
        return True
    
    crlf_extensions = ['.sln', '.vcxproj', '.vcxproj.filters', '.props']
    return any(path.endswith(ext) for ext in crlf_extensions)

def commit_callback(commit, metadata):
    """Build mapping of blob IDs to filenames"""
    for change in commit.file_changes:
        if change.blob_id and change.type in (b'M', b'A'):
            blob_to_filename[change.blob_id] = change.filename

def blob_callback(blob, metadata):
    """Normalize line endings based on filename"""
    if not blob.data:
        return
    
    # Skip binary files
    if b'\x00' in blob.data[:8192]:
        return
    
    # Get filename for this blob (if we've seen it)
    filename = blob_to_filename.get(blob.original_id)
    
    if not filename:
        # Default to LF if we don't know the filename
        blob.data = blob.data.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
        return
    
    needs_crlf = should_use_crlf(filename)
    
    if needs_crlf:
        # Normalize to LF first, then convert to CRLF
        data = blob.data.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
        blob.data = data.replace(b'\n', b'\r\n')
    else:
        # Convert to LF
        blob.data = blob.data.replace(b'\r\n', b'\n').replace(b'\r', b'\n')

# Run the filter
args = fr.FilteringOptions.parse_args(['--force'])
filter = fr.RepoFilter(args, commit_callback=commit_callback, blob_callback=blob_callback)
filter.run()
