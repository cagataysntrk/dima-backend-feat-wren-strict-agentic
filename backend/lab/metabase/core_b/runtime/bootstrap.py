#!/usr/bin/env python3
"""Bootstrap exact Core-B live Metabase runtime over the neutral fixture."""
from __future__ import annotations
import json, os, sys, time, urllib.error, urllib.parse, urllib.request

BASE=os.environ["METABASE_URL"].rstrip("/")
ADMIN_EMAIL=os.environ["MB_ADMIN_EMAIL"]
ADMIN_PASSWORD=os.environ["MB_ADMIN_PASSWORD"]
RESTRICTED_EMAIL=os.environ["MB_RESTRICTED_EMAIL"]
RESTRICTED_PASSWORD=os.environ["MB_RESTRICTED_PASSWORD"]
RESTRICTED_GROUP=os.environ.get("MB_RESTRICTED_GROUP","Dima Core B Restricted")
SITE_NAME=os.environ.get("MB_SITE_NAME","Dima Core B Seal")
DB_NAME=os.environ["ANALYTICS_DB_NAME"]
DB_USER=os.environ["ANALYTICS_DB_USER"]
DB_PASSWORD=os.environ["ANALYTICS_DB_PASSWORD"]
WAREHOUSE="Dima Core B Neutral Fixture"

class HttpError(RuntimeError):
    def __init__(self,status,body):
        super().__init__(f"HTTP {status}: {body}")
        self.status=status; self.body=body

def req(method,path,payload=None,session=None):
    data=None if payload is None else json.dumps(payload).encode()
    headers={"Accept":"application/json"}
    if payload is not None: headers["Content-Type"]="application/json"
    if session: headers["X-Metabase-Session"]=session
    request=urllib.request.Request(BASE+path,data=data,method=method,headers=headers)
    try:
        with urllib.request.urlopen(request,timeout=30) as response:
            raw=response.read()
            return response.status,(json.loads(raw) if raw else None)
    except urllib.error.HTTPError as exc:
        raw=exc.read()
        try: body=json.loads(raw) if raw else None
        except json.JSONDecodeError: body=raw.decode(errors="replace")
        raise HttpError(exc.code,body) from exc

def wait_health():
    last=None
    for _ in range(120):
        try:
            status,body=req("GET","/api/health")
            if status==200:
                print(json.dumps({"health":body},sort_keys=True)); return
        except Exception as exc: last=repr(exc)
        time.sleep(2)
    raise RuntimeError(f"Metabase health timeout: {last}")

def login(email,password):
    _,body=req("POST","/api/session",{"username":email,"password":password})
    token=str((body or {}).get("id") or "")
    if not token: raise RuntimeError("session token missing")
    return token

def setup():
    _,props=req("GET","/api/session/properties")
    if not bool((props or {}).get("has-user-setup")):
        token=(props or {}).get("setup-token")
        if not token: raise RuntimeError("setup token missing")
        _,body=req("POST","/api/setup",{
          "token":token,
          "user":{"email":ADMIN_EMAIL,"first_name":"Dima","last_name":"Core B Admin","password":ADMIN_PASSWORD},
          "prefs":{"allow_tracking":False,"site_name":SITE_NAME},
          "database":{
            "name":WAREHOUSE,"engine":"postgres",
            "details":{"host":"analytics-db","port":5432,"dbname":DB_NAME,"user":DB_USER,"password":DB_PASSWORD},
          },
        })
        return str((body or {}).get("id") or "") or login(ADMIN_EMAIL,ADMIN_PASSWORD)
    return login(ADMIN_EMAIL,ADMIN_PASSWORD)

def list_items(body):
    if isinstance(body,list): return body
    if isinstance(body,dict):
        for key in ("data","items"):
            if isinstance(body.get(key),list): return body[key]
    return []

def ensure_database(session):
    _,body=req("GET","/api/database",session=session)
    for item in list_items(body):
        if item.get("name")==WAREHOUSE: return int(item["id"])
    _,created=req("POST","/api/database",{
      "name":WAREHOUSE,"engine":"postgres",
      "details":{"host":"analytics-db","port":5432,"dbname":DB_NAME,"user":DB_USER,"password":DB_PASSWORD},
    },session=session)
    return int(created["id"])

def ensure_group(session):
    _,body=req("GET","/api/permissions/group",session=session)
    for item in list_items(body):
        if item.get("name")==RESTRICTED_GROUP:return int(item["id"])
    _,created=req("POST","/api/permissions/group",{"name":RESTRICTED_GROUP},session=session)
    return int(created["id"])

def ensure_user(session):
    _,body=req("GET","/api/user",session=session)
    for item in list_items(body):
        if item.get("email")==RESTRICTED_EMAIL:return int(item["id"])
    _,created=req("POST","/api/user",{
      "email":RESTRICTED_EMAIL,"first_name":"Dima","last_name":"Core B Restricted","password":RESTRICTED_PASSWORD
    },session=session)
    return int(created["id"])

def ensure_membership(session,user_id,group_id):
    _,body=req("GET","/api/permissions/membership",session=session)
    memberships=[]
    if isinstance(body,dict):
        memberships=body.get(str(group_id)) or body.get(group_id) or []
        if not memberships:
            memberships=[m for value in body.values() if isinstance(value,list) for m in value]
    if any(int(m.get("user_id",-1))==user_id and int(m.get("group_id",group_id))==group_id for m in memberships):
        return
    try:req("POST","/api/permissions/membership",{"user_id":user_id,"group_id":group_id},session=session)
    except HttpError as exc:
        if exc.status not in (400,409): raise

def setting(session,key,value):
    req("PUT","/api/setting/"+urllib.parse.quote(key,safe=""),{"value":value},session=session)

def wait_fixture(session,database_id):
    try:req("POST",f"/api/database/{database_id}/sync_schema",{},session=session)
    except HttpError as exc:
        if exc.status not in (200,202,204): raise
    last=None
    for _ in range(90):
        try:
            _,body=req("GET",f"/api/database/{database_id}/metadata",session=session)
            tables=(body or {}).get("tables") if isinstance(body,dict) else None
            if isinstance(tables,list):
                for table in tables:
                    if table.get("name")=="machine_operations":
                        names={f.get("name") for f in (table.get("fields") or []) if isinstance(f,dict)}
                        required={"event_date","department","machine_id","machine_downtime_minutes","fault_count","performance_score"}
                        if required.issubset(names):
                            return
            last=str(body)[:500]
        except Exception as exc:last=repr(exc)
        time.sleep(2)
    raise RuntimeError(f"fixture metadata sync timeout: {last}")

def main():
    wait_health()
    admin=setup()
    setting(admin,"ai-features-enabled?",True)
    setting(admin,"agent-api-enabled?",True)
    setting(admin,"mcp-execute-sql-enabled",False)
    database_id=ensure_database(admin)
    group_id=ensure_group(admin)
    user_id=ensure_user(admin)
    ensure_membership(admin,user_id,group_id)
    wait_fixture(admin,database_id)
    restricted=login(RESTRICTED_EMAIL,RESTRICTED_PASSWORD)
    _,current=req("GET","/api/user/current",session=restricted)
    if not isinstance(current,dict) or current.get("is_superuser"):
        raise RuntimeError("restricted user is missing or unexpectedly superuser")
    print(json.dumps({"bootstrap":"ok","database_id":database_id,"restricted_user_id":user_id},sort_keys=True))

if __name__=="__main__":
    try:main()
    except Exception as exc:
        print(f"bootstrap failed: {exc}",file=sys.stderr); raise
