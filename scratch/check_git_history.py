import subprocess

cmd = "git log -S 153 -p"
res = subprocess.run(["git", "log", "-S", "153", "--oneline"], cwd=r"C:\IGRIS", capture_output=True, text=True)
print("Git log -S 153:", res.stdout[:500])

res2 = subprocess.run(["git", "log", "-S", "Tanglish: 115", "--oneline"], cwd=r"C:\IGRIS", capture_output=True, text=True)
print("Git log -S 'Tanglish: 115':", res2.stdout[:500])
