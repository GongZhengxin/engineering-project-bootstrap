"""Preview, install and disable this specific skill bundle. Uses the Python standard library."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from zipfile import ZipFile

BASE = Path(__file__).resolve().parent
NAME = "engineering-project-bootstrap"
WORKFLOWS = ("build-from-requirements", "change-existing-software", "rebuild-from-reference")
ARCHIVE_HASH = "f9a2602dccd2350849c26899558fa68b45bad54e13e6b31b848132eaac189897"


def linked(path):
    return path.is_symlink() or getattr(path, "is_junction", lambda: False)()


def files(folder):
    result = {}
    for path in folder.rglob("*"):
        if linked(path):
            raise ValueError(f"review linked path manually: {path}")
        if path.is_file():
            result[path.relative_to(folder).as_posix()] = path.read_bytes()
    return result


def sources(include_workflows):
    items = {NAME: files(BASE / NAME)}
    if not items[NAME].get("SKILL.md"):
        raise ValueError("missing packaged skill")
    if include_workflows:
        archive = BASE / "dependencies" / "engineering-skills-B1.zip"
        if hashlib.sha256(archive.read_bytes()).hexdigest() != ARCHIVE_HASH:
            raise ValueError("workflow archive hash differs")
        with ZipFile(archive) as bundle:
            for name in WORKFLOWS:
                prefix = f"skills/{name}/"
                items[name] = {path[len(prefix):]: bundle.read(path) for path in bundle.namelist()
                               if path.startswith(prefix) and not path.endswith("/")}
    return items


def inspect(root, items):
    missing, conflicts = [], []
    for name, expected in items.items():
        target = root / name
        if linked(target) or (target.exists() and not target.is_dir()):
            print("CONFLICT", target)
            conflicts.append(name)
        elif not target.exists():
            print("ADD", target)
            for relative in sorted(expected):
                print("  +", relative)
            missing.append(name)
        else:
            current = files(target)
            if current == expected:
                print("REUSE", target)
            else:
                conflicts.append(name)
                print("CONFLICT", target)
                for path in sorted(current.keys() | expected.keys()):
                    if current.get(path) != expected.get(path):
                        print("  differs", path)
    return missing, conflicts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "install", "check", "rollback"))
    parser.add_argument("--skills-dir", required=True, type=Path)
    parser.add_argument("--with-workflows", action="store_true")
    parser.add_argument("--record", type=Path, help="new receipt outside the skill root, required for install/rollback")
    args = parser.parse_args()
    root = args.skills_dir.expanduser().resolve()
    items = sources(args.with_workflows)
    record = args.record.expanduser().resolve() if args.record else None
    if args.action in ("install", "rollback") and (not record or record.is_relative_to(root)):
        parser.error("use a receipt path outside the skills directory")
    if args.action == "rollback":
        info = json.loads(record.read_text(encoding="utf-8"))
        if info["root"] != str(root):
            raise ValueError("receipt points to a different catalog")
        names = info["created"]
        backup = record.with_name(record.name + ".disabled")
        if not names:
            print("Nothing added by this install")
            return
        if any(name not in items for name in names):
            raise ValueError("repeat the original workflow option or review receipt")
        for name in names:
            target = root / name
            if linked(target) or not target.is_dir() or files(target) != items[name]:
                raise ValueError(f"review changed files before rollback: {target}")
        backup.mkdir(exist_ok=False)
        for name in names:
            shutil.move(str(root / name), str(backup / name))
            print("DISABLED", name)
        return

    missing, conflicts = inspect(root, items)
    if conflicts:
        raise SystemExit(2)
    if args.action == "check":
        raise SystemExit(1 if missing else 0)
    if args.action == "install":
        created = []
        with record.open("x", encoding="utf-8") as receipt:
            try:
                root.mkdir(parents=True, exist_ok=True)
                for name in missing:
                    target = root / name
                    target.mkdir()
                    created.append(name)
                    for relative, data in items[name].items():
                        path = target / relative
                        path.parent.mkdir(parents=True, exist_ok=True)
                        with path.open("xb") as output:
                            output.write(data)
                    if files(target) != items[name]:
                        raise ValueError(f"installed files differ: {target}")
            finally:
                json.dump({"root": str(root), "created": created}, receipt, indent=2)
        print("Receipt", record)


if __name__ == "__main__":
    main()
