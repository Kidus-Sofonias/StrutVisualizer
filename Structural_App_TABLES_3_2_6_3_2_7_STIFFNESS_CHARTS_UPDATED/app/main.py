
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from pathlib import Path
import json, math, re, shutil

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
DATA.mkdir(exist_ok=True)

app = FastAPI(title="Structural App - Tables 3.2.2 to 3.2.8")



@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

templates = Jinja2Templates(directory=str(BASE / "templates"))

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"d": load_state()},
    )

def fmt3(value):
    if value is None or value == "":
        return "-"
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return value

templates.env.filters["fmt3"] = fmt3

def norm(v):
    return re.sub(r"[^a-z0-9]", "", str(v or "").lower())

def q(v):
    return "[" + str(v).replace("]", "]]") + "]"

def state_path():
    return DATA / "project.json"

def load_state():
    if state_path().exists():
        return json.loads(state_path().read_text(encoding="utf-8"))
    return {
        "message": "", "access_file": "", "tables": [],
        "table_322": [], "table_323": [], "table_324": [], "table_325": [], "table_326": [], "table_327": [], "table_328": [],
        "map_322": {}, "map_323": {}
    }

def save_state(d):
    state_path().write_text(json.dumps(d, indent=2), encoding="utf-8")

def connect(path):
    import pyodbc
    driver = next((x for x in pyodbc.drivers() if "ACCESS" in x.upper()), None)
    if not driver:
        raise RuntimeError("Microsoft Access ODBC driver was not found.")
    return pyodbc.connect(f"DRIVER={{{driver}}};DBQ={path};", autocommit=True)

def find_table(names, aliases):
    lookup = {norm(x): x for x in names}
    for a in aliases:
        if norm(a) in lookup:
            return lookup[norm(a)]
    # relaxed containment fallback
    for n in names:
        nn = norm(n)
        if all(norm(a) in nn or nn in norm(a) for a in aliases[:1]):
            return n
    return None

def find_col(cols, aliases):
    lookup = {norm(x): x for x in cols}
    for a in aliases:
        if norm(a) in lookup:
            return lookup[norm(a)]
    return None

def num(v):
    try:
        return None if v is None or v == "" else float(v)
    except (ValueError, TypeError):
        return None

def storey_elevation(story):
    """
    Extract a numeric elevation from common ETABS/Excel storey names.
    Examples: '0.00', 'STORY 3.00', 'B1 -3.50', '-7.00'.
    If no reliable elevation can be read, return None and keep the storey.
    """
    text = str(story or "").strip()
    match = re.search(r"[-+]?\d+(?:\.\d+)?", text.replace(",", "."))
    if not match:
        return None
    try:
        return float(match.group())
    except ValueError:
        return None

def include_storey(story):
    elevation = storey_elevation(story)
    return elevation is None or elevation >= 0.0

def story_key(story):
    """Normalize ETABS story labels so equivalent labels match across Access tables."""
    s = str(story or "").strip().upper()
    s = re.sub(r"\s+", "", s)
    s = s.replace("_", "").replace("-", "")
    return s

def story_keys_equivalent(a, b):
    if story_key(a) == story_key(b):
        return True
    ea, eb = storey_elevation(a), storey_elevation(b)
    return ea is not None and eb is not None and abs(ea - eb) < 1e-9

def get_objects(cur):
    out, seen = [], set()
    for r in cur.tables():
        n = str(r.table_name or "").strip()
        typ = str(r.table_type or "").upper()
        if n and not n.upper().startswith("MSYS") and typ in {"TABLE","VIEW"} and norm(n) not in seen:
            seen.add(norm(n)); out.append(n)
    return out

def get_nonnegative_story_keys(cur, story_table):
    """Return Story Data story keys whose actual elevation is >= 0.00.

    Elevation from STORY DATA is authoritative. This explicitly includes the
    storey at exactly 0.00 and excludes only storeys below 0.00.
    """
    cols = [str(c.column_name) for c in cur.columns(table=story_table)]
    story_col = find_col(cols, ["Story", "Storey"]) or (cols[0] if cols else None)
    elev_col = find_col(cols, ["Elevation", "Story Elevation", "Storey Elevation", "Z", "Level"])
    if not story_col or not elev_col:
        return set()
    out = set()
    for r in cur.execute(f"SELECT {q(story_col)},{q(elev_col)} FROM {q(story_table)}").fetchall():
        st = str(r[0]).strip() if r[0] is not None else ""
        ev = num(r[1])
        if st and ev is not None and ev >= 0.0:
            out.add(story_key(st))
    return out

def story_data_order(cur, story_table):
    """Return canonical Story Data rows ordered by actual elevation, highest to 0.00."""
    cols=[str(c.column_name) for c in cur.columns(table=story_table)]
    ys=find_col(cols,["Story","Storey"]) or (cols[0] if cols else None)
    ye=find_col(cols,["Elevation","Story Elevation","Storey Elevation","Z","Level"])
    if not ye and len(cols)>=3: ye=cols[2]
    if not ys or not ye: return []
    rows=[]; seen=set()
    for r in cur.execute(f"SELECT {q(ys)},{q(ye)} FROM {q(story_table)}").fetchall():
        st=str(r[0]).strip() if r[0] is not None else ""
        ev=num(r[1])
        key=story_key(st)
        if not st or key in seen or ev is None or ev < 0.0: continue
        seen.add(key); rows.append((key,st,ev))
    rows.sort(key=lambda x:x[2], reverse=True)
    return rows

def ensure_zero_story(rows, cur, story_table):
    """Ensure the elevation 0.00 storey is present in every report table.

    Existing calculated data is never overwritten. If an upstream source does
    not contain a ground record, a Ground FL row is still displayed with its
    elevation and missing calculated fields rather than silently dropping the
    required elevation-0 storey.
    """
    sd=story_data_order(cur, story_table)
    zero=next((x for x in sd if abs(x[2]) < 1e-9), None)
    if zero is None: return rows
    _,ground_label,ground_elev=zero
    out=[dict(r) for r in rows]
    zero_keys={story_key(r.get("story")) for r in out}
    if story_key(ground_label) not in zero_keys:
        out.append({"story":ground_label,"elevation":ground_elev})
    else:
        for r in out:
            if story_key(r.get("story"))==story_key(ground_label):
                r["story"]=ground_label; r["elevation"]=ground_elev
    return out

def process_322(cur, table, allowed_story_keys=None):
    cols = [str(c.column_name) for c in cur.columns(table=table)]

    story = find_col(cols, ["Story", "Storey"])
    # Auto-detect common Center of Mass / Center of Rigidity field names.
    cmx = find_col(cols, ["CMX", "XCM", "X Center of Mass", "XCMass", "X_CMass", "CenterMassX"])
    cmy = find_col(cols, ["CMY", "YCM", "Y Center of Mass", "YCMass", "Y_CMass", "CenterMassY"])
    crx = find_col(cols, ["CRX", "XCR", "X Center of Rigidity", "XCRigidity", "X_CRigidity", "CenterRigidityX"])
    cry = find_col(cols, ["CRY", "YCR", "Y Center of Rigidity", "YCRigidity", "Y_CRigidity", "CenterRigidityY"])

    # If exact names are unusual, look for CM/CR semantic patterns.
    if not cmx:
        cmx = next((c for c in cols if ("cm" in norm(c) or "centermass" in norm(c)) and norm(c).endswith("x")), None)
    if not cmy:
        cmy = next((c for c in cols if ("cm" in norm(c) or "centermass" in norm(c)) and norm(c).endswith("y")), None)
    if not crx:
        crx = next((c for c in cols if ("cr" in norm(c) or "centerrigidity" in norm(c)) and norm(c).endswith("x")), None)
    if not cry:
        cry = next((c for c in cols if ("cr" in norm(c) or "centerrigidity" in norm(c)) and norm(c).endswith("y")), None)

    mapping = {"Story":story, "CMX":cmx, "CMY":cmy, "CRX":crx, "CRY":cry}
    if not all(mapping.values()):
        return [], mapping

    sql = f"SELECT {q(story)}, {q(cmx)}, {q(cmy)}, {q(crx)}, {q(cry)} FROM {q(table)}"
    rows = []
    for r in cur.execute(sql).fetchall():
        s = str(r[0]).strip() if r[0] is not None else ""
        xcm,ycm,xcr,ycr = map(num, r[1:5])
        if not s or not include_storey(s):
            continue
        if allowed_story_keys is not None and story_key(s) not in allowed_story_keys:
            continue
        # Structural eccentricities: absolute CM-to-CR distances.
        eox = abs(xcm-xcr) if xcm is not None and xcr is not None else None
        eoy = abs(ycm-ycr) if ycm is not None and ycr is not None else None
        rows.append({"story":s,"cmx":xcm,"cmy":ycm,"crx":xcr,"cry":ycr,"eox":eox,"eoy":eoy})
    return rows, mapping

def process_323(cur, table, allowed_story_keys=None):
    cols = [str(c.column_name) for c in cur.columns(table=table)]
    story = find_col(cols, ["Story","Storey"])
    dia = find_col(cols, ["Diaphragm"])
    load = find_col(cols, ["Load","OutputCase","LoadCase","Case"])
    ux = find_col(cols, ["UX"])
    uy = find_col(cols, ["UY"])
    rz = find_col(cols, ["RZ"])
    mapping = {"Story":story,"Diaphragm":dia,"Load":load,"UX":ux,"UY":uy,"RZ":rz}
    if not all(mapping.values()):
        return [], mapping, []

    sql = f"SELECT {q(story)}, {q(dia)}, {q(load)}, {q(ux)}, {q(uy)}, {q(rz)} FROM {q(table)}"
    grouped, order, cases = {}, [], set()

    for r in cur.execute(sql).fetchall():
        s = str(r[0]).strip() if r[0] is not None else ""
        d = str(r[1]).strip() if r[1] is not None else ""
        lc = str(r[2]).strip().upper() if r[2] is not None else ""
        if lc: cases.add(lc)
        if not s or not include_storey(s): continue
        if allowed_story_keys is not None and story_key(s) not in allowed_story_keys: continue
        if s not in grouped:
            grouped[s] = {"diaphragm":d,"UL1":None,"UL2":None,"UL3":None}
            order.append(s)
        if lc == "UL1": grouped[s]["UL1"] = num(r[3])
        elif lc == "UL2": grouped[s]["UL2"] = num(r[4])
        elif lc == "UL3": grouped[s]["UL3"] = num(r[5])

    out=[]
    for s in order:
        v=grouped[s]
        a,b,c=v["UL1"],v["UL2"],v["UL3"]
        kfx=None if a in (None,0) else 1/a
        kfy=None if b in (None,0) else 1/b
        kmt=None if c in (None,0) else 1/c
        rx=math.sqrt(kmt/kfy) if kmt is not None and kfy not in (None,0) and kmt/kfy>=0 else None
        ry=math.sqrt(kmt/kfx) if kmt is not None and kfx not in (None,0) and kmt/kfx>=0 else None
        out.append({"story":s,"diaphragm":v["diaphragm"],"ux":a,"uy":b,"rz":c,
                    "kfx":kfx,"kfy":kfy,"kmt":kmt,"rx":rx,"ry":ry})
    return out, mapping, sorted(cases)

def process_324(t322, t323):
    # Match by normalized story key first, then by numeric elevation where
    # source labels differ (for example "GROUND FL" vs another ETABS label).
    a={story_key(r.get("story")):r for r in t322}
    b={story_key(r.get("story")):r for r in t323}
    stories=list(dict.fromkeys(list(a.keys())+[k for k in b if k not in a]))
    out=[]
    for k in stories:
        x=a.get(k,{})
        y=b.get(k,{})
        eox,eoy=x.get("eox"),x.get("eoy")
        rx,ry=y.get("rx"),y.get("ry")
        lx=0.3*rx if rx is not None else None
        ly=0.3*ry if ry is not None else None
        sx="OK" if eox is not None and lx is not None and eox <= lx else ("NOT OK" if eox is not None and lx is not None else "Missing data")
        sy="OK" if eoy is not None and ly is not None and eoy <= ly else ("NOT OK" if eoy is not None and ly is not None else "Missing data")
        out.append({"story":x.get("story") or y.get("story"),"eox":eox,"rx":rx,"limit_x":lx,"status_x":sx,
                    "eoy":eoy,"ry":ry,"limit_y":ly,"status_y":sy})
    return out



def process_325(cur, area_table, cm_table, allowed_story_keys=None):
    """Calculate Table 3.2.5 Ls from Area Assignments Summary.

    Exact Excel logic:
      Y = X + S*((U-CMx)^2 + (V-CMy)^2)
      Ls = sqrt(sum(Y) / sum(S))

    Access mappings:
      S = ObjectArea
      X = PolarInertia
      U = CentroidX
      V = CentroidY
      CMx = XCM
      CMy = YCM

    The source Access database is read-only. Calculated Y is stored separately.\n    The Excel formula uses Center of Mass; this prototype uses the requested Center Mass Rigidity source for the equivalent CMx/CMy fields.
    """
    acols=[str(c.column_name) for c in cur.columns(table=area_table)]
    ccols=[str(c.column_name) for c in cur.columns(table=cm_table)]
    astory=find_col(acols,["Story","Storey"])
    atype=find_col(acols,["SectionType","Section Type","AreaType","Type","Object Type","Property Type","Area Type","Element Type"])
    aS=find_col(acols,["ObjectArea","S"])
    aX=find_col(acols,["PolarInertia","X"])
    aU=find_col(acols,["CentroidX","U"])
    aV=find_col(acols,["CentroidY","V"])
    cmstory=find_col(ccols,["Story","Storey"])
    cmx=find_col(ccols,["XCM","XCCM","CMX","X","X Center of Mass","Center Mass X"])
    cmy=find_col(ccols,["YCM","YCCM","CMY","Y","Y Center of Mass","Center Mass Y"])
    amap={"Story":astory,"Type":atype,"S":aS,"X":aX,"U":aU,"V":aV}
    cmap={"Story":cmstory,"CMX":cmx,"CMY":cmy}

    if not all(amap.values()) or not all(cmap.values()):
        return [],[],amap,cmap

    # Read CM data and build both exact and normalized/elevation lookup keys.
    cm_rows = cur.execute(
        f"SELECT {q(cmstory)},{q(cmx)},{q(cmy)} FROM {q(cm_table)}"
    ).fetchall()
    cms={}
    for r in cm_rows:
        st=str(r[0]).strip() if r[0] is not None else ""
        if not st:
            continue
        cms[story_key(st)] = (num(r[1]), num(r[2]), st)

    # Read area assignments.
    area_rows = cur.execute(
        f"SELECT {q(astory)},{q(atype)},{q(aS)},{q(aX)},{q(aU)},{q(aV)} FROM {q(area_table)}"
    ).fetchall()

    detail=[]; summary={}; order=[]
    total_rows=0; slab_rows=0; matched_cm_rows=0; valid_y_rows=0

    for r in area_rows:
        total_rows += 1
        st=str(r[0]).strip() if r[0] is not None else ""
        typ=str(r[1]).strip() if r[1] is not None else ""
        if not st or not include_storey(st):
            continue
        if allowed_story_keys is not None and story_key(st) not in allowed_story_keys:
            continue

        # Excel formula uses Area Assign column D = "Slab".
        # In the exported data, column D is SectionType.
        typ_key=re.sub(r"\\s+", "", typ).lower()
        if typ_key != "slab":
            continue
        slab_rows += 1

        sval,xval,uval,vval=map(num,r[2:6])

        pair=cms.get(story_key(st))
        if pair is None:
            # Fallback: compare numeric storey elevations.
            for cm_label, cm_pair in ((v[2],v) for v in cms.values()):
                if story_keys_equivalent(st, cm_label):
                    pair=cm_pair
                    break

        if pair:
            cmxv,cmyv=pair[0],pair[1]
            matched_cm_rows += 1
        else:
            cmxv,cmyv=None,None

        yval=None
        if None not in (sval,xval,uval,vval,cmxv,cmyv):
            yval=xval+sval*((uval-cmxv)**2+(vval-cmyv)**2)
            valid_y_rows += 1

        if st not in summary:
            summary[st]={"story":st,"sum_s":0.0,"sum_y":0.0,"count":0,
                         "cmx":cmxv,"cmy":cmyv}
            order.append(st)

        # IMPORTANT: Sum S only for rows with valid numeric S.
        if sval is not None:
            summary[st]["sum_s"] += sval
        if yval is not None:
            summary[st]["sum_y"] += yval
            summary[st]["count"] += 1

        detail.append({
            "story":st,"type":typ,"s":sval,"x":xval,"u":uval,"v":vval,
            "cmx":cmxv,"cmy":cmyv,"y":yval
        })

    out=[]
    for st in order:
        z=summary[st]
        ls=math.sqrt(z["sum_y"]/z["sum_s"]) if (
            z["sum_s"] > 0 and z["sum_y"] >= 0 and z["count"] > 0
        ) else None
        out.append({
            "story":st,"cmx":z["cmx"],"cmy":z["cmy"],
            "sum_s":z["sum_s"],"sum_y":z["sum_y"],
            "slab_count":z["count"],"ls":ls
        })

    # If no usable Ls values exist, return a detailed diagnostic mapping.
    if not any(r["ls"] is not None for r in out):
        # Capture a compact sample of SectionType values to make future data mismatches obvious.
        type_values = {}
        for rr in area_rows:
            vv = str(rr[1]).strip() if rr[1] is not None else ""
            if vv:
                type_values[vv] = type_values.get(vv, 0) + 1
        type_sample = sorted(type_values.items(), key=lambda x: (-x[1], x[0]))[:10]
        amap["_diagnostic"] = (
            f"Area rows={total_rows}; Slab rows at/above 0.00={slab_rows}; "
            f"Slab rows matched to Center Mass Rigidity={matched_cm_rows}; "
            f"rows with valid calculated Y={valid_y_rows}; "
            f"Center Mass Rigidity rows={len(cm_rows)}; "
            f"SectionType values={type_sample}."
        )

    return out,detail,amap,cmap



def process_326(cur, shears_table, drift_table, story_table):
    """Calculate Table 3.2.6 exactly from the Excel source logic.

    Excel stiffness formula:
      Kx = ABS( STOREY SHEARS matched by Story + EQX, column 5 of B:J
                / 4.5 Storey drift control dr Xx )

    Excel dr Xx formula:
      dr Xx = Diaphram Drift matched by Story + EQX, column 8 of B:J
               * STORY DATA column 2 (storey height)

    The resulting check is: Ki >= 0.7 * Ki+1, where Ki+1 is the
    stiffness of the next higher storey.
    """
    scols=[str(c.column_name) for c in cur.columns(table=shears_table)]
    dcols=[str(c.column_name) for c in cur.columns(table=drift_table)]
    ycols=[str(c.column_name) for c in cur.columns(table=story_table)]

    # Match the Excel positions exactly, while using the actual Access names.
    s_story=find_col(scols,["Story","Storey"])
    s_load=find_col(scols,["Load","OutputCase","LoadCase","Case"])
    d_story=find_col(dcols,["Story","Storey"])
    d_load=find_col(dcols,["Load","OutputCase","LoadCase","Case"])
    d_driftx=find_col(dcols,["DriftX","Drift X","DrX"])
    y_story=find_col(ycols,["Story","Storey"])
    y_height=find_col(ycols,["Story Height","Height","Storey Height","H","Elevation Difference","StoryHeight"])

    # If the exported table uses ETABS-style standard columns, use the exact
    # positional fields corresponding to the Excel ranges B:J and B:E.
    if not s_story and len(scols)>=1: s_story=scols[0]
    if not s_load and len(scols)>=2: s_load=scols[1]
    if not d_story and len(dcols)>=1: d_story=dcols[0]
    if not d_load and len(dcols)>=3: d_load=dcols[2]
    if not d_driftx and len(dcols)>=8: d_driftx=dcols[7]
    if not y_story and len(ycols)>=1: y_story=ycols[0]
    if not y_height and len(ycols)>=2: y_height=ycols[1]

    mapping={
        "Story Shears":{"Story":s_story,"Load":s_load,
                          "ShearField":scols[4] if len(scols)>=5 else None},
        "Diaphragm Drifts":{"Story":d_story,"Load":d_load,"DriftX":d_driftx},
        "STORY DATA":{"Story":y_story,"Height":y_height},
        "LoadCase":"EQX"
    }
    if not all([s_story,s_load,d_story,d_load,d_driftx,y_story,y_height]) or len(scols)<5:
        return [], mapping

    # Storey heights: Excel STORY DATA column 2 = height.
    heights={}
    for r in cur.execute(f"SELECT {q(y_story)},{q(y_height)} FROM {q(story_table)}").fetchall():
        st=str(r[0]).strip() if r[0] is not None else ""
        h=num(r[1])
        if st and h is not None:
            heights[story_key(st)]=(h,st)

    # Storey shear: Excel INDEX(B:J,...,5) => the 5th field of B:J.
    # Excel MATCH returns the FIRST matching row.  Do not overwrite duplicate
    # Story+Load rows (Story Shears has Top/Bottom rows; Diaphragm Drifts can
    # have multiple diaphragm items).
    shear_map={}
    sf=scols[4]
    for r in cur.execute(f"SELECT {q(s_story)},{q(s_load)},{q(sf)} FROM {q(shears_table)}").fetchall():
        st=str(r[0]).strip() if r[0] is not None else ""
        lc=str(r[1]).strip().upper() if r[1] is not None else ""
        key=story_key(st) if st else ""
        if key and lc=="EQX" and key not in shear_map:
            shear_map[key]=num(r[2])

    # Excel Diaphram Drift formula: MATCH(Story&EQX, B:B&D:D,0), then
    # INDEX(B:J,...,8).  Therefore use the FIRST Story+EQX match and the
    # eighth field of the B:J range (DriftX).
    drift_map={}
    for r in cur.execute(f"SELECT {q(d_story)},{q(d_load)},{q(d_driftx)} FROM {q(drift_table)}").fetchall():
        st=str(r[0]).strip() if r[0] is not None else ""
        lc=str(r[1]).strip().upper() if r[1] is not None else ""
        key=story_key(st) if st else ""
        if key and lc=="EQX" and key not in drift_map:
            drift_map[key]=num(r[2])

    # Table 3.2.6 is required for storeys whose elevation is AT OR ABOVE 0.00.
    # Therefore Ground (0.00) is included, while basement/base storeys below 0.00 are excluded.
    # ETABS story labels in this database do not reliably encode signed
    # elevations, so use the building-level convention explicitly: numbered
    # floors (1ST and above), ROOF FL and UP ROOF FL are positive-elevation
    # storeys; GROUND FL is included at 0.00, while BASE/BASEMENT storeys are excluded.
    def is_above_zero_story(st):
        u = str(st or '').strip().upper()
        if not u:
            return False
        if re.search(r"\b(BASE|BASEMENT)\b", u):
            return False
        if re.search(r"\bGROUND\b", u):
            return True
        if 'ROOF' in u:
            return True
        m = re.search(r"(\d+)(?:ST|ND|RD|TH)\b", u)
        if m:
            return int(m.group(1)) >= 0
        # If a raw signed numeric elevation is supplied as the story label,
        # retain it when it is at or above 0.00.
        ev = storey_elevation(u)
        return ev is not None and ev >= 0.0

    # Use the single authoritative report master: >= 0.00, omit only the
    # highest/final top story, and keep GROUND FL at 0.00.  This same list is
    # used by the final display for every table, so stiffness comparisons do
    # not use an omitted top floor as their adjacent storey.
    master = report_story_master(cur, story_table)
    ordered=[(m["key"], m["story"], m.get("elevation")) for m in master if m["key"] in heights]

    raw=[]
    for key,st,ev in ordered:
        shear=shear_map.get(key)
        drift=drift_map.get(key)
        height=heights.get(key,(None,st))[0]
        dr_xx=abs(drift*height) if drift is not None and height is not None else None
        kx=abs(shear/dr_xx) if shear is not None and dr_xx not in (None,0) else None
        raw.append({"story":st,"elevation":ev,"storey_shear":shear,"drift_x":drift,
                    "storey_height":height,"dr_xx":dr_xx,"stiffness_x":kx})

    # Compare each storey with the next higher storey. Story DATA is normally
    # bottom-to-top; if so, the next row is higher. If the source is top-down,
    # use the following row only when its elevation is higher is unavailable;
    # the Excel reference itself is top-down, so sort using known numeric floor
    # names where possible.
    def floor_rank(st):
        t=st.upper()
        if "UP ROOF" in t: return 10000
        if "ROOF" in t: return 9000
        m=re.search(r"(\d+)(?:ST|ND|RD|TH)?",t)
        if m: return int(m.group(1))
        if "GROUND" in t: return 0
        return -1
    raw.sort(key=lambda r: floor_rank(r["story"]), reverse=True)

    out=[]
    for i,r in enumerate(raw):
        next_k=raw[i+1]["stiffness_x"] if i+1<len(raw) else None
        limit=0.7*next_k if next_k is not None else None
        status=("OK" if r["stiffness_x"] is not None and limit is not None and r["stiffness_x"]>=limit
                else ("NOT OK" if r["stiffness_x"] is not None and limit is not None else "-"))
        out.append({**r,"next_stiffness_x":next_k,"limit_x":limit,"status_x":status})

    if not any(r["stiffness_x"] is not None for r in out):
        mapping["_diagnostic"]=(f"Story Shears EQX first-match rows={len(shear_map)}; Diaphragm Drifts EQX first-match rows={len(drift_map)}; "
                                f"STORY DATA rows={len(heights)}. Check Access table names and column mappings.")
    return out,mapping


def process_327(cur, shears_table, drift_table, story_table):
    """Table 3.2.7 — Story stiffness along Y, matching the workbook formula exactly.

    Workbook formula (C180):
      =ABS(INDEX('STOREY SHEARS'!B:J,
          MATCH(Story&EQY, StoryShears!B:B&StoryShears!C:C,0),6)
          /
          INDEX('4.5 Storey drift control'!N:R,
          MATCH(Story, '4.5 Storey drift control'!N:N,0),5))

    The 5th field of N:R is the Y-direction inter-storey drift (already
    multiplied by storey height by the 4.5 drift-control calculation). In the
    source Diaphragm Drifts table, the workbook obtains that value from the
    EQY match + 1 row and the 9th field of B:J, then multiplies by Story Data
    height. We reproduce that logic here rather than using a guessed DriftY
    column.
    """
    scols=[str(c.column_name) for c in cur.columns(table=shears_table)]
    dcols=[str(c.column_name) for c in cur.columns(table=drift_table)]
    ycols=[str(c.column_name) for c in cur.columns(table=story_table)]

    s_story=find_col(scols,["Story","Storey"])
    s_load=find_col(scols,["Load","OutputCase","LoadCase","Case"])
    d_story=find_col(dcols,["Story","Storey"])
    d_load=find_col(dcols,["Load","OutputCase","LoadCase","Case"])
    y_story=find_col(ycols,["Story","Storey"])
    y_height=find_col(ycols,["Story Height","Height","Storey Height","H","Elevation Difference","StoryHeight"])
    y_elev=find_col(ycols,["Elevation","Story Elevation","Storey Elevation","Z","Level"])

    # Positional fallbacks corresponding to the workbook's exported ranges.
    if not s_story and len(scols)>=1: s_story=scols[0]
    if not s_load and len(scols)>=2: s_load=scols[1]
    if not d_story and len(dcols)>=1: d_story=dcols[0]
    if not d_load and len(dcols)>=3: d_load=dcols[2]
    if not y_story and len(ycols)>=1: y_story=ycols[0]
    if not y_height and len(ycols)>=2: y_height=ycols[1]
    # STORY DATA B:E: Story, Height, Elevation, irregularity flag.
    if not y_elev and len(ycols)>=3: y_elev=ycols[2]

    mapping={
        "Story Shears":{"Story":s_story,"Load":s_load,
                         "ShearYField":scols[5] if len(scols)>=6 else None},
        "Diaphragm Drifts":{"Story":d_story,"Load":d_load,
                             "YField_BJ_9th":dcols[8] if len(dcols)>=9 else None},
        "STORY DATA":{"Story":y_story,"Height":y_height,"Elevation":y_elev},
        "LoadCase":"EQY"
    }
    if not all([s_story,s_load,d_story,d_load,y_story,y_height]) or len(scols)<6 or len(dcols)<9:
        return [], mapping

    # Story Data: height and actual elevation. Elevation is the authoritative
    # filter/order source; Ground FL at elevation 0.00 is included.
    heights={}; elevations={}; story_labels={}
    for r in cur.execute(f"SELECT {q(y_story)},{q(y_height)},{q(y_elev)} FROM {q(story_table)}").fetchall():
        st=str(r[0]).strip() if r[0] is not None else ""
        h=num(r[1]); ev=num(r[2])
        if st:
            key=story_key(st)
            if h is not None: heights[key]=h
            if ev is not None: elevations[key]=ev
            story_labels[key]=st

    # Story shear: Excel INDEX(B:J,...,6) => sixth field = Y shear.
    # MATCH(...,0) keeps the FIRST Story+EQY record.
    shear_map={}
    sf=scols[5]
    for r in cur.execute(f"SELECT {q(s_story)},{q(s_load)},{q(sf)} FROM {q(shears_table)}").fetchall():
        st=str(r[0]).strip() if r[0] is not None else ""
        lc=str(r[1]).strip().upper() if r[1] is not None else ""
        key=story_key(st) if st else ""
        if key and lc=="EQY" and key not in shear_map:
            shear_map[key]=num(r[2])

    # Diaphragm drift: reproduce the workbook's +1 and 9th-field behavior.
    # We first locate the first Story+EQY row, then take the NEXT physical row,
    # exactly as the Excel formula does with MATCH(...)+1.
    drows=cur.execute(f"SELECT {q(d_story)},{q(d_load)},{q(dcols[8])} FROM {q(drift_table)}").fetchall()
    drift_y_next={}
    first_match={}
    for i,r in enumerate(drows):
        st=str(r[0]).strip() if r[0] is not None else ""
        lc=str(r[1]).strip().upper() if r[1] is not None else ""
        key=story_key(st) if st else ""
        if key and lc=="EQY" and key not in first_match:
            first_match[key]=i
    for key,i in first_match.items():
        j=i+1
        if j < len(drows):
            drift_y_next[key]=num(drows[j][2])

    # Use the authoritative report master.  It already excludes only the
    # final/highest top story while retaining every story down to elevation 0.00.
    ordered=[(m["key"],m["story"],m["elevation"]) for m in report_story_master(cur, story_table)]

    raw=[]
    for key,st,ev in ordered:
        shear=shear_map.get(key)
        dy=drift_y_next.get(key)
        h=heights.get(key)
        dr_yy=abs(dy*h) if dy is not None and h is not None else None
        ky=abs(shear/dr_yy) if shear is not None and dr_yy not in (None,0) else None
        raw.append({"story":st,"elevation":ev,"storey_shear_y":shear,
                    "drift_y_raw":dy,"storey_height":h,"dr_yy":dr_yy,
                    "stiffness_y":ky})

    out=[]
    for i,r in enumerate(raw):
        next_k=raw[i+1]["stiffness_y"] if i+1<len(raw) else None
        limit=0.7*next_k if next_k is not None else None
        status=("OK" if r["stiffness_y"] is not None and limit is not None and r["stiffness_y"]>=limit
                else ("NOT OK" if r["stiffness_y"] is not None and limit is not None else "-"))
        out.append({**r,"next_stiffness_y":next_k,"limit_y":limit,"status_y":status})

    if not any(r["stiffness_y"] is not None for r in out):
        mapping["_diagnostic"]=(f"Story Shears EQY first-match rows={len(shear_map)}; "
                                f"Diaphragm Drifts EQY first-match rows={len(first_match)}; "
                                f"EQY next-row Y-drift rows={len(drift_y_next)}; "
                                f"STORY DATA rows={len(heights)}. Check the EQY row pairing in Diaphragm Drifts.")
    return out,mapping



def process_328(cur, cm_table, story_table):
    """Table 3.2.8 — Mass Distribution along height of the Building.

    Workbook source logic:
      Mass = VLOOKUP(Story, 'Center of Mass'!B:M, 3, 0)

    In the Access database the corresponding source is Center Mass Rigidity.
    Its mass field is mapped flexibly, with MassX preferred because the Excel
    source's third field is MassX.  Story Data elevation is authoritative:
    include elevation >= 0.00 and display highest elevation to 0.00.

    Checks reproduce the workbook pattern:
      Mi < 2Mi+1  and  Mi < 2Mi-1
    with the first/top and last/bottom rows left blank where the adjacent
    comparison does not exist.
    """
    ccols = [str(c.column_name) for c in cur.columns(table=cm_table)]
    scols = [str(c.column_name) for c in cur.columns(table=story_table)]

    cm_story = find_col(ccols, ["Story", "Storey"])
    cm_mass = find_col(ccols, ["MassX", "Mass X", "Mass", "MassY", "Mass Y"])
    sd_story = find_col(scols, ["Story", "Storey"])
    sd_elev = find_col(scols, ["Elevation", "Story Elevation", "Storey Elevation", "Z", "Level"])

    if not cm_story and ccols:
        cm_story = ccols[0]
    if not cm_mass and len(ccols) >= 3:
        cm_mass = ccols[2]
    if not sd_story and scols:
        sd_story = scols[0]
    if not sd_elev and len(scols) >= 3:
        sd_elev = scols[2]

    mapping = {
        "Center Mass Rigidity": {
            "Story": cm_story,
            "Mass": cm_mass,
        },
        "STORY DATA": {
            "Story": sd_story,
            "Elevation": sd_elev,
        }
    }

    if not all([cm_story, cm_mass, sd_story, sd_elev]):
        return [], mapping

    # First-match behavior, consistent with Excel VLOOKUP(...,0).
    mass_map = {}
    cm_rows = cur.execute(
        f"SELECT {q(cm_story)},{q(cm_mass)} FROM {q(cm_table)}"
    ).fetchall()
    for r in cm_rows:
        st = str(r[0]).strip() if r[0] is not None else ""
        key = story_key(st) if st else ""
        if key and key not in mass_map:
            mass_map[key] = num(r[1])

    # Use the same authoritative report master as every other table.
    stories = [(m["key"], m["story"], m["elevation"])
               for m in report_story_master(cur, story_table)]

    raw = []
    for key, st, ev in stories:
        raw.append({
            "story": st,
            "elevation": ev,
            "mass": mass_map.get(key)
        })

    out = []
    for i, r in enumerate(raw):
        # Top row: no upper-floor comparison.
        # Bottom row at elevation 0.00: no lower-floor comparison.
        upper = raw[i-1]["mass"] if i > 0 else None
        lower = raw[i+1]["mass"] if i + 1 < len(raw) else None

        # In the workbook's top-to-bottom display, Mi < 2Mi+1 compares
        # the current mass with the mass on the row above it, while
        # Mi < 2Mi-1 compares with the row below it.
        status_upper = (
            "OK" if r["mass"] is not None and upper is not None and r["mass"] < 2 * upper
            else ("NOT OK" if r["mass"] is not None and upper is not None else "-")
        )
        status_lower = (
            "OK" if r["mass"] is not None and lower is not None and r["mass"] < 2 * lower
            else ("NOT OK" if r["mass"] is not None and lower is not None else "-")
        )

        out.append({
            **r,
            "mass_status_upper": status_upper,
            "mass_status_lower": status_lower
        })

    if not any(r["mass"] is not None for r in out):
        mapping["_diagnostic"] = (
            f"Center Mass Rigidity rows={len(cm_rows)}; "
            f"mapped mass rows={len(mass_map)}; "
            f"STORY DATA rows at/above 0.00={len(stories)}. "
            "Check the Story and MassX fields in Center Mass Rigidity."
        )

    return out, mapping


def save_325_calculation_db(path, detail, summary):
    import sqlite3
    cn=sqlite3.connect(path); cur=cn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS calculated_area_y (id INTEGER PRIMARY KEY AUTOINCREMENT, story TEXT, element_type TEXT, s REAL, x REAL, u REAL, v REAL, cmx REAL, cmy REAL, calculated_y REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS storey_ls_summary (story TEXT PRIMARY KEY, sum_s REAL, sum_y REAL, slab_count INTEGER, ls REAL)")
    cur.execute("DELETE FROM calculated_area_y"); cur.execute("DELETE FROM storey_ls_summary")
    for r in detail:
        cur.execute("INSERT INTO calculated_area_y(story,element_type,s,x,u,v,cmx,cmy,calculated_y) VALUES(?,?,?,?,?,?,?,?,?)",(r["story"],r["type"],r["s"],r["x"],r["u"],r["v"],r["cmx"],r["cmy"],r["y"]))
    for r in summary:
        cur.execute("INSERT INTO storey_ls_summary(story,sum_s,sum_y,slab_count,ls) VALUES(?,?,?,?,?)",(r["story"],r["sum_s"],r["sum_y"],r["slab_count"],r["ls"]))
    cn.commit(); cn.close()

@app.post("/import")
async def import_database(request: Request, file: UploadFile = File(...)):
    # Save the uploaded Access database locally, then run all calculations.
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".mdb", ".accdb"}:
        state = load_state()
        state["message"] = "Please select a Microsoft Access .mdb or .accdb database."
        save_state(state)
        return templates.TemplateResponse(
            request=request, name="index.html", context={"d": state, "selected": None}
        )

    DATA.mkdir(exist_ok=True)
    target = DATA / ("uploaded_access" + suffix)
    with target.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        state = process_db(str(target))
        state["access_file"] = str(target)
        save_state(state)
    except Exception as exc:
        state = load_state()
        state["access_file"] = str(target)
        state["message"] = f"Calculation error: {exc}"
        save_state(state)

    return templates.TemplateResponse(
        request=request, name="index.html", context={"d": state, "selected": None}
    )

@app.post("/recalculate")
async def recalculate(request: Request):
    state = load_state()
    path = state.get("access_file")
    if not path or not Path(path).exists():
        state["message"] = "No Access database has been imported yet."
        save_state(state)
        return templates.TemplateResponse(
            request=request, name="index.html", context={"d": state, "selected": None}
        )
    try:
        state = process_db(path)
        state["access_file"] = path
        save_state(state)
    except Exception as exc:
        state["message"] = f"Calculation error: {exc}"
        save_state(state)
    return templates.TemplateResponse(
        request=request, name="index.html", context={"d": state, "selected": None}
    )

def report_story_master(cur, story_table):
    """Return the authoritative report story list from STORY DATA.

    Report rule requested by the user:
      - exclude ONLY stories below elevation 0.00;
      - exclude ONLY the final/highest top story;
      - include every other story, including GROUND FL at elevation 0.00;
      - order from highest retained elevation down to 0.00.
    """
    cols=[str(c.column_name) for c in cur.columns(table=story_table)]
    ys=find_col(cols,["Story","Storey"]) or (cols[0] if cols else None)
    ye=find_col(cols,["Elevation","Story Elevation","Storey Elevation","Z","Level"])
    # STORY DATA exported layout is B:E = Story, Height, Elevation, ...
    if not ye and len(cols)>=3:
        ye=cols[2]
    if not ys or not ye:
        raise RuntimeError(f"Could not identify Story/Elevation columns in STORY DATA: {cols}")

    rows=[]; seen=set()
    sql=f"SELECT {q(ys)},{q(ye)} FROM {q(story_table)}"
    for raw_story, raw_elev in cur.execute(sql).fetchall():
        st=str(raw_story).strip() if raw_story is not None else ""
        ev=num(raw_elev)
        if not st or ev is None or ev < 0.0:
            continue
        k=story_key(st)
        if not k or k in seen:
            continue
        seen.add(k)
        rows.append({"key":k,"story":st,"elevation":ev})

    # Remove ONLY the highest/final top floor.  Never remove elevation 0.00.
    # In the normal multi-storey case the highest row is > 0.00, so it is
    # dropped and every remaining row, including GROUND FL, is retained.
    rows.sort(key=lambda x:x["elevation"], reverse=True)
    if len(rows) > 1 and rows[0]["elevation"] > 0.0:
        rows = rows[1:]
    return rows


def _ground_alias_key(k):
    return k in {
        "groundfl", "groundfloor", "groundlevel", "ground",
        "base1fl", "base1floor", "base1"
    }


def reorder_and_filter_by_elevation(rows, cur, story_table):
    """Merge calculated rows onto the common STORY DATA report list.

    This function is intentionally used as the final population step for every
    table. It prevents an absent source-calculation row from deleting a valid
    Story Data row. In particular, GROUND FL (0.00) is always rendered.
    """
    master=report_story_master(cur, story_table)
    existing={}
    for row in rows or []:
        st=str(row.get("story","")).strip()
        if not st:
            continue
        k=story_key(st)
        if k not in existing:
            existing[k]=dict(row)

    # Match common zero-elevation aliases to the actual STORY DATA ground row.
    ground=next((m for m in master if abs(m["elevation"]) < 1e-9), None)
    if ground:
        gk=ground["key"]
        if gk not in existing:
            for k,row in existing.items():
                if _ground_alias_key(k):
                    existing[gk]=row
                    break

    merged=[]
    for m in master:
        row=dict(existing.get(m["key"], {}))
        row["story"]=m["story"]
        row["elevation"]=m["elevation"]
        merged.append(row)
    return merged


def reorder_report325_by_elevation(rows, cur, story_table):
    return reorder_and_filter_by_elevation(rows, cur, story_table)

def process_db(path):
    state = load_state()
    cn = connect(path)
    try:
        cur = cn.cursor()
        names = get_objects(cur)

        t322 = find_table(names, ["Center Mass Rigidity", "Center Mass Rigidity Table"])
        t323 = find_table(names, ["Diaphragm CM Displacements"])
        area = find_table(names, ["Area Assignments Summary"])
        cm = find_table(names, ["Center Mass Rigidity", "Center Mass Rigidity Table"])
        shears = find_table(names, ["Story Shears", "Story Shear", "Storey Shears", "Storey Shear", "STOREY SHEARS"])
        drift = find_table(names, ["Diaphragm Drifts", "Diaphram Drift", "Diaphragm Drift", "Story Drifts", "Story Drift"])
        story_data = find_table(names, ["STORY DATA", "Story Data", "Storey Data"])

        if not t322:
            raise RuntimeError("The source table for Table 3.2.2 ('Center Mass Rigidity') was not found.")
        if not t323:
            raise RuntimeError("The source table 'Diaphragm CM Displacements' was not found.")
        if not area:
            raise RuntimeError("The source table 'Area Assignments Summary' was not found.")
        if not cm:
            raise RuntimeError("The source table 'Center Mass Rigidity' was not found.")
        if not shears:
            raise RuntimeError("The source table 'Story Shears' was not found. Expected the Access table named Story Shears.")
        if not drift:
            raise RuntimeError("The source table 'Diaphragm Drifts' was not found.")
        if not story_data:
            raise RuntimeError("The source table 'STORY DATA' was not found.")

        # STORY DATA elevation is authoritative for every storey-based table.
        # Keep elevation 0.00; exclude only rows below 0.00.
        allowed_story_keys = get_nonnegative_story_keys(cur, story_data)

        r322, m322 = process_322(cur, t322, allowed_story_keys)
        r323, m323, cases = process_323(cur, t323, allowed_story_keys)
        r325, detail325, marea, mcm = process_325(cur, area, cm, allowed_story_keys)
        r326, m326 = process_326(cur, shears, drift, story_data)
        r327, m327 = process_327(cur, shears, drift, story_data)
        r328, m328 = process_328(cur, cm, story_data)

        if not r322:
            raise RuntimeError(
                "Table 3.2.2 could not be calculated. Detected mapping: "
                + json.dumps(m322)
            )
        if not r323:
            raise RuntimeError(
                "Table 3.2.3 could not be calculated. Detected mapping: "
                + json.dumps(m323)
            )
        if not r325:
            raise RuntimeError(
                "Table 3.2.5 could not be calculated. Detected mapping: "
                + json.dumps({
                    "Area Assignments Summary": marea,
                    "Center Mass Rigidity": mcm
                })
            )
        if not r326:
            raise RuntimeError(
                "Table 3.2.6 could not be calculated. Detected mapping: "
                + json.dumps(m326)
            )
        if not r327:
            raise RuntimeError(
                "Table 3.2.7 could not be calculated. Detected mapping: "
                + json.dumps(m327)
            )
        if not r328:
            raise RuntimeError(
                "Table 3.2.8 could not be calculated. Detected mapping: "
                + json.dumps(m328)
            )

        r324 = process_324(r322, r323)

        # Elevation 0.00 / Ground FL is mandatory in every displayed table.
        # Story Data remains authoritative for the actual elevation.
        r322 = ensure_zero_story(r322, cur, story_data)
        r323 = ensure_zero_story(r323, cur, story_data)
        r324 = ensure_zero_story(r324, cur, story_data)
        r325 = ensure_zero_story(r325, cur, story_data)
        r326 = ensure_zero_story(r326, cur, story_data)
        r327 = ensure_zero_story(r327, cur, story_data)
        r328 = ensure_zero_story(r328, cur, story_data)

        # All report tables use the same authoritative Story Data elevation: 0.00 is included,
        # while the highest/final elevation is omitted from the displayed report.
        r322 = reorder_and_filter_by_elevation(r322, cur, story_data)
        r323 = reorder_and_filter_by_elevation(r323, cur, story_data)
        r324 = reorder_and_filter_by_elevation(r324, cur, story_data)
        r325 = reorder_and_filter_by_elevation(r325, cur, story_data)
        r326 = reorder_and_filter_by_elevation(r326, cur, story_data)
        r327 = reorder_and_filter_by_elevation(r327, cur, story_data)
        r328 = reorder_and_filter_by_elevation(r328, cur, story_data)

        # Build the report-format Table 3.2.5 output.
        r324_by_story = {story_key(r.get("story")): r for r in r324}

        # Use the union of the calculated Ls rows and Table 3.2.4 rows so the
        # required elevation-0 storey cannot disappear from Table 3.2.5.
        report_source = {story_key(r.get("story")): r for r in r325}
        for r in r324:
            report_source.setdefault(story_key(r.get("story")), {"story": r.get("story"), "ls": None})
        report325 = []
        for k, r in report_source.items():
            st = str(r.get("story", "")).strip()
            old = r324_by_story.get(k, {})

            rx = old.get("rx", old.get("r_x"))
            ry = old.get("ry", old.get("r_y"))
            ls = r.get("ls")

            report325.append({
                "story": st,
                "rx": rx,
                "ls_x": ls,
                "status_x": (
                    "OK" if rx is not None and ls is not None and rx >= ls
                    else ("NOT OK" if rx is not None and ls is not None else "Missing data")
                ),
                "ry": ry,
                "ls_y": ls,
                "status_y": (
                    "OK" if ry is not None and ls is not None and ry >= ls
                    else ("NOT OK" if ry is not None and ls is not None else "Missing data")
                ),
            })

        calc_path = str(DATA / "structural_calculations.db")
        save_325_calculation_db(calc_path, detail325, r325)

        state.update({
            "tables": names,
            "table_322": r322,
            "table_323": r323,
            "table_324": r324,
            "table_325": r325,
            "table_325_report": report325,
            "table_326": r326,
            "table_327": r327,
            "table_328": r328,
            "area_detail_325": detail325,
            "map_322": m322,
            "map_323": m323,
            "map_325_area": marea,
            "map_325_cm": mcm,
            "map_326": m326,
            "map_327": m327,
            "map_328": m328,
            "calc_db": calc_path,
            "message": (
                f"Successfully calculated Tables 3.2.2 ({len(r322)} storeys), "
                f"3.2.3 ({len(r323)} storeys), 3.2.4 ({len(r324)} storeys), "
                f"3.2.5 ({len(r325)} storeys), 3.2.6 ({len(r326)} storeys), 3.2.7 ({len(r327)} storeys), and 3.2.8 ({len(r328)} storeys). "
                "Storeys below 0.00 and the highest/final elevation were omitted from the displayed tables; elevation 0.00 is included. "
                "Table 3.2.5 uses Area Assignments Summary and Center Mass Rigidity. "
                f"Load cases detected: {', '.join(cases)}."
            )
        })
        return state
    finally:
        cn.close()
