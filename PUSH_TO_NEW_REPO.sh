#!/bin/bash
# Push Mordomo 3.0 to new dedicated repository
# Run this after creating https://github.com/aamsilva/mordomo3-edp

cd ~/clawd/projects/mordomo3-edp

# Remove old remote
git remote remove origin 2>/dev/null || true

# Add new remote
git remote add origin https://github.com/aamsilva/mordomo-edp.git

# Push to new repo
git push -u origin main

echo "✅ Mordomo 3.0 pushed to https://github.com/aamsilva/mordomo3-edp"
