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
