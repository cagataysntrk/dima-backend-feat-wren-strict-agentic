#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
import uuid
from pathlib import Path

import httpx


def login(base_url: str, email: str, password: str) -> str:
    r=httpx.post(base_url+"/api/session",json={"username":email,"password":password},timeout=30)
    r.raise_for_status()
    token=r.json().get("id")
    if not token:
        raise RuntimeError("restricted session token missing")
    return str(token)


def wait_catalog(client: httpx.Client, timeout: int=240) -> dict:
    deadline=time.time()+timeout
    last=None
    while time.time()<deadline:
        try:
            r=client.post("/api/agent/v1/search",json={"term_queries":["satis_siparisleri"],"semantic_queries":[]})
            if r.status_code==200:
                body=r.json()
                data=body.get("data") or []
                if data:
                    return {"search_total":body.get("total_count"),"first":data[0]}
                last={"status":r.status_code,"body":body}
            else:
                last={"status":r.status_code,"text":r.text[:500]}
        except Exception as exc:
            last=repr(exc)
        time.sleep(3)
    raise RuntimeError(f"catalog not ready: {last}")


def parse_stream(response: httpx.Response) -> dict:
    text_parts=[]
    tool_calls=[]
    tool_results=[]
    data_parts=[]
    starts=[]
    finishes=[]
    errors=[]
    raw_lines=[]
    for line in response.iter_lines():
        if not line:
            continue
        raw_lines.append(line)
        prefix,payload=(line.split(":",1)+[""])[:2] if ":" in line else ("",line)
        try:
            obj=json.loads(payload)
        except Exception:
            obj=payload
        if prefix=="0":
            if isinstance(obj,str):
                text_parts.append(obj)
        elif prefix=="2":
            data_parts.append(obj)
        elif prefix=="9":
            tool_calls.append(obj)
        elif prefix=="a":
            tool_results.append(obj)
        elif prefix=="3":
            errors.append(obj)
        elif prefix=="d":
            finishes.append(obj)
        elif prefix=="f":
            starts.append(obj)
    return {
        "answer_text":"".join(text_parts),
        "tool_calls":tool_calls,
        "tool_results":tool_results,
        "data_parts":data_parts,
        "starts":starts,
        "finishes":finishes,
        "errors":errors,
        "raw_line_count":len(raw_lines),
    }


def extract_generated_query(parsed: dict):
    for part in parsed["data_parts"]:
        if isinstance(part,dict) and part.get("type")=="generated_entity":
            value=part.get("value") or {}
            query=(value.get("query") or {}).get("query")
            if isinstance(query,dict):
                return query
    return None


def extract_state(parsed: dict):
    states=[]
    for part in parsed["data_parts"]:
        if isinstance(part,dict) and part.get("type")=="state":
            states.append(part.get("value"))
    return states[-1] if states else None


def safe_version(props):
    candidates={}
    if isinstance(props,dict):
        for key,value in props.items():
            if "version" in str(key).lower() and isinstance(value,(str,int,float,bool,type(None),dict)):
                candidates[str(key)]=value
    return candidates


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base-url",required=True)
    ap.add_argument("--email",required=True)
    ap.add_argument("--password",required=True)
    ap.add_argument("--question",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    base=args.base_url.rstrip("/")
    token=login(base,args.email,args.password)
    headers={"X-Metabase-Session":token,"Accept":"application/json"}
    with httpx.Client(base_url=base,headers=headers,timeout=60) as client:
        props=client.get("/api/session/properties").json()
        perms_resp=client.get("/api/metabot/permissions/user-permissions")
        perms_resp.raise_for_status()
        catalog=wait_catalog(client)
        body={
            "profile_id":"nlq",
            "message":args.question,
            "context":{},
            "conversation_id":str(uuid.uuid4()),
            "history":None,
            "state":{},
            "debug":False,
        }
        started=time.perf_counter()
        with client.stream("POST","/api/metabot/agent-streaming",json=body,timeout=180) as response:
            status=response.status_code
            response.raise_for_status()
            parsed=parse_stream(response)
        latency=time.perf_counter()-started
        query=extract_generated_query(parsed)
        dataset_result=None
        if query is not None:
            rr=client.post("/api/dataset",json=query,timeout=120)
            dataset_result={"status":rr.status_code}
            if rr.status_code in (200, 202):
                body=rr.json()
                data=body.get("data") or {}
                dataset_result.update({
                    "rows":data.get("rows"),
                    "cols":data.get("cols"),
                    "row_count":len(data.get("rows") or []),
                    "database_id":body.get("database_id"),
                    "native_form":data.get("native_form"),
                })
            else:
                dataset_result["body"]=rr.text[:2000]
        out={
            "status_code":status,
            "question":args.question,
            "latency_seconds":round(latency,6),
            "session_version_fields":safe_version(props),
            "metabot_permissions":perms_resp.json(),
            "catalog_probe":catalog,
            "answer_text":parsed["answer_text"],
            "tool_calls":parsed["tool_calls"],
            "tool_results":parsed["tool_results"],
            "data_parts":parsed["data_parts"],
            "errors":parsed["errors"],
            "finish":parsed["finishes"][-1] if parsed["finishes"] else None,
            "final_state":extract_state(parsed),
            "generated_query":query,
            "generated_query_dataset_result":dataset_result,
            "raw_line_count":parsed["raw_line_count"],
        }
        Path(args.output).write_text(json.dumps(out,ensure_ascii=False,indent=2,default=str)+"\n",encoding="utf-8")
        print(json.dumps({
            "status_code":status,
            "latency_seconds":out["latency_seconds"],
            "tool_names":[x.get("toolName") for x in parsed["tool_calls"] if isinstance(x,dict)],
            "errors":parsed["errors"],
            "has_generated_query":query is not None,
            "dataset_rows":None if dataset_result is None else dataset_result.get("rows"),
            "answer_text":out["answer_text"][:600],
            "session_version_fields":out["session_version_fields"],
            "metabot_permissions":out["metabot_permissions"],
        },ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
