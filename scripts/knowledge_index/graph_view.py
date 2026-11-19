"""Read-only, public-only projections. Experimental, not an auth service."""
import html
import hashlib
import base64
import json
import re
import sqlite3
from pathlib import Path
from urllib.parse import urlsplit

def safe_url(value):
    if not isinstance(value, str):
        return ""
    if any(ord(ch) < 33 or ch in '<>"\x27[]' for ch in value):
        return ""
    parts = urlsplit(value)
    return value if parts.scheme == "https" and parts.hostname and not parts.username and not parts.password else ""

def public_projection(db):
    with sqlite3.connect(db) as con:
        rows = con.execute(
            "SELECT id,kind,title,source_uri,authority FROM nodes "
            "WHERE visibility='public' ORDER BY id").fetchall()
        nodes = [{"id": row[0], "kind": row[1], "title": row[2],
                  "source_uri": safe_url(row[3]), "authority": row[4]} for row in rows]
        allowed = {n["id"] for n in nodes}
        raw_edges = con.execute(
            "SELECT e.id,e.source_id,e.target_id,e.relation,e.review_status,"
            "e.assessment,e.evidence_refs,e.explanation FROM edges e "
            "JOIN nodes a ON a.id=e.source_id JOIN nodes b ON b.id=e.target_id "
            "WHERE e.visibility='public' AND a.visibility='public' "
            "AND b.visibility='public' ORDER BY e.id").fetchall()
    edges = []
    for e in raw_edges:
        evidence = json.loads(e[6])
        # An evidence ref may disclose private content or merely its existence.
        if not isinstance(evidence, list) or any(x not in allowed for x in evidence):
            continue
        edges.append({"id": e[0], "from": e[1], "to": e[2],
                      "relation": e[3], "review_status": e[4],
                      "assessment": e[5], "evidence_refs": evidence,
                      "explanation": e[7]})
    return {"schema_version": 1, "nodes": nodes, "edges": edges}

def neighborhood(projection, focus=None, maximum=36):
    indexed = {n["id"]: n for n in projection["nodes"]}
    seeds = set(x for x in (focus or []) if x in indexed)
    selected = set(indexed) if not focus else set(seeds)
    if focus:
        for e in projection["edges"]:
            if e["from"] in seeds or e["to"] in seeds:
                selected.update((e["from"], e["to"]))
    order = sorted(selected, key=lambda x: (x not in seeds, x))[:maximum]
    allowed = set(order)
    return ([indexed[x] for x in order],
            [e for e in projection["edges"] if e["from"] in allowed and e["to"] in allowed])

def safe_markdown_metadata(value):
    """Treat authority labels as text, not Markdown/HTML or a new list item."""
    value = html.escape(value, quote=True)
    value = value.translate({10: 32, 13: 32, 9: 32})
    slash = chr(92)
    for marker in (slash, "`", "*", "_", "{", "}", "[", "]", "(", ")", "!", "|"):
        value = value.replace(marker, slash + marker)
    return value


def render_mermaid(db, focus=None):
    nodes, edges = neighborhood(public_projection(db), focus)
    labels = {n["id"]: f"n{i}" for i, n in enumerate(nodes)}
    fence = chr(96) * 3
    result = ["# Public research relationship graph", "",
        "Generated read-only view. All graph edges are **candidate** links, not validated findings.",
        "", fence + "mermaid", "flowchart LR"]
    for n in nodes:
        label = re.sub(r"[^A-Za-z0-9 .:/_-]", " ", n["title"])[:60].strip() or "Untitled"
        result.append(f'    {labels[n["id"]]}["{label}"]')
    for e in edges:
        result.append(f'    {labels[e["from"]]} -->|{e["relation"]} candidate| {labels[e["to"]]}')
    result.extend([fence, "", "## Source references", ""])
    for n in nodes:
        title = html.escape(n["title"], quote=True).replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")
        authority = safe_markdown_metadata(n["authority"] or "unspecified")
        url = n["source_uri"].replace("(", "%28").replace(")", "%29")
        if url:
            result.append(f"- [{title}]({url}) — {n['kind']}, {authority}")
        else:
            result.append(f"- {title} — no safe public URL")
    result.extend(["", f"Visible subset: {len(nodes)} nodes, {len(edges)} candidate edges.", ""])
    return "\n".join(result)

def render_html(db):
    """Portable, dependency-free interactive SVG: public data and no network calls."""
    payload = json.dumps(public_projection(db), sort_keys=True, ensure_ascii=True)
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    prefix = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<title>Knowledge graph (read only)</title>
<style>body{font:15px system-ui,sans-serif;margin:1em;background:#fafafa;color:#222}
svg{width:100%;height:470px;background:white;border:1px solid #bbb}
.controls{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
button,input{font:inherit;padding:5px}li{margin:7px 0}a{color:#0645ad}
circle:focus{stroke:#f50;stroke-width:4;outline:0}</style></head><body>
<h1>Research knowledge graph — public candidates</h1>
<p>Read-only experimental view. Selecting a node shows its immediate neighbors. All links are candidates pending review.</p>
<div class="controls"><label>Search <input id="search" type="search"></label>
<button id="reset">Show all</button><button id="plus">Zoom +</button><button id="minus">Zoom −</button>
<span id="count" role="status"></span></div>
<svg id="graph" viewBox="0 0 940 470" role="img" aria-label="Interactive graph; accessible source list below"></svg>
<h2>Visible source list</h2><ul id="sourceList"></ul>
<script id="data" type="application/json">"""
    suffix = """</script><script>
"use strict";
const data=JSON.parse(document.getElementById("data").textContent);
const svg=document.getElementById("graph"), list=document.getElementById("sourceList");
const search=document.getElementById("search"), count=document.getElementById("count");
const NS="http://www.w3.org/2000/svg";
let focus=null,zoom=1;
function element(tag,props,parent,text){
 const e=document.createElementNS(NS,tag);
 for(const k in props)e.setAttribute(k,String(props[k]));
 if(text!==undefined)e.textContent=text;
 parent.appendChild(e);return e;
}
function draw(){
 const q=search.value.toLowerCase();
 let selected=data.nodes.filter(n=>n.title.toLowerCase().includes(q)||n.id.toLowerCase().includes(q));
 if(focus){
   const neighbors=new Set([focus]);
   for(const e of data.edges){if(e.from===focus)neighbors.add(e.to);if(e.to===focus)neighbors.add(e.from);}
   selected=selected.filter(n=>neighbors.has(n.id));
 }
 const ids=new Set(selected.map(n=>n.id));
 const edges=data.edges.filter(e=>ids.has(e.from)&&ids.has(e.to));
 svg.replaceChildren();list.replaceChildren();
 const layer=element("g",{transform:"translate(470 235) scale("+zoom+") translate(-470 -235)"},svg);
 const positions=new Map();
 selected.forEach((n,i)=>{let r=15*Math.sqrt(i+1);positions.set(n.id,{x:470+1.5*r*Math.cos(i*2.399963),y:235+r*Math.sin(i*2.399963)});});
 for(const e of edges){
   const a=positions.get(e.from),b=positions.get(e.to);
   element("line",{x1:a.x,y1:a.y,x2:b.x,y2:b.y,stroke:"#aaa","stroke-width":1.4},layer);
 }
 for(const n of selected){
   const p=positions.get(n.id);
   const circle=element("circle",{cx:p.x,cy:p.y,r:n.id===focus?9:6,
     fill:n.kind==="concept"?"#2277ad":n.kind==="source"?"#7c4db1":"#16886f",
     tabindex:"0",role:"button","aria-label":n.title},layer);
   element("title",{},circle,n.title);
   const pick=()=>{focus=focus===n.id?null:n.id;search.value="";draw();};
   circle.addEventListener("click",pick);
   circle.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();pick();}});
   const li=document.createElement("li"),a=document.createElement("a");a.textContent=n.title+" ["+n.kind+"]";
   if(n.source_uri){a.href=n.source_uri;a.target="_blank";a.rel="noopener noreferrer";}
   li.appendChild(a);li.appendChild(document.createTextNode(" "));
   const btn=document.createElement("button");btn.textContent="Focus";btn.addEventListener("click",pick);
   li.appendChild(btn);list.appendChild(li);
 }
 count.textContent=selected.length+" nodes, "+edges.length+" candidate edges";
}
search.addEventListener("input",draw);
document.getElementById("reset").addEventListener("click",()=>{focus=null;zoom=1;search.value="";draw();});
document.getElementById("plus").addEventListener("click",()=>{zoom=Math.min(4,zoom*1.3);draw();});
document.getElementById("minus").addEventListener("click",()=>{zoom=Math.max(.5,zoom/1.3);draw();});
draw();
</script></body></html>"""
    # The embedded JavaScript is pinned by its exact content hash; the
    # JSON payload is inert and HTML-escaped. No third-party network scripts.
    script = suffix.split("<script>", 1)[1].split("</script>", 1)[0]
    digest = base64.b64encode(hashlib.sha256(script.encode("utf-8")).digest()).decode("ascii")
    prefix = prefix.replace("script-src 'unsafe-inline'", "script-src 'sha256-" + digest + "'")
    return prefix + payload + suffix

def write_views(db, folder, focus=None):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "graph.md").write_text(render_mermaid(db, focus), encoding="utf-8")
    (folder / "graph.html").write_text(render_html(db), encoding="utf-8")
    (folder / "public-graph.json").write_text(
        json.dumps(public_projection(db), sort_keys=True, indent=2) + "\n", encoding="utf-8")
