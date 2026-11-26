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

print("== C submodule 的 clean 驱动：基线 vs 加固（配置写在硬固之前） ==")
root2 = ROOT / "c"
root2.mkdir(parents=True, exist_ok=True)
sub2 = new_repo(root2 / "subsrc")
(sub2 / "s.txt").write_text("s\n")
(sub2 / ".gitattributes").write_text("* filter=evil3\n")
run("add", ".", cwd=sub2)
run("commit", "-qm", "sub2", cwd=sub2)
sup2 = new_repo(root2 / "super")
(sup2 / "m.txt").write_text("m\n")
run("add", ".", cwd=sup2)
run("commit", "-qm", "m2", cwd=sup2)
add2 = subprocess.run(
    ["git", "-c", "protocol.file.allow=always", "submodule", "add", "-q", str(sub2), "sub"],
    cwd=sup2, capture_output=True, text=True)
print("C0 submodule add rc:", add2.returncode)
m2mark = root2 / "pwn_clean"
cfg2 = Path(sup2 / ".git" / "modules" / "sub" / "config")
cfg2.write_text(cfg2.read_text() + f'\n[filter "evil3"]\n\tclean = touch {m2mark}\n\tsmudge = cat\n')

m2mark.unlink(missing_ok=True)
(sup2 / "sub" / "s.txt").write_text("c1\n")
run("add", "s.txt", cwd=sup2 / "sub")
print("C1 对照 submodule 内 git add -> marker:", m2mark.exists())

m2mark.unlink(missing_ok=True)
rs2 = git.Repo(sup2)
S.harden_repo(rs2)
(sup2 / "sub" / "s.txt").write_text("c2\n")
try:
    rs2.git.add(A=True)
    print("C2 harden 后 add 成功")
except Exception as e:
    print("C2 add 失败:", type(e).__name__, str(e)[:60])
print("C3 harden 后 add -> marker:", m2mark.exists())

