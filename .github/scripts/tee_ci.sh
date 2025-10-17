#!/usr/bin/env bash
set -euo pipefail
title="$1"; shift
mkdir -p ci
: > ci/last.txt   # reset au 1er appel
echo -e "\n=== ${title} ===" | tee -a ci/last.txt
"$@" 2>&1 | tee -a ci/last.txt
