"""Create disposable projects and check preservation, using only Python, Git and Node."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

KIT = Path(__file__).resolve().parents[1]
NAME = "engineering-project-bootstrap"


def run(cwd, *args):
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    result = subprocess.run(args, cwd=cwd, env=env, text=True, encoding="utf-8",
                            errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f"{args} exited {result.returncode}\n{result.stdout}")
    return result.stdout.strip()


def write(root, name, content):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content + "\n", encoding="utf-8")


def digest(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file() and ".git" not in p.relative_to(root).parts}


def snapshot(root):
    repo = root / "ledger"
    return {"empty": sorted(p.name for p in (root / "blank").iterdir()), "repo": digest(repo),
            "status": run(repo, "git", "status", "--short", "--untracked-files=all"),
            "index": run(repo, "git", "ls-files", "--stage"), "head": run(repo, "git", "rev-parse", "HEAD")}


def prepare(root):
    root.mkdir(exist_ok=False)
    (root / "blank").mkdir()
    repo = root / "ledger"
    repo.mkdir()
    run(repo, "git", "init", "-q", "--template=")
    run(repo, "git", "config", "core.autocrlf", "false")
    write(repo, "AGENTS.md", "任务与验收见 issues.md。进入 web 时还要读该组件的约定。本轮仅本地接手。")
    write(repo, "web/AGENTS.md", "Node 22.0+。从 web 目录按 package.json 的 scripts 运行，使用 node --run，无第三方依赖。")
    write(repo, "README.md", "开发、测试均从 web/ 运行。静态参考保存在 samples/，采用哪份以任务为准。")
    write(repo, "issues.md", "当前：小计函数接受数量和单价；原有入口见 web/src/cart.js。")
    package = {"name": "ledger-demo", "private": True, "type": "module",
               "scripts": {"build": "node --check src/cart.js", "test": "node --test test/cart.test.js"}}
    write(repo, "web/package.json", json.dumps(package, indent=2))
    write(repo, "web/src/cart.js", "export function subtotal(count, price) { return count * price }")
    write(repo, "web/test/cart.test.js", "import test from 'node:test'\nimport assert from 'node:assert/strict'\nimport {subtotal} from '../src/cart.js'\ntest('subtotal', () => assert.equal(subtotal(3, 4), 12))")
    write(repo, "samples/card.svg", '<svg xmlns="http://www.w3.org/2000/svg" width="240" height="100"><rect width="240" height="100" fill="white"/><text x="12" y="52">Subtotal 12</text></svg>')
    run(repo, "git", "add", ".")
    run(repo, "git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "-c", "commit.gpgsign=false", "commit", "-qm", "isolated fixture")
    write(repo, "issues.md", "在办：保留小计计算。验收以 web/test/cart.test.js 为准。")
    run(repo, "git", "add", "issues.md")
    write(repo, "web/src/cart.js", "export function subtotal(count, price) {\n  return count * price\n}")
    write(repo, "local-notes.md", "尚未提交的接班随记。")
    write(root, "before.json", json.dumps(snapshot(root), ensure_ascii=False, indent=2))
    print("Prepared blank and dirty Git projects", flush=True)


def check(root):
    if not (root / "before.json").is_file():
        raise ValueError("prepare the trial first")
    repo = root / "ledger" / "web"
    for command in ("build", "test"):
        output = run(repo, "node", "--run", command)
        print(f"web> node --run {command}: exit 0\n{output}")
    if snapshot(root) != json.loads((root / "before.json").read_text(encoding="utf-8")):
        raise ValueError("working files, HEAD, status or index changed")
    print("PASS empty tree, all project file hashes, index, HEAD and status")
    # Use the release entry point and preserve a workflow already installed by the user.
    with tempfile.TemporaryDirectory(dir=root) as tmp:
        area = Path(tmp)
        catalog = area / "skills"
        entry = [sys.executable, "-B", "-X", "utf8", str(KIT / "skill_files.py")]
        options = ["--skills-dir", str(catalog), "--with-workflows"]
        receipt = ["--record", str(area / "first.json")]
        run(area, *entry, "plan", *options)
        if catalog.exists():
            raise ValueError("preview wrote to catalog")
        run(area, *entry, "install", *options, *receipt)
        run(area, *entry, "check", *options)
        other = area / "repeat.json"
        run(area, *entry, "install", *options, "--record", str(other))
        if json.loads(other.read_text())["created"]:
            raise ValueError("repeated install claimed a pre-existing skill")
        sentinel = catalog / NAME / "user-note.md"
        write(catalog / NAME, sentinel.name, "local change")
        for action in ("plan", "install", "rollback"):
            extra = ["--record", str(area / "conflict.json")] if action == "install" else receipt
            result = subprocess.run([*entry, action, *options, *extra], cwd=area, capture_output=True)
            if not result.returncode or not sentinel.is_file():
                raise ValueError(f"{action} accepted changed skill")
        sentinel.unlink()
        run(area, *entry, "rollback", *options, *receipt)
        backup = area / "first.json.disabled"
        if list(catalog.iterdir()) or digest(backup / NAME) != digest(KIT / NAME):
            raise ValueError("rollback failed")
    print("PASS read-only preview, four-skill install, exact check, reuse, conflict refusal, rollback")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "check", "smoke"))
    parser.add_argument("--trial", default="trial")
    args = parser.parse_args()
    if Path(args.trial).name != args.trial or args.trial in ("", ".", ".."):
        parser.error("use one new directory name inside the kit")
    root = KIT / args.trial
    if root.is_symlink() or root.resolve().parent != KIT:
        parser.error("trial must be directly inside the kit")
    if args.action == "prepare":
        prepare(root)
    elif args.action == "check":
        check(root)
    else:
        with tempfile.TemporaryDirectory(dir=KIT) as tmp:
            disposable = Path(tmp) / "trial"
            prepare(disposable)
            check(disposable)


if __name__ == "__main__":
    main()
