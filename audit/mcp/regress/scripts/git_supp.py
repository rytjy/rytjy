"""CASE 003 补测：真实 hook / bare 仓库 / submodule driver / 未配 --repository
环境同 runtime_test.py：venv + mcp-server-git 2026.11.18，git 2.43.0
"""
import shutil
import subprocess
from pathlib import Path

import git

import mcp_server_git.server as S

ROOT = Path("/tmp/case003b")
shutil.rmtree(ROOT, ignore_errors=True)
ROOT.mkdir(parents=True)
allowed = ROOT / "allowed"
allowed.mkdir()


def run(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


def new_repo(path):
    path.mkdir(parents=True, exist_ok=True)
    run("init", "-q", "-b", "main", cwd=path)
    run("config", "user.email", "t@example.com", cwd=path)
    run("config", "user.name", "t", cwd=path)
    return path


print("== H1 真实 pre-commit hook ==")
hookrepo = new_repo(allowed / "hookrepo")
(hookrepo / "a.txt").write_text("1\n")
run("add", ".", cwd=hookrepo)
run("commit", "-qm", "init", cwd=hookrepo)
hooks = ROOT / "hooksdir"
hooks.mkdir()
pre = hooks / "pre-commit"
pre.write_text(f"#!/bin/sh\ntouch {ROOT}/pwn_hook\n")
pre.chmod(0o755)
run("config", "core.hooksPath", str(hooks), cwd=hookrepo)

marker = ROOT / "pwn_hook"
marker.unlink(missing_ok=True)
(hookrepo / "a.txt").write_text("2\n")
run("add", ".", cwd=hookrepo)
run("commit", "-qm", "baseline", cwd=hookrepo)
print("H1a 未加固 commit -> hook 执行:", marker.exists())

repo = git.Repo(hookrepo)
S.harden_repo(repo)
print("H1b harden 后 hooksPath:", repo.git.config("--show-scope", "core.hooksPath").strip().replace("\t", " | "))
marker.unlink(missing_ok=True)
(hookrepo / "a.txt").write_text("3\n")
repo.git.add(A=True)
try:
    repo.git.commit(m="hardened")
    print("H1c 加固后 commit 成功")
except Exception as e:
    print("H1c 加固后 commit 失败:", type(e).__name__, str(e)[:60])
print("H1d 加固后 commit -> hook 执行:", marker.exists())

print("== H2 bare 仓库 ==")
bare = allowed / "bare.git"
run("init", "-q", "--bare", str(bare), cwd=ROOT)
try:
    rb = git.Repo(bare)
    S.harden_repo(rb)
    S.validate_opened_repo(rb, bare, allowed)
    print("H2 allowed 内 bare 仓库: PASSED, bare =", rb.bare)
except Exception as e:
    print("H2 REFUSED:", type(e).__name__, str(e)[:80])

print("== H3 submodule driver ==")
sub = new_repo(allowed / "subsrc")
(sub / "s.txt").write_text("s\n")
run("add", ".", cwd=sub)
run("commit", "-qm", "sub", cwd=sub)
superp = new_repo(allowed / "super")
(superp / "m.txt").write_text("m\n")
run("add", ".", cwd=superp)
run("commit", "-qm", "m", cwd=superp)
add = subprocess.run(
    ["git", "-c", "protocol.file.allow=always", "submodule", "add", "-q", str(sub), "sub"],
    cwd=superp, capture_output=True, text=True)
print("H3a submodule add rc:", add.returncode, add.stderr.strip()[:60])
rs = git.Repo(superp)
S.harden_repo(rs)
drivers_before = S._submodule_drivers(rs)
print("H3b harden 后 _submodule_drivers:", sorted(drivers_before))
# 在 submodule 自己的 config 里放一个 driver，看枚举能不能看到
subcfg = Path(rs.submodules[0].module().git_dir) / "config" if rs.submodules else None
if subcfg and subcfg.exists():
    text = subcfg.read_text()
    if "[filter \"evil2\"]" not in text:
        subcfg.write_text(text + '\n[filter "evil2"]\n\tsmudge = touch ' + str(ROOT / "pwn_sub") + '\n')
    print("H3c submodule config 已写入 evil2:", 'evil2' in subcfg.read_text())
    print("H3d _submodule_drivers 是否枚举到 evil2:", "filter.evil2" in S._submodule_drivers(rs))
try:
    print("H3e harden 后 git_status 正常:", S.git_status(rs).splitlines()[0][:40])
except Exception as e:
    print("H3e git_status 失败:", type(e).__name__, str(e)[:60])

print("== H4 未配置 --repository ==")
try:
    S.validate_repo_path(Path("/etc"), None)
    print("H4 validate_repo_path(/etc, None): PASSED（无限制，属文档行为）")
except Exception as e:
    print("H4 REFUSED:", type(e).__name__, str(e)[:60])
