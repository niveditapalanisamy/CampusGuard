import math, time

from collections import deque

from heapq import heappush, heappop

import plotly.graph_objects as go
import requests
import streamlit as st



st.set_page_config(page_title="CampusGuard · SRM KTR", page_icon="✦", layout="wide")

st.markdown("""

<style>

.stApp{background:radial-gradient(ellipse at 10% 0%,#102a3b 0,#07131d 48%,#061019 100%);color:#e5eef5}

.block-container{padding-top:1.2rem;max-width:1600px}

.cgbrand{display:flex;gap:14px;align-items:center;margin-bottom:1.5rem}

.cglogo{background:#123545;border:1px solid #1d6470;border-radius:14px;padding:10px 15px;color:#67e8f9;font-size:26px}

.cgtitle{font-size:24px;font-weight:900;letter-spacing:1.6px}.cgtitle span{color:#5eead4}

.cgsub{font-size:10px;letter-spacing:1.7px;color:#8ba3b5;margin-top:4px}

.eyebrow{font-size:10px;font-weight:800;letter-spacing:2px;color:#62e6d2;text-transform:uppercase}

.hero{font-size:clamp(34px,4vw,54px);font-weight:850;line-height:1.04;letter-spacing:-1.8px;margin:12px 0}

.hero span{color:#5eead4}.desc{color:#9eb3c1;line-height:1.7}

.metric{background:linear-gradient(145deg,#142938,#0a1924);border:1px solid #20394a;border-radius:16px;padding:16px 18px;min-height:116px}

.metric-label{color:#8ca6b8;font-size:10px;font-weight:800;letter-spacing:1.4px}

.metric-value{font-size:30px;font-weight:850;color:#effcfb;margin:7px 0}

.metric-note{font-size:11px;color:#8ca6b8}

.stButton>button{border-radius:10px;border:1px solid #28495a;min-height:42px;font-weight:700}

.stButton>button[kind=primary]{background:linear-gradient(100deg,#0f766e,#0e9f91);border-color:#2dd4bf;color:white}

div[data-testid=stMetric]{background:#102433;border:1px solid #20394a;border-radius:14px;padding:12px}

div[data-testid=stMetricLabel]{color:#94adbd} div[data-testid=stMetricValue]{color:#effcfb}

hr{border-color:#20394a}

</style>

<div class="cgbrand"><div class="cglogo">✦</div><div><div class="cgtitle">CAMPUS<span>GUARD</span></div><div class="cgsub">SRM KTR · EVACUATION COMMAND</div></div><div style="margin-left:auto;text-align:right"><div class="eyebrow">● OFFLINE SIMULATION</div><div class="cgsub">LOCAL GRAPH · NO MAP TILES</div></div></div>

""", unsafe_allow_html=True)



N={
"ENG_GATE":("Engineering Gate",60,260,"start"),
"ENG_A":("Engineering Block A",155,190,"building"),
"JUNCTION_N":("North Junction",255,120,"junction"),
"LIBRARY":("Library Walkway",355,150,"building"),
"SAFE_NORTH":("North Assembly Point",535,90,"exit"),
"JUNCTION_C":("Central Walkway",270,265,"junction"),
"ENG_B":("Engineering Block B",385,270,"building"),
"LAB":("Laboratory Complex",465,365,"building"),
"SAFE_EAST":("East Assembly Point",570,300,"exit"),
"HOSTEL_PATH":("Hostel Connector",160,390,"building"),
"JUNCTION_S":("South Junction",285,405,"junction"),
"SAFE_SOUTH":("South Assembly Point",430,470,"exit"),
"ADMIN_BLOCK":("Administrative Block",95,115,"building"),
"AUDITORIUM":("Main Auditorium",185,65,"building"),
"FOOD_COURT":("Food Court",75,355,"building"),
"BOYS_HOSTEL":("Boys Hostel Connector",75,445,"building"),
"GIRLS_HOSTEL":("Girls Hostel Connector",190,475,"building"),
"SPORTS_COMPLEX":("Sports Complex",330,500,"building"),
"MEDICAL_CENTRE":("Medical Centre",555,420,"building"),
"TECH_PARK":("Tech Park",470,205,"building"),
"PARKING_AREA":("Parking Area",610,175,"building"),
"SAFE_WEST":("West Assembly Point",35,75,"exit"),
"SAFE_CENTRAL":("Central Assembly Point",330,45,"exit"),
"SAFE_MEDICAL":("Medical-side Assembly Point",630,455,"exit")}

E=[
("ENG_GATE","ENG_A",1),("ENG_A","JUNCTION_N",1.2),("JUNCTION_N","LIBRARY",1),
("LIBRARY","SAFE_NORTH",1.7),("ENG_A","JUNCTION_C",1.1),("JUNCTION_N","JUNCTION_C",1),
("JUNCTION_C","ENG_B",1.1),("ENG_B","SAFE_EAST",1.8),("ENG_B","LAB",1.2),
("LAB","SAFE_EAST",1),("JUNCTION_C","HOSTEL_PATH",1.5),("HOSTEL_PATH","JUNCTION_S",1.1),
("JUNCTION_S","SAFE_SOUTH",1.6),("JUNCTION_S","LAB",1.4),("JUNCTION_C","JUNCTION_S",1.5),
("LIBRARY","ENG_B",1.8),
("ENG_GATE","ADMIN_BLOCK",1.1),("ADMIN_BLOCK","AUDITORIUM",1.0),
("AUDITORIUM","JUNCTION_N",1.3),("ADMIN_BLOCK","SAFE_WEST",1.5),
("ENG_GATE","FOOD_COURT",1.4),("FOOD_COURT","HOSTEL_PATH",1.2),
("FOOD_COURT","BOYS_HOSTEL",1.1),("BOYS_HOSTEL","GIRLS_HOSTEL",1.3),
("GIRLS_HOSTEL","JUNCTION_S",1.2),("JUNCTION_S","SPORTS_COMPLEX",1.1),
("SPORTS_COMPLEX","SAFE_SOUTH",1.0),("AUDITORIUM","SAFE_CENTRAL",1.4),
("SAFE_CENTRAL","LIBRARY",1.6),("LIBRARY","TECH_PARK",1.2),
("TECH_PARK","ENG_B",1.0),("TECH_PARK","PARKING_AREA",1.1),
("PARKING_AREA","SAFE_NORTH",1.4),("LAB","MEDICAL_CENTRE",1.0),
("MEDICAL_CENTRE","SAFE_MEDICAL",1.2),("MEDICAL_CENTRE","SAFE_EAST",1.5)
]
S={

"All clear":([],[],"All demo walkways are open."),

"North walkway blocked":([("JUNCTION_N","LIBRARY"),("LIBRARY","SAFE_NORTH")],[],"North approach closed."),

"Lab-area incident":([("ENG_B","LAB"),("LAB","SAFE_EAST"),("JUNCTION_S","LAB")],["LAB"],"Laboratory complex excluded."),

"Multiple obstructions":([("JUNCTION_N","LIBRARY"),("ENG_B","SAFE_EAST"),("JUNCTION_C","JUNCTION_S")],[],"Multiple corridors closed.")}



def graph(scenario):

    blocked, badnodes, _=S[scenario]; blocked={frozenset(e) for e in blocked}; g={n:[] for n in N if n not in badnodes}

    for a,b,w in E:

        if a not in badnodes and b not in badnodes and frozenset((a,b)) not in blocked:

            g[a].append((b,w));g[b].append((a,w))

    return g



def bfs(start,goal,g):

    t=time.perf_counter();q=deque([start]);parent={start:None};seen=[]

    while q:

        u=q.popleft();seen.append(u)

        if u==goal:break

        for v,_ in g.get(u,[]):

            if v not in parent:parent[v]=u;q.append(v)

    if goal not in parent:return None,seen,(time.perf_counter()-t)*1000,None

    p=[];u=goal

    while u is not None:p.append(u);u=parent[u]

    p.reverse();w={(a,b):c for a,b,c in E};cost=sum(w.get((a,b),w.get((b,a),1)) for a,b in zip(p,p[1:]))

    return p,seen,(time.perf_counter()-t)*1000,cost



def astar(start,goal,g):

    h=lambda n: math.dist(N[n][1:3],N[goal][1:3])/100

    t=time.perf_counter();heap=[(h(start),0,start)];parent={start:None};costs={start:0};seen=[]

    while heap:

        _,gc,u=heappop(heap)

        if gc>costs.get(u,float("inf")):continue

        seen.append(u)

        if u==goal:break

        for v,w in g.get(u,[]):

            nc=costs[u]+w

            if nc<costs.get(v,float("inf")):

                costs[v]=nc;parent[v]=u;heappush(heap,(nc+h(v),nc,v))

    if goal not in parent:return None,seen,(time.perf_counter()-t)*1000,None

    p=[];u=goal

    while u is not None:p.append(u);u=parent[u]

    p.reverse();return p,seen,(time.perf_counter()-t)*1000,costs[goal]



def point(path,progress,offset=0):

    if not path:return None

    if len(path)==1:return N[path[0]][1:3]

    z=max(0,min(1,progress-offset))*(len(path)-1);i=min(int(z),len(path)-2);f=1 if progress>=1 else z-i

    a,b=N[path[i]],N[path[i+1]]

    return (a[1]+(b[1]-a[1])*f,a[2]+(b[2]-a[2])*f)



def mapfig(start,goal,scenario,path,seen,progress,groups,possible_routes=None,best_path=None):

    blocked,badnodes,_=S[scenario];blocked={frozenset(e) for e in blocked};fig=go.Figure()

    for a,b,w in E:

        na,nb=N[a],N[b];closed=frozenset((a,b)) in blocked or a in badnodes or b in badnodes

        fig.add_trace(go.Scatter(x=[na[1],nb[1]],y=[na[2],nb[2]],mode="lines",

          line=dict(color="#fb7185" if closed else "#415668",width=5 if closed else 3,dash="dash" if closed else "solid"),

          hoverinfo="text",text=[f"{na[0]} ↔ {nb[0]} · {'BLOCKED' if closed else str(w)+' units'}"]*2,showlegend=False))

        if closed:

            fig.add_trace(go.Scatter(x=[(na[1]+nb[1])/2],y=[(na[2]+nb[2])/2],mode="markers+text",

              marker=dict(symbol="x",size=15,color="#fb7185"),text=["CLOSED"],textposition="top center",

              textfont=dict(color="#fda4af",size=9),showlegend=False,hoverinfo="skip"))

    colors={"start":"#38bdf8","building":"#8298aa","junction":"#fbbf24","exit":"#34d399"}

    for kind in colors:

        ids=[i for i,d in N.items() if d[3]==kind and i not in badnodes]

        fig.add_trace(go.Scatter(x=[N[i][1] for i in ids],y=[N[i][2] for i in ids],mode="markers+text",

          name={"start":"Start","building":"Buildings","junction":"Junctions","exit":"Safe exits"}[kind],

          text=[N[i][0] for i in ids],textposition="bottom center",textfont=dict(size=10,color="#d8e6ef"),

          marker=dict(size=[22 if i in (start,goal) else 15 for i in ids],

          color=[("#38bdf8" if i==start else "#34d399" if i==goal else colors[kind]) for i in ids],

          line=dict(color="#e2e8f0",width=1.2),symbol=["square" if kind=="building" else "circle"]*len(ids)),

          customdata=ids,hovertemplate="%{text}<br>%{customdata}<extra></extra>"))

    if seen:

        ids=[i for i in seen if i not in (start,goal) and i not in badnodes]

        fig.add_trace(go.Scatter(x=[N[i][1] for i in ids],y=[N[i][2] for i in ids],mode="markers",

          marker=dict(size=11,color="#a78bfa",symbol="circle-open",line=dict(width=2,color="#a78bfa")),name="Explored nodes"))

    # Draw up to three candidate routes so users can compare alternatives.
    route_colors = ["#818cf8", "#f59e0b", "#38bdf8"]
    possible_routes = possible_routes or []
    for idx, candidate in enumerate(possible_routes):
        candidate_path = candidate.get("path", [])
        if not candidate_path or candidate_path == best_path:
            continue
        fig.add_trace(go.Scatter(
            x=[N[i][1] for i in candidate_path], y=[N[i][2] for i in candidate_path],
            mode="lines", line=dict(color=route_colors[idx % len(route_colors)], width=4, dash="dash"),
            name=f"{candidate.get('label', f'Alternative {idx}') } · {candidate.get('cost', 0):.1f}",
            hoverinfo="text", text=[" → ".join(N[n][0] for n in candidate_path)] * len(candidate_path),
        ))

    # Best route (lowest weighted cost) is the primary highlighted path.
    if best_path:
        fig.add_trace(go.Scatter(x=[N[i][1] for i in best_path],y=[N[i][2] for i in best_path],mode="lines",
          line=dict(color="#2dd4bf",width=8),name="BEST ROUTE",hoverinfo="text",
          text=[" → ".join(N[n][0] for n in best_path)] * len(best_path)))

    # If BFS chose a different path, show it distinctly from the weighted best route.
    if path and best_path and path != best_path:
        fig.add_trace(go.Scatter(x=[N[i][1] for i in path],y=[N[i][2] for i in path],mode="lines",
          line=dict(color="#f8fafc",width=3,dash="dot"),name="Selected algorithm route",hoverinfo="skip"))

    if path:

        animation_path = best_path or path
        pts=[point(animation_path,progress,i/(groups*1.8)) for i in range(groups)]

        fig.add_trace(go.Scatter(x=[p[0] for p in pts],y=[p[1] for p in pts],mode="markers",

          marker=dict(size=13,color="#f8fafc",line=dict(color="#06b6d4",width=3)),name="Evacuee groups"))

    if scenario=="Lab-area incident":

        x,y=N["LAB"][1:3];fig.add_shape(type="circle",x0=x-35,y0=y-35,x1=x+35,y1=y+35,line=dict(color="#fb7185",width=2,dash="dash"),fillcolor="rgba(251,113,133,.15)")

        fig.add_annotation(x=x,y=y+44,text="INCIDENT ZONE",showarrow=False,font=dict(color="#fda4af",size=10))

    fig.update_layout(height=560,margin=dict(l=4,r=4,t=8,b=4),paper_bgcolor="#0b1722",plot_bgcolor="#0b1722",

      font=dict(color="#d8e6ef"),legend=dict(orientation="h",yanchor="bottom",y=1.01,x=0),

      xaxis=dict(visible=False,range=[5,680]),yaxis=dict(visible=False,range=[535,5],scaleanchor="x",scaleratio=1),

      dragmode="pan",hoverlabel=dict(bgcolor="#132735",font_color="#e5f4fa"))

    return fig



if "result" not in st.session_state: st.session_state.result=None

if "progress" not in st.session_state: st.session_state.progress=0.0

if "logs" not in st.session_state: st.session_state.logs=["Offline campus graph initialized.","Choose a scenario and calculate a route."]

def log(msg):
    st.session_state.logs.insert(0, time.strftime("%H:%M:%S") + "  " + msg)
    st.session_state.logs = st.session_state.logs[:8]


def reset_simulation():
    """Reset state in a callback before Streamlit recreates the widgets."""
    st.session_state.result = None
    st.session_state.progress = 0.0
    st.session_state.scenario = "All clear"
    st.session_state.algo = "A*"
    st.session_state.logs = [
        "Offline campus graph initialized.",
        "Simulation reset. Choose a scenario and calculate a route.",
    ]


st.markdown('<div class="eyebrow">SMART CAMPUS SAFETY SYSTEM</div><div class="hero">Every second.<br><span>Every safe step.</span></div><div class="desc">Explore evacuation paths, simulate corridor hazards, and compare BFS with A* through the connected FastAPI routing service. Routes, hazards, markers and metrics update with your selections.</div>',unsafe_allow_html=True)

st.write("")

with st.sidebar:

    st.markdown("## ⌁ Control deck")

    api_base = st.text_input("FastAPI backend URL", value="http://127.0.0.1:8000").strip().rstrip("/")
    try:
        health_response = requests.get(f"{api_base}/api/health", timeout=1.5)
        backend_online = health_response.ok and health_response.json().get("status") == "ok"
    except (requests.RequestException, ValueError):
        backend_online = False
    if backend_online:
        st.success("Backend connected", icon="🟢")
    else:
        st.error("Backend unavailable", icon="🔴")
        st.caption("Start it with: uvicorn backend.main:app --reload --port 8000")

    scenario=st.selectbox("Emergency scenario",list(S),key="scenario")

    st.caption(S[scenario][2])

    starts=[i for i,d in N.items() if d[3]!="exit"]

    goals=[i for i,d in N.items() if d[3]=="exit"]

    start=st.selectbox("Starting location",starts,format_func=lambda i:N[i][0],key="start")

    goal=st.selectbox("Safe destination",goals,format_func=lambda i:N[i][0],key="goal")

    algo=st.radio("Routing algorithm",["A*","BFS"],horizontal=True,key="algo")

    groups=st.slider("Evacuee groups",2,12,6)

    speed=st.slider("Animation speed",0.5,2.5,1.0,0.5)

    live=st.toggle("Live rerouting when inputs change",value=True)

    run=st.button("↗ Find safe route",type="primary",use_container_width=True)

    animate=st.button("▶ Advance animation",use_container_width=True,disabled=not bool(st.session_state.result and st.session_state.result["path"]))

    st.button("↻ Reset simulation", use_container_width=True, on_click=reset_simulation)




signature=(scenario,start,goal,algo)

old=st.session_state.result

if run or (live and old and old["signature"]!=signature):
    try:
        api_response = requests.post(
            f"{api_base}/api/route",
            json={
                "start": start,
                "goal": goal,
                "algorithm": "astar" if algo == "A*" else "bfs",
                "scenario": scenario,
            },
            timeout=8,
        )
        api_response.raise_for_status()
        api_result = api_response.json()
        path = api_result.get("path")
        seen = api_result.get("explored", [])
        elapsed = float(api_result.get("elapsed_ms", 0.0))
        cost = api_result.get("cost")
        routes_response = requests.post(
            f"{api_base}/api/routes",
            json={"start": start, "goal": goal, "algorithm": "astar" if algo == "A*" else "bfs", "scenario": scenario},
            timeout=8,
        )
        routes_response.raise_for_status()
        routes_data = routes_response.json()
        candidates = routes_data.get("routes", [])
        best_route = routes_data.get("best_route")
        st.session_state.result={
            "signature": signature, "path": path, "seen": seen,
            "elapsed": elapsed, "cost": cost, "algo": algo, "error": None,
            "routes": candidates, "best_route": best_route,
        }
        st.session_state.progress=0.0
        log(f"FastAPI: {algo} found route with {len(path)} nodes." if path else f"FastAPI: no route found for {scenario}.")
    except requests.RequestException as exc:
        detail = str(exc)
        try:
            detail = exc.response.json().get("detail", detail) if exc.response is not None else detail
        except (ValueError, AttributeError):
            pass
        st.session_state.result={
            "signature": signature, "path": None, "seen": [], "elapsed": 0.0,
            "cost": None, "algo": algo, "error": str(detail), "routes": [], "best_route": None,
        }
        st.session_state.progress=0.0
        log(f"Backend request failed: {detail}")

result=st.session_state.result

if animate and result and result["path"]:

    st.session_state.progress=min(1.0,st.session_state.progress+0.15*speed)

    log(f"Evacuation progress {st.session_state.progress:.0%}.");st.rerun()

path=result["path"] if result and result["signature"]==signature else None

seen=result["seen"] if result and result["signature"]==signature else None

cost=result["cost"] if result and result["signature"]==signature else None
routes=result.get("routes",[]) if result and result["signature"]==signature else []
best_route=result.get("best_route") if result and result["signature"]==signature else None
best_path=best_route.get("path") if best_route else None
best_cost=best_route.get("cost") if best_route else None

safe=int(round(groups*st.session_state.progress)) if (best_path or path) else 0



cols=st.columns(4)

values=[("SIMULATED SAFE",f"{safe:02d} / {groups}","Evacuee groups at destination"),

("ROUTE DISTANCE",f"{cost:.1f} units" if cost is not None else "—","Weighted graph cost"),

("SEARCHED NODES",str(len(seen)) if seen is not None else "—","Explored by selected algorithm"),

("ROUTE STATUS","NO ROUTE" if result and not path else "ARRIVED" if path and st.session_state.progress>=1 else "IN PROGRESS" if path else "STANDBY",f"{algo} · {scenario}")]

for c,(label,value,note) in zip(cols,values):

    c.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',unsafe_allow_html=True)



st.write("")

left,right=st.columns([1.75,1],gap="large")

with left:

    st.markdown('<div class="eyebrow">LIVE CAMPUS MODEL</div><div style="font-size:23px;font-weight:800;margin:5px 0 12px">Expanded campus network <span style="font-size:12px;color:#8ca6b8;font-weight:500">· schematic view</span></div>',unsafe_allow_html=True)

    st.plotly_chart(mapfig(start,goal,scenario,path,seen,st.session_state.progress,groups,routes,best_path),use_container_width=True,config={"displaylogo":False,"scrollZoom":True})

    st.caption("Schematic graph · routes calculated by FastAPI. Teal = best weighted route; dashed lines = alternatives; dotted white = selected algorithm path when different; red = blocked edges.")

    if best_path:
        st.markdown("**BEST ROUTE:** "+" → ".join(N[n][0] for n in best_path))
    if path and path != best_path:
        st.markdown("**Selected algorithm route:** "+" → ".join(N[n][0] for n in path))
    if result and not best_path:
        st.error("No available route. Select a different exit or clear an obstruction.")
    elif not result:
        st.info("Choose a scenario and press **Find safe route**.")

with right:

    st.markdown('<div class="eyebrow">PATH ANALYSIS</div><div style="font-size:23px;font-weight:800;margin:5px 0 12px">Route intelligence</div>',unsafe_allow_html=True)

    if result and path:

        a,b=st.columns(2);a.metric("Path nodes",len(path));b.metric("Search time",f"{result['elapsed']:.3f} ms")

        st.metric("Route edges",len(path)-1)

        st.progress(st.session_state.progress,text=f"Evacuation progress · {st.session_state.progress:.0%}")

        st.slider("Move markers along route",0.0,1.0,key="progress",step=0.05)

        st.caption(f"Animation speed setting: {speed:.1f}×. Press **Advance animation** to move markers.")

        if st.session_state.progress>=1: st.success("Demo groups reached the selected destination.")

    elif result: st.error("No route exists in this graph state.")

    else: st.info("Run a scenario to inspect path nodes, search time, route cost and explored nodes.")

    if result and routes:
        st.markdown("### Possible routes")
        st.caption("Ranked by total weighted graph cost. The first route is the recommended best route.")
        for candidate in routes:
            route_nodes = candidate.get("path", [])
            route_names = " → ".join(N[n][0] for n in route_nodes)
            if candidate.get("rank") == 1:
                st.success(f"⭐ BEST ROUTE · Cost {candidate.get('cost', 0):.1f} units\n\n{route_names}")
            else:
                st.info(f"{candidate.get('label', 'Alternative')} · Cost {candidate.get('cost', 0):.1f} units\n\n{route_names}")
    elif result:
        st.warning("No possible route was returned for this scenario.")

    st.markdown('<div class="eyebrow" style="margin-top:20px">EVENT STREAM</div><div style="font-size:23px;font-weight:800;margin:5px 0 12px">Simulation log</div>',unsafe_allow_html=True)

    for item in st.session_state.logs[:7]:

        st.markdown(f'<div style="border-left:2px solid #2dd4bf;padding:8px 10px;margin:7px 0;background:rgba(16,36,51,.65);border-radius:0 8px 8px 0;font-size:12px;color:#c7d6df">{item}</div>',unsafe_allow_html=True)

st.divider()

st.caption("CampusGuard · SRM KTR expanded campus-network prototype · illustrative graph only. Do not use for real emergency navigation. Campus safety personnel must verify map geometry, walkways and exits.")
