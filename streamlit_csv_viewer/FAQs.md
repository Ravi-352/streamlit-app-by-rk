# Q. checking different directories and their ownerships

Ans: 
```
 docker exec -i --user root ccad9b940c0 /opt/venv/bin/python - <<'PY'
import os, stat
print("uid,gid =", os.getuid(), os.getgid())
print("HOME =", os.environ.get("HOME"))
print("STREAMLIT_HOME =", os.environ.get("STREAMLIT_HOME"))
print("TMPDIR =", os.environ.get("TMPDIR"))
paths = ["/home", "/home/appuser", "/app", "/app/.streamlit", "/app/tmp", "/app/data"]
for p in paths:
    exists = os.path.exists(p)
    if exists:
        s = os.stat(p)
        print(p, "EXISTS mode", oct(s.st_mode), "uid", s.st_uid, "gid", s.st_gid)
    else:
        print(p, "MISSING")
PY
```

OUTPUT:  
```
uid,gid = 0 0
HOME = /root
STREAMLIT_HOME = /app/.streamlit
TMPDIR = /app/tmp
/home EXISTS mode 0o40755 uid 65532 gid 65532
/home/appuser MISSING
/app EXISTS mode 0o40755 uid 1000 gid 1000
/app/.streamlit MISSING
/app/tmp MISSING
/app/data EXISTS mode 0o40755 uid 0 gid 0
```

# Q. Creating missing direcotries with appropriate ownership.

Ans:  
```
 docker exec -i --user root ccad9b940c04 /opt/venv/bin/python - <<'PY'
import os, sys
uid = 1000
gid = 1000
for p in ("/home/appuser","/app/.streamlit","/app/tmp"):
    try:
        os.makedirs(p, exist_ok=True)
        os.chown(p, uid, gid)
        print("OK:", p)
    except Exception as e:
        print("ERR:", p, e)
PY
```

OUTPUT:  
```
OK: /home/appuser
OK: /app/.streamlit
OK: /app/tmp
```

Q. Troubleshooting storage leak by wsl - wsl mount space keeps exapnding but never release disk. If we have windows pro - we have option to optimize virtual disk usage. But in case no, we have to do manual cleaning. How shall we do that?

Ans: 
From Powershell - Troubleshoot path of wsl that is leaking disk storage. ---> on of the below must give appropriate output.

```
 Get-ChildItem "C:\Users\$env:USERNAME\AppData\Local\Docker\wsl\data" -Recurse -Filter *.vhdx -ErrorAction SilentlyContinue |
>> Select-Object FullName,@{N='SizeGB';E={"{0:N2}" -f ($_.Length/1GB)}}

 Get-ChildItem "C:\Users\$env:USERNAME\AppData\Local\DockerDesktop" -Recurse -Filter *.vhdx -ErrorAction SilentlyContinue |
>> Select-Object FullName,@{N='SizeGB';E={"{0:N2}" -f ($_.Length/1GB)}}

# In our case this worked - 
PS C:\Users\ARKiran> Get-ChildItem "C:\Users\$env:USERNAME\AppData\Local\wsl" -Recurse -Filter *.vhdx -ErrorAction SilentlyContinue |
>> Select-Object FullName,@{N='SizeGB';E={"{0:N2}" -f ($_.Length/1GB)}}
```

OUTPUT sample:  
```

FullName                                                                            SizeGB
--------                                                                            ------
C:\Users\ARKiran\AppData\Local\wsl\{62458a0c-5062-4aa4-8593-a1d31a030e30}\ext4.vhdx 54.09
```
Before proceeding for cleanup --
<img width="497" height="107" alt="image" src="https://github.com/user-attachments/assets/2c6a7534-1612-496d-8e49-7bd4e1892f5f" />


### ✅ Step 1 — inside WSL: Fill free space with zeroes
SO now we run below commands from **unix shell (wsl terminal)**:  
```
sudo dd if=/dev/zero of=/zerofile bs=1M
sudo sync
sudo rm /zerofile
sudo sync

```
<img width="835" height="232" alt="image" src="https://github.com/user-attachments/assets/de86e97d-f2f2-46a7-b102-8a577cbacf18" />


### ✅ Step 2 — Open Powershell and Shut down WSL completely

```
wsl --shutdown

```

### ✅ Step 2 — Open Powershell as Administrator and ---  
From above sample output, our GUID = 62458a0c-5062-4aa4-8593-a1d31a030e30

```
diskpart
select vdisk file="C:\Users\ARKiran\AppData\Local\wsl\{62458a0c-5062-4aa4-8593-a1d31a030e30}\ext4.vhdx"
attach vdisk readonly
compact vdisk
detach vdisk
exit

```
<img width="912" height="373" alt="image" src="https://github.com/user-attachments/assets/9ef366dd-4f8e-4e6c-8092-e4268e39bcd3" />

After cleanup -->  


#### what does the command do -->  ```sudo dd if=/dev/zero of=/zerofile bs=1M``` ?

- Creates a big temporary file named /zerofile
- Fills it with zeros (0x00 bytes) until there is no free space left
- Purpose: overwrite deleted/unused disk blocks with zeros

When Windows tries to shrink the VHDX, it can only reduce size where free space is zero-filled.
Random garbage data cannot be compressed.

✅ So this prepares the filesystem to be shrinkable.

## Q. How do you clean Disk in windows.
Ans: Clean Manager tool in windows. Run ```cleanmgr``` in Powershell. It opens up a GUI and we need to specify what to clean.

Alternately. we can directly give - ```cleanmgr /verylowdisk``` --
- Runs Disk Cleanup automatically
- Assumes the disk is critically low on space
- Cleans everything it safely can without asking
- Automatically deletes temporary files, old logs, cache, Recycle Bin, etc
It behaves like: “Disk is full. Clean as much as possible without asking user.
