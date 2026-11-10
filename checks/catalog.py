"""Check what Codex exposes to a plain-language request with an isolated local home."""
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile

KIT = Path(__file__).resolve().parents[1]
NAME = "engineering-project-bootstrap"
PROMPT = "接管这个项目，按我的标准软件工程工作流准备开发。"


def catalog_input(area, project):
    home = area / "user"
    codex_home = home / ".codex"
    codex_home.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    for key in list(env):
        if key.startswith(("CODEX_", "OPENAI_", "OTEL_")):
            del env[key]
    for key, path in {"USERPROFILE": home, "HOME": home, "CODEX_HOME": codex_home,
                      "LOCALAPPDATA": home / "local", "APPDATA": home / "roaming",
                      "TEMP": area / "tmp", "TMP": area / "tmp",
                      "XDG_CONFIG_HOME": home / "config", "XDG_CACHE_HOME": home / "cache",
                      "XDG_STATE_HOME": home / "state", "XDG_DATA_HOME": home / "data"}.items():
        path.mkdir(parents=True, exist_ok=True)
        env[key] = str(path)
    env.update({"HTTP_PROXY": "http://127.0.0.1:1", "HTTPS_PROXY": "http://127.0.0.1:1",
                "ALL_PROXY": "http://127.0.0.1:1", "NO_PROXY": ""})
    result = subprocess.run(["codex", "debug", "prompt-input", PROMPT], cwd=project, env=env,
                            capture_output=True, timeout=50, encoding="utf-8", errors="replace")
    if result.returncode:
        raise RuntimeError(f"codex debug prompt-input exited {result.returncode}: {result.stderr[-500:]}")
    return json.dumps(json.loads(result.stdout), ensure_ascii=False).replace("\\\\", "/")


def listed(content, skill):
    # Match the skill file in this isolated install, never just the words of the user prompt.
    if (skill / "SKILL.md").as_posix().casefold() in content.casefold():
        return True
    match = re.search(r"`(r[0-9]+)` = `" + re.escape(skill.parent.as_posix()) + r"`", content, re.I)
    return bool(match and f"(file: {match[1]}/{skill.name}/SKILL.md)" in content)


def main():
    with tempfile.TemporaryDirectory(dir=KIT) as tmp:
        area = Path(tmp)
        project = area / "project"
        project.mkdir()
        root = area / "user" / ".codex" / "skills"
        names = (NAME, "build-from-requirements", "change-existing-software", "rebuild-from-reference")
        options = ["--skills-dir", str(root), "--with-workflows", "--record", str(area / "trial.json")]
        for action, expected in (("install", True), ("rollback", False)):
            subprocess.run([sys.executable, "-B", str(KIT / "skill_files.py"), action, *options],
                           check=True, stdout=subprocess.PIPE)
            content = catalog_input(area, project)
            for name in names:
                if listed(content, root / name) != expected:
                    raise RuntimeError(f"unexpected catalog entry after {action}: {name}")
            print(f"PASS {action}, checked four exact skill paths in Codex prompt inputs")


if __name__ == "__main__":
    main()
