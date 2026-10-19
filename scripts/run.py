"""Runs one target through one arm with headless Claude Code and saves the raw result.

  python3 scripts/run.py t01 none
  python3 scripts/run.py t01 rea
  python3 scripts/run.py t04 rea --heldout     (held-out: refused unless --heldout, refused a second time)

Arms differ only in the tool: 'rea' adds REA's MCP server (pinned version). Same model, same
prompt, same built-in tools, same machine. Runs happen in an empty temp folder holding a copy of
the binary named 'target', so this repo's CLAUDE.md and source are not in the working folder. The answer key (targets/keys.json) is not kept on the run machine.
"""
import argparse, json, os, pathlib, platform, shutil, subprocess, sys, tempfile, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODEL = "claude-sonnet-5-5"
REA_VERSION = "6.7.0"
TOOLS = ["Bash", "Read", "Glob", "Grep"]
REA_MCP = {"mcpServers": {"rea": {"command": "npx", "args": ["-y", f"rea-agents@{REA_VERSION}", "mcp"]}}}

def load_prompt(path):
    text = (ROOT / "docs" / "prompt.md").read_text()
    quoted = [l[2:] for l in text.splitlines() if l.startswith("> ")]
    return "\n".join(quoted).replace("{PATH}", path)

def build_cmd(arm, prompt, mcp_file, claude="claude"):
    tools = TOOLS + (["mcp__rea"] if arm == "rea" else [])
    cmd = [claude, "-p", prompt, "--model", MODEL, "--output-format", "stream-json", "--verbose",
           "--no-session-persistence", "--permission-mode", "acceptEdits",
           "--allowedTools", *tools, "--strict-mcp-config"]
    if arm == "rea":
        cmd += ["--mcp-config", str(mcp_file)]
    return cmd

def parse_stream(text):
    """stream-json: one event per line. Returns (result_event, tool_counts, init_event)."""
    result, init, tools = None, None, {}
    for line in text.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "system" and ev.get("subtype") == "init":
            init = ev
        elif ev.get("type") == "assistant":
            for block in (ev.get("message") or {}).get("content") or []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tools[block.get("name", "?")] = tools.get(block.get("name", "?"), 0) + 1
        elif ev.get("type") == "result":
            result = ev
    return result, tools, init

def split_of(target, keys):
    return "heldout" if target in keys["split"]["heldout"] else "dev"

def check_allowed(target, arm, heldout_flag, keys, raw_dir):
    split = split_of(target, keys)
    if split == "heldout" and not heldout_flag:
        sys.exit(f"{target} is held out: pass --heldout, once the rules and prompt are frozen")
    if split == "dev" and heldout_flag:
        sys.exit(f"{target} is a dev target, drop --heldout")
    out = raw_dir / split / arm / f"{target}.json"
    if split == "heldout" and out.exists():
        sys.exit(f"{out} exists: held-out is scored once")
    return split, out

def main(argv=None, claude="claude"):
    ap = argparse.ArgumentParser()
    ap.add_argument("target"); ap.add_argument("arm", choices=["none", "rea"])
    ap.add_argument("--heldout", action="store_true")
    ap.add_argument("--claude-cmd", default=claude)
    ap.add_argument("--raw-dir", default=str(ROOT / "results" / "raw"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    keys = {"split": json.loads((ROOT / "targets" / "split.json").read_text())}
    if a.target not in keys["split"]["dev"] + keys["split"]["heldout"]:
        sys.exit(f"unknown target {a.target}")
    split, out = check_allowed(a.target, a.arm, a.heldout, keys, pathlib.Path(a.raw_dir))
    binary = next(iter((ROOT / "targets" / "bin").glob(f"{a.target}_*")), None)
    if binary is None:
        sys.exit("binary missing: run scripts/build_targets.sh on this machine first")
    work = pathlib.Path(tempfile.mkdtemp(prefix="reastudy-"))
    shutil.copy(binary, work / "target")
    mcp_file = work / ".mcp-rea.json"
    mcp_file.write_text(json.dumps(REA_MCP))
    cmd = build_cmd(a.arm, load_prompt(str(work / "target")), mcp_file, a.claude_cmd)
    if a.dry_run:
        print(" ".join(map(str, cmd))); return 0
    t0 = time.time()
    p = subprocess.run(cmd, cwd=work, capture_output=True, text=True)
    wall = round(time.time() - t0, 1)
    result, tools, init = parse_stream(p.stdout)
    if result is None:
        result = {"result": "", "parse_error": p.stdout[-500:]}
    version = subprocess.run([a.claude_cmd, "--version"], capture_output=True, text=True).stdout.strip()
    record = {"target": a.target, "arm": a.arm, "split": split, "model": MODEL, "effort": "default",
              "rea_version": REA_VERSION if a.arm == "rea" else None, "claude_version": version,
              "machine": f"{platform.system()} {platform.release()} {platform.machine()}",
              "date": time.strftime("%Y-%m-%d %H:%M"), "wall_s": wall, "exit": p.returncode,
              "stderr_tail": p.stderr[-500:], "tools_used": tools,
              "mcp_servers": (init or {}).get("mcp_servers"),
              "rea_tools_available": sum(1 for t in (init or {}).get("tools", []) if str(t).startswith("mcp__rea")),
              "raw": result}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=1))
    shutil.rmtree(work, ignore_errors=True)
    print(f"{a.target} {a.arm}: exit {p.returncode}, {wall}s -> {out}")
    return p.returncode

if __name__ == "__main__":
    sys.exit(main())
