#!/bin/sh
# Builds every target with the same flags, then strips the symbol names in a separate step
# (the -s linker flag is ignored on macOS, which left names in). Build on the machine that runs the study.
#
# Sources default to targets/src. Their comments state each program's behaviour (the answers), so
# on the run machine keep them outside the repo and point at them: SRC=~/rea-study-src ./scripts/build_targets.sh
# A target is either one file (SRC/name.c) or a folder of .c files (SRC/name/*.c) built together.
# Go targets are cross-built ahead of time and shipped as ready-made binaries in targets/prebuilt/.
set -e
cd "$(dirname "$0")/.."
SRC="${SRC:-targets/src}"
ls "$SRC"/*.c "$SRC"/*/*.c >/dev/null 2>&1 || { echo "no .c files in $SRC (set SRC=/path/to/sources)"; exit 1; }
mkdir -p targets/bin
FLAGS="-O1 -DDJB2_EXPECTED=0x16c91852UL"
finish() {
  strip "$1"
  # on Apple silicon, stripping breaks the signature and the system kills unsigned programs
  if [ "$(uname -s)" = "Darwin" ]; then codesign -s - -f "$1" 2>/dev/null; fi
}
for src in "$SRC"/*.c; do
  out="targets/bin/$(basename "$src" .c)"
  cc $FLAGS -o "$out" "$src" -lm
  finish "$out"
done
for dir in "$SRC"/*/; do
  ls "$dir"*.c >/dev/null 2>&1 || continue
  out="targets/bin/$(basename "$dir")"
  cc $FLAGS -o "$out" "$dir"*.c -lm
  finish "$out"
done
for pre in targets/prebuilt/*; do
  [ -f "$pre" ] || continue
  cp "$pre" "targets/bin/$(basename "$pre")"
  chmod +x "targets/bin/$(basename "$pre")"
done
echo "built: $(ls targets/bin | wc -l | tr -d ' ') targets with $(cc --version | head -1)"
uname -srm
