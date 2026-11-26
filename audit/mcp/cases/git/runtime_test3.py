"""CASE 003 补测 3：submodule 里的 filter 驱动是否真的会在 super 的 git 操作中执行、加固后是否被挡住
"""
import shutil
import subprocess
from pathlib import Path

import git

import mcp_server_git.server as S

ROOT = Path("/tmp/case003c")
shutil.rmtree(ROOT, ignore_errors=True)
allowed = ROOT / "allowed"
allowed.mkdir(parents=True)


def run(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


def new_repo(path):
    path.mkdir(parents=True, exist_ok=True)
    run("init", "-q", "-b", "main", cwd=path)
    run("config", "user.email", "t@example.com", cwd=path)
    run("config", "user.name", "t", cwd=path)
    return path


sub = new_repo(allowed / "subsrc")
(sub / "s.txt").write_text("s\n")
(sub / ".gitattributes").write_text("* filter=evil2\n")
run("add", ".", cwd=sub)
run("commit", "-qm", "sub", cwd=sub)

sup = new_repo(allowed / "super")
(sup / "m.txt").write_text("m\n")
run("add", ".", cwd=sup)
run("commit", "-qm", "m", cwd=sup)
add = subprocess.run(
    ["git", "-c", "protocol.file.allow=always", "submodule", "add", "-q", str(sub), "sub"],
    cwd=sup, capture_output=True, text=True)
print("S1 submodule add rc:", add.returncode, add.stderr.strip()[:60])

marker = ROOT / "pwn_sub_filter"
sub_cfg = Path(sup / ".git" / "modules" / "sub" / "config")
cfg = sub_cfg.read_text()
if "evil2" not in cfg:
    sub_cfg.write_text(cfg + '\n[filter "evil2"]\n\tsmudge = touch ' + str(marker) + '\n\tclean = cat\n')
print("S2 submodule config 有 evil2:", "evil2" in sub_cfg.read_text())

print("S3 枚举（未加固前）:", sorted(S._submodule_drivers(git.Repo(sup))))

marker.unlink(missing_ok=True)
(sup / "sub" / "s.txt").write_text("changed\n")
run("status", "--porcelain", cwd=sup / "sub")
print("S4 对照：submodule 内直接 git status -> marker:", marker.exists())

marker.unlink(missing_ok=True)
rs = git.Repo(sup)
S.harden_repo(rs)
print("S5 harden 后枚举:", sorted(S._submodule_drivers(rs)))
(sup / "sub" / "s.txt").write_text("changed2\n")
try:
    out = S.git_status(rs)
    print("S6 harden 后 S.git_status 正常:", out.splitlines()[0][:30])
except Exception as e:
    print("S6 git_status 失败:", type(e).__name__, str(e)[:70])
print("S7 harden 后 super 操作 -> marker:", marker.exists())

marker.unlink(missing_ok=True)
(sup / "sub" / "s.txt").write_text("changed3\n")
try:
    rs.git.add(A=True)
    print("S8 harden 后 rs.git.add(A=True) 成功")
except Exception as e:
    print("S8 add 失败:", type(e).__name__, str(e)[:70])
print("S9 harden 后 add -> marker:", marker.exists())
