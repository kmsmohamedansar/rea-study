#!/bin/sh
# Builds every target with the same flags, then strips the symbol names in a separate step
# (the -s linker flag is ignored on macOS, which left names in). Build on the machine that runs the study.
set -e
cd "$(dirname "$0")/.."
mkdir -p targets/bin
for src in targets/src/*.c; do
  name=$(basename "$src" .c)
  out="targets/bin/$name"
  cc -O1 -DDJB2_EXPECTED=0x16c91852UL -o "$out" "$src"
  strip "$out"
  # on Apple silicon, stripping breaks the signature and the system kills unsigned programs
  if [ "$(uname -s)" = "Darwin" ]; then codesign -s - -f "$out" 2>/dev/null; fi
done
echo "built: $(ls targets/bin | wc -l | tr -d ' ') targets with $(cc --version | head -1)"
uname -srm
