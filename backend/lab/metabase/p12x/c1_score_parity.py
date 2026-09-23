#!/usr/bin/env python3
"""P12X-C1 stock-vs-fork native capability parity scorer."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

EXPECTED_CORPUS = "fd6e5934438795f64e9ec7d64b74b56056c3c1304aa51598d18c170839b792a0"
EXPECTED_DB = "Dima Analytics Lab"


def load(path: Path) -> dict[str, Any]:
    obj=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj,dict):
        raise ValueError(f"{path} must be object")
    return obj


def tool_error_count(a: dict[str, Any]) -> int:
    n=0
    for item in a.get("tool_results") or []:
        if isinstance(item,dict) and (item.get("isError") is True or item.get("is_error") is True or item.get("error")):
            n+=1
    return n


def eq_cell(a: Any,b: Any,tol: float) -> bool:
    if isinstance(a,bool) or isinstance(b,bool):
        return a==b
    if isinstance(a,(int,float)) and isinstance(b,(int,float)):
        return math.isclose(float(a),float(b),rel_tol=0.0,abs_tol=float(tol))
    return a==b


def eq_row(a:list[Any],b:list[Any],tol:float)->bool:
    return len(a)==len(b) and all(eq_cell(x,y,tol) for x,y in zip(a,b))


def rows_match(observed:list[list[Any]], expected:list[list[Any]], comparison:str, tol:float)->bool:
    if comparison in {"scalar","single_row"}:
        return len(observed)==len(expected) and all(eq_row(a,b,tol) for a,b in zip(observed,expected))
    if comparison=="ordered_rows":
        return len(observed)==len(expected) and all(eq_row(a,b,tol) for a,b in zip(observed,expected))
    if comparison=="unordered_rows":
        if len(observed)!=len(expected):
            return False
        unused=list(range(len(observed)))
        for erow in expected:
            hit=None
            for idx in unused:
                if eq_row(observed[idx],erow,tol):
                    hit=idx
                    break
            if hit is None:
                return False
            unused.remove(hit)
        return not unused
    raise ValueError(f"unsupported comparison {comparison!r}")


def evaluate(artifact:dict[str,Any], oracle:dict[str,Any])->dict[str,Any]:
    out={"pass":False,"silent_wrong":False,"failure":None}
    try:
        if artifact.get("status_code")!=202:
            raise ValueError("agent-streaming status != 202")
        if artifact.get("errors"):
            raise ValueError(f"stream/provider errors={len(artifact.get('errors') or [])}")
        te=tool_error_count(artifact)
        if te:
            raise ValueError(f"structured tool errors={te}")
        catalog=artifact.get("catalog_probe")
        resource=(catalog or {}).get("first") if isinstance(catalog,dict) else None
        if not isinstance(resource,dict) or resource.get("database_name")!=EXPECTED_DB:
            raise ValueError("dataset scope drift: catalog database")
        q=artifact.get("generated_query")
        if not isinstance(q,dict):
            raise ValueError("no generated query")
        if q.get("database")!=resource.get("database_id"):
            raise ValueError("dataset scope drift: query database")
        result=artifact.get("generated_query_dataset_result")
        if not isinstance(result,dict) or result.get("status") not in {200,202}:
            raise ValueError("query execution missing/non-success")
        rows=result.get("rows")
        if not isinstance(rows,list):
            raise ValueError("query rows missing")
        expected=oracle.get("rows")
        if not isinstance(expected,list):
            raise ValueError("oracle rows missing")
        comparison=str(oracle.get("comparison") or "")
        tol=float(oracle.get("numeric_tolerance") or 0)
        ok=rows_match(rows,expected,comparison,tol)
        if not ok:
            out["silent_wrong"]=True
            out["observed_rows"]=rows
            out["expected_rows"]=expected
            raise ValueError("executed result != independent oracle")
        out.update({
            "pass":True,
            "observed_rows":rows,
            "expected_rows":expected,
            "latency_seconds":artifact.get("latency_seconds"),
            "tool_call_count":len(artifact.get("tool_calls") or []),
            "query_count":1,
            "runtime":artifact.get("session_version_fields"),
            "permissions":artifact.get("metabot_permissions"),
            "database_id":resource.get("database_id"),
        })
    except Exception as exc:
        out["failure"]=f"{type(exc).__name__}: {exc}"
    return out


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--cases",type=Path,required=True)
    ap.add_argument("--oracle",type=Path,required=True)
    ap.add_argument("--stock-dir",type=Path,required=True)
    ap.add_argument("--fork-dir",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    case_set=load(args.cases)
    oracle_all=load(args.oracle)
    if oracle_all.get("corpus_fingerprint")!=EXPECTED_CORPUS or case_set.get("corpus_fingerprint")!=EXPECTED_CORPUS:
        raise SystemExit("frozen corpus fingerprint drift")
    oracle_by={x["id"]:x for x in oracle_all.get("results") or [] if isinstance(x,dict)}
    rows=[]
    permission_regressions=0
    scope_drift=0
    new_silent_wrong=0
    stock_pass=0
    retained=0

    for case_id in case_set["case_ids"]:
        oracle=oracle_by[case_id]
        if oracle.get("kind")!="query":
            raise SystemExit(f"{case_id} is not executable query oracle")
        stock_art=load(args.stock_dir/f"{case_id}.json")
        fork_art=load(args.fork_dir/f"{case_id}.json")
        stock=evaluate(stock_art,oracle)
        fork=evaluate(fork_art,oracle)

        if stock["pass"]:
            stock_pass+=1
            if fork["pass"]:
                retained+=1
        if fork.get("silent_wrong"):
            new_silent_wrong+=1

        stock_perm=stock_art.get("metabot_permissions")
        fork_perm=fork_art.get("metabot_permissions")
        perm_equal=stock_perm==fork_perm
        if not perm_equal:
            permission_regressions+=1

        def scope_ok(a:dict[str,Any])->bool:
            c=a.get("catalog_probe")
            r=(c or {}).get("first") if isinstance(c,dict) else None
            q=a.get("generated_query")
            return isinstance(r,dict) and r.get("database_name")==EXPECTED_DB and isinstance(q,dict) and q.get("database")==r.get("database_id")
        stock_scope=scope_ok(stock_art)
        fork_scope=scope_ok(fork_art)
        if stock_scope and not fork_scope:
            scope_drift+=1

        rows.append({
            "case_id":case_id,
            "family":oracle.get("family"),
            "stock":stock,
            "fork":fork,
            "permissions_equal":perm_equal,
            "stock_scope_ok":stock_scope,
            "fork_scope_ok":fork_scope,
        })

    retention=(retained/stock_pass) if stock_pass else 0.0
    min_stock=int(case_set["closure"]["minimum_stock_pass"])
    closure={
        "stock_pass_count":stock_pass,
        "selected_case_count":len(case_set["case_ids"]),
        "fork_retained_stock_pass":retained,
        "fork_capability_retention":retention,
        "new_silent_wrong":new_silent_wrong,
        "permission_regression":permission_regressions,
        "dataset_scope_drift":scope_drift,
        "minimum_stock_pass_required":min_stock,
    }
    green=(
        stock_pass>=min_stock
        and math.isclose(retention,1.0,abs_tol=0.0,rel_tol=0.0)
        and new_silent_wrong==0
        and permission_regressions==0
        and scope_drift==0
    )
    report={
        "schema_version":"p12x_c1_parity_v1",
        "corpus_fingerprint":EXPECTED_CORPUS,
        "status":"GREEN" if green else "RED",
        "closure":closure,
        "cases":rows,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2,default=str))
    return 0 if green else 1

if __name__=="__main__":
    raise SystemExit(main())
