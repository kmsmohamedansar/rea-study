#!/bin/sh
# Builds every target with the same flags, symbols stripped. Run on the machine that will run the study.
set -e
cd "$(dirname "$0")/.."
mkdir -p targets/bin
for src in targets/src/*.c; do
  name=$(basename "$src" .c)
  cc -O1 -s -DDJB2_EXPECTED=0x16c91852UL -o "targets/bin/$name" "$src"
done
echo "built: $(ls targets/bin | wc -l) targets with $(cc --version | head -1)"
uname -srm
