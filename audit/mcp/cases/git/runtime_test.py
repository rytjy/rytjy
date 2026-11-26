"""CASE 003 运行测试：路径限制 / flag 注入 / harden_repo（hooks 与 filter）/ 打开后复核
环境：venv + mcp-server-git 2026.11.18（wheel sha256 已核），git 2.43.0
"""
import shutil
import subprocess
from pathlib import Path

import git

import mcp_server_git.server as S

ROOT = Path("/tmp/case003")
shutil.rmtree(ROOT, ignore_errors=True)
ROOT.mkdir(parents=True)
allowed = ROOT / "allowed"
outside = ROOT / "outside"
repo_dir = allowed / "repo"
for d in (allowed, outside, repo_dir):
    d.mkdir(parents=True)


def run(*args, cwd=repo_dir):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


print("== T1 validate_repo_path（配置了 --repository=allowed） ==")
cases = [
    ("allowed /repo", allowed / "repo"),
    ("allowed /repo/../repo", allowed / "repo" / ".." / "repo"),
    ("outside", outside),
    ("allowed/../outside", allowed / ".." / "outside"),
    ("/etc", Path("/etc")),
]
for name, path in cases:
    try:
        S.validate_repo_path(path, allowed)
        print(f"T1 {name}: PASSED")
    except ValueError as e:
        print(f"T1 {name}: REFUSED -> {str(e)[:60]}")
link = allowed / "link_out"
link.symlink_to(outside)
try:
    S.validate_repo_path(link, allowed)
    print("T1 symlink->outside: PASSED (未拦)")
except ValueError as e:
    print(f"T1 symlink->outside: REFUSED -> {str(e)[:60]}")

print("== T3 仓库自带配置能否让 git 执行程序（filter） ==")
run("init", "-q", "-b", "main")
run("config", "user.email", "t@example.com")
run("config", "user.name", "t")
run("config", "filter.evil.smudge", f"touch {ROOT}/pwn_filter")
run("config", "filter.evil.clean", "cat")
(repo_dir / ".gitattributes").write_text("* filter=evil\n")
(repo_dir / "f.txt").write_text("hello\n")
run("add", ".gitattributes", "f.txt")
run("commit", "-qm", "one")

marker = ROOT / "pwn_filter"
marker.unlink(missing_ok=True)
(repo_dir / "f.txt").unlink()
run("checkout", "--", "f.txt")  # 未加固：smudge 应执行
print("T3a 未加固 checkout -> marker:", marker.exists())

repo = git.Repo(repo_dir)
S.harden_repo(repo)
scope = repo.git.config("--show-scope", "core.hooksPath").strip()
print("T3b harden 后 core.hooksPath:", scope.replace("\t", " | "))
marker.unlink(missing_ok=True)
(repo_dir / "f.txt").unlink()
repo.git.checkout("--", "f.txt")  # 加固后：走 GitPython（server 内部走的就是这条），smudge 应被空命令覆盖
print("T3c 加固后 checkout（GitPython）-> marker:", marker.exists())
marker.unlink(missing_ok=True)
(repo_dir / "f.txt").unlink()
run("checkout", "--", "f.txt")  # 对照：进程外新起的 git 不继承 harden 环境
print("T3e 对照：进程外 git checkout -> marker:", marker.exists())
print("T3d .git/config 里 evil 配置仍在:", "evil" in (repo_dir / ".git" / "config").read_text())

print("== T2 flag 注入 ==")
for target in ["-x", "HEAD..-x"]:
    try:
        S.git_diff(repo, target)
        print(f"T2 {target}: PASSED (未拦)")
    except S.FlagInjectionError as e:
        print(f"T2 {target}: REFUSED -> {str(e)[:60]}")
    except Exception as e:
        print(f"T2 {target}: 其它异常 {type(e).__name__}: {str(e)[:60]}")

print("== T4 validate_opened_repo（.git 文件指向外部） ==")
fake = allowed / "fake"
fake.mkdir()
ext_gitdir = outside / "ext.gitdir"
subprocess.run(["git", "init", "-q", "--bare", str(ext_gitdir)], capture_output=True, text=True)
(fake / ".git").write_text(f"gitdir: {ext_gitdir}\n")
try:
    r2 = git.Repo(fake)
    S.harden_repo(r2)
    S.validate_opened_repo(r2, fake, allowed)
    print("T4: PASSED (未拦)")
except Exception as e:
    print(f"T4: REFUSED -> {type(e).__name__}: {str(e)[:90]}")
