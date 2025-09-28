# /bin/bash

cd target-repo

# Ensure git configuration is set up properly
git config user.name "GitHub Actions"
git config user.email "actions@github.com"

if [ ! -d ../patches ] || [ -z "$(ls -A ../patches/*.patch 2>/dev/null)" ]; then
  echo "No patches found or patches directory is empty"
  exit 0
fi

echo "Found $(ls ../patches/*.patch | wc -l) patch(es) to apply"

applied_count=0
skipped_count=0
failed_count=0
already_applied_count=0
failed_patches=()

for patch in ../patches/*.patch; do
  patch_name=$(basename "$patch")
  echo "=== Processing: $patch_name ==="
  
  if [ ! -f "$patch" ] || [ ! -s "$patch" ]; then
    echo "> Skipping invalid or empty patch"
    ((skipped_count++))
    continue
  fi
  
  # Check if patch is already applied
  if git apply --reverse --check "$patch" 2>/dev/null; then
    echo "> Patch already applied: $patch_name"
    ((already_applied_count++))
    continue
  fi
  
  # Check if patch can be applied
  if git apply --check "$patch" 2>&1; then
    echo "✓ Patch can be applied cleanly"
    echo "* Applying: $patch_name"
    
    # Apply the patch
    if git apply "$patch" 2>&1; then
      # Extract commit message from patch file
      commit_msg=$(grep -E '^Subject: |^Description:' "$patch" | head -1 | sed 's/^Subject: //;s/^Description: //')
      if [ -z "$commit_msg" ]; then
        # Fallback: use patch filename or generic message
        commit_msg="Apply $patch_name"
      fi
      
      # Commit the changes
      git add -A
      if git commit -m "$commit_msg"; then
        ((applied_count++))
        echo "✓ Successfully applied and committed: $patch_name"
      else
        echo "✗ Failed to commit applied patch: $patch_name"
        git reset --hard HEAD
        failed_patches+=("$patch_name")
        ((failed_count++))
      fi
    else
      echo "✗ Failed to apply patch: $patch_name"
      failed_patches+=("$patch_name")
      ((failed_count++))
      exit 1
    fi
  else      
    echo "✗ Patch cannot be applied: $patch_name"
    failed_patches+=("$patch_name")
    ((failed_count++))
  fi
  echo ""
done

echo "=== Final Summary ==="
echo "Applied: $applied_count"
echo "Already applied: $already_applied_count"
echo "Skipped: $skipped_count" 
echo "Failed: $failed_count"

if [ ${#failed_patches[@]} -gt 0 ]; then
  echo "Failed patches:"
  printf '  - %s\n' "${failed_patches[@]}"
fi

# Show final commit history
echo ""
echo "=== Final commit history ==="
git log --oneline -10

# Only fail if ALL patches failed and none were already applied
if [ $applied_count -eq 0 ] && [ $already_applied_count -eq 0 ] && [ $failed_count -gt 0 ]; then
  echo "Error: No patches were successfully applied"
  exit 1
fi