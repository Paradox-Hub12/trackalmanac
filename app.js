
const teamOf=n=>(DRIVERS.find(d=>d[0]===n)||[])[2];
Object.keys(ARCHTXT).forEach(y=>{ARCHIVE[y]=ARCHTXT[y];});ARCHIVE[2027]={next:true};
const $=s=>document.querySelector(s);
/* ---------- ROUTING: #hash inside the claude.ai artifact, real paths on trackalmanac.com ---------- */
const PATHMODE=!!window.TA_PATHS;
let NAVD=false;
if(PATHMODE){try{const dsc=Object.getOwnPropertyDescriptor(Document.prototype,"title");Object.defineProperty(document,"title",{configurable:true,get(){return dsc.get.call(document);},set(v){if(NAVD)dsc.set.call(document,v);}});}catch(e){}}
const SLUG=r=>r.short.replace(" (Sepang)","").toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"");
const STATIC_KEYS=["season","championship","drivers","teams","calendar","archive","about","contact","privacy","terms","disclaimer","sitemap"];
function keyToPath(k){let m;if(!k||k==="season")return "/";
  if(m=k.match(/^detail-(\d+)(?:-(\w+))?$/)){const r=RACES.find(x=>x.r===+m[1]);return r?`/races/2026/${SLUG(r)}/${m[2]?"#"+m[2]:""}`:"/";}
  if(m=k.match(/^race-(\d+)$/))return "/?race="+m[1];
  if(m=k.match(/^driver-(\w+)$/))return "/drivers/?driver="+m[1];
  if(m=k.match(/^team-([\w-]+)$/))return "/teams/?team="+m[1];
  if(m=k.match(/^archive-(\d{4})$/))return `/archive/${m[1]}/`;
  if(k==="archive-1946-1949")return "/archive/1946-1949/";
  if(k==="sitemap")return "/site-map/";
  return "/"+k+"/";}
const H=k=>PATHMODE?keyToPath(k):"#"+k;
const isLegacy=h=>!!h&&(STATIC_KEYS.includes(h)||/^(race|detail|driver|team|archive)-/.test(h));
function pathToKey(){const p=location.pathname.replace(/index\.html$/,""),q=new URLSearchParams(location.search),h=decodeURIComponent(location.hash.slice(1));let m;
  if(p==="/"){if(isLegacy(h))return {legacy:h};return q.get("race")?"race-"+q.get("race"):"season";}
  if(m=p.match(/^\/races\/2026\/([a-z0-9-]+)\/?$/)){const r=RACES.find(x=>SLUG(x)===m[1]);return r?"detail-"+r.r+(h&&/^\w+$/.test(h)?"-"+h:""):"notfound";}
  if(m=p.match(/^\/archive\/(\d{4})\/?$/))return ARCHIVE[+m[1]]?"archive-"+m[1]:"notfound";
  if(/^\/archive\/1946-1949\/?$/.test(p))return "archive-1946-1949";
  if(/^\/drivers\/?$/.test(p))return q.get("driver")?"driver-"+q.get("driver"):"drivers";
  if(/^\/teams\/?$/.test(p))return q.get("team")?"team-"+q.get("team"):"teams";
  if(/^\/site-map\/?$/.test(p))return "sitemap";
  m=p.match(/^\/([a-z]+)\/?$/);return m&&STATIC_KEYS.includes(m[1])?m[1]:"notfound";}
function curKey(){if(!PATHMODE)return (location.hash||"#season").slice(1)||"season";
  const k=pathToKey();if(k&&k.legacy){const L=k.legacy.replace(/^race-(\d+)$/,"detail-$1");history.replaceState(null,"",keyToPath(L));NAVD=true;return L;}return k;}
function go(k,replace){NAVD=true;if(PATHMODE){history[replace?"replaceState":"pushState"](null,"",keyToPath(k));route();}
  else if(replace){history.replaceState(null,"","#"+k);route();} else if(location.hash==="#"+k)route(); else location.hash=k;}
function pageTitle(k){const T=" | Track Almanac";let m;
  if(!k||k==="season"||k.startsWith("race-"))return "Track Almanac · Races. Drivers. Teams. Numbers.";
  if(m=k.match(/^detail-(\d+)/)){const r=RACES.find(x=>x.r===+m[1]);if(!r)return "Track Almanac";const n=r.gp.replace(" (Sepang)","");return r.res?`${n} 2026: Results, Grid & Lap Chart${T}`:`${n} 2026: Schedule, Session Times & Results${T}`;}
  if(k==="archive-1946-1949")return `Grand Prix Racing 1946–1949: Before the F1 World Championship${T}`;
  if(m=k.match(/^archive-(\d{4})$/)){const y=+m[1],a=ARCHIVE[y]||{};return a.next?`2027 F1 Calendar: All ${CAL2027.length} Races & Sprint Dates${T}`:a.live?`2026 Formula 1 Season${T}`:`${y} Formula 1 Season: Results, Standings & Champion${T}`;}
  if(k.startsWith("driver-")){const b=BIO[k.slice(7)];return b?`${b.name}: Profile, 2026 Season & Career Stats${T}`:`2026 F1 Drivers${T}`;}
  if(k.startsWith("team-")){const n=teamByKey(k.slice(5));return n?`${(TEAMBIO[n]||{}).name||n}: 2026 Line-up, Car & Record${T}`:`2026 F1 Teams${T}`;}
  return ({championship:"2026 F1 Championship Standings & Points Breakdown",drivers:"2026 F1 Drivers: Profiles, Stats & Standings",teams:"2026 F1 Teams: Line-ups, Cars & Standings",calendar:"2026 F1 Calendar: Dates, Circuits & Results",archive:"F1 Season Archive 1946–2025: Results & Champions",sitemap:"Site Map",notfound:"Page not found"}[k]||((PAGES[k]||{}).t)||"Track Almanac")+T;}
function h1Text(k){let m;
  if(!k||k==="season"||k.startsWith("race-"))return "2026 Formula 1 season";
  if(m=k.match(/^detail-(\d+)/)){const r=RACES.find(x=>x.r===+m[1]);return r?r.gp.replace(" (Sepang)","")+" 2026":"";}
  if(k==="archive")return "Formula 1 season archive";
  if(k==="archive-1946-1949")return "Grand Prix racing 1946–1949";
  if(m=k.match(/^archive-(\d{4})$/)){const a=ARCHIVE[+m[1]];return !a?"Formula 1 season archive":a.next?"2027 F1 calendar":m[1]+" Formula 1 season";}
  if(k.startsWith("driver"))return "2026 F1 drivers";
  if(k.startsWith("team"))return "2026 F1 teams";
  return {championship:"2026 F1 Championship standings",calendar:"2026 F1 calendar"}[k]||"";}
function setKey(k){if(PATHMODE)history.replaceState(null,"",keyToPath(k));else history.replaceState(null,"","#"+k);}
function viewCalendar(){return `<div class="pagehead"><div><span class="lbl">2026 Formula 1 World Championship</span><h2 class="h1">2026 Calendar</h2>
  <p>All ${RACES.length} rounds of the 2026 season with dates, circuits and results. Select a race for the full weekend.</p></div></div>
  <div class="tw"><table class="t gpt"><thead><tr><th class="n">Rd</th><th>Grand Prix</th><th>Circuit</th><th>Weekend</th><th>Race (your time)</th><th>Format</th><th>Winner</th></tr></thead><tbody>
  ${RACES.map(r=>{const st=raceStart(r);const w=r.res?r.res.pod[0][0]:null;return `<tr class="go" data-detail="${r.r}"><td class="n">${r.r}</td><td>${flagOf(RACECC[r.track])} <a href="${H("detail-"+r.r)}" data-detail="${r.r}"><b>${esc(r.gp.replace(" (Sepang)",""))}</b></a></td><td style="color:var(--ink-2)">${esc(r.circuit)}, ${esc(r.city)}</td><td class="m">${esc(r.days||fmt(r.date))}</td><td class="m">${st?tfmt(st,null):fmt(r.date)}</td><td>${r.sprint?'<span class="tag sig" style="margin:0">Sprint</span>':'<span style="color:var(--ink-3)">Standard</span>'}</td><td>${w?`<b>${esc(w)}</b>`:r===nextRace?'<span class="tag" style="margin:0">Next</span>':'<span style="color:var(--ink-3)">—</span>'}</td></tr>`;}).join("")}
  </tbody></table></div>`;}
function viewNotFound(){return `<article class="doc"><span class="lbl">404</span><h1>Page not found</h1><p>That page doesn't exist. Try the <a href="${H("season")}" data-go="season">2026 season</a>, the <a href="${H("calendar")}" data-go="calendar">calendar</a> or the <a href="${H("archive")}" data-go="archive">season archive</a>.</p></article>`;}

const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const fmt=(iso,o={day:"numeric",month:"short"})=>new Date(iso+"T12:00:00Z").toLocaleDateString("en-GB",o);
const done=RACES.filter(r=>r.res), nextRace=RACES.find(r=>!r.res);
const sur=n=>n.split(" ").slice(-1)[0];
const code=n=>sur(n).normalize("NFD").replace(/[^A-Za-z]/g,"").slice(0,3).toUpperCase();
const norm=s=>s.normalize("NFD").replace(/[^A-Za-z]/g,"").toLowerCase();
const FULL={}; DRIVERS.forEach(d=>FULL[norm(sur(d[0]))]=d[0]);
const fullName=s=>FULL[norm(s)]||s;
function teamAt(s,r){const n=norm(s);
  if(n==="lawson"&&r>=12&&r<=14) return "Red Bull Racing";
  if(n==="tsunoda") return "Racing Bulls";
  const f=FULL[n]; return f?teamOf(f):null;}
const tcol=t=>TEAMS[t]||"var(--ink-3)";
$("#fr").textContent=done.length;
const secs=t=>{if(!t||!/\d/.test(t))return null;const p=t.split(":");return p.length===2?(+p[0])*60+(+p[1]):+p[0];};

/* ---------- circuit drawing (real geometry, MIT data by Tomislav Bacinger) ---------- */
function pathFor(p){return "M"+p.map(q=>q[0]+","+q[1]).join(" L")+"Z";}
function trkAt(T,f){const p=T.p;f=((f%1)+1)%1;for(let i=1;i<p.length;i++){if(p[i][2]>=f){const a=p[i-1],b=p[i],k=(f-a[2])/((b[2]-a[2])||1);return [a[0]+(b[0]-a[0])*k,a[1]+(b[1]-a[1])*k,i];}}const a=p[p.length-1],b=p[0],k=(f-a[2])/((1-a[2])||1);return [a[0]+(b[0]-a[0])*k,a[1]+(b[1]-a[1])*k,p.length];}
function trkSeg(T,a,b){const p=T.p;if(b<a)return trkSeg(T,a,1).concat(trkSeg(T,0,b).slice(1));
  const out=[trkAt(T,a).slice(0,2)];for(const q of p)if(q[2]>a&&q[2]<b)out.push([q[0],q[1]]);if(b>=1)out.push([p[0][0],p[0][1]]);else out.push(trkAt(T,b).slice(0,2));return out;}
const polyD=a=>"M"+a.map(q=>q[0].toFixed(2)+","+q[1].toFixed(2)).join(" L");
function trkNormal(T,f){const a=trkAt(T,f-0.002),b=trkAt(T,f+0.002);const dx=b[0]-a[0],dy=b[1]-a[1],n=Math.hypot(dx,dy)||1;return [-dy/n,dx/n,dx/n,dy/n];}
function zoneSide(T,seg){let best=1,bs=-1;for(const sgn of [1,-1]){let m=1e9;for(let i=0;i<seg.length;i+=2){const q=seg[i],n=segN(seg,i);const ox=q[0]+n[0]*2.6*sgn,oy=q[1]+n[1]*2.6*sgn;for(let j=0;j<T.p.length;j+=3){const d=Math.hypot(T.p[j][0]-ox,T.p[j][1]-oy);if(d<m)m=d;}}if(m>bs){bs=m;best=sgn;}}return best;}
function segN(seg,i){const a=seg[Math.max(0,i-1)],b=seg[Math.min(seg.length-1,i+1)];const dx=b[0]-a[0],dy=b[1]-a[1],n=Math.hypot(dx,dy)||1;return [-dy/n,dx/n];}
function plan(key,{big=false,label="",len=null,sectors=false}={}){
  const T=TRACKS[key];if(!T)return "";
  const all=T.p.map(q=>[q[0],q[1]]);const d=polyD(all)+"Z";
  const s0=trkAt(T,0),n0=trkNormal(T,0);
  if(!big){return `<svg viewBox="0 0 100 64" role="img" aria-label="${esc(label)} layout"><path d="${d}" fill="none" stroke="var(--ink)" stroke-width="3.4" stroke-linejoin="round" opacity=".09"/><path d="${d}" fill="none" stroke="var(--ink)" stroke-width="1.4" stroke-linejoin="round"/><line x1="${(s0[0]+n0[0]*2.4).toFixed(2)}" y1="${(s0[1]+n0[1]*2.4).toFixed(2)}" x2="${(s0[0]-n0[0]*2.4).toFixed(2)}" y2="${(s0[1]-n0[1]*2.4).toFixed(2)}" stroke="var(--signal)" stroke-width="1.4"/></svg>`;}
  const ys=T.p.map(q=>q[1]),xs=T.p.map(q=>q[0]);const x0=Math.min(...xs),x1=Math.max(...xs),y1=Math.max(...ys);
  const [f1,f2]=T.s;const secs=[[0,f1],[f1,f2],[f2,1]];
  const sec=secs.map((s,i)=>`<path d="${polyD(trkSeg(T,s[0],s[1]))}" fill="none" stroke="var(--s${i+1})" stroke-width="1.05" stroke-linejoin="round" stroke-linecap="round"/>`).join("");
  const zones=(T.z||[]).map(([a,b])=>{const seg=trkSeg(T,a,b);const sg=zoneSide(T,seg);const off=seg.map((q,i)=>{const n=segN(seg,i);return [q[0]+n[0]*2.6*sg,q[1]+n[1]*2.6*sg];});
    return `<path d="${polyD(off)}" fill="none" stroke="var(--signal)" stroke-width="1.5" stroke-dasharray=".35 .45"><title>Straight mode zone</title></path>`;}).join("");
  const dot=(f,fill,stroke,title,ring)=>{if(f==null)return "";const q=trkAt(T,f);return `<circle cx="${q[0].toFixed(2)}" cy="${q[1].toFixed(2)}" r="${ring?1.05:0.95}" fill="${ring?"var(--sheet)":fill}" stroke="${stroke}" stroke-width="${ring?0.55:0.3}"><title>${title}</title></circle>`;};
  const turns=(T.c||[]).map(c=>`<g><circle cx="${c[1]}" cy="${c[2]}" r="1.75" fill="var(--sheet)" stroke="var(--ink-3)" stroke-width=".22"/><text x="${c[1]}" y="${(c[2]+0.62).toFixed(2)}" text-anchor="middle" font-family="IBM Plex Mono,monospace" font-size="${String(c[0]).length>2?1.35:1.7}" fill="var(--ink)">${esc(c[0])}</text></g>`).join("");
  // chequered start/finish
  const t0=[n0[2],n0[3]],w=1.9;let chk="";for(let a=-2;a<2;a++)for(let b=0;b<2;b++){const cx=s0[0]+n0[0]*(a+0.5)*w/2+t0[0]*(b-0.5)*0.95,cy=s0[1]+n0[1]*(a+0.5)*w/2+t0[1]*(b-0.5)*0.95;
    chk+=`<rect x="${(cx-0.475).toFixed(2)}" y="${(cy-0.475).toFixed(2)}" width=".95" height=".95" fill="${(a+b)%2?"#fff":"#111"}" transform="rotate(${(Math.atan2(t0[1],t0[0])*180/Math.PI).toFixed(1)} ${cx.toFixed(2)} ${cy.toFixed(2)})"/>`;}
  const ang=Math.atan2(t0[1],t0[0]),ax=s0[0]+t0[0]*4.2,ay=s0[1]+t0[1]*4.2;
  const arrow=`<path d="M${(ax+Math.cos(ang)*1.8).toFixed(2)},${(ay+Math.sin(ang)*1.8).toFixed(2)} L${(ax+Math.cos(ang+2.5)*1.3).toFixed(2)},${(ay+Math.sin(ang+2.5)*1.3).toFixed(2)} L${(ax+Math.cos(ang-2.5)*1.3).toFixed(2)},${(ay+Math.sin(ang-2.5)*1.3).toFixed(2)}Z" fill="var(--ink-2)"><title>Direction of travel</title></path>`;
  const dims=`<g stroke="var(--ink-3)" stroke-width=".3" fill="var(--ink-3)" font-family="IBM Plex Mono,monospace" font-size="2.6"><line x1="${x0}" y1="${y1+6}" x2="${x1}" y2="${y1+6}"/><line x1="${x0}" y1="${y1+4}" x2="${x0}" y2="${y1+8}"/><line x1="${x1}" y1="${y1+4}" x2="${x1}" y2="${y1+8}"/>${len?`<text x="${(x0+x1)/2}" y="${y1+10.5}" text-anchor="middle" stroke="none">LAP ${dist(len,3).toUpperCase()}</text>`:""}</g>`;
  return `<svg viewBox="-3 -4 106 ${y1+20}" role="img" aria-label="${esc(label)} layout with turn numbers, sectors and aero zones">
    <path d="${d}" fill="none" stroke="var(--rule-2)" stroke-width="4.2" stroke-linejoin="round"/>
    <path d="${d}" fill="none" stroke="#05070b" stroke-width="3.1" stroke-linejoin="round"/>
    ${zones}${sec}${chk}${arrow}
    ${dot(T.st,"#d7ff3a","#000","Speed trap"+(T.stA?" (approximate: point of highest speed)":""))}
    ${dot(T.od,"#3ddc84","#000","Overtake detection")}${dot(T.oa,"#3ddc84","#3ddc84","Overtake activation",true)}
    ${turns}${dims}</svg>`;}
function mapLegend(key){const T=TRACKS[key]||{};const has=(T.z||[]).length,ov=T.od!=null;
  return `<div class="legend mlg"><span><i style="background:var(--s1)"></i>Sector 1</span><span><i style="background:var(--s2)"></i>Sector 2</span><span><i style="background:var(--s3)"></i>Sector 3</span>
  ${has?`<span><i class="zz"></i>Straight mode zone</span>`:""}<span><b class="dt" style="background:#d7ff3a"></b>Speed trap${T.stA?" (approx.)":""}</span>
  ${ov?`<span><b class="dt" style="background:#3ddc84"></b>Overtake detection</span>`:""}${T.oa!=null?`<span><b class="dt ring"></b>Overtake activation</span>`:""}<span><b class="tn">1</b>Turn number${T.ca?"s (approx.)":""}</span></div>
  ${!has&&ov?`<p class="note2" style="margin:4px 0 0">No straight mode zones are used at this circuit.</p>`:""}${!has&&!ov?`<p class="note2" style="margin:4px 0 0">Straight mode and overtake points for this circuit are published by the FIA in race week and will be added then.</p>`:""}`;}

/* ---------- derived season stats ---------- */
const RN=done.map(r=>r.r);
function resultCell(r,s){const d=SEASON[r];if(!d)return null;const row=d.race.find(x=>norm(x[2])===norm(s));
  const sp=d.sprint?d.sprint.find(x=>norm(x[2])===norm(s)):null;return {row,sp};}
const stat=t=>/DNS/.test(t)?"DNS":/DSQ|DQ/.test(t)?"DSQ":/DNF/.test(t)?"Ret":null;
function cellInfo(row){if(!row)return{txt:"",cls:"c-none"};const st=stat(row[4]);const pos=row[0];
  if(st==="DNS")return{txt:"DNS",cls:"c-dns"};if(st==="DSQ")return{txt:"DSQ",cls:"c-dns"};
  if(pos==="NC"||pos==="DQ"){return{txt:st==="Ret"?"Ret":"NC",cls:"c-ret"};}
  const p=+pos;if(p===1)return{txt:"1",cls:"c-p1"};if(p===2)return{txt:"2",cls:"c-p2"};if(p===3)return{txt:"3",cls:"c-p3"};
  if(row[5]>0)return{txt:String(p),cls:"c-pts"};return{txt:String(p),cls:st?"c-ret":"c-fin"};}
const ptsAt=(r,s)=>{const d=SEASON[r];let t=0;(d.race||[]).concat(d.sprint||[]).forEach(x=>{if(norm(x[2])===norm(s))t+=x[5];});return t;};
const poleOf=r=>SEASON[r].quali[0][2];
const flOf=r=>RACES.find(x=>x.r===r).res.fl[0];
function cumulative(names){return names.map(n=>{let c=0;return [0,...RN.map(r=>c+=ptsAt(r,sur(n)))];});}
function teamPtsAt(r,t){const d=SEASON[r];let s=0;(d.race||[]).concat(d.sprint||[]).forEach(x=>{if(teamAt(x[2],r)===t)s+=x[5];});return s;}
function standingsAfter(r){const tot={};RN.filter(x=>x<=r).forEach(x=>{const d=SEASON[x];(d.race||[]).concat(d.sprint||[]).forEach(y=>{const n=fullName(y[2]);tot[n]=(tot[n]||0)+y[5];});});
  return Object.entries(tot).sort((a,b)=>b[1]-a[1]);}
function teamStandingsAfter(r){const tot={};Object.keys(TEAMS).forEach(t=>tot[t]=0);RN.filter(x=>x<=r).forEach(x=>Object.keys(TEAMS).forEach(t=>tot[t]+=teamPtsAt(x,t)));
  return Object.entries(tot).sort((a,b)=>b[1]-a[1]);}

/* ---------- SEASON ---------- */
const RCODE={1:"AUS",2:"CHN",3:"JPN",4:"MIA",5:"CAN",6:"MON",7:"BCN",8:"AUT",9:"GBR",10:"BEL",11:"HUN",12:"NED",13:"ITA",14:"MAD",15:"AZE",16:"BHR",17:"SGP",18:"USA",19:"MEX",20:"BRA",21:"LVG",22:"QAT",23:"ABU"};
const TODAY=new Date();
let CLOCK="12";try{CLOCK=localStorage.getItem("ta-clock")||"12";}catch(e){}
/* distance units: KM (default) or MI; distances in km and speeds in km/h are converted when MI is chosen */
/* colour theme: dark (default) or light; build.py applies a saved choice before the page draws */
let THEME=document.documentElement.getAttribute("data-theme")==="light"?"light":"dark";
function setTheme(t){THEME=t==="light"?"light":"dark";if(THEME==="light")document.documentElement.setAttribute("data-theme","light");else document.documentElement.removeAttribute("data-theme");
  try{localStorage.setItem("ta-theme",THEME)}catch(e){}const m=document.querySelector('meta[name="theme-color"]');if(m)m.content=THEME==="light"?"#f3f5f8":"#000000";}
let UNIT="km";try{UNIT=localStorage.getItem("ta-unit")==="mi"?"mi":"km";}catch(e){}
const KM2MI=0.621371;
const dist=(km,d)=>UNIT==="mi"?(km*KM2MI).toFixed(d)+" mi":km.toFixed(d)+" km";
const spd=(kmh,d)=>UNIT==="mi"?(kmh*KM2MI).toFixed(d)+" mph":kmh.toFixed(d)+" km/h";
function tfmt(iso,tz,o={weekday:"short",day:"numeric",month:"short",hour:"2-digit",minute:"2-digit"}){try{const h=o.hour?{hour:CLOCK==="12"?"numeric":"2-digit",hour12:CLOCK==="12"}:{};return new Intl.DateTimeFormat("en-GB",{...o,...h,...(tz?{timeZone:tz}:{})}).format(new Date(iso)).replace(/\b(am|pm)\b/g,m=>m.toUpperCase());}catch(e){return new Date(iso).toUTCString().slice(0,22);}}
function tzName(iso,tz){try{const p=new Intl.DateTimeFormat("en-GB",{timeZoneName:"short",...(tz?{timeZone:tz}:{})}).formatToParts(new Date(iso));return (p.find(x=>x.type==="timeZoneName")||{}).value||"";}catch(e){return "";}}
const raceStart=r=>SCHED[r.r]?SCHED[r.r][1].slice(-1)[0][1]:null;
let plateOrder="desc";try{plateOrder=localStorage.getItem("pa-order2")||"desc";}catch(e){}
function ribbon(){
  const t0=Date.parse("2026-03-01T00:00:00Z"),t1=Date.parse("2026-12-15T00:00:00Z");
  const X=d=>((Date.parse(d+"T12:00:00Z")-t0)/(t1-t0)*100);
  const months=["Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"].map((m,i)=>`<span class="mon" style="left:${X(`2026-${String(i+3).padStart(2,"0")}-01`)}%">${m}</span>`).join("");
  const today=X(TODAY.toISOString().slice(0,10));
  const nr=nextRace;
  return `<section class="ribbon" aria-label="2026 calendar">
    <div class="rib-head"><b>2026 Season · <span>${done.length}</span> of ${RACES.length} rounds run</b><span class="lbl">Next: Round ${nr.r} ${esc(nr.short)} · ${esc(nr.days)}</span></div>
    <div class="rib-scroll"><div class="rib">
      ${months}<div class="rail"></div><div class="fill" style="width:${Math.min(100,today)}%"></div>
      <div class="today" style="left:${today}%"><i>TODAY<br>${TODAY.toLocaleDateString("en-GB",{day:"numeric",month:"short"}).toUpperCase()}</i></div>
      ${RACES.map(r=>`<button class="${r.res?"done":r===nr?"next":"fut"}" style="left:${X(r.date)}%" data-quick="${r.r}" aria-label="Round ${r.r}, ${esc(r.gp)}, ${fmt(r.date,{day:"numeric",month:"long"})}${r.res?", won by "+esc(r.res.pod[0][0]):""}" title="R${r.r} ${esc(r.gp)} · ${fmt(r.date,{day:"numeric",month:"short"})}${r.res?" · "+esc(r.res.pod[0][0]):""}">
        ${r.sprint?'<span class="sp" aria-hidden="true"></span>':""}<span class="chip">${r.r}</span><span class="cc">${RCODE[r.r]}</span></button>`).join("")}
    </div></div>
    <div class="rib-key"><span><i style="background:var(--done)"></i>Completed</span><span><i style="background:var(--signal)"></i>Next race</span><span><i style="border:1.5px solid var(--ink-3)"></i>Upcoming</span><span><i style="background:var(--signal);border-radius:50%;width:6px;height:6px"></i>Sprint weekend</span><span>Select a round for quick info</span></div>
  </section>`;
}
const PLATECTRY={"Miami":"USA","Barcelona":"Spain","Madrid":"Spain","Las Vegas":"USA","Abu Dhabi":"UAE","Bahrain (Sepang)":"Malaysia"};
const plateName=r=>`${esc(r.short.replace(" (Sepang)",""))}${PLATECTRY[r.short]?`<small class="ctyc">(${PLATECTRY[r.short]})</small>`:""}`;
function plateHTML(r){
  if(r.res){const w=r.res.pod[0][0];return `
    <article class="plate" tabindex="0" role="button" data-quick="${r.r}" aria-label="${esc(r.gp)} quick info">
      <div class="fig">${r.sprint?'<span class="spb">Sprint weekend</span>':""}${plan(r.track,{label:r.circuit})}</div>
      <div class="cap"><h3${r.short.replace(" (Sepang)","").length>=10?' class="long"':""}>${plateName(r)}</h3><span class="rn">R${String(r.r).padStart(2,"0")}<br>${fmt(r.date)}</span>
      <ol class="pod">${r.res.pod.map((p,k)=>`<li><b>P${k+1}</b><i style="background:${tcol(teamAt(p[0],r.r)||teamOf(p[0]))}"></i><span>${esc(p[0])}</span></li>`).join("")}</ol></div>
      <div class="acts"><button data-quick="${r.r}">Quick info</button><a href="${H("detail-"+r.r)}" data-detail="${r.r}">Detailed info</a></div>
    </article>`;}
  const st=raceStart(r), tz=SCHED[r.r]?SCHED[r.r][0]:null, nx=r===nextRace;
  return `
    <article class="plate up${nx?" nx":""}" tabindex="0" role="button" data-quick="${r.r}" aria-label="${esc(r.gp)} weekend times">
      ${nx?'<span class="flag">Next race</span>':""}
      <div class="fig">${r.sprint?'<span class="spb">Sprint weekend</span>':""}${plan(r.track,{label:r.circuit})}</div>
      <div class="cap"><h3${r.short.replace(" (Sepang)","").length>=10?' class="long"':""}>${plateName(r)}</h3><span class="rn">R${String(r.r).padStart(2,"0")}<br>${esc(r.days)}</span>
      ${st?`<span class="when"><span class="lbl">Race · your time</span><b>${tfmt(st,null)}</b></span><span class="when"><span class="lbl">Race · track time</span><b>${tfmt(st,tz)}</b></span>`:""}</div>
      <div class="acts"><button data-quick="${r.r}">Weekend times</button><a href="${H("detail-"+r.r)}" data-detail="${r.r}">Detailed view</a></div>
    </article>`;
}
function viewSeason(){
  const nr=nextRace, n=RACES.length, st=raceStart(nr), tz=SCHED[nr.r][0];
  const list=plateOrder==="asc"?done:[...done].reverse();
  const upcoming=RACES.filter(r=>!r.res);
  return `
  ${ribbon()}
  <div class="home">
    <section class="sheet" aria-labelledby="nr">
      <div class="l">
        <span class="lbl">Next · Round ${nr.r} / ${n}</span>
        <h2 class="h1" id="nr">${esc(nr.short)}</h2>
        <div style="color:var(--ink-2)">${esc(nr.circuit)}, ${esc(nr.city)}</div>
        <div><span class="tag sig">${esc(nr.days)}</span>${nr.sprint?'<span class="tag">Sprint</span>':""}<span class="tag">Night</span></div>
        <div class="cdx" id="cdx" aria-live="off"></div>
        <div class="spec"><div><span class="lbl">Lap</span><b>${dist(nr.len,3)}</b></div><div><span class="lbl">Laps</span><b>${nr.laps}</b></div><div><span class="lbl">Distance</span><b>${dist(nr.len*nr.laps,1)}</b></div></div>
        ${tyreBlock(nr.r)}
        <button class="navbtn" data-quick="${nr.r}" style="align-self:flex-start">Weekend schedule →</button>
      </div>
      <div class="r">
        <span class="corner" style="top:8px;left:12px">FIG. ${String(nr.r).padStart(2,"0")}</span>
        ${plan(nr.track,{big:true,label:nr.circuit,len:nr.len,sectors:true})}
        ${mapLegend(nr.track)}
      </div>
    <div class="wk">
        <div class="wkh"><span class="lbl">Weekend schedule</span><span class="lbl">Select a session for full results</span></div>
        <div class="nxs" aria-label="Weekend schedule">
          <div class="nr h"><span>Session</span><span>Your time (${esc(tzName(st,null))})</span><span>Track time (${esc(tzName(st,tz))})</span><span>Top three</span></div>
          ${SCHED[nr.r][1].map(([nm,t,du])=>`<div class="nr go${nm==="Grand Prix"?" gp":""}" data-t="${Date.parse(t)}" data-d="${du||120}" ${sesAttr(nr.r,nm)}><span>${esc(nm==="Grand Prix"?"Race":nm)}</span><span>${tfmt(t,null)}</span><span>${tfmt(t,tz)}</span><div class="sres">${top3(nr.r,SESKEY[nm])}</div></div>`).join("")}
        </div>
    </div>
    </section>

    <aside class="tower" aria-label="Championship standings">
      <header><span class="lbl">Classification · after R${done.length}</span><h2>Standings</h2>
        <div class="tg" role="group" aria-label="Championship"><button id="t-d" aria-pressed="true">Drivers</button><button id="t-c" aria-pressed="false">Teams</button></div></header>
      <div class="tscroll" tabindex="0" aria-label="Standings list, scrolls independently"><ol id="tower"></ol></div>
      <div class="gapline"><span id="gapline"></span> <button data-go="championship">Full breakdown</button></div>
    </aside>

    <div class="plates-wrap">
      <div class="sec" style="margin-top:4px"><h2>Race plates</h2>
        <div class="secbar"><span class="lbl">${done.length} completed</span>
          <div class="sort" role="group" aria-label="Order"><button data-order="asc" aria-pressed="${plateOrder==="asc"}">Round 1 first</button><button data-order="desc" aria-pressed="${plateOrder==="desc"}">Latest first</button></div></div></div>
      <div class="plates">${list.map(plateHTML).join("")}</div>
      <div class="sec"><h2>Upcoming races</h2><span class="lbl">${upcoming.length} to go · times shown for the track and for you</span></div>
      <div class="plates">${upcoming.map(plateHTML).join("")}</div>
    </div>
  </div>`;
}
function tower(kind){
  const ol=$("#tower"); if(!ol) return;
  if(kind==="d"){ const top=DRIVERS[0][3];
    ol.innerHTML=DRIVERS.map((d,i)=>{const b=bioOf(d[0]),[fn,ln]=nameParts(d[0]);return `<li${b?` data-driver="${b.code}" tabindex="0" role="button"`:""}><span class="p">${i+1}</span><span class="c" style="background:${tcol(d[2])}"></span><span class="nm" title="${esc(d[0])} · ${esc(d[2])}">${esc(fn)}<b>${esc(ln)}</b></span><span class="pt">${d[3]}<small>${i?"−"+(top-d[3]):"PTS"}</small></span></li>`;}).join("");
    $("#gapline").textContent=`${DRIVERS[0][0]} leads by ${top-DRIVERS[1][3]}.`;
  }else{ const top=CONSTRUCTORS[0][1];
    ol.innerHTML=CONSTRUCTORS.map((c,i)=>`<li class="cons" data-team="${esc(c[0])}" tabindex="0" role="button"><span class="p">${i+1}</span><span class="c" style="background:${tcol(c[0])}"></span><span class="code">${esc(c[0])}</span><span class="pt">${c[1]}<small>${i?"−"+(top-c[1]):"PTS"}</small></span></li>`).join("");
    $("#gapline").textContent=`${CONSTRUCTORS[0][0]} lead by ${top-CONSTRUCTORS[1][1]}.`;
  }
  $("#t-d").setAttribute("aria-pressed",kind==="d"); $("#t-c").setAttribute("aria-pressed",kind==="c");
}

/* ---------- QUICK INFO DRAWER ---------- */
const shortName=r=>esc(r.short.replace(" (Sepang)",""));
function navPair(i,attr){const p=i>0?done[i-1]:null,n=i<done.length-1?done[i+1]:null;
  return [`<button class="navbtn" ${p?`${attr}="${p.r}"`:"disabled"}>← ${p?shortName(p):"Season start"}</button>`,
          `<button class="navbtn" ${n?`${attr}="${n.r}"`:"disabled"}>${n?shortName(n):"Latest race"} →</button>`];}
function navAll(r){const i=RACES.indexOf(r),p=RACES[i-1],n=RACES[i+1];
  return [`<button class="navbtn" ${p?`data-quick="${p.r}"`:"disabled"}>← ${p?`R${p.r} ${shortName(p)}`:"Season start"}</button>`,
          `<button class="navbtn" ${n?`data-quick="${n.r}"`:"disabled"}>${n?`R${n.r} ${shortName(n)}`:"Season end"} →</button>`];}
function sessionTable(r){const sc=SCHED[r.r];if(!sc)return "";const tz=sc[0];
  return `<div class="sess"><div class="row h"><span>Session</span><span>Your time</span><span>Track time (${esc(tzName(sc[1][0][1],tz))})</span></div>
    ${sc[1].map(([nm,st,dur])=>{const en=dur?new Date(Date.parse(st)+dur*60000).toISOString():null;
      const k=SESKEY[nm],ss=sesState(r.r,k);
      return `<div class="row go${nm==="Grand Prix"?" gp":""}" ${sesAttr(r.r,nm)}><strong>${esc(nm)}<small>${ss==="done"?"Results ›":ss==="live"?"Live now":ss==="wait"?"Yet to update":"Coming soon"}</small></strong>
        <span class="t">${tfmt(st,null,{weekday:"short",day:"numeric",month:"short"})}<small>${tfmt(st,null,{hour:"2-digit",minute:"2-digit"})}${en?"–"+tfmt(en,null,{hour:"2-digit",minute:"2-digit"}):""} ${esc(tzName(st,null))}</small></span>
        <span class="t">${tfmt(st,tz,{weekday:"short",day:"numeric",month:"short"})}<small>${tfmt(st,tz,{hour:"2-digit",minute:"2-digit"})}${en?"–"+tfmt(en,tz,{hour:"2-digit",minute:"2-digit"}):""}</small></span><div class="sres">${top3(r.r,k)}</div></div>`;}).join("")}</div>`;}
function openUpcoming(r){
  const [pv,nx]=navAll(r);
  $("#drawer-root").innerHTML=`<div class="scrim" data-close></div>
  <aside class="drawer" role="dialog" aria-modal="true" aria-labelledby="dt">
    <div class="dtop">${pv}<button class="navbtn" data-close id="dclose">Close ✕</button>${nx}</div>
    <div class="lbl" style="margin-top:16px">Round ${r.r} · ${esc(r.days)} 2026${r===nextRace?" · next race":""}</div>
    <div class="dhead"><h2 class="h1" id="dt">${esc(r.short)}</h2><button class="navbtn sig" data-detail="${r.r}">Detailed view →</button></div>
    <div style="color:var(--ink-2)">${esc(r.gp)} · ${esc(r.circuit)}, ${esc(r.city)}</div>
    <div class="fig">${plan(r.track,{big:true,label:r.circuit,len:r.len,sectors:true})}</div>
    <div class="dl">
      <div><span class="lbl">Format</span><b>${r.sprint?"Sprint weekend":"Standard"}</b><span class="s">${r.sprint?"1 practice, sprint quali, sprint":"3 practice sessions"}</span></div>
      <div><span class="lbl">Race distance</span><b>${r.laps} laps</b><span class="s">${dist(r.len*r.laps,1)} · ${dist(r.len,3)} lap</span></div>
    </div>
    ${tyreBlock(r.r)}
    ${sessionTable(r)}
    <p class="dnote">Session times are from the official 2026 schedule. "Your time" uses this device's time zone. Each session's top three appears once it finishes; select a session for the full results.</p>
    <div class="dnav">${pv}<button class="navbtn sig" data-detail="${r.r}">Detailed view →</button>${nx}</div>
  </aside>`;
  $("#dclose").focus();
}
function openRace(n){
  const r=RACES.find(x=>x.r===n); if(!r) return;
  if(!r.res) return openUpcoming(r);
  const x=r.res, S=SEASON[n];
  const row=(nm,gap,k,time)=>{const t=teamAt(nm,n)||teamOf(nm);return `<div class="row p${k+1}"><span class="pos">P${k+1}</span><span class="c" style="background:${tcol(t)}"></span><span><strong>${esc(nm)}</strong><small>${esc(t)}</small></span><span class="t">${k?esc(gap):esc(time)}</span></div>`;};
  const na=(k,w)=>`<div><span class="lbl">${k}</span><b class="na">Not available</b><span class="s">${w}</span></div>`;
  const [pv,nx]=navAll(r);
  const spPod=S&&S.sprint?`<div class="res"><div class="hd lbl">Sprint podium · ${S.sprint[0][3]} laps</div>${S.sprint.slice(0,3).map((y,k)=>row(fullName(y[2]),y[4],k,y[4])).join("")}</div>`:"";
  $("#drawer-root").innerHTML=`<div class="scrim" data-close></div>
  <aside class="drawer" role="dialog" aria-modal="true" aria-labelledby="dt">
    <div class="dtop">${pv}<button class="navbtn" data-close id="dclose">Close ✕</button>${nx}</div>
    <div class="lbl" style="margin-top:16px">Round ${r.r} · ${fmt(r.date,{day:"numeric",month:"long",year:"numeric"})}</div>
    <div class="dhead"><h2 class="h1" id="dt">${esc(r.short)}</h2><button class="navbtn sig" data-detail="${r.r}">Detailed view →</button></div>
    <div style="color:var(--ink-2)">${esc(r.gp)} · ${esc(r.circuit)}</div>
    <div class="fig">${plan(r.track,{big:true,label:r.circuit,len:r.len,sectors:true})}</div>
    <div class="res"><div class="hd lbl">Grand Prix podium · ${r.laps} laps</div>${x.pod.map((p,k)=>row(p[0],p[1],k,x.time)).join("")}</div>
    ${spPod}
    <div class="dl">
      <div><span class="lbl">Fastest lap</span><b class="fl">${x.fl[1]}</b><span class="s">${esc(x.fl[0])} · lap ${x.fl[2]}</span></div>
      <div><span class="lbl">Pole</span><b>${esc(code(x.pole))}</b><span class="s">${esc(x.pole)}</span></div>
      <div><span class="lbl">FL avg speed</span><b>${spd(x.fl[3],1)}</b><span class="s">Best lap average</span></div>
      ${x.pit?`<div><span class="lbl">Fastest pit stop</span><b>${x.pit[2]}</b><span class="s">${esc(x.pit[0])}</span></div>`:na("Fastest pit stop","Not in published results")}
      <div><span class="lbl">Tyres</span><b>C${S.tyres[0]} · C${S.tyres[1]} · C${S.tyres[2]}</b><span class="s">Hard · Medium · Soft</span></div>
      <div><span class="lbl">${r.sprint?"Sprint winner":"Distance"}</span><b>${r.sprint?esc(code(r.sprint)):dist(r.len*r.laps,1)}</b><span class="s">${r.sprint?esc(r.sprint):r.laps+" laps"}</span></div>
    </div>
    <p class="dnote">${esc(x.cls)}</p>
    <div class="dnav">${pv}<button class="navbtn sig" data-detail="${r.r}">Detailed info →</button>${nx}</div>
  </aside>`;
  $("#dclose").focus();
}
const closeDrawer=()=>{$("#drawer-root").innerHTML="";};

/* ---------- LIVE WEEKEND: per-session results ---------- */
const SESKEY={"Practice 1":"fp1","Practice 2":"fp2","Practice 3":"fp3","Sprint Qualifying":"sq","Sprint":"sprint","Qualifying":"quali","Grand Prix":"race"};
const SESLAB={fp1:"Practice 1",fp2:"Practice 2",fp3:"Practice 3",sq:"Sprint Qualifying",sprint:"Sprint",quali:"Qualifying",race:"Race"};
const sesRows=(n,k)=>{const S=SEASON[n]||{};return S[k]&&S[k].length?S[k]:null;};
function sesState(n,k){if(sesRows(n,k))return "done";const sc=SCHED[n];if(!sc)return "soon";
  const it=sc[1].find(x=>SESKEY[x[0]]===k);if(!it)return "soon";
  const a=Date.parse(it[1]),e=a+(it[2]||120)*60000,now=Date.now();return now<a?"soon":now<e?"live":"wait";}
const sesTime=(k,x)=>k==="sq"||k==="quali"?([x[5],x[4],x[3]].find(v=>v&&/\d:\d/.test(v))||""):k.startsWith("fp")?(x[3]||""):(x[4]||"");
const STATE_TXT={live:"Session in progress · results soon",wait:"Finished · yet to update",soon:"Coming soon"};
function top3(n,k){const rows=sesRows(n,k);const st=sesState(n,k);
  if(!rows)return `<em class="st st-${st}">${STATE_TXT[st]}</em>`;
  return rows.slice(0,3).map((x,i)=>`<span class="t3"><b>P${i+1}</b><i style="background:${tcol(teamAt(x[2],n))}"></i><strong>${esc(code(x[2]))}</strong><em>${esc(sesTime(k,x))}</em></span>`).join("");}
const sesAttr=(n,nm)=>`data-sess="${n}:${SESKEY[nm]||"race"}" tabindex="0" role="button" title="Open ${esc(nm==="Grand Prix"?"Race":nm)} details"`;
function soonBox(n,k){const st=sesState(n,k)==="done"?"soon":sesState(n,k);const sc=SCHED[n];const it=sc?sc[1].find(x=>SESKEY[x[0]]===k):null;
  const msg=st==="live"?["Session in progress","Results will be added here once the session ends."]:st==="wait"?["Yet to update","This session has finished. Results are being added."]:["Coming soon","This session hasn't taken place yet."];
  return `<div class="soon ${st}"><span class="lbl">${esc(SESLAB[k])}</span><b>${msg[0]}</b><span>${msg[1]}</span>${it?`<span class="mono">${tfmt(it[1],null)} your time · ${tfmt(it[1],sc[0])} track time</span>`:""}</div>`;}
function fpOut(n,k){const rows=sesRows(n,k);return rows?practiceTable(rows,n):soonBox(n,k);}
function jumpTo(k){if(!k)return;if(/^fp\d$/.test(k)){const b=document.querySelector(`[data-fp="${k}"]`);if(b)b.click();k="practice";}
  const el=$("#s-"+k);if(el)setTimeout(()=>el.scrollIntoView({block:"start"}),30);}
function viewLive(n){
  const r=RACES.find(x=>x.r===n);if(!r)return viewSeason();
  const S=SEASON[n]||{},sc=SCHED[n],tz=sc?sc[0]:null,i=RACES.indexOf(r),p=RACES[i-1],nx=RACES[i+1];
  const pv=`<button class="navbtn" ${p?`data-detail="${p.r}"`:"disabled"}>← ${p?`R${p.r} ${shortName(p)}`:"Season start"}</button>`;
  const nb=`<button class="navbtn" ${nx?`data-detail="${nx.r}"`:"disabled"}>${nx?`R${nx.r} ${shortName(nx)}`:"Season end"} →</button>`;
  const sessions=sc?sc[1]:[];const keys=sessions.map(x=>SESKEY[x[0]]);
  const doneN=keys.filter(k=>sesRows(n,k)).length;
  const fps=keys.filter(k=>/^fp/.test(k));
  const pole=sesRows(n,"quali"),spw=sesRows(n,"sprint");
  const jumps=[["weekend","Weekend"],["practice","Practice"],...(r.sprint?[["sq","Sprint quali"],["sprint","Sprint"]]:[]),["quali","Qualifying"],["grid","Grid"],["race","Race"],["after","Standings"]];
  const tbl=(k,f)=>sesRows(n,k)?f(sesRows(n,k)):soonBox(n,k);
  return `
  <div class="dnav pin">${pv}<span class="dmid"><button class="navbtn" data-go="season">Home</button><button class="navbtn" data-top>Top ↑</button></span>${nb}</div>
  <section class="dhero">
    <div class="info">
      <span class="lbl">Round ${r.r} of ${RACES.length} · ${esc(r.days)} 2026${r===nextRace?" · race weekend":""}</span>
      <h2 class="h1">${esc(r.short)}</h2>
      <div style="color:var(--ink-2)">${esc(r.gp)} · ${esc(r.circuit)}, ${esc(r.city)}</div>
      <div>${r.sprint?'<span class="tag sig">Sprint weekend</span>':""}<span class="tag">${r.laps} laps</span><span class="tag">${dist(r.len,3)} lap</span><span class="tag">${dist(r.len*r.laps,1)}</span></div>
      <div class="spec"><div><span class="lbl">Sessions done</span><b>${doneN} / ${keys.length||"—"}</b></div><div><span class="lbl">Pole</span><b>${pole?esc(code(pole[0][2])):"—"}</b></div><div><span class="lbl">${r.sprint?"Sprint winner":"Race winner"}</span><b>${r.sprint?(spw?esc(code(spw[0][2])):"—"):"—"}</b></div></div>
      <p class="note2" style="margin:0">Results are added after each session finishes. Sessions still to run show as coming soon.</p>
    </div>
    <div class="map">
      <span class="corner" style="top:8px;left:12px">FIG. ${String(r.r).padStart(2,"0")} · SECTORS</span>
      ${plan(r.track,{big:true,label:r.circuit,len:r.len,sectors:true})}
      ${mapLegend(r.track)}
    </div>
  </section>
  <nav class="jump" aria-label="Jump to section">${jumps.map(j=>`<a href="#detail-${n}" data-jump="${j[0]}">${j[1]}</a>`).join("")}</nav>
  <section class="dsec" id="s-weekend">
    <div class="sec"><h2>Weekend</h2><span class="lbl">Select a session for its results</span></div>
    ${sc?`<div class="sess" style="margin-top:0"><div class="row h"><span>Session</span><span>Your time</span><span>Track time</span></div>
      ${sessions.map(([nm,st])=>{const k=SESKEY[nm];const s=sesState(n,k);return `<div class="row go${nm==="Grand Prix"?" gp":""}" ${sesAttr(n,nm)}><strong>${esc(nm)} <span class="wstat ${s}">${s==="done"?"Results":s==="live"?"Live":s==="wait"?"Updating":"Soon"}</span></strong><span class="t">${tfmt(st,null)}</span><span class="t">${tfmt(st,tz)}</span><div class="sres">${top3(n,k)}</div></div>`;}).join("")}</div>`:`<p class="note2">Schedule not published yet.</p>`}
    <div style="margin-top:14px">${tyreBlock(n)}</div>
  </section>
  <section class="dsec" id="s-practice">
    <div class="sec"><h2>Practice</h2><span class="lbl">Best lap per driver</span></div>
    ${fps.length?`<div class="subtabs" role="group" aria-label="Practice session">${fps.map((k,j)=>`<button data-fp="${k}" aria-pressed="${j===0}">${k.toUpperCase()}</button>`).join("")}</div><div id="fp-out">${fpOut(n,fps[0])}</div>`:soonBox(n,"fp1")}
    ${r.sprint?'<p class="note2">Sprint weekends have a single practice session.</p>':""}
  </section>
  ${r.sprint?`<section class="dsec" id="s-sq"><div class="sec"><h2>Sprint qualifying</h2><span class="lbl">SQ1 · SQ2 · SQ3</span></div>${tbl("sq",rows=>qualiTable(rows,n,["SQ1","SQ2","SQ3"]))}</section>
  <section class="dsec" id="s-sprint"><div class="sec"><h2>Sprint</h2><span class="lbl">${spw?`${spw[0][3]} laps · winner ${esc(fullName(spw[0][2]))}`:"Sprint race"}</span></div>${tbl("sprint",rows=>classTable(rows,n,false))}</section>`:""}
  <section class="dsec" id="s-quali"><div class="sec"><h2>Qualifying</h2><span class="lbl">Q1 · Q2 · Q3</span></div>${tbl("quali",rows=>qualiTable(rows,n,["Q1","Q2","Q3"])+`<p class="note2">Dashed lines mark the Q1 and Q2 cut-offs. Purple marks the fastest time in each part.</p>`)}</section>
  <section class="dsec" id="s-grid"><div class="sec"><h2>Starting grid</h2><span class="lbl">After penalties${S.grid?" · official":""}</span></div>
    ${S.grid?gridSection(n):`<div class="soon ${pole?"wait":"soon"}"><span class="lbl">Starting grid</span><b>${pole?"Yet to update":"Coming soon"}</b><span>${pole?"The official grid, including any penalties, is added with the race result. Until then the qualifying order above is the provisional grid.":"The grid is set by qualifying."}</span></div>`}</section>
  <section class="dsec" id="s-race"><div class="sec"><h2>Race</h2><span class="lbl">${r.laps} laps</span></div>${soonBox(n,"race")}</section>
  <section class="dsec" id="s-after"><div class="sec"><h2>Championship now</h2><span class="lbl">Includes points scored so far this weekend</span></div>
    <div class="two">
      <div class="tw"><table class="t" style="min-width:0"><thead><tr><th class="n">Pos</th><th>Driver</th><th class="n">Pts</th></tr></thead><tbody>${DRIVERS.slice(0,10).map((d,k)=>`<tr><td class="n">${k+1}</td><td><span class="sw" style="background:${tcol(d[2])}"></span>${esc(d[0])}</td><td class="n">${d[3]}</td></tr>`).join("")}</tbody></table></div>
      <div class="tw"><table class="t" style="min-width:0"><thead><tr><th class="n">Pos</th><th>Constructor</th><th class="n">Pts</th></tr></thead><tbody>${CONSTRUCTORS.map((c,k)=>`<tr><td class="n">${k+1}</td><td><span class="sw" style="background:${tcol(c[0])}"></span>${esc(c[0])}</td><td class="n">${c[1]}</td></tr>`).join("")}</tbody></table></div>
    </div></section>
  <div class="dnav" style="margin-top:28px">${pv}<span class="dmid"><button class="navbtn" data-go="season">Home</button><button class="navbtn" data-top>Top ↑</button></span>${nb}</div>`;}
function scrollHome(sel){const go2=()=>{const el=$(sel);if(el)el.scrollIntoView({behavior:"smooth",block:"start"});};if($(".home"))go2();else{go("season");setTimeout(go2,120);}}

/* ---------- DETAIL PAGE ---------- */
function tyreBlock(n){const S=SEASON[n]||{};const nm=["Hard","Medium","Soft"],col=["var(--tH)","var(--tM)","var(--tS)"];
  if(!S.tyres)return `<div class="tyrebox"><span class="lbl">Tyre compounds</span><span class="tyna">Not announced yet. Pirelli names the hard, medium and soft before race week.</span></div>`;
  return `<div class="tyrebox"><span class="lbl">Tyre compounds · Pirelli</span><div class="tyrow">${[0,1,2].map(k=>`<span class="tychip"><i style="border-color:${col[k]}"></i><b>C${S.tyres[k]}</b><small>${nm[k]}</small></span>`).join("")}</div></div>`;}
function tyreSVG(c,on){const col=["","var(--tH)","var(--tM)","var(--tS)"][on]||"var(--ink-3)";
  return `<svg viewBox="0 0 46 46" aria-hidden="true"><circle cx="23" cy="23" r="20" fill="#111" stroke="#2a2f38" stroke-width="3"/><circle cx="23" cy="23" r="15" fill="none" stroke="${col}" stroke-width="3.5"/><circle cx="23" cy="23" r="7" fill="#1a1f27"/></svg>`;}
function nmSpan(full){return `<span class="fn">${esc(full)}</span><span class="c3">${esc(code(full))}</span>`;}
function drvCell(s,r){const t=teamAt(s,r);return `<td class="stk1"><span class="sw" style="background:${tcol(t)}"></span>${nmSpan(fullName(s))}</td><td style="color:var(--ink-2)">${esc(t||"Reserve driver")}</td>`;}
function qualiTable(rows,r,labels){
  const best=rows.map(x=>{const ts=[x[3],x[4],x[5]].map(secs).filter(v=>v);return ts.length?Math.min(...ts):null;});
  const pole=Math.min(...best.filter(v=>v));const worst=Math.max(...best.filter(v=>v));
  const colBest=[3,4,5].map(c=>Math.min(...rows.map(x=>secs(x[c])).filter(v=>v)));
  return `<div class="tw"><table class="t"><thead><tr><th class="n stk0">Pos</th><th class="n">No</th><th class="stk1">Driver</th><th>Team</th>${labels.map(l=>`<th class="n">${l}</th>`).join("")}<th class="n">Gap</th><th>To pole</th><th class="n">Laps</th></tr></thead><tbody>
  ${rows.map((x,i)=>{const g=best[i]&&best[i]!==pole?"+"+(best[i]-pole).toFixed(3):(best[i]?"—":"");const w=best[i]?Math.max(2,(best[i]-pole)/(worst-pole||1)*100):0;
    const cut=(i===9||i===15)&&rows.length>16?' class="cut"':"";
    return `<tr${cut}><td class="n stk0">${esc(x[0])}</td><td class="n">${x[1]}</td>${drvCell(x[2],r)}${[3,4,5].map(c=>`<td class="n${secs(x[c])===colBest[c-3]?" best":""}">${esc(x[c])}</td>`).join("")}<td class="n">${g}</td><td>${best[i]?`<span class="gapbar"><i style="width:${w}%"></i></span>`:""}</td><td class="n">${esc(x[6])}</td></tr>`;}).join("")}
  </tbody></table></div>`;}
function practiceTable(rows,r){return `<div class="tw"><table class="t"><thead><tr><th class="n stk0">Pos</th><th class="n">No</th><th class="stk1">Driver</th><th>Team</th><th class="n">Time / gap</th><th class="n">Laps</th></tr></thead><tbody>
  ${rows.map((x,i)=>`<tr><td class="n stk0">${esc(x[0])}</td><td class="n">${x[1]}</td>${drvCell(x[2],r)}<td class="n${i===0?" best":""}">${esc(x[3])||"No time"}</td><td class="n">${esc(x[4])}</td></tr>`).join("")}</tbody></table></div>`;}
function classTable(rows,r,withGrid,flName){return `<div class="tw"><table class="t"><thead><tr><th class="n stk0">Pos</th><th class="n">No</th><th class="stk1">Driver</th><th>Team</th><th class="n">Laps</th><th class="n">Time / retired</th>${withGrid?'<th class="n">Grid</th><th class="n">+/−</th>':""}<th class="n">Pts</th></tr></thead><tbody>
  ${rows.map(x=>{const g=x[6];let dl="";if(withGrid&&g!==""&&/^\d+$/.test(x[0])){const gn=g==="PL"?22:+g;const d=gn-(+x[0]);dl=d>0?`<span class="up">▲${d}</span>`:d<0?`<span class="dn">▼${-d}</span>`:"–";}
    const isFl=flName&&norm(x[2])===norm(sur(flName));
    return `<tr><td class="n stk0">${esc(x[0]==="NC"?(stat(x[4])||"NC"):x[0])}</td><td class="n">${x[1]}</td>${drvCell(x[2],r)}<td class="n">${x[3]}</td><td class="n">${esc(x[4])}${isFl?' <span style="color:var(--purple)" title="Fastest lap">◆</span>':""}</td>${withGrid?`<td class="n">${g===""?"–":g==="PL"?"Pit lane":g}</td><td class="n">${dl}</td>`:""}<td class="n">${x[5]||""}</td></tr>`;}).join("")}
  </tbody></table></div>`;}
function gridSection(n){
  const S=SEASON[n], g=GRIDNOTES[n];
  const qpos={};S.quali.forEach((q,i)=>{if(/^\d+$/.test(q[0]))qpos[norm(q[2])]=+q[0];});
  const rows=S.race?S.race.filter(y=>y[6]!==""):(S.grid||[]).map(g=>["",g[1],g[2],"","","",g[0]]);
  const slots=rows.filter(y=>y[6]!=="PL").sort((a,b)=>a[6]-b[6]), pl=rows.filter(y=>y[6]==="PL");
  const slot=(y)=>{const t=teamAt(y[2],n),q=qpos[norm(y[2])],gp=y[6]==="PL"?null:+y[6];
    const d=q&&gp?q-gp:null;const mark=y[6]==="PL"?'<em style="color:var(--ink-3)">PIT</em>':d?`<em class="${d>0?"up":"dn"}" title="Qualified P${q}">${d>0?"▲"+d:"▼"+(-d)}</em>`:q?"":'<em style="color:var(--ink-3)">NO TIME</em>';
    return `<div class="slot${y[6]==="PL"?" pl":""}" style="border-top-color:${tcol(t)}"><b>${y[6]==="PL"?"PL":y[6]}</b><span>${esc(fullName(y[2]))}</span>${mark}</div>`;};
  const changed=rows.filter(y=>{const q=qpos[norm(y[2])];return y[6]==="PL"||q!==+y[6];});
  return `<div class="gridwrap">
    <div><div class="gridviz"><div class="gcol l">${slots.filter((y,i)=>i%2===0).map(slot).join("")}</div><div class="gcol r">${slots.filter((y,i)=>i%2===1).map(slot).join("")}</div></div>
      ${pl.length?`<div class="pitlane"><span class="lbl">Pit lane start</span>${pl.map(slot).join("")}</div>`:""}</div>
    <div class="gnotes"><h3>${g?"Why the grid differs from qualifying":"Grid matches qualifying"}</h3>
      ${g?`<ul>${g.split(/(?<=\.)\s+/).map(x=>`<li>${esc(x)}</li>`).join("")}</ul>`:'<p class="note2" style="margin:0">Every driver started where they qualified.</p>'}
      ${changed.length?`<table><tbody>${changed.map(y=>{const q=qpos[norm(y[2])];return `<tr><td>${esc(fullName(y[2]))}</td><td class="n">${q?"Qualified P"+q:"No time"}</td><td class="n">${y[6]==="PL"?"Pit lane":(S.race?"Started P":"Starts P")+y[6]}</td></tr>`;}).join("")}</tbody></table>`:""}
      <p class="note2">▲ / ▼ on a grid slot shows places gained or lost against qualifying, often because someone ahead took a penalty.</p>
    </div></div>`;
}
let lapSel=new Set();
/* ---------- safety cars and tyre stints ---------- */
const NEUTRAL={SC:"Safety car",VSC:"Virtual safety car",RF:"Red flag",PIT:"Field through the pit lane"};
const TYRE={S:["Soft","var(--tS)"],M:["Medium","var(--tM)"],H:["Hard","var(--tH)"],I:["Intermediate","var(--tI)"],W:["Wet","var(--tW)"],"?":["Unknown","var(--ink-3)"]};
const lapsTxt=(a,b)=>a===b?`lap ${a}`:`laps ${a}–${b}`;
function neutralAt(S,L){const z=S.neutral||[];return z.find(([k,a,b])=>k!=="PIT"&&L>=a&&L<=b)||z.find(([k,a,b])=>L>=a&&L<=b);}
function neutralBands(S,X,y1,y2){const at={};return (S.neutral||[]).map(([k,a,b])=>{const x1=X(a-1),x2=X(b),w=Math.max(2,x2-x1),dy=10*((at[a]=(at[a]||0)+1)-1);
  if(k==="PIT")return `<g class="nb"><line x1="${x2}" x2="${x2}" y1="${y1}" y2="${y2}" stroke="var(--ink-2)" stroke-width="1.4" stroke-dasharray="2 3"><title>${NEUTRAL[k]} · end of lap ${a} (no tyre change)</title></line><text x="${x2}" y="${y1+9+dy}" text-anchor="middle" class="lbl2" font-weight="700" fill="var(--ink-2)">PIT</text></g>`;
  const fill=k==="RF"?"rgba(255,45,45,.20)":k==="SC"?"rgba(255,210,63,.16)":"rgba(255,210,63,.07)";
  return `<g class="nb"><rect x="${x1}" y="${y1}" width="${w}" height="${y2-y1}" fill="${fill}"${k==="VSC"?' stroke="rgba(255,210,63,.55)" stroke-dasharray="3 3"':""}><title>${NEUTRAL[k]} · ${lapsTxt(a,b)}</title></rect>`+
    `<text x="${x1+w/2}" y="${y1+9+dy}" text-anchor="middle" class="lbl2" font-weight="700" fill="${k==="RF"?"var(--signal)":"var(--tM)"}">${k}</text></g>`;}).join("");}
function neutralChips(S){if(!S.neutral)return "";
  if(!S.neutral.length)return `<div class="racebands"><span class="rb none">No safety car, virtual safety car or red flag</span></div>`;
  return `<div class="racebands" role="list" aria-label="Safety cars and red flags">${S.neutral.map(([k,a,b])=>`<span class="rb ${k.toLowerCase()}" role="listitem"><i></i>${NEUTRAL[k]}<small>${lapsTxt(a,b)}</small></span>`).join("")}</div>`;}
function tyreChart(n){const S=SEASON[n],ST=S.stints;
  if(!ST)return `<div class="soon wait"><span class="lbl">Tyre strategy</span><b>Yet to update</b><span>Each driver's tyre stints are added from the official timing data after the race.</span></div>`;
  const rows=S.race.filter(y=>ST[String(y[1])]);const r=RACES.find(x=>x.r===n);
  const nL=Math.max(r.laps||0,...rows.map(y=>ST[String(y[1])].slice(-1)[0][2]));
  const W=980,ml=118,mr=14,mt=16,rowH=19,H=mt+rows.length*rowH+26,X=i=>ml+(W-ml-mr)*i/nL;
  let g=neutralBands(S,X,mt-4,H-22);
  const step=nL>60?10:5;for(let i=0;i<=nL;i+=step)g+=`<line x1="${X(i)}" x2="${X(i)}" y1="${mt-4}" y2="${H-22}" stroke="var(--rule)"/><text x="${X(i)}" y="${H-8}" text-anchor="middle" class="lbl2" fill="var(--ink-3)">${i===0?"Start":"L"+i}</text>`;
  const used=new Set();
  rows.forEach((y,k)=>{const top=mt+k*rowH,t=teamAt(y[2],n),code=(LAPS[n]&&LAPS[n].c[S.race.indexOf(y)])||y[2].slice(0,3).toUpperCase();
    g+=`<text x="8" y="${top+12.5}" class="lbl2" fill="var(--ink-3)">${esc(y[0])}</text><rect x="30" y="${top+4}" width="3" height="11" fill="${tcol(t)}"/><text x="38" y="${top+12.5}" class="lbl2" font-weight="600" fill="var(--ink)">${esc(y[2])}</text>`;
    const ss=ST[String(y[1])];
    ss.forEach(([c,a,b,age],j)=>{used.add(c);const x1=X(a-1)+1,w=Math.max(2,X(b)-X(a-1)-2),T=TYRE[c]||TYRE["?"];
      const lab=w>34?`${c}${age?" ·"+age:""}`:w>12?c:"";
      g+=`<g class="st"><rect x="${x1}" y="${top+3}" width="${w}" height="${rowH-6}" rx="2" fill="${T[1]}"/>${lab?`<text x="${x1+w/2}" y="${top+12.5}" text-anchor="middle" class="lbl2" font-weight="700" fill="#000">${lab}</text>`:""}<title>${esc(code)} · ${T[0]} · ${lapsTxt(a,b)} (${b-a+1} lap${b===a?"":"s"})${age?` · set ${age} laps old at fit`:" · new set"}</title></g>`;});
    const last=ss.slice(-1)[0][2],ret=!/^\d+$/.test(y[0])||/DNF|DNS|DSQ/.test(y[4]);
    if(ret&&last<nL)g+=`<text x="${X(last)+7}" y="${top+13}" text-anchor="middle" font-size="11" fill="var(--ink-3)">✕</text>`;});
  const legend=["S","M","H","I","W","?"].filter(c=>used.has(c)).map(c=>`<span><i style="background:${TYRE[c][1]}"></i>${TYRE[c][0]}</span>`).join("")+
    ((S.neutral||[]).some(x=>x[0]==="SC"||x[0]==="VSC")?`<span><i style="background:rgba(255,210,63,.35)"></i>SC / VSC laps</span>`:"")+((S.neutral||[]).some(x=>x[0]==="RF")?`<span><i style="background:rgba(255,45,45,.5)"></i>Red flag</span>`:"")+((S.neutral||[]).some(x=>x[0]==="PIT")?`<span><i style="width:2px;background:var(--ink-2)"></i>PIT = field sent through the pit lane, tyres not changed</span>`:"");
  const outl=(S.neutral||[]).filter(x=>x[0]!=="PIT").map(([k,a,b])=>{const x1=X(a-1),w=Math.max(2,X(b)-x1);return `<rect x="${x1}" y="${mt-4}" width="${w}" height="${H-22-mt+4}" fill="none" stroke="${k==="RF"?"var(--signal)":"var(--tM)"}" stroke-width="1.2"${k==="VSC"?' stroke-dasharray="4 3"':""} pointer-events="none"/>`;}).join("");
  return `<div class="tyrechart"><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Tyre strategy for every driver, lap by lap">${g}${outl}</svg></div><div class="tylegend">${legend}<span>Number = laps already on the set when fitted</span></div>`;}
function drawLapChart(){
  const el=$("#lapchart"); if(!el) return; cancelAnimationFrame(el._raf);el._playing=false;
  const n=+el.dataset.round, L=LAPS[n], S=SEASON[n];
  const codes=L.c, laps=L.l, nL=laps.length, maxP=Math.max(...laps.map(x=>x.length),codes.length);
  const W=980,ml=46,mr=50,mt=14,rowH=17,H=mt+maxP*rowH+30;
  const X=i=>ml+(W-ml-mr)*i/nL, Y=p=>mt+(p-0.5)*rowH;
  const gridPos={};S.race.forEach((y,i)=>{if(y[6]!=="")gridPos[i]=y[6]==="PL"?maxP:+y[6];});
  const seen={};let g="";
  for(let p=1;p<=maxP;p++)g+=`<text x="${ml-24}" y="${Y(p)+3.5}" text-anchor="end" class="lbl2" fill="var(--ink-3)">${p}</text>`;
  const step=nL>60?10:5;for(let i=0;i<=nL;i+=step)g+=`<line x1="${X(i)}" x2="${X(i)}" y1="${mt}" y2="${H-24}" stroke="var(--rule)"/><text x="${X(i)}" y="${H-10}" text-anchor="middle" class="lbl2" fill="var(--ink-3)">${i===0?"Grid":"L"+i}</text>`;
  const cid="lapclip", ser=[];
  const lines=codes.map((c,di)=>{const row=S.race[di];const t=teamAt(row[2],n);const dash=seen[t];seen[t]=1;
    const pts=[];if(gridPos[di]!==undefined)pts.push([0,Math.min(gridPos[di],maxP)]);
    laps.forEach((lp,li)=>{const k=lp.indexOf(di);if(k>=0)pts.push([li+1,k+1]);});
    if(!pts.length)return "";const ret=!/^\d+$/.test(row[0])||/DNF|DNS|DSQ/.test(row[4]);
    ser.push({di,pts,ret});
    const ptsS=pts.map(q=>X(q[0]).toFixed(1)+","+Y(q[1]).toFixed(1)).join(" ");
    return `<g class="ln" data-d="${di}"><g clip-path="url(#${cid})"><polyline points="${ptsS}" fill="none" stroke="transparent" stroke-width="9" style="cursor:pointer"/><polyline points="${ptsS}" fill="none" stroke="${tcol(t)}" stroke-width="1.8" ${dash?'stroke-dasharray="5 3"':""} stroke-linejoin="round"/></g>
      <text class="rx" x="${X(pts[pts.length-1][0])}" y="${Y(pts[pts.length-1][1])+4}" text-anchor="middle" font-size="12" fill="${tcol(t)}" style="display:none">✕</text>
      <text x="${X(pts[0][0])-6}" y="${Y(pts[0][1])+3.5}" text-anchor="end" class="lbl2" fill="${tcol(t)}" ${pts[0][0]>0?'opacity="0"':""}>${c}</text>
      <circle class="hd" r="3" fill="${tcol(t)}"/><text class="hl lbl2" font-weight="600" fill="${tcol(t)}">${c}</text></g>`;}).join("");
  const cw=Math.max(4,(W-ml-mr)/nL);
  const strip=Array.from({length:nL+1},(_,i)=>`<rect class="lapcell" data-l="${i}" x="${X(i)-cw/2}" y="${mt}" width="${cw}" height="${H-mt-24}" fill="transparent"/>`).join("");
  el.innerHTML=animBar("lapchart","race")+`<div class="lapstep" role="group" aria-label="Inspect a lap"><button class="navbtn" id="lp-prev" aria-label="Previous lap">‹</button><span id="lp-lab" class="lbl">Hover or tap a lap to see the order</span><button class="navbtn" id="lp-next" aria-label="Next lap">›</button><button class="navbtn" id="lp-clr" hidden>Clear</button></div>`+
    `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Lap-by-lap positions"><defs><clipPath id="${cid}"><rect x="0" y="0" width="${W}" height="${H}"/></clipPath></defs>${neutralBands(S,X,mt,H-24)}${g}<g class="cells">${strip}</g>${lines}<g id="lapinsp" style="display:none"></g></svg>`;
  const insp=el.querySelector("#lapinsp"), lab=el.querySelector("#lp-lab"), clr=el.querySelector("#lp-clr"), svgEl=el.querySelector("svg");
  const orderAt=L=>L===0?Object.keys(gridPos).map(Number).sort((a,b)=>gridPos[a]-gridPos[b]):laps[L-1];
  function showLap(L){L=Math.max(0,Math.min(nL,L));const ord=orderAt(L);const x=X(L);const left=L>nL*0.72;
    let h=`<line x1="${x}" x2="${x}" y1="${mt-4}" y2="${H-24}" stroke="var(--ink)" stroke-width="1" stroke-dasharray="3 3"/>`;
    ord.forEach((di,k)=>{const t=teamAt(S.race[di][2],n),y=Y(k+1),bx=left?x-62:x+6;
      h+=`<rect x="${bx}" y="${y-7.5}" width="56" height="15" fill="var(--sheet)" stroke="${tcol(t)}" stroke-width="1"/><text x="${bx+5}" y="${y+3.5}" class="lbl2" fill="var(--ink-3)">${k+1}</text><text x="${bx+22}" y="${y+3.5}" class="lbl2" font-weight="600" fill="${tcol(t)}">${codes[di]}</text>`;});
    insp.innerHTML=h;insp.style.display="";el._lap=L;
    const nz=L?neutralAt(S,L):null;
    lab.textContent=L===0?`Grid · pole ${codes[ord[0]]}`:`Lap ${L}/${nL} · leader ${codes[ord[0]]} · ${ord.length} running${nz?" · "+NEUTRAL[nz[0]]:""}`;}
  function hideLap(){if(el._pin!=null){showLap(el._pin);return;}insp.style.display="none";el._lap=null;lab.textContent="Hover or tap a lap to see the order";}
  const lapFromEvt=e=>{const b=svgEl.getBoundingClientRect();const x=(e.clientX-b.left)/b.width*W;return Math.round((x-ml)/(W-ml-mr)*nL);};
  svgEl.addEventListener("pointermove",e=>{if(el._playing||el._pin!=null)return;const L=lapFromEvt(e);if(L<0||L>nL){hideLap();return;}showLap(L);});
  svgEl.addEventListener("pointerleave",()=>{if(!el._playing)hideLap();});
  el.querySelectorAll(".lapcell").forEach(c=>c.addEventListener("click",()=>{const L=+c.dataset.l;el._pin=el._pin===L?null:L;clr.hidden=el._pin==null;el._pin==null?hideLap():showLap(L);}));
  const stepTo=d=>{const cur=el._pin!=null?el._pin:(el._lap!=null?el._lap:(d>0?-1:nL+1));el._pin=Math.max(0,Math.min(nL,cur+d));clr.hidden=false;showLap(el._pin);};
  el.querySelector("#lp-prev").onclick=()=>stepTo(-1);el.querySelector("#lp-next").onclick=()=>stepTo(1);
  clr.onclick=()=>{el._pin=null;clr.hidden=true;hideLap();};
  el._hideInsp=()=>{el._pin=null;clr.hidden=true;insp.style.display="none";};
  const gs=[...el.querySelectorAll(".ln")];
  attachProgress(el,{n:nL,X,Y,clipId:cid,dur:Math.max(6000,nL*160),series:ser.map((s,k)=>({...s,g:gs[k]})),
    caption:p=>p<0.5?"Grid":(Math.ceil(p)>=nL?`Lap ${nL}/${nL} · Finish`:`Lap ${Math.ceil(p)}/${nL}`)});
  el.classList.toggle("focus",lapSel.size>0);
  gs.forEach(x=>x.classList.toggle("on",lapSel.has(+x.dataset.d)));
  $("#lapkey").innerHTML=codes.map((c,di)=>{const t=teamAt(S.race[di][2],n);return `<button data-lap="${di}" aria-pressed="${lapSel.has(di)}"><i style="background:${tcol(t)}"></i>${c}</button>`;}).join("")+`<button data-lap="clear">Show all</button>`;
  gs.forEach(x=>{x.addEventListener("pointerenter",()=>{if(!lapSel.size){el.classList.add("focus");x.classList.add("on");}});
    x.addEventListener("pointerleave",()=>{if(!lapSel.size){el.classList.remove("focus");x.classList.remove("on");}});
    x.addEventListener("click",()=>{const d=+x.dataset.d;lapSel.has(d)?lapSel.delete(d):lapSel.add(d);applyLapSel();});});
}
function applyLapSel(){const el=$("#lapchart");if(!el)return;el.classList.toggle("focus",lapSel.size>0);
  el.querySelectorAll(".ln").forEach(x=>x.classList.toggle("on",lapSel.has(+x.dataset.d)));
  document.querySelectorAll("#lapkey [data-lap]").forEach(b=>{if(b.dataset.lap!=="clear")b.setAttribute("aria-pressed",lapSel.has(+b.dataset.lap));});}
function viewDetail(n){
  const r=RACES.find(x=>x.r===n); if(!r) return viewSeason(); if(!r.res) return viewLive(n);
  const S=SEASON[n], x=r.res, i=done.indexOf(r);
  const [pv,nx]=navPair(i,"data-detail");
  const days=n===15?["Thu","Fri","Sat"]:["Fri","Sat","Sun"];
  const ses=r.sprint?[["Practice 1","Sprint Qualifying"],["Sprint","Qualifying"],["Grand Prix"]]:[["Practice 1","Practice 2"],["Practice 3","Qualifying"],["Grand Prix"]];
  const wx=S.wx;
  const tyreNames=["Hard","Medium","Soft"];
  const jumps=[["weekend","Weekend"],["practice","Practice"],...(r.sprint?[["sq","Sprint quali"],["sprint","Sprint"]]:[]),["quali","Qualifying"],["grid","Grid"],["race","Race"],["after","Standings"],["chart","Race chart"],["tyres","Tyres"]];
  const g=SEASON[n].race.filter(y=>y[6]!=="").slice().sort((a,b)=>(a[6]==="PL"?99:a[6])-(b[6]==="PL"?99:b[6]));
  const fps=["fp1","fp2","fp3"].filter(k=>S[k]);
  const ds=standingsAfter(n), dsPrev=i>0?standingsAfter(done[i-1].r):[];
  const ts=teamStandingsAfter(n), tsPrev=i>0?teamStandingsAfter(done[i-1].r):[];
  const gain=(prev,z)=>{const p=prev.find(y=>y[0]===z[0]);const g=z[1]-(p?p[1]:0);return g>0?`<span class="gain">+${g}</span>`:'<span style="color:var(--ink-3)">–</span>';};
  const mv=(list,prev,name,k)=>{if(!prev.length)return"–";const j=prev.findIndex(z=>z[0]===name);if(j<0)return"–";const d=j-k;return d>0?`<span class="up">▲${d}</span>`:d<0?`<span class="dn">▼${-d}</span>`:"–";};
  return `
  <div class="dnav pin">${pv}<span class="dmid"><button class="navbtn" data-go="season">Home</button><button class="navbtn" data-top>Top ↑</button></span>${nx}</div>
  <section class="dhero">
    <div class="info">
      <span class="lbl">Round ${r.r} of ${RACES.length} · ${fmt(r.date,{weekday:"long",day:"numeric",month:"long",year:"numeric"})}</span>
      <h2 class="h1">${esc(r.short)}</h2>
      <div style="color:var(--ink-2)">${esc(r.gp)} · ${esc(r.circuit)}, ${esc(r.city)}</div>
      <div>${r.sprint?'<span class="tag sig">Sprint weekend</span>':""}<span class="tag">${r.laps} laps</span><span class="tag">${dist(r.len,3)} lap</span><span class="tag">${dist(r.len*r.laps,1)}</span></div>
      <div class="spec"><div><span class="lbl">Winner</span><b>${esc(code(x.pod[0][0]))}</b></div><div><span class="lbl">Pole</span><b>${esc(code(x.pole))}</b></div><div><span class="lbl">Fastest lap</span><b style="color:var(--purple)">${x.fl[1]}</b></div></div>
      <p class="note2" style="margin:0">${esc(x.cls)}</p>
    </div>
    <div class="map">
      <span class="corner" style="top:8px;left:12px">FIG. ${String(r.r).padStart(2,"0")} · SECTORS</span>
      ${plan(r.track,{big:true,label:r.circuit,len:r.len,sectors:true})}
      ${mapLegend(r.track)}
    </div>
  </section>

  <nav class="jump" aria-label="Jump to section">${jumps.map(j=>`<a href="#detail-${n}" data-jump="${j[0]}">${j[1]}</a>`).join("")}</nav>

  <section class="dsec" id="s-weekend">
    <div class="sec"><h2>Weekend</h2><span class="lbl">Sessions · weather · tyres</span></div>
    <div class="week">${days.map((d,k)=>{const w=wx?wx[k]:null,m=S.wxm?S.wxm[k]:null;return `<div class="day"><span class="lbl">${d==="Thu"?"Thursday":d==="Fri"?"Friday":d==="Sat"?"Saturday":"Sunday"}</span><h3 class="sesn">${ses[k].map(x=>`<span>${x}</span>`).join("")}</h3>
      ${m?`<div class="wx"><b>${Math.round(m[1])}°C</b><span>${m[3]!=null?`Track up to ${Math.round(m[3])}°C · `:""}${m[4]>=50?"Wet":m[4]>0?"Some rain":"Dry"}${m[5]!=null?` · wind up to ${spd(m[5]*3.6,0)}`:""}</span></div>${w?`<div class="wxf">Forecast: ${w[2]?w[2]+"°C, ":""}${esc(w[1])}${w[3]?` · rain ${esc(w[3])}`:""}</div>`:""}`
        :`<div class="wx">${w?`<b>${w[2]?w[2]+"°C":"—"}</b><span>${esc(w[1])}${w[3]?` · rain ${esc(w[3])}`:""}</span>`:`<span>Weather not available</span>`}</div>`}</div>`;}).join("")}</div>
    <p class="note2">${S.wxm?"Weather measured at the track during the sessions: highest air temperature, highest track temperature, rain and strongest wind (official F1 timing feed via TracingInsights). The forecast published before the event is shown underneath.":"Weather is the weekend forecast published before the event (high temperature, conditions, chance of rain)."}${S.wxnote?" On the day: "+esc(S.wxnote):""}</p>
    <div class="tyres">${[1,2,3,4,5].map(c=>{const k=S.tyres.indexOf(String(c));const on=k>=0?k+1:0;return `<div class="ty ${on?"on":""}">${tyreSVG(c,on)}<b>C${c}</b><span>${on?tyreNames[k]:"Not used"}</span></div>`;}).join("")}</div>
    <p class="note2">Pirelli nominated C${S.tyres[0]}, C${S.tyres[1]} and C${S.tyres[2]}. C1 is the hardest compound in the range and C5 the softest.</p>
  </section>

  <section class="dsec" id="s-practice">
    <div class="sec"><h2>Practice</h2><span class="lbl">Best lap per driver</span></div>
    <div class="subtabs" role="group" aria-label="Practice session">${fps.map((k,j)=>`<button data-fp="${k}" aria-pressed="${j===0}">${k.toUpperCase()}</button>`).join("")}</div>
    <div id="fp-out">${practiceTable(S[fps[0]],n)}</div>
    ${r.sprint?'<p class="note2">Sprint weekends have a single practice session.</p>':""}
  </section>

  ${r.sprint?`<section class="dsec" id="s-sq"><div class="sec"><h2>Sprint qualifying</h2><span class="lbl">SQ1 · SQ2 · SQ3</span></div>${qualiTable(S.sq,n,["SQ1","SQ2","SQ3"])}<p class="note2">Dashed lines mark the SQ1 and SQ2 cut-offs. Purple marks the fastest time in each part.</p></section>
  <section class="dsec" id="s-sprint"><div class="sec"><h2>Sprint</h2><span class="lbl">${S.sprint[0][3]} laps · winner ${esc(fullName(S.sprint[0][2]))}</span></div>${classTable(S.sprint,n,false)}</section>`:""}

  <section class="dsec" id="s-quali">
    <div class="sec"><h2>Qualifying</h2><span class="lbl">Q1 · Q2 · Q3</span></div>
    ${qualiTable(S.quali,n,["Q1","Q2","Q3"])}
    <p class="note2">Dashed lines mark the Q1 and Q2 cut-offs. Purple marks the fastest time in each part. Per-sector qualifying times are not in the published results used here, so they are not shown yet.${n===13?" Antonelli qualified seventh but started from the back after taking extra power unit elements.":""}</p>
  </section>

  <section class="dsec" id="s-grid">
    <div class="sec"><h2>Starting grid</h2><span class="lbl">After penalties</span></div>
    ${gridSection(n)}
  </section>

  <section class="dsec" id="s-race">
    <div class="sec"><h2>Race classification</h2><span class="lbl">${r.laps} laps · ${esc(x.time)}</span></div>
    ${classTable(S.race,n,true,x.fl[0])}
    <p class="note2"><span style="color:var(--purple)">◆</span> Fastest lap: ${esc(x.fl[0])}, ${x.fl[1]} on lap ${x.fl[2]} (${spd(x.fl[3],3)} average). ${x.pit?`Fastest pit stop: ${esc(x.pit[1])}, ${esc(x.pit[0])}, ${x.pit[2]}.`:""} No point is awarded for fastest lap in 2026.</p>
  </section>

  <section class="dsec" id="s-after">
    <div class="sec"><h2>Standings after round ${n}</h2><span class="lbl">Places and points gained vs round ${i>0?done[i-1].r:"–"}</span></div>
    <div class="two stand">
      <div><div class="tw"><table class="t" style="min-width:0"><thead><tr><th class="n">Pos</th><th class="n">±</th><th>Driver</th><th class="n">Pts</th><th class="n" title="Points scored this round">+Pts</th></tr></thead><tbody>${ds.map((z,k)=>`<tr${k>=10?' class="xr"':""}><td class="n">${k+1}</td><td class="n">${mv(ds,dsPrev,z[0],k)}</td><td><span class="sw" style="background:${tcol(teamOf(z[0])||teamAt(z[0],n))}"></span>${esc(z[0])}</td><td class="n">${z[1]}</td><td class="n">${gain(dsPrev,z)}</td></tr>`).join("")}</tbody></table></div>
        ${ds.length>10?`<button class="navbtn standall" data-standall aria-expanded="false">Show all ${ds.length} drivers</button>`:""}</div>
      <div class="tw"><table class="t" style="min-width:0"><thead><tr><th class="n">Pos</th><th class="n">±</th><th>Constructor</th><th class="n">Pts</th><th class="n" title="Points scored this round">+Pts</th></tr></thead><tbody>${ts.map((z,k)=>`<tr><td class="n">${k+1}</td><td class="n">${mv(ts,tsPrev,z[0],k)}</td><td><span class="sw" style="background:${tcol(z[0])}"></span>${esc(z[0])}</td><td class="n">${z[1]}</td><td class="n">${gain(tsPrev,z)}</td></tr>`).join("")}</tbody></table></div>
    </div>
  </section>

  <section class="dsec" id="s-chart">
    <div class="sec"><h2>How the race went</h2><span class="lbl">Position on every lap · start = grid</span></div>
    ${neutralChips(S)}
    ${fsbox("fs-lap",`${esc(r.short)} · lap chart`,`<div class="lapchart" id="lapchart" data-round="${n}"></div><div class="lapkey" id="lapkey" role="group" aria-label="Highlight drivers"></div>`)}
    <p class="note2">Lines show running order at the end of each lap from the official lap timing. A cross marks a retirement. ${(S.neutral||[]).length?"Shaded laps were run under the safety car (SC), virtual safety car (VSC) or red flag (RF)"+((S.neutral||[]).some(x=>x[0]==="PIT")?"; PIT marks the field being sent through the pit lane":"")+". ":""}Post-race time penalties can change the final classification, so the last lap may differ from the result table.</p>
  </section>

  <section class="dsec" id="s-tyres">
    <div class="sec"><h2>Tyre strategy</h2><span class="lbl">Every stint, lap by lap · finishing order</span></div>
    ${tyreChart(n)}
    <p class="note2">Bars show which compound each driver ran on every lap, from the official F1 timing feed (via TracingInsights), checked against the official pit stop laps. Hover or tap a bar for the laps and the age of the set.</p>
  </section>


  <div class="dnav" style="margin-top:28px">${pv}<span class="dmid"><button class="navbtn" data-go="season">Home</button><button class="navbtn" data-top>Top ↑</button></span>${nx}</div>`;
}

/* ---------- full-screen chart boxes ---------- */
function fsbox(id,title,inner){return `<div class="fsbox" id="${id}"><div class="fsbar"><span class="lbl">${esc(title)}</span><button class="navbtn fsbtn" data-fs="${id}" aria-expanded="false">⤢ Full screen</button></div><div class="fsbody">${inner}</div></div>`;}
function toggleFS(id,force){const b=document.getElementById(id);if(!b)return;const on=force!==undefined?force:!b.classList.contains("full");
  document.querySelectorAll(".fsbox.full").forEach(x=>{if(x!==b){x.classList.remove("full");const k=x.querySelector(".fsbtn");k.textContent="⤢ Full screen";k.setAttribute("aria-expanded","false");}});
  b.classList.toggle("full",on);document.body.classList.toggle("fs-lock",on);const k=b.querySelector(".fsbtn");k.textContent=on?"✕ Close":"⤢ Full screen";k.setAttribute("aria-expanded",String(on));if(on)k.focus();}
/* ---------- CHAMPIONSHIP ---------- */
let chartSel=null;
function viewChampionship(){
  const flags=RACES.map(r=>`<th title="${esc(r.gp)}">${code(r.short.replace("(Sepang)","").trim()).slice(0,3)}<br>${r.r}</th>`).join("");
  const drvRows=DRIVERS.map((d,i)=>{const s=sur(d[0]);
    const cells=RACES.map(r=>{if(!r.res)return `<td class="cell c-none"></td>`;const {row,sp}=resultCell(r.r,s);const c=cellInfo(row);
      const pole=norm(poleOf(r.r))===norm(s), fl=norm(sur(flOf(r.r)))===norm(s);
      const spx=sp?spTag(/^\d+$/.test(sp[0])?sp[0]:(stat(sp[4])||sp[0]),2026):"";
      return `<td class="cell ${c.cls}${pole?" pole":""}${fl?" flap":""}" title="${esc(r.short)}: ${esc(row?row[4]:"Did not take part")}${sp?` · Sprint P${sp[0]}`:""}">${c.txt}${spx}</td>`;}).join("");
    return `<tr><td class="ps">${i+1}</td><td class="nm"><span class="sw" style="background:${tcol(d[2])}"></span>${nmSpan(d[0])}</td>${cells}<td class="tot">${d[3]}</td></tr>`;}).join("");
  const teamRows=CONSTRUCTORS.map((c,i)=>{const drivers=[...new Set(RN.flatMap(r=>SEASON[r].race.filter(x=>teamAt(x[2],r)===c[0]).map(x=>fullName(x[2]))))];
    return drivers.map((dn,k)=>`<tr>${k===0?`<td class="ps" rowspan="${drivers.length}">${i+1}</td><td class="nm" rowspan="${drivers.length}"><span class="sw" style="background:${tcol(c[0])}"></span>${esc(c[0])}</td>`:""}
      <td class="nm" style="position:static;min-width:110px;color:var(--ink-2)">${esc(sur(dn))}</td>
      ${RACES.map(r=>{if(!r.res)return `<td class="cell c-none"></td>`;const {row,sp}=resultCell(r.r,sur(dn));if(!row||teamAt(row[2],r.r)!==c[0])return `<td class="cell c-none"></td>`;const ci=cellInfo(row);const spx=sp?spTag(/^\d+$/.test(sp[0])?sp[0]:(stat(sp[4])||sp[0]),2026):"";return `<td class="cell ${ci.cls}">${ci.txt}${spx}</td>`;}).join("")}
      ${k===0?`<td class="tot" rowspan="${drivers.length}">${c[1]}</td>`:""}</tr>`).join("");}).join("");
  // stats
  const st=DRIVERS.map(d=>{const s=sur(d[0]);let w=0,pod=0,pol=0,fl=0,dnf=0,sw=0,best=99;RN.forEach(r=>{const {row,sp}=resultCell(r,s);
    if(row){const p=+row[0];if(p===1)w++;if(p>=1&&p<=3)pod++;if(p)best=Math.min(best,p);if(stat(row[4])==="Ret")dnf++;}
    if(sp&&sp[0]==="1")sw++;if(norm(poleOf(r))===norm(s))pol++;if(norm(sur(flOf(r)))===norm(s))fl++;});
    return [d,w,pod,pol,fl,sw,dnf,best===99?"–":best];});
  const teamBars=CONSTRUCTORS.map(c=>{const ds=DRIVERS.filter(d=>d[2]===c[0]);return {t:c[0],tot:c[1],ds};});
  const maxT=CONSTRUCTORS[0][1];
  return `
  <div class="sec" style="margin-top:24px"><h2>Grands Prix</h2><span class="lbl">${RACES.length} rounds · ${RACES.filter(r=>r.sprint).length} sprints · select a race for details</span></div>
  ${gpTableHTML(gpRows2026(),true)}
  <div class="sec"><h2>Points progression</h2><span class="lbl">Cumulative points after each round</span></div>
  ${fsbox("fs-prog","Points progression · drivers",`<div class="chips" id="chips"></div><div class="chart" id="chart"></div>`)}

  <div class="sec"><h2>Drivers' championship</h2><span class="lbl">Finishing position by round</span></div>
  ${fsbox("fs-dmx","Drivers' championship",`<div class="mx"><table class="mxt"><thead><tr><th class="ps">Pos</th><th class="nm" style="text-align:left;padding-left:10px">Driver</th>${flags}<th>Pts</th></tr></thead><tbody>${drvRows}</tbody></table></div>`)}
  <div class="keyrow"><span><i class="c-p1"></i>Winner</span><span><i class="c-p2"></i>2nd</span><span><i class="c-p3"></i>3rd</span><span><i class="c-pts"></i>Points</span><span><i class="c-fin"></i>Finished, no points</span><span><i class="c-ret"></i>Retired / not classified</span><span><i class="c-dns" style="border:1px solid var(--rule-2)"></i>Did not start / disqualified</span><span><b style="text-decoration:underline">Underline</b> pole</span><span><i style="box-shadow:inset 0 -3px 0 var(--purple);background:var(--panel-2)"></i>Fastest lap</span><span><small class="spx pts" style="position:static">S3</small> Sprint result (purple = scored points)</span></div>

  <div class="sec"><h2>Constructors' championship</h2><span class="lbl">Each driver's result for the team</span></div>
  ${fsbox("fs-cmx","Constructors' championship",`<div class="mx"><table class="mxt"><thead><tr><th class="ps">Pos</th><th class="nm" style="text-align:left;padding-left:10px">Constructor</th><th>Driver</th>${flags}<th>Pts</th></tr></thead><tbody>${teamRows}</tbody></table></div>`)}

  <div class="two" style="margin-top:28px">
    <div><div class="sec" style="margin-top:0"><h2>Team points split</h2><span class="lbl">Per driver</span></div>
      <div class="box" style="padding:14px"><div class="bars">${teamBars.map(b=>`<div class="bar"><span>${esc(b.t)}</span><span class="tr">${b.ds.map(d=>`<i style="width:${d[3]/maxT*100}%;background:${tcol(b.t)}" title="${esc(d[0])}: ${d[3]}"></i>`).join("")}</span><b>${b.tot}</b></div>`).join("")}</div>
      <p class="note2">Darker segment is the higher-placed driver. Constructor totals include points scored by stand-in drivers.</p></div></div>
    <div><div class="sec" style="margin-top:0"><h2>Team progression</h2><span class="lbl">Cumulative</span></div>${fsbox("fs-team","Team progression",`<div class="chart" id="tchart"></div>`)}</div>
  </div>

  <div class="sec"><h2>Season statistics</h2><span class="lbl">Grand Prix and sprint</span></div>
  <div class="tw"><table class="t"><thead><tr><th class="n stk0">Pos</th><th class="stk1 nonum">Driver</th><th>Team</th><th class="n">Pts</th><th class="n">Wins</th><th class="n">Podiums</th><th class="n">Poles</th><th class="n">Fastest laps</th><th class="n">Sprint wins</th><th class="n">Retirements</th><th class="n">Best finish</th></tr></thead><tbody>
  ${st.map((z,i)=>`<tr><td class="n stk0">${i+1}</td><td class="stk1 nonum"><span class="sw" style="background:${tcol(z[0][2])}"></span>${nmSpan(z[0][0])}</td><td style="color:var(--ink-2)">${esc(z[0][2])}</td><td class="n">${z[0][3]}</td>${z.slice(1).map(v=>`<td class="n">${v||"–"}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
}
/* shared: interpolate a series [[x,y]...] at fractional x */
function interpAt(pts,p){if(p<=pts[0][0])return pts[0][1];for(let i=1;i<pts.length;i++){if(p<=pts[i][0]){const a=pts[i-1],b=pts[i],f=(p-a[0])/((b[0]-a[0])||1);return a[1]+(b[1]-a[1])*f;}}return pts[pts.length-1][1];}
let ANIM_SPEED=1;
function animBar(id,label){return `<div class="animbar"><button class="navbtn" id="${id}-play" aria-label="Animate ${esc(label)}">▶ Animate</button>
  <span class="spd" role="group" aria-label="Animation speed">${[[0.5,"½× slower"],[1,"1×"],[2,"2× faster"]].map(([v,t])=>`<button data-spd="${v}" aria-pressed="${ANIM_SPEED===v}">${t}</button>`).join("")}</span>
  <span class="animcap" id="${id}-cap" aria-live="off"></span></div>`;}
/* attaches progress + animation to a chart whose groups are already drawn */
function attachProgress(el,{n,X,Y,series,caption,spread=0,dur=0,clipId,headLabelsAtEnd=true}){
  const clip=el.querySelector(`#${clipId} rect`), cap=el.querySelector(`#${el.id}-cap`), btn=el.querySelector(`#${el.id}-play`);
  function set(p){
    clip.setAttribute("width",Math.max(0,X(p)+1));
    const heads=series.map(s=>{const last=s.pts[s.pts.length-1][0], first=s.pts[0][0];const pp=Math.min(p,last);const y=Y(interpAt(s.pts,pp));
      return {s,y,ly:y,vis:p>=first,fin:p>=last,x:X(pp)};});
    if(spread){const v=heads.filter(h=>h.vis).sort((a,b)=>a.y-b.y);for(let i=1;i<v.length;i++)if(v[i].ly-v[i-1].ly<spread)v[i].ly=v[i-1].ly+spread;}
    heads.forEach(h=>{const g=h.s.g;const c=g.querySelector(".hd"),t=g.querySelector(".hl"),x=g.querySelector(".rx");
      c.setAttribute("cx",h.x);c.setAttribute("cy",h.y);c.style.display=h.vis?"":"none";
      const showL=h.vis&&(!h.fin||!h.s.ret||!headLabelsAtEnd)&&!(h.fin&&h.s.ret);
      t.setAttribute("x",h.x+7);t.setAttribute("y",h.ly+3.5);t.style.display=showL?"":"none";
      if(x){x.style.display=h.fin&&h.s.ret?"":"none";if(h.fin&&h.s.ret)c.style.display="none";}});
    if(cap)cap.textContent=caption(p);
  }
  set(n);
  if(btn)btn.onclick=()=>{cancelAnimationFrame(el._raf);if(el._playing){el._playing=false;btn.textContent="▶ Animate";set(n);return;}
    el._playing=true;btn.textContent="■ Stop";if(el._hideInsp)el._hideInsp();const D=(dur||Math.max(4000,n*420))*2;let last=null,p=0;
    const step=ts=>{if(!el.isConnected)return;if(last===null)last=ts;p=Math.min(n,p+(ts-last)/D*n*ANIM_SPEED);last=ts;set(p);
      if(p<n&&el._playing)el._raf=requestAnimationFrame(step);else{el._playing=false;btn.textContent="↺ Replay";}};
    set(0);el._raf=requestAnimationFrame(step);};
}
function lineChart(el,series,{h=320,label="pts",rn=null,names=null}={}){
  cancelAnimationFrame(el._raf);el._playing=false;
  if(!series.length){el.innerHTML='<p class="note2" style="margin:0">Pick drivers above to compare.</p>';return;}
  const W=760,H=h,ml=40,mr=84,mt=12,mb=30;const RNx=rn||RN,NM=names||RNx.map(r=>RACES[r-1].short.replace(" (Sepang)",""));const n=RNx.length;
  const max=Math.ceil(Math.max(...series.flatMap(s=>s.vals))/50)*50||50;
  const X=i=>ml+(W-ml-mr)*i/n, Y=v=>mt+(H-mt-mb)*(1-v/max);
  let g="";for(let v=0;v<=max;v+=max>300?100:50)g+=`<line x1="${ml}" x2="${W-mr}" y1="${Y(v)}" y2="${Y(v)}" stroke="var(--rule)" stroke-width="1"/><text x="${ml-6}" y="${Y(v)+4}" text-anchor="end" font-size="10" fill="var(--ink-3)" font-family="IBM Plex Mono,monospace">${v}</text>`;
  RNx.forEach((r,i)=>{g+=`<text x="${X(i+1)}" y="${H-10}" text-anchor="middle" font-size="10" fill="var(--ink-3)" font-family="IBM Plex Mono,monospace">${r}</text>`;});
  const cid=`${el.id}-clip`;
  const lines=series.map((s,k)=>`<g class="sr" data-k="${k}"><polyline clip-path="url(#${cid})" points="${s.vals.map((v,i)=>X(i)+","+Y(v)).join(" ")}" fill="none" stroke="${s.col}" stroke-width="2" ${s.dash?'stroke-dasharray="5 3"':""} stroke-linejoin="round"/>
    <circle class="hd" r="3.5" fill="${s.col}"/><text class="hl" font-size="10.5" font-weight="600" fill="${s.col}" font-family="IBM Plex Mono,monospace">${esc(s.lab||s.name)}</text></g>`).join("");
  el.innerHTML=animBar(el.id,"points progression")+`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Cumulative points by round"><defs><clipPath id="${cid}"><rect x="0" y="0" width="${W}" height="${H}"/></clipPath></defs>${g}${lines}<line id="${el.id}-g" x1="0" x2="0" y1="${mt}" y2="${H-mb}" stroke="var(--ink-3)" stroke-dasharray="2 3" opacity="0"/><rect x="${ml}" y="${mt}" width="${W-ml-mr}" height="${H-mt-mb}" fill="transparent" id="${el.id}-hit"/></svg><div class="tip" hidden></div>`;
  const svg=el.querySelector("svg"),tip=el.querySelector(".tip"),gl=el.querySelector(`#${el.id}-g`);
  const groups=[...el.querySelectorAll(".sr")];
  attachProgress(el,{n,X,Y,clipId:cid,spread:11,series:series.map((s,k)=>({g:groups[k],ret:false,pts:s.vals.map((v,i)=>[i,v])})),
    caption:p=>{const i=Math.min(n,Math.max(0,Math.ceil(p-1e-6)));return i===0?"Before round 1":`After R${RNx[i-1]} · ${NM[i-1]}`;}});
  const move=e=>{if(el._playing)return;const b=svg.getBoundingClientRect();const x=(e.clientX-b.left)/b.width*W;let i=Math.round((x-ml)/(W-ml-mr)*n);i=Math.max(1,Math.min(n,i));
    gl.setAttribute("x1",X(i));gl.setAttribute("x2",X(i));gl.setAttribute("opacity","1");
    const rows=series.map(s=>[s.name,s.vals[i],s.col]).sort((a,b)=>b[1]-a[1]);
    tip.innerHTML=`<b>R${RNx[i-1]} ${esc(NM[i-1])}</b>${rows.map(z=>`<div><span style="color:${z[2]}">${esc(z[0])}</span><span>${z[1]}</span></div>`).join("")}`;
    tip.hidden=false;const px=X(i)/W*b.width;tip.style.left=Math.min(px+14,b.width-170)+"px";tip.style.top="44px";};
  svg.addEventListener("pointermove",move);svg.addEventListener("pointerleave",()=>{tip.hidden=true;gl.setAttribute("opacity","0");});
}
function drawCharts(){
  const el=$("#chart"); if(!el) return;
  if(!chartSel) chartSel=new Set(DRIVERS.map(d=>d[0]));
  const seen={};const series=DRIVERS.filter(d=>chartSel.has(d[0])).map(d=>{const dash=seen[d[2]];seen[d[2]]=1;return {name:sur(d[0]),lab:code(d[0]),col:tcol(d[2]),dash,vals:cumulative([d[0]])[0]};});
  $("#chips").innerHTML=`<button data-chipset="all" aria-pressed="false">All drivers</button><button data-chipset="top" aria-pressed="false">Top 6</button><button data-chipset="none" aria-pressed="false">Clear</button>`+DRIVERS.map(d=>`<button data-chip="${esc(d[0])}" aria-pressed="${chartSel.has(d[0])}"><i style="background:${tcol(d[2])}"></i>${code(d[0])}</button>`).join("");
  lineChart(el,series,{h:420});
  const tser=CONSTRUCTORS.slice(0,6).map(c=>{let s=0;return {name:c[0],lab:({"Red Bull Racing":"Red Bull","Racing Bulls":"RB","Haas F1 Team":"Haas","Aston Martin":"Aston"})[c[0]]||c[0],col:tcol(c[0]),vals:[0,...RN.map(r=>s+=teamPtsAt(r,c[0]))]};});
  lineChart($("#tchart"),tser,{h:300});
}

/* ---------- SEASON ARCHIVE: full championship pages 1950–2025 ---------- */
const HCOL={"red-bull":"#3671c6","mercedes":"#00a19c","ferrari":"#dc0000","mclaren":"#ff8000","williams":"#1868db","renault":"#ffd800","lotus-f1":"#c9a227","force-india":"#f596c8","racing-point":"#f596c8","aston-martin":"#229971","alpine":"#ff5fa2","sauber":"#9b9fa6","alfa-romeo":"#a6192e","kick-sauber":"#52e252","toro-rosso":"#469bff","alphatauri":"#7d9bb8","rb":"#6c98ff","racing-bulls":"#6c98ff","haas":"#b6babd","caterham":"#1f9e57","lotus-racing":"#1f9e57","virgin":"#d62d3a","marussia":"#e2231a","manor":"#e8434b","hrt":"#b5a26a","benetton":"#5fb0e8","jordan":"#c6d300","arrows":"#ff8c1a","bar":"#f0f0f0","jaguar":"#1a8a55","prost":"#2f49c4","minardi":"#b07cc6","toyota":"#ff6f61","honda":"#4caf50","bmw-sauber":"#bcd4f6","super-aguri":"#d94f8b","midland":"#b23a48","spyker":"#ff7f00","brawn":"#c8f000","alfa-romeo-1":"#a6192e","maserati":"#2f5fd0","vanwall":"#1f7a5c","cooper":"#3aa0a0","lotus":"#2f9e5f","brm":"#5b6b2e","brabham":"#2e9bd6","march":"#ff9f40","matra":"#4a7bd8","tyrrell":"#2d5fc0","ligier":"#4f9be8","shadow":"#5a5f6a","surtees":"#c94040","hesketh":"#d9d9d9","wolf":"#c8a048","lola":"#e06666","porsche":"#bfbfbf","gordini":"#3d6fb5","simca-gordini":"#3d6fb5","talbot-lago":"#4766b3","connaught":"#3c8f3c","era":"#6b8e23","alta":"#8a9a5b","hwm":"#4f7f4f","kurtis-kraft":"#c79a3a","toleman":"#5a8fd6","leyton-house":"#3fb7b0","footwork":"#d9d9d9","dallara":"#e05050","larrousse":"#e66aa8","stewart":"#f2f2f2","prost":"#2f49c4","eagle":"#3f62c8","honda":"#4caf50","bugatti":"#2f6fd6","delage":"#3a7fc1","delahaye":"#4c6fa8","cisitalia":"#c9503c"};
const hcol=(id,y)=>id&&id.includes("@")?hcol(id.split("@")[0],y):id==="mclaren"&&y<2017?"#a8b0b8":id==="force-india"&&y<2017?"#ff8f1f":id==="williams"&&y<2014?"#5b8ad6":HCOL[id]||"var(--ink-3)";
const gpShort=n=>n.replace(/ Grand Prix$/,"").replace(/^Grand Prix of /,"");
const RACECC={albert:"AU",shanghai:"CN",suzuka:"JP",miami:"US",montreal:"CA",monaco:"MC",catalunya:"ES",rbring:"AT",silverstone:"GB",spa:"BE",hungaro:"HU",zandvoort:"NL",monza:"IT",madring:"ES",baku:"AZ",sepang:"MY",marina:"SG",cota:"US",mexico:"MX",interlagos:"BR",vegas:"US",lusail:"QA",yas:"AE"};
function seasonModel(y){const A=ARCHDATA[y];if(!A)return null;
  const split=a=>a?a.map(s=>s.split("|")):null;const res=split(A.res),sp=split(A.sp),tm=split(A.tm);
  return {y,n:A.R.length,R:A.R.map(r=>({r:r[0],gp:r[1],cc:r[2],date:r[3],circuit:r[4],pole:r[5],fl:r[6],win:r[7],wc:r[8],sw:r[9]})),
    D:A.D.map((d,i)=>({name:d[0],abbr:d[1],team:d[2],pts:d[3],pos:d[4],cc:d[5],i})),C:A.C.map(c=>({id:c[0],name:c[1],pts:c[2],pos:c[3],cc:c[4]})),
    res,sp,team:(i,k)=>(tm[i][k]||A.D[i][2]),cum:A.cum,ccum:A.ccum,
    tname:id=>((A.C.find(c=>c[0]===id)||[])[1])||((A.cn||{})[id]||[])[0]||id,tcc:id=>((A.C.find(c=>c[0]===id)||[])[4])||((A.cn||{})[id]||[])[1]};}
const ptsCut=y=>y<1960?5:y<2003?6:y<2010?8:10, spCut=y=>y===2021?3:8;   /* points went to the top 5 until 1959, top 6 1960-2002, top 8 2003-2009 */
function aCell(t,y){if(!t)return {cls:"c-none",txt:""};if(/^\d+$/.test(t)){const p=+t;return {txt:t,cls:p===1?"c-p1":p===2?"c-p2":p===3?"c-p3":p<=ptsCut(y)?"c-pts":"c-fin"};}
  if(t==="Ret"||t==="NC")return {txt:t,cls:"c-ret"};return {txt:t,cls:"c-dns"};}
const spTag=(t,y)=>t?`<small class="spx${/^\d+$/.test(t)&&+t<=spCut(y)?" pts":""}">S${t.replace("Ret","R")}</small>`:"";
const pflag=(cc)=>flagOf(cc);
function gpTableHTML(rows,hasSprint){
  return `<div class="tw"><table class="t gpt"><thead><tr><th class="n">Rd</th><th>Grand Prix</th><th>Date</th><th>Pole position</th><th>Fastest lap</th><th>Winning driver</th><th>Winning constructor</th>${hasSprint?"<th>Sprint winner</th>":""}</tr></thead><tbody>
  ${rows.map(r=>{const who=p=>p&&p.n?`${pflag(p.cc)} ${esc(p.n)}`:'<span style="color:var(--ink-3)">—</span>';
    return `<tr${r.go?` data-go="${r.go}" class="go"`:""}><td class="n">${r.r}</td><td>${pflag(r.cc)} <b>${esc(r.gp)}</b></td><td class="m">${r.date?new Date(r.date+"T12:00:00Z").toLocaleDateString("en-GB",{day:"numeric",month:"short",timeZone:"UTC"}):""}</td><td>${who(r.pole)}</td><td>${who(r.fl)}</td><td>${r.win&&r.win.n?`<b>${who(r.win)}</b>`:who(r.win)}</td><td>${r.wc&&r.wc.n?`<span class="sw" style="background:${r.wc.col}"></span>${pflag(r.wc.cc)} ${esc(r.wc.n)}`:who(null)}</td>${hasSprint?`<td>${r.sprint?(r.sw&&r.sw.n?`<span class="tag" style="margin:0 6px 0 0;padding:1px 5px;font-size:9.5px">Sprint</span>${who(r.sw)}`:'<span class="tag" style="margin:0;padding:1px 5px;font-size:9.5px">Sprint</span>'):'<span style="color:var(--ink-3)">—</span>'}</td>`:""}</tr>`;}).join("")}
  </tbody></table></div>`;}
function archGpRows(S){const D=S.D,cn={};S.C.forEach(c=>cn[c.id]=c);
  const p=i=>i!=null&&i>=0?{n:D[i].name,cc:D[i].cc}:null;
  return S.R.map(r=>({r:r.r,gp:r.gp,cc:r.cc,date:r.date,pole:p(r.pole),fl:p(r.fl),win:p(r.win),wc:r.wc?{n:S.tname(r.wc),cc:S.tcc(r.wc),col:hcol(r.wc,S.y)}:null,sprint:r.sw!=null,sw:p(r.sw)}));}
function gpRows2026(){return RACES.map(r=>{const S=SEASON[r.r]||{};const nat=n=>{const b=n&&bioOf(n);return b?b.iso2:null;};
  const pq=S.quali&&S.quali[0]?fullName(S.quali[0][2]):null;
  const sw=S.sprint&&S.sprint[0]?fullName(S.sprint[0][2]):(typeof r.sprint==="string"?r.sprint:null);
  const win=r.res?r.res.pod[0][0]:null,team=win?(teamAt(win,r.r)||teamOf(win)):null;
  return {r:r.r,gp:r.gp.replace(" (Sepang)",""),cc:RACECC[r.track],date:r.date,go:r.res?`detail-${r.r}`:(S.quali||S.sprint||S.fp1?`detail-${r.r}`:null),
    pole:pq?{n:pq,cc:nat(pq)}:null,fl:r.res?{n:r.res.fl[0],cc:nat(r.res.fl[0])}:null,win:win?{n:win,cc:nat(win)}:null,
    wc:team?{n:team,cc:(TEAMNAT[team]||[])[0],col:tcol(team)}:null,sprint:!!r.sprint,sw:sw?{n:sw,cc:nat(sw)}:null};});}
const startedAny=(S,d)=>S.R.some((r,k)=>{const t=S.res[d.i][k];return t&&!/^(DNQ|DNPQ|DNS|DNP)$/.test(t);});
function archDriverMatrix(S){const fl=S.R.map(r=>r.fl),po=S.R.map(r=>r.pole);const shown=S.D.filter(d=>startedAny(S,d)),hidden=S.D.length-shown.length;
  const head=S.R.map(r=>`<th title="${esc(r.gp)}">${pflag(r.cc)}<br>${r.r}</th>`).join("");
  const rows=shown.map(d=>`<tr><td class="ps">${esc(d.pos)}</td><td class="nm"><span class="sw" style="background:${hcol(d.team,S.y)}"></span><span class="fn">${esc(d.name)}</span><span class="c3">${esc(d.abbr)}</span></td>${S.R.map((r,k)=>{const c=aCell(S.res[d.i][k],S.y);const s=S.sp?S.sp[d.i][k]:"";
    return `<td class="cell ${c.cls}${po[k]===d.i?" pole":""}${fl[k]===d.i?" flap":""}" title="${esc(gpShort(r.gp))}: ${esc(S.res[d.i][k]||"—")}${s?" · Sprint "+esc(s):""}">${c.txt}${spTag(s,S.y)}</td>`;}).join("")}<td class="tot">${d.pts}</td></tr>`).join("");
  return `<div class="mx"><table class="mxt"><thead><tr><th class="ps">Pos</th><th class="nm" style="text-align:left;padding-left:10px">Driver</th>${head}<th>Pts</th></tr></thead><tbody>${rows}</tbody></table></div>${hidden?`<p class="note2">${hidden} entrant${hidden===1?"":"s"} who did not start a race ${hidden===1?"is":"are"} not shown.</p>`:""}`;}
function archConsMatrix(S){const head=S.R.map(r=>`<th title="${esc(r.gp)}">${pflag(r.cc)}<br>${r.r}</th>`).join("");
  const rows=S.C.map(c=>{const ds=S.D.filter(d=>S.R.some((r,k)=>S.res[d.i][k]&&S.team(d.i,k)===c.id));
    return ds.map((d,j)=>`<tr>${j===0?`<td class="ps" rowspan="${ds.length}">${esc(c.pos)}</td><td class="nm" rowspan="${ds.length}"><span class="sw" style="background:${hcol(c.id,S.y)}"></span>${esc(c.name)}</td>`:""}<td class="nm" style="position:static;min-width:110px;color:var(--ink-2)">${esc(d.name.split(" ").slice(-1)[0])}</td>
      ${S.R.map((r,k)=>{if(S.team(d.i,k)!==c.id||!S.res[d.i][k])return `<td class="cell c-none"></td>`;const x=aCell(S.res[d.i][k],S.y);return `<td class="cell ${x.cls}">${x.txt}${spTag(S.sp?S.sp[d.i][k]:"",S.y)}</td>`;}).join("")}
      ${j===0?`<td class="tot" rowspan="${ds.length}">${c.pts}</td>`:""}</tr>`).join("");}).join("");
  return `<div class="mx"><table class="mxt"><thead><tr><th class="ps">Pos</th><th class="nm" style="text-align:left;padding-left:10px">Constructor</th><th>Driver</th>${head}<th>Pts</th></tr></thead><tbody>${rows}</tbody></table></div>`;}
function archStats(S){const st=S.D.map(d=>{let w=0,pod=0,pol=0,fl=0,sw=0,dnf=0,best=99;S.R.forEach((r,k)=>{const t=S.res[d.i][k];if(/^\d+$/.test(t)){const p=+t;if(p===1)w++;if(p<=3)pod++;best=Math.min(best,p);}else if(t==="Ret")dnf++;
    if(r.pole===d.i)pol++;if(r.fl===d.i)fl++;if(r.sw===d.i)sw++;});return [d,w,pod,pol,fl,sw,dnf,best===99?"–":best];}).filter(z=>z[0].pts>0||z[1]||z[3]);
  const hasS=S.R.some(r=>r.sw!=null);
  return `<div class="tw"><table class="t"><thead><tr><th class="n stk0">Pos</th><th class="stk1">Driver</th><th>Team</th><th class="n">Pts</th><th class="n">Wins</th><th class="n">Podiums</th><th class="n">Poles</th><th class="n">Fastest laps</th>${hasS?'<th class="n">Sprint wins</th>':""}<th class="n">Retirements</th><th class="n">Best finish</th></tr></thead><tbody>
  ${st.map(z=>`<tr><td class="n stk0">${esc(z[0].pos)}</td><td class="stk1"><span class="sw" style="background:${hcol(z[0].team,S.y)}"></span><span class="fn">${esc(z[0].name)}</span><span class="c3">${esc(z[0].abbr)}</span></td><td style="color:var(--ink-2)">${esc(S.tname(z[0].team)||"")}</td><td class="n">${z[0].pts}</td>${[z[1],z[2],z[3],z[4]].concat(hasS?[z[5]]:[]).concat([z[6],z[7]]).map(v=>`<td class="n">${v||"–"}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;}
const MATKEY=`<div class="keyrow"><span><i class="c-p1"></i>Winner</span><span><i class="c-p2"></i>2nd</span><span><i class="c-p3"></i>3rd</span><span><i class="c-pts"></i>Points</span><span><i class="c-fin"></i>Finished, no points</span><span><i class="c-ret"></i>Retired / not classified</span><span><i class="c-dns" style="border:1px solid var(--rule-2)"></i>Did not start / disqualified</span><span><b style="text-decoration:underline">Underline</b> pole</span><span><i style="box-shadow:inset 0 -3px 0 var(--purple);background:var(--panel-2)"></i>Fastest lap</span><span><small class="spx pts" style="position:static">S3</small> Sprint result (purple = scored points)</span></div>`;
function archSections(S){const hasS=S.R.some(r=>r.sw!=null);
  return `<div class="sec"><h2>Grands Prix</h2><span class="lbl">${S.n} rounds${hasS?` · ${S.R.filter(r=>r.sw!=null).length} sprints`:""}</span></div>
  ${gpTableHTML(archGpRows(S),hasS)}
  <div class="sec"><h2>Points progression</h2><span class="lbl">Cumulative points after each round · top 10</span></div>
  ${fsbox("fs-aprog",`${S.y} points progression`,`<div class="chart" id="achart"></div>`)}
  <div class="sec"><h2>Drivers' championship</h2><span class="lbl">Finishing position by round${hasS?" · with sprint":""}</span></div>
  ${fsbox("fs-admx",`${S.y} drivers' championship`,archDriverMatrix(S))}${MATKEY}
  ${S.C.length?`<div class="sec"><h2>Constructors' championship</h2><span class="lbl">Each driver's result for the team</span></div>
  ${fsbox("fs-acmx",`${S.y} constructors' championship`,archConsMatrix(S))}
  <div class="sec"><h2>Team progression</h2><span class="lbl">Cumulative constructors' points</span></div>
  ${fsbox("fs-ateam",`${S.y} team progression`,`<div class="chart" id="atchart"></div>`)}`:`<p class="note2">There was no constructors' championship until 1958.</p>`}
  <div class="sec"><h2>Season statistics</h2><span class="lbl">Drivers who scored or won</span></div>${archStats(S)}
  <p class="note2">Results data: F1DB (CC BY 4.0). Pole is the driver who started first on merit; in 2021 sprint weekends that was the sprint winner.</p>`;}
function drawArchCharts(y){const S=seasonModel(y);if(!S)return;const rn=S.R.map(r=>r.r),names=S.R.map(r=>gpShort(r.gp));const seen={};
  const ser=S.D.slice(0,10).map(d=>{const dash=seen[d.team];seen[d.team]=1;return {name:d.name.split(" ").slice(-1)[0],lab:d.abbr,col:hcol(d.team,y),dash,vals:[0,...S.cum[d.i]]};});
  const el=$("#achart");if(el)lineChart(el,ser,{h:420,rn,names});
  const tser=S.C.slice(0,6).map((c,i)=>({name:c.name,lab:c.name.split(" ")[0],col:hcol(c.id,y),vals:[0,...S.ccum[i]]}));
  const te=$("#atchart");if(te&&tser.length)lineChart(te,tser,{h:300,rn,names});}
/* ---------- 2027 SEASON ROUTE: world map with every Grand Prix, animated like a flight route ---------- */
/* Natural Earth projection, same scale and centre as the map in /data/world.json (scale 190, centre 500,280) */
const NE1=(lat,lon)=>{const l=lon*Math.PI/180,p=lat*Math.PI/180,p2=p*p,p4=p2*p2;
  return [500+190*l*(0.8707-0.131979*p2+p4*(-0.013791+p4*(0.003971*p2-0.001529*p4))),280-190*p*(1.007226+p2*(0.015085+p4*(-0.044475+0.028874*p2-0.005916*p4)))];};
const hav=(a,b)=>{const r=Math.PI/180,dl=(b[0]-a[0])*r,dn=(b[1]-a[1])*r,q=Math.sin(dl/2)**2+Math.cos(a[0]*r)*Math.cos(b[0]*r)*Math.sin(dn/2)**2;return 12742*Math.asin(Math.sqrt(q));};
const MONS=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
function raceDay(c,y=2027){const m=c[5].split("–").pop().trim().match(/^(\d+)\s*([A-Za-z]{3})?/),mo=MONS.indexOf(m[2]||c[5].trim().slice(-3));
  const d=new Date(Date.UTC(y,mo,+m[1]));return `${["Sun","Mon","Tue","Wed","Thu","Fri","Sat"][d.getUTCDay()]} ${d.getUTCDate()} ${MONS[mo]}`;}
/* 2026 race start at the same circuit, local time, as a guide until F1 publishes the 2027 times */
function ref26(g){return g&&g[4]?tfmt(g[4],g[2],{hour:"2-digit",minute:"2-digit"}):null;}
const RFULL=[-20,10,1040,465],RAR=RFULL[2]/RFULL[3];
const RREG={world:RFULL,europe:[[35,-12],[57,32]],americas:[[-38,-125],[56,-35]],asia:[[-40,34],[46,150]]};
let WORLD=null,RT=null;
function loadWorld(){if(WORLD)return Promise.resolve(WORLD);return fetch(`/data/world.json?v=${WORLDV}`).then(r=>r.json()).then(j=>WORLD=j);}
function rPts(){return CALGEO2027.map(g=>NE1(g[0],g[1]));}
/* each leg is a quadratic curve bowed to the north, like a flight path on a flat map */
function rLeg(a,b){const mx=(a[0]+b[0])/2,my=(a[1]+b[1])/2,dx=b[0]-a[0],dy=b[1]-a[1],L=Math.hypot(dx,dy)||1;let nx=-dy/L,ny=dx/L;if(ny>0){nx=-nx;ny=-ny;}const k=Math.min(.22*L,90);return [a,[mx+nx*k,my+ny*k],b,L];}
function routeMapHTML(){const C=CAL2027,G=CALGEO2027,P=rPts();let km=0;for(let i=1;i<G.length;i++)km+=hav(G[i-1],G[i]);
  const legs=P.slice(1).map((b,i)=>rLeg(P[i],b));
  return `<div class="sec"><h2>Season route</h2><span class="lbl">${C.length} races · about ${dist(km,0).replace(/\B(?=(\d{3})+(?!\d))/g,",")} of travel</span></div>
  <div class="rmap" id="rmap">
    <div class="rbar"><div class="rbtns"><button type="button" class="rplay" data-rplay aria-pressed="false">▶ Play route</button><button type="button" data-rreset>Restart</button></div>
      <div class="rzoom" role="group" aria-label="Map area">${[["world","World"],["europe","Europe"],["americas","Americas"],["asia","Asia & Middle East"]].map(([k,n])=>`<button type="button" data-rzoom="${k}" aria-pressed="${k==="world"}">${n}</button>`).join("")}</div></div>
    <div class="rwrap"><svg id="rsvg" viewBox="${RFULL.join(" ")}" role="img" aria-label="World map of the ${C.length} Grands Prix of 2027 in calendar order">
      <g id="rland"></g>
      <g>${legs.map(l=>`<path class="rleg" d="M${l[0]}Q${l[1]} ${l[2]}"/>`).join("")}</g>
      <g id="rtrail">${legs.map(()=>`<path class="rtr" d=""/>`).join("")}</g>
      <g id="rpins">${P.map((p,i)=>`<g class="rpin" data-rpin="${i}" transform="translate(${p[0].toFixed(1)} ${p[1].toFixed(1)})"><title>R${C[i][0]} ${esc(C[i][1])} · ${esc(C[i][5])}</title><circle r="7"/><text>${C[i][0]}</text></g>`).join("")}</g>
      <g id="rplane" style="display:none"><path d="M9 0 1-1.6-2.5-7.5H-4.6L-2.6-1.6H-6.4L-8.4-4.3H-9.6L-8.6 0-9.6 4.3H-8.4L-6.4 1.6H-2.6L-4.6 7.5H-2.5L1 1.6Z"/></g>
    </svg><div class="rcard" id="rcard" aria-live="polite"></div></div>
    <div class="rstops" id="rstops">${C.map((c,i)=>`<button type="button" data-rstop="${i}" aria-pressed="false"><b>${c[0]}</b>${flagOf(c[2])}<span>${esc(c[4])}</span><small>${esc(raceDay(c).replace(/^\w+ /,""))}</small></button>`).join("")}</div>
  </div>
  <p class="note2">Race start times for 2027 haven't been published yet. Where the circuit also raced in 2026, the card shows that year's start time as a guide. Distances are straight-line distances between circuits.</p>`;}
function rCard(i,next){const C=CAL2027,G=CALGEO2027,c=C[i],ref=ref26(G[i]);
  return `<span class="lbl">${next?"Next stop · ":""}Round ${c[0]}${c[6]?" · Sprint weekend":""}</span><b class="rgp">${flagOf(c[2])} ${esc(c[1])}</b><span class="rci">${esc(c[3])}, ${esc(c[4])}</span>
  <dl><dt>Weekend</dt><dd>${esc(c[5])} 2027</dd><dt>Race day</dt><dd>${raceDay(c)} 2027</dd><dt>Race start</dt><dd>TBC${ref?` <small>· 2026: ${ref} local</small>`:G[i][3]?"":` <small>· no 2026 race here</small>`}</dd>${i?`<dt>From ${esc(C[i-1][4])}</dt><dd>${dist(hav(G[i-1],G[i]),0).replace(/\B(?=(\d{3})+(?!\d))/g,",")}</dd>`:`<dt>Season</dt><dd>Opening round</dd>`}</dl>`;}
function rBox(pts,pad=70,minw=300){const xs=pts.map(p=>p[0]),ys=pts.map(p=>p[1]);let x0=Math.min(...xs)-pad,x1=Math.max(...xs)+pad,y0=Math.min(...ys)-pad,y1=Math.max(...ys)+pad;
  let w=Math.max(x1-x0,minw),h=Math.max(y1-y0,w/RAR);w=Math.max(w,h*RAR);const cx=(x0+x1)/2,cy=(y0+y1)/2;w=Math.min(w,RFULL[2]);h=w/RAR;
  const x=Math.max(RFULL[0],Math.min(RFULL[0]+RFULL[2]-w,cx-w/2)),y=Math.max(RFULL[1],Math.min(RFULL[1]+RFULL[3]-h,cy-h/2));return [x,y,w,h];}
function initRoute(){const svg=$("#rsvg");if(!svg)return;const P=rPts(),N=P.length,legs=P.slice(1).map((b,i)=>rLeg(P[i],b));
  const calm=window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches;
  if(RT&&RT.raf)cancelAnimationFrame(RT.raf);
  const R=RT={svg,P,N,legs,i:0,leg:-1,t:0,phase:"idle",playing:false,vb:RFULL.slice(),tg:RFULL.slice(),raf:0,last:0,wait:0,calm};
  loadWorld().then(w=>{if(svg.isConnected)$("#rland").innerHTML=`<path class="rland" d="${w.land}"/><path class="rbord" d="${w.borders}"/>`;}).catch(()=>{});
  const trs=[...svg.querySelectorAll(".rtr")],pins=[...svg.querySelectorAll(".rpin")],plane=$("#rplane"),card=$("#rcard"),stops=[...document.querySelectorAll("#rstops button")];
  const ez=t=>t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2,lerp=(a,b,t)=>[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t];
  R.select=(i,next)=>{R.i=i;card.innerHTML=rCard(i,next);pins.forEach((p,k)=>{p.classList.toggle("on",k===i);});stops.forEach((b,k)=>b.setAttribute("aria-pressed",String(k===i)));
    const rs=$("#rstops"),b=stops[i];if(rs&&b)rs.scrollLeft=Math.max(0,b.offsetLeft-rs.offsetLeft-(rs.clientWidth-b.offsetWidth)/2);svg.appendChild($("#rpins"));svg.appendChild(plane);};
  R.trails=()=>{trs.forEach((el,k)=>{const l=legs[k];if(k<R.leg||(R.phase!=="fly"&&k<R.i)){el.setAttribute("d",`M${l[0]}Q${l[1]} ${l[2]}`);}else if(k===R.leg&&R.phase==="fly"){const t=ez(R.t),a=lerp(l[0],l[1],t),b=lerp(l[1],l[2],t),c=lerp(a,b,t);el.setAttribute("d",`M${l[0]}Q${a} ${c}`);}else el.setAttribute("d","");});
    pins.forEach((p,k)=>p.classList.toggle("seen",R.phase!=="idle"&&k<R.i));};
  R.setBtn=()=>{const b=$("[data-rplay]");if(b){b.textContent=R.playing?"❚❚ Pause":R.phase==="done"?"▶ Replay":R.phase==="idle"?"▶ Play route":"▶ Resume";b.setAttribute("aria-pressed",String(R.playing));}};
  R.zoom=k=>{const z=RREG[k];R.tg=k==="world"?RFULL.slice():rBox([NE1(z[0][0],z[0][1]),NE1(z[1][0],z[1][1])],10,150);document.querySelectorAll("[data-rzoom]").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.rzoom===k)));R.kick();};
  const startLeg=i=>{R.leg=i;R.t=0;R.phase="fly";R.dur=R.calm?1:Math.max(900,Math.min(2600,700+legs[i][3]*3.2));R.tg=rBox([P[i],P[i+1]]);card.innerHTML=rCard(i+1,true);plane.style.display="";};
  const arrive=j=>{R.phase="dwell";R.wait=R.calm?700:900;R.select(j);if(j<N-1)R.tg=rBox([P[j],P[j+1]]);};
  R.play=()=>{if(R.phase==="done"||R.phase==="idle"){R.leg=-1;R.phase="dwell";R.wait=700;R.select(0);R.tg=rBox([P[0],P[1]]);document.querySelectorAll("[data-rzoom]").forEach(b=>b.setAttribute("aria-pressed","false"));}R.playing=true;R.setBtn();R.kick();};
  /* bring a stop into view (keeps the zoom level) */
  R.show=i=>{const p=P[i],v=R.tg;if(p[0]>v[0]+v[2]*.08&&p[0]<v[0]+v[2]*.92&&p[1]>v[1]+v[3]*.08&&p[1]<v[1]+v[3]*.92)return;const w=v[2],h=v[3];
    R.tg=[Math.max(RFULL[0],Math.min(RFULL[0]+RFULL[2]-w,p[0]-w/2)),Math.max(RFULL[1],Math.min(RFULL[1]+RFULL[3]-h,p[1]-h/2)),w,h];document.querySelectorAll("[data-rzoom]").forEach(b=>b.setAttribute("aria-pressed","false"));R.kick();};
  R.pause=()=>{R.playing=false;R.setBtn();};
  R.reset=()=>{R.playing=false;R.phase="idle";R.leg=-1;plane.style.display="none";R.select(0);R.tg=RFULL.slice();R.trails();R.setBtn();R.zoom("world");};
  R.kick=()=>{if(!R.raf){R.last=performance.now();R.raf=requestAnimationFrame(tick);}};
  const tick=ts=>{R.raf=0;if(!svg.isConnected)return;const dt=Math.min(64,ts-R.last);R.last=ts;
    if(R.playing){if(R.phase==="fly"){R.t+=dt/R.dur;if(R.t>=1){R.t=1;R.leg=-1;arrive(R.i+1);plane.style.display="none";}}
      else if(R.phase==="dwell"){R.wait-=dt;if(R.wait<=0){if(R.i>=N-1){R.playing=false;R.phase="done";R.tg=RFULL.slice();R.setBtn();document.querySelectorAll("[data-rzoom]").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.rzoom==="world")));}else startLeg(R.i);}}}
    if(R.phase==="fly"){const l=legs[R.leg],t=ez(R.t),a=lerp(l[0],l[1],t),b=lerp(l[1],l[2],t),c=lerp(a,b,t),ang=Math.atan2(b[1]-a[1],b[0]-a[0])*180/Math.PI;
      plane.setAttribute("transform",`translate(${c[0].toFixed(2)} ${c[1].toFixed(2)}) rotate(${ang.toFixed(1)}) scale(${(R.vb[2]/Math.max(300,svg.getBoundingClientRect().width)*1.25).toFixed(3)})`);}
    R.trails();
    const f=R.calm?1:1-Math.exp(-dt/320);let moving=false;R.vb=R.vb.map((v,k)=>{const d=R.tg[k]-v;if(Math.abs(d)>.3)moving=true;return Math.abs(d)>.3?v+d*f:R.tg[k];});
    svg.setAttribute("viewBox",R.vb.map(v=>v.toFixed(2)).join(" "));
    const px=svg.getBoundingClientRect().width||1000,u=R.vb[2]/px,rr=(px<600?7:8.5)*u;
    pins.forEach(p=>{const c=p.firstElementChild.nextElementSibling,t=c.nextElementSibling;c.setAttribute("r",rr.toFixed(2));t.setAttribute("font-size",(rr*1.15).toFixed(2));});
    if(R.playing||moving)R.raf=requestAnimationFrame(tick);};
  R.select(0);R.setBtn();R.kick();
  /* plays once by itself when the map first comes into view */
  if(!calm&&"IntersectionObserver" in window){const io=new IntersectionObserver(es=>{if(es.some(e=>e.isIntersecting)){io.disconnect();if(R.phase==="idle"&&svg.isConnected)R.play();}},{threshold:.5});io.observe(svg);}
  window.addEventListener("resize",()=>R.kick(),{passive:true});}
function view2027(){const C=CAL2027;
  return `<div class="arch" style="grid-template-columns:minmax(0,1fr)"><div class="txt"><span class="lbl">Season 2027</span><h2 class="h1" style="font-size:clamp(56px,10vw,120px)">2027</h2>
    <p style="font-size:19px;color:var(--ink)"><b>Calendar.</b> The 2027 calendar is confirmed: ${C.length} Grands Prix, ${C.filter(c=>c[6]).length} with a sprint, starting in Bahrain on 14 March and ending in Abu Dhabi on 12 December. Portugal and Türkiye return to the calendar. Pre-season testing runs in Bahrain from 24 to 27 February.</p></div></div>
  ${routeMapHTML()}
  <div class="sec"><h2>2027 calendar</h2><span class="lbl">Provisional · subject to change</span></div>
  <div class="tw"><table class="t gpt"><thead><tr><th class="n">Rd</th><th>Grand Prix</th><th>Circuit</th><th>Location</th><th>Weekend</th><th>Race day</th><th>Format</th></tr></thead><tbody>
  ${C.map(c=>`<tr><td class="n">${c[0]}</td><td>${flagOf(c[2])} <b>${esc(c[1])}</b></td><td>${esc(c[3])}</td><td style="color:var(--ink-2)">${esc(c[4])}</td><td class="m">${esc(c[5])}</td><td class="m">${raceDay(c)}</td><td>${c[6]?'<span class="tag sig" style="margin:0">Sprint</span>':'<span style="color:var(--ink-3)">Standard</span>'}</td></tr>`).join("")}</tbody></table></div>
  <div class="sec"><h2>Confirmed line-ups</h2><span class="lbl">As announced so far</span></div>
  <div class="tw"><table class="t" style="min-width:0"><thead><tr><th>Team</th><th>Drivers</th></tr></thead><tbody>${ENTRIES2027.map(e=>`<tr><td><span class="sw" style="background:${tcol(e[0])}"></span>${esc(e[0])}</td><td>${e[1].map(x=>x?esc(x):'<span style="color:var(--ink-3)">TBC</span>').join(" · ")}</td></tr>`).join("")}</tbody></table></div>
  <p class="note2">Sources: Formula 1 calendar announcement (16 September 2026), RaceFans and Wikipedia. Full race weekends, results and standings will appear here once the season starts.</p>`;}

/* ---------- ARCHIVE ---------- */
/* year rail: keep the selected year in the middle; slides from where the rail was before the page re-rendered */
function centreDecs(){const d=$(".decs"),b=d&&d.querySelector('[aria-pressed="true"]');if(!b||d.scrollWidth<=d.clientWidth)return;
  d.scrollLeft=Math.max(0,d.scrollLeft+b.getBoundingClientRect().left-d.getBoundingClientRect().left-(d.clientWidth-b.offsetWidth)/2);}
function centreYrail(prevX){centreDecs();const rail=$(".yrail"),on=rail&&rail.querySelector('[aria-pressed="true"]');if(!on)return;
  const rb=rail.getBoundingClientRect(),ob=on.getBoundingClientRect();
  const x=Math.max(0,Math.min(rail.scrollWidth-rail.clientWidth,rail.scrollLeft+(ob.left-rb.left)-(rail.clientWidth-ob.width)/2-rail.clientLeft));
  const calm=window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches;
  if(prevX==null||calm){rail.scrollLeft=x;return;}rail.scrollLeft=prevX;requestAnimationFrame(()=>rail.scrollTo({left:x,behavior:"smooth"}));}
/* archive seasons are separate files (/data/archive/<year>.json), loaded when a season page opens */
const SEASONLOAD={};
function loadSeason(y){if(ARCHDATA[y])return Promise.resolve();if(!SEASONLOAD[y])SEASONLOAD[y]=fetch(`/data/archive/${y}.json?v=${ARCHV[y]}`).then(r=>{if(!r.ok)throw new Error(r.status);return r.json();}).then(j=>{ARCHDATA[y]=j;}).catch(e=>{delete SEASONLOAD[y];const n=$(".arch .note2");if(n)n.textContent="The results could not be loaded. Check your connection and reload the page.";});return SEASONLOAD[y];}
/* year rail with decade shortcuts above it; the decade buttons only scroll the rail */
const DECADES=(()=>{const top=Math.max(...Object.keys(ARCHIVE).map(Number)),d=[[top,2020]];for(let y=2019;y>=1950;y-=10)d.push([y,y-9]);d.push(["1946-1949","1949–1946"]);return d;})();
const decOf=y=>y==="1946-1949"?"1946-1949":String(y>=2020?DECADES[0][0]:y-y%10+9);
function yearRail(sel){const ys=Object.keys(ARCHIVE).map(Number).sort((a,b)=>b-a),on=decOf(sel);
  return `<div class="decs" role="group" aria-label="Jump to decade">${DECADES.map(([a,b])=>`<button type="button" data-dec="${a}" aria-pressed="${String(a)===on}">${typeof b==="string"?b:a+"–"+b}</button>`).join("")}</div>`+
  `<div class="yrail" role="group" aria-label="Season">${ys.map(y=>`<a href="${H("archive-"+y)}" data-year="${y}" aria-pressed="${y===sel}">${y}${y===2027?'<small>Calendar</small>':""}</a>`).join("")}<a href="${H("archive-1946-1949")}" data-year="1946-1949" class="pw" aria-pressed="${sel==="1946-1949"}">1946–49<small>Pre-1950</small></a></div>`;}
function scrollDecade(a){const rail=$(".yrail"),t=rail&&rail.querySelector(`[data-year="${a}"]`);if(!t)return;
  const x=Math.max(0,Math.min(rail.scrollWidth-rail.clientWidth,rail.scrollLeft+t.getBoundingClientRect().left-rail.getBoundingClientRect().left-rail.clientLeft));
  const calm=window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches;rail.scrollTo({left:x,behavior:calm?"auto":"smooth"});
  document.querySelectorAll(".decs [data-dec]").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.dec===String(a))));centreDecs();}

/* 1946-1949: Grand Prix racing before the World Championship (no points, no champion) */
const MAKECOL={"Alfa Romeo":"alfa-romeo-1","Maserati":"maserati","Ferrari":"ferrari","Talbot-Lago":"talbot-lago","ERA":"era","Simca-Gordini":"simca-gordini","Bugatti":"bugatti","Delage":"delage","Delahaye":"delahaye","Cisitalia":"cisitalia"};
const makeCol=m=>hcol(MAKECOL[m]||"",1949);
function viewPrewar(){const P=PREWAR,yrs=Object.keys(P.years).sort();
  const all=yrs.flatMap(y=>P.years[y].races.map(r=>({y,d:r[0],gp:r[1],cc:r[2],circ:r[3],who:r[4].split(" / "),wcc:r[5],car:r[6],ge:!!r[7]})));
  const nat={};all.forEach(r=>r.who.forEach(w=>nat[w]=r.wcc));
  const tally=(key,list)=>{const t={};list.forEach(r=>key(r).forEach(k=>{t[k]=t[k]||{n:0,ge:0,y:{}};t[k].n++;if(r.ge)t[k].ge++;t[k].y[r.y]=(t[k].y[r.y]||0)+1;}));return Object.entries(t).sort((a,b)=>b[1].n-a[1].n||b[1].ge-a[1].ge||a[0].localeCompare(b[0]));};
  const drv=tally(r=>r.who,all),mk=tally(r=>[r.car],all),ges=all.filter(r=>r.ge);
  const dt=d=>new Date(d+"T12:00:00Z").toLocaleDateString("en-GB",{day:"numeric",month:"short",timeZone:"UTC"});
  const who=r=>r.who.map(w=>`${flagOf(r.wcc)} ${esc(w)}`).join(" / ");
  const car=m=>`<span class="sw" style="background:${makeCol(m)}"></span>${esc(m)}`;
  const getag='<span class="tag" style="margin:0 0 0 6px;padding:1px 5px;font-size:9.5px">Grande Épreuve</span>';
  const row=(p,i)=>`<div class="row"><span class="pp">${i+1}</span><span class="c" style="background:${p[2]}"></span><span><strong>${p[0]}</strong></span><span class="mono">${p[1]}</span></div>`;
  const tbl=(rs,yr)=>`<div class="tw"><table class="t gpt"><thead><tr>${yr?"<th>Year</th>":""}<th>Date</th><th>Race</th><th>Circuit</th><th>Winner</th><th>Car</th></tr></thead><tbody>${rs.map(r=>`<tr>${yr?`<td class="n">${r.y}</td>`:""}<td class="m">${dt(r.d)}</td><td>${flagOf(r.cc)} ${r.ge?`<b>${esc(r.gp)}</b>${getag}`:esc(r.gp)}</td><td>${esc(r.circ)}</td><td>${r.ge?`<b>${who(r)}</b>`:who(r)}</td><td>${car(r.car)}</td></tr>`).join("")}</tbody></table></div>`;
  const yt=(t,name)=>`<div class="tw"><table class="t"><thead><tr><th class="n">#</th><th>${name}</th>${yrs.map(y=>`<th class="n">${y}</th>`).join("")}<th class="n">Grandes Épreuves</th><th class="n">Wins</th></tr></thead><tbody>${t.map(([k,v],i)=>`<tr><td class="n">${i+1}</td><td>${name==="Driver"?`${flagOf(nat[k])} <b>${esc(k)}</b>`:car(k)}</td>${yrs.map(y=>`<td class="n">${v.y[y]||'<span style="color:var(--ink-3)">–</span>'}</td>`).join("")}<td class="n">${v.ge||'<span style="color:var(--ink-3)">–</span>'}</td><td class="n"><b>${v.n}</b></td></tr>`).join("")}</tbody></table></div>`;
  const yearSec=y=>{const Y=P.years[y],rs=all.filter(r=>r.y===y),g=rs.filter(r=>r.ge).length,top=tally(r=>r.who,rs)[0],tm=tally(r=>[r.car],rs)[0];
    return `<section class="dsec" id="pw-${y}"><div class="sec"><h2>${y}</h2><span class="lbl">${rs.length} races · ${g?g+" Grande"+(g>1?"s":"")+" Épreuve"+(g>1?"s":""):"no Grandes Épreuves"}</span></div>
      <p class="pwsum">${esc(Y.sum)}</p><ul class="pwkeys">${(Y.keys||[]).map(k=>`<li>${esc(k)}</li>`).join("")}</ul>
      <p class="note2" style="margin:0 0 10px">Most wins: <b>${esc(top[0])}</b> (${top[1].n}) · Most successful car: <b>${esc(tm[0])}</b> (${tm[1].n})</p>${tbl(rs,false)}</section>`;};
  return yearRail("1946-1949")+`<div class="arch">
    <div class="txt"><span class="lbl">Before the World Championship</span><h2 class="h1">1946–49</h2><p>${esc(P.sum)}</p><ul>${P.keys.map(k=>`<li>${esc(k)}</li>`).join("")}</ul></div>
    <div class="side">
      <div class="box"><div class="bh lbl">Most race wins · 1946–1949</div>${drv.slice(0,3).map(([k,v])=>[`${flagOf(nat[k])} ${esc(k)}`,v.n,"var(--ink-3)"]).map(row).join("")}</div>
      <div class="box"><div class="bh lbl">Most wins by car</div>${mk.slice(0,3).map(([k,v])=>[esc(k),v.n,makeCol(k)]).map(row).join("")}</div>
      <div class="box"><div class="bh lbl">Four seasons</div><div class="row" style="grid-template-columns:1fr auto"><span>Races listed</span><span class="mono">${all.length}</span></div><div class="row" style="grid-template-columns:1fr auto"><span>Grandes Épreuves</span><span class="mono">${ges.length}</span></div><div class="row" style="grid-template-columns:1fr auto"><span>Different winners</span><span class="mono">${drv.length}</span></div><div class="row" style="grid-template-columns:1fr auto"><span>Championship</span><span class="mono">None</span></div></div>
    </div></div>
  <div class="pwjump" role="group" aria-label="Jump to section">${yrs.map(y=>`<button type="button" data-pwj="pw-${y}">${y}</button>`).join("")}<button type="button" data-pwj="pw-ge">Grandes Épreuves</button><button type="button" data-pwj="pw-drv">Most wins</button></div>
  <section class="dsec" id="pw-ge"><div class="sec"><h2>Grandes Épreuves</h2><span class="lbl">The ${ges.length} most prestigious races, 1947–1949</span></div><p class="note2" style="margin:0 0 10px">There were none in 1946. These races came closest to a championship, and most became World Championship rounds from 1950.</p>${tbl(ges,true)}</section>
  ${yrs.map(yearSec).join("")}
  <section class="dsec" id="pw-drv"><div class="sec"><h2>Most wins</h2><span class="lbl">Drivers with two or more wins, 1946–1949</span></div>${yt(drv.filter(([k,v])=>v.n>1),"Driver")}</section>
  <section class="dsec"><div class="sec"><h2>Wins by car</h2><span class="lbl">1946–1949</span></div>${yt(mk,"Car")}</section>
  <p class="note2">There were no points and no champion before 1950, so there are no standings for these years. Race lists: the 1946–1949 Grand Prix season pages on Wikipedia (CC BY-SA 4.0); smaller national and voiturette races are not included. A shared drive (Sommer and Louveau, Lille 1946) counts as a win for both drivers.</p>`;}

function viewArchive(yr){
  const ys=Object.keys(ARCHIVE).map(Number).sort((a,b)=>b-a); yr=yr||2025; const a=ARCHIVE[yr];
  const rail=yearRail(yr);
  if(a.next) return rail+view2027();
  if(a.live) return rail+`<div class="arch"><div class="txt"><h2 class="h1">${yr}</h2><p>In progress: ${done.length} of ${RACES.length} rounds run. ${esc(DRIVERS[0][0])} leads for Mercedes in the first year of the new power unit and active-aero rules.</p><button class="tag sig" data-go="championship" style="cursor:pointer">Open the 2026 championship →</button></div></div>`;
  if(ARCHV[yr]&&!ARCHDATA[yr])return rail+`<div class="arch"><div class="txt"><span class="lbl">Season report</span><h2 class="h1">${yr}</h2><p>${esc(a.sum||"")}</p><p class="note2">Loading the ${yr} results…</p></div></div>`;
  const S=seasonModel(yr), tn=id=>S?S.tname(id):id;
  const top=S?S.D.slice(0,3).map(d=>[d.name,tn(d.team),d.pts,hcol(d.team,yr)]):[a.champ,a.p2,a.p3].map(p=>[p[0],p[1],p[2],tcol(p[1])]);
  const cons=S?(S.C.length?[S.C[0].name,S.C[0].pts,hcol(S.C[0].id,yr)]:null):[a.cons[0],a.cons[1],tcol(a.cons[0])];
  const races=S?S.n:a.races, wins=S?S.R.filter(r=>r.win===0).length:+(a.wins||"").split(" ")[0];
  const row=(p,i)=>`<div class="row"><span class="pp">${i+1}</span><span class="c" style="background:${p[3]}"></span><span><strong>${esc(p[0])}</strong><small style="display:block;color:var(--ink-3);font-size:12px">${esc(p[1])}</small></span><span class="mono">${p[2]}</span></div>`;
  return rail+`<div class="arch">
    <div class="txt"><span class="lbl">Season report</span><h2 class="h1">${yr}</h2><p>${esc(a.sum)}</p><ul>${(a.keys||[]).map(k=>`<li>${esc(k)}</li>`).join("")}</ul></div>
    <div class="side">
      <div class="box"><div class="bh lbl">Drivers' championship · top 3</div>${top.map(row).join("")}</div>
      <div class="box"><div class="bh lbl">Constructors' champion</div>${cons?`<div class="row"><span class="pp">1</span><span class="c" style="background:${cons[2]}"></span><strong>${esc(cons[0])}</strong><span class="mono">${cons[1]}</span></div>`:`<div class="row" style="grid-template-columns:1fr"><span style="color:var(--ink-2)">No constructors' championship until 1958</span></div>`}</div>
      <div class="box"><div class="bh lbl">Season data</div><div class="row" style="grid-template-columns:1fr auto"><span>Races</span><span class="mono">${races}</span></div><div class="row" style="grid-template-columns:1fr auto"><span>Champion's wins</span><span class="mono">${wins}</span></div>${S&&S.R.some(r=>r.sw!=null)?`<div class="row" style="grid-template-columns:1fr auto"><span>Sprints</span><span class="mono">${S.R.filter(r=>r.sw!=null).length}</span></div>`:""}</div>
    </div></div>${S?archSections(S):""}`;
}

/* ---------- SITE PAGES (about, legal, contact) ---------- */
/* ---------- DRIVERS & TEAMS ---------- */
const BIOBY={};Object.values(BIO).forEach(b=>{BIOBY[norm(b.last)]=b;});
const bioOf=name=>BIOBY[norm(sur(name))]||null;
const grid26=DRIVERS.filter(d=>bioOf(d[0]));
const extras26=DRIVERS.filter(d=>!bioOf(d[0]));
const nameParts=n=>{const p=n.split(" ");return [p.slice(0,-1).join(" "),p[p.length-1]];};
const fullName26=d=>{const b=bioOf(d[0]);return b?b.name:d[0];};
const ageOf=dob=>{const b=new Date(dob+"T00:00:00Z"),n=new Date();let a=n.getUTCFullYear()-b.getUTCFullYear();if(n.getUTCMonth()<b.getUTCMonth()||(n.getUTCMonth()===b.getUTCMonth()&&n.getUTCDate()<b.getUTCDate()))a--;return a;};
const longDate=iso=>new Date(iso+"T12:00:00Z").toLocaleDateString("en-GB",{day:"numeric",month:"long",year:"numeric",timeZone:"UTC"});
const flagOf=(iso,cls="")=>iso&&FLAGS[iso.toUpperCase()]?`<img class="flg ${cls}" src="${FLAGS[iso.toUpperCase()]}" alt="" width="20" height="15">`:"";
const TEAMNAT={"McLaren":["GB","United Kingdom"],"Mercedes":["DE","Germany"],"Red Bull Racing":["AT","Austria"],"Ferrari":["IT","Italy"],"Williams":["GB","United Kingdom"],"Racing Bulls":["IT","Italy"],"Aston Martin":["GB","United Kingdom"],"Haas F1 Team":["US","United States"],"Audi":["DE","Germany"],"Alpine":["FR","France"],"Cadillac":["US","United States"]};
const ord=n=>n+(["th","st","nd","rd"][(n%100-20)%10]||["th","st","nd","rd"][n%100]||"th");
const lastRound=done.length;
function stats26(name){const k=norm(sur(name));const o={starts:0,wins:0,pod:0,poles:0,fl:0,dnf:0,best:null,swins:0,res:[]};
  RACES.filter(r=>r.res).forEach(r=>{const S=SEASON[r.r]||{};const row=(S.race||[]).find(x=>norm(x[2])===k);
    const q=(S.quali||[]).find(x=>norm(x[2])===k);if(q&&q[0]==="1")o.poles++;
    const sp=(S.sprint||[]).find(x=>norm(x[2])===k);if(sp&&sp[0]==="1")o.swins++;
    if(r.res.fl&&norm(sur(r.res.fl[0]))===k)o.fl++;
    if(!row){o.res.push({r:r.r,t:"—",c:"dn",tip:"Did not take part"});return;}
    const st=row[4];if(st!=="DNS")o.starts++;
    const p=+row[0];let c="",t;
    if(p){t="P"+p;if(p===1)o.wins++;if(p<=3)o.pod++;o.best=o.best?Math.min(o.best,p):p;c=p<=3?"p"+p:row[5]>0?"pt":"";}
    else{t=st==="DNS"?"DNS":st==="DSQ"?"DSQ":"Ret";c=st==="DNS"?"dn":"rt";if(st==="DNF")o.dnf++;}
    o.res.push({r:r.r,t,c,tip:`R${r.r} ${r.short}: ${t}${row[5]?` · ${row[5]} pts`:""}`});});
  return o;}
function teamStats26(team){const o={wins:0,pod:0,poles:0,onetwo:0,best:null};
  RACES.filter(r=>r.res).forEach(r=>{const S=SEASON[r.r]||{};const mine=(S.race||[]).filter(x=>teamAt(x[2],r.r)===team);
    const ps=mine.map(x=>+x[0]).filter(Boolean);ps.forEach(p=>{if(p===1)o.wins++;if(p<=3)o.pod++;o.best=o.best?Math.min(o.best,p):p;});
    if(ps.includes(1)&&ps.includes(2))o.onetwo++;
    const q=(S.quali||[])[0];if(q&&teamAt(q[2],r.r)===team)o.poles++;});
  return o;}
const pimg=(code3,alt)=>PORTRAIT[code3]?`<img src="${PORTRAIT[code3]}" alt="${esc(alt)}" loading="lazy">`:"";
let driverSort="team";try{driverSort=localStorage.getItem("ta-dsort")||"team";}catch(e){}
function driverCard(d){const b=bioOf(d[0]),i=DRIVERS.indexOf(d),[fn,ln]=nameParts(d[0]);
  return `<a class="dcard" href="${H("driver-"+b.code)}" data-driver="${b.code}" style="--tc:${tcol(d[2])}" aria-label="${esc(d[0])}, ${esc(d[2])}">
    <div class="ph">${pimg(b.code,d[0])}</div><span class="num">${b.num}</span><span class="pos">P${i+1}</span>
    <div class="bd"><span class="toprow"><span class="fn">${esc(fn)}</span><span class="ctry">${esc(b.country)}${flagOf(b.iso2,"big")}</span></span><span class="ln">${esc(ln)}</span>
    <span class="tmn"><span>${esc(d[2].replace(" F1 Team",""))}</span><b>${d[3]} pts</b></span></div></a>`;}
function viewDrivers(){
  let list=[...grid26];
  if(driverSort==="team"){const ord=CONSTRUCTORS.map(c=>c[0]);list.sort((a,b)=>ord.indexOf(a[2])-ord.indexOf(b[2])||DRIVERS.indexOf(a)-DRIVERS.indexOf(b));}
  else if(driverSort==="num")list.sort((a,b)=>bioOf(a[0]).num-bioOf(b[0]).num);
  return `<div class="pagehead"><div><span class="lbl">2026 Formula 1 World Championship</span><h2 class="h1">Drivers</h2>
    <p>The ${grid26.length} drivers on the 2026 grid. Select a driver for their profile, 2026 season and career record.</p></div>
    <div class="dsort" role="group" aria-label="Sort drivers"><button data-dsort="team" aria-pressed="${driverSort==="team"}">By team</button><button data-dsort="pos" aria-pressed="${driverSort==="pos"}">By standings</button><button data-dsort="num" aria-pressed="${driverSort==="num"}">By number</button></div></div>
  <div class="dcards">${list.map(driverCard).join("")}</div>
  ${extras26.length?`<p class="mnote" style="margin-top:14px">Also raced in 2026: ${extras26.map(d=>`${esc(d[0])} (${esc(d[2])}, ${d[3]} pt${d[3]===1?"":"s"})`).join(", ")}.</p>`:""}`;}
function teamCard(c,i){const [team,pts]=c,tb=TEAMBIO[team]||{},ds=grid26.filter(d=>d[2]===team);
  return `<a class="tcard" href="${H("team-"+(tb.key||""))}" data-team="${esc(team)}" style="--tc:${tcol(team)}"><div class="tbar"></div>
   <div class="th"><div><span class="lbl">P${i+1} · Constructors</span><h3>${esc(tb.name||team)}</h3></div><div class="ps">${pts}<small>PTS</small></div></div>
   <div class="ent"><span>${esc(tb.entry||"")}</span>${TEAMNAT[team]?`<span class="ctry">${TEAMNAT[team][1]}${flagOf(TEAMNAT[team][0],"big")}</span>`:""}</div>
   <div class="duo">${ds.map(d=>{const b=bioOf(d[0]);return `<div>${pimg(b.code,d[0])}<span>${esc(nameParts(d[0])[0])}<b>${esc(sur(d[0]))}</b></span></div>`;}).join("")}</div>
   <div class="tf"><div><span class="lbl">Chassis</span><b>${esc(tb.chassis||"—")}</b></div><div><span class="lbl">Power unit</span><b>${esc(tb.power||"—")}</b></div><div><span class="lbl">Titles</span><b>${tb.constructors_titles??"—"}</b></div></div></a>`;}
function viewTeams(){return `<div class="pagehead"><div><span class="lbl">2026 Formula 1 World Championship</span><h2 class="h1">Teams</h2>
  <p>All ${CONSTRUCTORS.length} constructors, in championship order. Select a team for its profile, line-up and record.</p></div></div>
  <div class="tcards">${CONSTRUCTORS.map(teamCard).join("")}</div>`;}
const num=v=>v==null?"—":Number.isInteger(v)?v.toLocaleString("en-GB"):v.toLocaleString("en-GB",{maximumFractionDigits:1});
function modalShell(base,inner,tc,pv,nx){
  $("#drawer-root").innerHTML=`<div class="scrim" data-mclose="${base}"></div>
  <div class="modal" role="dialog" aria-modal="true" style="--tc:${tc}">
   <div class="mtop">${pv}<button class="navbtn" data-mclose="${base}" id="mclose">Close ✕</button>${nx}</div>${inner}</div>`;
  const m=$(".modal");if(m){m.scrollTop=0;$("#mclose").focus({preventScroll:true});}}
function openDriver(code3){const b=BIO[code3];if(!b)return;
  const d=DRIVERS.find(x=>bioOf(x[0])===b);const team=d?d[2]:"",pos=d?DRIVERS.indexOf(d)+1:null,pts=d?d[3]:0;
  const s=stats26(d?d[0]:b.name);const order=Array.from(document.querySelectorAll(".dcard[data-driver]")).map(x=>x.dataset.driver);
  const seq=order.length?order:grid26.map(x=>bioOf(x[0]).code);const i=seq.indexOf(code3);
  const nb=c=>{const x=BIO[c];return x?esc(x.last):"";};
  const pv=i>0?`<button class="navbtn" data-driver="${seq[i-1]}">← ${nb(seq[i-1])}</button>`:`<span></span>`;
  const nx=i>=0&&i<seq.length-1?`<button class="navbtn" data-driver="${seq[i+1]}">${nb(seq[i+1])} →</button>`:`<span></span>`;
  const [fn,ln]=d?nameParts(d[0]):[b.first,b.last];
  const car=k=>(b[k]||0)+(k==="starts"?s.starts:k==="wins"?s.wins:k==="podiums"?s.pod:k==="poles"?s.poles:k==="fastest_laps"?s.fl:k==="points"?pts:0);
  const tb=TEAMBIO[team]||{};
  const inner=`<div class="mhero"><div class="ph">${pimg(code3,b.name)}</div>
   <div class="tx"><span class="bign">${b.num}</span><span class="lbl">${flagOf(b.iso2)} ${esc(b.nationality)} · #${b.num} · ${esc(code3)}</span>
    <h2><small>${esc(b.first)}</small>${esc(b.last)}</h2>
    <div>${team?`<button class="tlink" data-team="${esc(team)}">${esc(tb.name||team)}</button>`:""}${pos?` · P${pos} in 2026 with ${pts} pts`:""}</div></div></div>
  <div class="mb">
   <div><div class="mh"><h3>Profile</h3></div><div class="facts">
    <div><span class="lbl">Age</span><b>${ageOf(b.dob)}</b></div>
    <div><span class="lbl">Birthday</span><b>${longDate(b.dob)}</b></div>
    <div><span class="lbl">Birthplace</span><b>${esc(b.birthplace)}</b></div>
    <div><span class="lbl">Country</span><b>${flagOf(b.iso2)} ${esc(b.country)}</b></div>
    <div><span class="lbl">Height</span><b>${b.height_cm?`${b.height_cm} cm · ${Math.floor(b.height_cm/30.48)}′${Math.round(b.height_cm/2.54%12)}″`:"—"}</b></div>
    <div><span class="lbl">F1 debut</span><b>${esc(b.debut)}</b></div>
    <div><span class="lbl">World titles</span><b>${b.titles?`${b.titles} (${b.title_years.join(", ")})`:"—"}</b></div>
    <div><span class="lbl">Best championship</span><b>${esc(b.best_champ||"—")}</b></div></div></div>
   <div><div class="mh"><h3>2026 season</h3><span class="lbl">After round ${lastRound}</span></div>
    <div class="facts big">
     <div><span class="lbl">Position</span><b>${pos?ord(pos):"—"}</b></div><div><span class="lbl">Points</span><b>${pts}</b></div>
     <div><span class="lbl">Wins</span><b>${s.wins}</b></div><div><span class="lbl">Podiums</span><b>${s.pod}</b></div>
     <div><span class="lbl">Poles</span><b>${s.poles}</b></div><div><span class="lbl">Best finish</span><b>${s.best?"P"+s.best:"—"}</b></div>
     <div><span class="lbl">Fastest laps</span><b>${s.fl}</b></div><div><span class="lbl">Sprint wins</span><b>${s.swins}</b></div>
     <div><span class="lbl">Starts</span><b>${s.starts}</b></div><div><span class="lbl">Retirements</span><b>${s.dnf}</b></div></div>
    <div class="lbl" style="margin:12px 0 6px">Race by race</div>
    <div class="rstrip">${s.res.map(x=>`<span class="${x.c}" title="${esc(x.tip)}"><i>R${x.r}</i>${x.t}</span>`).join("")}</div></div>
   <div><div class="mh"><h3>Career</h3><span class="lbl">All seasons to R${lastRound} 2026</span></div>
    <div class="facts big">
     <div><span class="lbl">Starts</span><b>${num(car("starts"))}</b></div><div><span class="lbl">Wins</span><b>${num(car("wins"))}</b></div>
     <div><span class="lbl">Podiums</span><b>${num(car("podiums"))}</b></div><div><span class="lbl">Poles</span><b>${num(car("poles"))}</b></div>
     <div><span class="lbl">Fastest laps</span><b>${num(car("fastest_laps"))}</b></div><div><span class="lbl">Points</span><b>${num(car("points"))}</b></div>
     <div><span class="lbl">Titles</span><b>${b.titles}</b></div></div></div>
   <div><div class="mh"><h3>F1 teams</h3></div><ul class="tline">${b.f1_teams.map(t=>`<li><span>${esc(t.years)}</span><b>${esc(t.team)}</b></li>`).join("")}</ul></div>
   ${b.junior?`<div><div class="mh"><h3>Before F1</h3></div><p style="margin:0;color:var(--ink-2)">${esc(b.junior)}</p></div>`:""}
   ${b.highlights&&b.highlights.length?`<div><div class="mh"><h3>Accomplishments</h3></div><ul class="hl">${b.highlights.map(h=>`<li>${esc(h)}</li>`).join("")}</ul></div>`:""}
   <p class="mnote">Career totals combine records to the end of 2025 with 2026 results on this site. Heights are as published by the press and may vary.</p>
  </div>`;
  const base=pageBase();modalShell(base,inner,tcol(team),pv,nx);if(base!=="season")setKey("driver-"+code3);
  NAVD=true;document.title=pageTitle("driver-"+code3);}
function openTeam(team){const tb=TEAMBIO[team];if(!tb)return;
  const ci=CONSTRUCTORS.findIndex(c=>c[0]===team),pts=ci>=0?CONSTRUCTORS[ci][1]:0,s=teamStats26(team);
  const seq=CONSTRUCTORS.map(c=>c[0]),i=seq.indexOf(team);
  const pv=i>0?`<button class="navbtn" data-team="${esc(seq[i-1])}">← ${esc((TEAMBIO[seq[i-1]]||{}).name||seq[i-1])}</button>`:`<span></span>`;
  const nx=i<seq.length-1?`<button class="navbtn" data-team="${esc(seq[i+1])}">${esc((TEAMBIO[seq[i+1]]||{}).name||seq[i+1])} →</button>`:`<span></span>`;
  const ds=grid26.filter(d=>d[2]===team);
  const inner=`<div class="mhero"><div class="tcrest"><b><small>2026 car</small>${esc(tb.chassis)}</b></div>
   <div class="tx"><span class="lbl">P${ci+1} in 2026 · ${pts} pts</span><h2><small>${esc(tb.entry)}</small>${esc(tb.name)}</h2>
    <div style="color:var(--ink-2)">${TEAMNAT[team]?`<span class="ctry2">${flagOf(TEAMNAT[team][0],"big")}${TEAMNAT[team][1]}</span> · `:""}${esc(tb.base)}</div></div></div>
  <div class="mb">
   <div><div class="mh"><h3>2026 line-up</h3></div><div class="tduo">${ds.map(d=>{const b=bioOf(d[0]);return `<button data-driver="${b.code}">${pimg(b.code,d[0])}<span><small>#${b.num} · P${DRIVERS.indexOf(d)+1} · ${d[3]} pts</small><b>${esc(d[0])}</b></span></button>`;}).join("")}</div></div>
   <div><div class="mh"><h3>Team profile</h3></div><div class="facts">
    ${TEAMNAT[team]?`<div><span class="lbl">Nationality</span><b>${flagOf(TEAMNAT[team][0])} ${TEAMNAT[team][1]}</b></div>`:""}<div><span class="lbl">Team principal</span><b>${esc(tb.principal)}</b></div>
    <div><span class="lbl">Base</span><b>${esc(tb.base)}</b></div>
    <div><span class="lbl">2026 chassis</span><b>${esc(tb.chassis)}</b></div>
    <div><span class="lbl">Power unit</span><b>${esc(tb.power)}</b></div>
    <div><span class="lbl">First entry</span><b>${esc(tb.first_entry)}</b></div>
    <div><span class="lbl">Founded</span><b>${esc(tb.founded)}</b></div>
    <div><span class="lbl">Founder</span><b>${esc(tb.founder)}</b></div>
    <div><span class="lbl">Constructors' titles</span><b>${tb.constructors_titles?`${tb.constructors_titles}`:"—"}</b></div>
    <div><span class="lbl">Drivers' titles</span><b>${tb.drivers_titles||"—"}</b></div></div>
    ${tb.constructors_years&&tb.constructors_years.length?`<p class="mnote" style="margin-top:8px">Constructors' titles: ${tb.constructors_years.join(", ")}</p>`:""}</div>
   <div><div class="mh"><h3>2026 season</h3><span class="lbl">After round ${lastRound}</span></div><div class="facts big">
    <div><span class="lbl">Position</span><b>${ord(ci+1)}</b></div><div><span class="lbl">Points</span><b>${pts}</b></div>
    <div><span class="lbl">Wins</span><b>${s.wins}</b></div><div><span class="lbl">Podiums</span><b>${s.pod}</b></div>
    <div><span class="lbl">Poles</span><b>${s.poles}</b></div><div><span class="lbl">1–2 finishes</span><b>${s.onetwo}</b></div>
    <div><span class="lbl">Best finish</span><b>${s.best?"P"+s.best:"—"}</b></div></div></div>
   <div><div class="mh"><h3>All-time record</h3><span class="lbl">To R${lastRound} 2026</span></div><div class="facts big">
    <div><span class="lbl">Race starts</span><b>${num((tb.starts||0)+lastRound)}</b></div>
    <div><span class="lbl">Wins</span><b>${num((tb.wins||0)+s.wins)}</b></div>
    <div><span class="lbl">Podiums</span><b>${tb.podiums==null?"—":num(tb.podiums+s.pod)}</b></div>
    <div><span class="lbl">Poles</span><b>${num((tb.poles||0)+s.poles)}</b></div></div>
    <p class="mnote" style="margin-top:8px">${esc(tb.stats_basis||"")}, plus 2026. Podiums count each car that finished in the top three.</p></div>
   <div><div class="mh"><h3>History</h3></div><p style="margin:0;color:var(--ink-2)">${esc(tb.history)}</p></div>
   <div><div class="mh"><h3>Accomplishments</h3></div><ul class="hl">${tb.highlights.map(h=>`<li>${esc(h)}</li>`).join("")}</ul></div>
  </div>`;
  const base=pageBase();modalShell(base,inner,tcol(team),pv,nx);if(base!=="season")setKey("team-"+tb.key);
  NAVD=true;document.title=pageTitle("team-"+tb.key);}
const pageBase=()=>$(".home")?"season":$(".tcards")?"teams":"drivers";
const teamByKey=k=>Object.keys(TEAMBIO).find(t=>TEAMBIO[t].key===k);
const closeModal=base=>{if(!$(".modal"))return false;closeDrawer();if(base)setKey(base);NAVD=true;document.title=base==="season"?"Track Almanac · Races. Drivers. Teams. Numbers.":(base==="teams"?"2026 Teams":"2026 Drivers")+" · Track Almanac";return true;};

const SITE={name:"Track Almanac",domain:"trackalmanac.com",email:"contact@trackalmanac.com",updated:"8 October 2026"};
const PAGES={
about:{t:"About Track Almanac",b:`
<p class="lead">Track Almanac is an independent, fan-made reference for Formula 1. Our tagline says what we care about: races, drivers, teams and numbers.</p>
<h3>What you'll find here</h3>
<ul><li><b>The current season at a glance.</b> A calendar on a real date scale, a countdown to the next race and every session shown in your own time zone and in local track time.</li>
<li><b>Standings after every round.</b> Drivers' and constructors' tables, plus a full points breakdown in the style of a championship results grid.</li>
<li><b>Every race in detail.</b> Practice, sprint qualifying, sprint, qualifying, the starting grid with penalties explained, the complete classification, fastest lap and a lap-by-lap chart you can animate.</li>
<li><b>Circuit maps.</b> Drawn from car telemetry, with sectors, turn numbers, straight mode zones, overtake points and the speed trap.</li>
<li><b>An archive.</b> Summaries of past seasons, which we are expanding into full race-by-race records.</li></ul>
<h3>Where the data comes from</h3>
<p>Results, grids and session times are compiled from official published classifications and timing, cross-checked against independent sources: the Jolpica F1 API, <a href="https://openf1.org" target="_blank" rel="noopener">OpenF1</a> (openf1.org) for practice classifications, lap timing and race control, and <a href="https://github.com/TracingInsights" target="_blank" rel="noopener">TracingInsights</a> for per-lap tyre data from the official timing feed (Apache-2.0). Every driver's points total is reconciled against the official championship standings before publication. Tyre compound selections and weekend forecasts come from published team and supplier previews. Lap-by-lap positions and circuit maps come from <a href="https://github.com/TracingInsights" target="_blank" rel="noopener">TracingInsights</a> telemetry and timing data (Apache-2.0), with lap positions for new races from <a href="https://openf1.org" target="_blank" rel="noopener">OpenF1</a>. Past seasons in the archive come from <a href="https://github.com/f1db/f1db" target="_blank" rel="noopener">F1DB</a> (CC BY 4.0).</p>
<h3>Accuracy and corrections</h3>
<p>We work hard to get the numbers right, but mistakes happen and results can change after stewards' decisions. If you spot an error, please <a href="${H("contact")}" data-go="contact">tell us</a> and we will correct it.</p>
<h3>Independence</h3>
<p>Track Almanac is not affiliated with, endorsed by or connected to Formula 1, the FIA, Formula One Management or any team. See our <a href="${H("disclaimer")}" data-go="disclaimer">disclaimer</a> for details.</p>`},
privacy:{t:"Privacy Policy",b:`
<p class="meta">Last updated: 18 October 2026</p>
<p>This policy explains what information ${SITE.name} ("we", "us") collects when you visit ${SITE.domain} (the "Site"), how it is used and the choices you have.</p>
<h3>1. Information we collect</h3>
<ul><li><b>Information you give us.</b> If you email us, we receive your email address and whatever you include in your message. We use it only to reply.</li>
<li><b>Preferences stored on your device.</b> The Site saves small settings in your browser's local storage, such as your 12/24-hour clock choice, kilometres or miles, light or dark theme, race card order and cookie choice. These stay on your device and are not sent to us.</li>
<li><b>Automatically collected information.</b> Like most websites, our hosting provider and any analytics or advertising partners may receive standard technical data such as IP address, browser type, device type, pages viewed and referring page.</li></ul>
<h3>2. Cookies and advertising</h3>
<p>We may use third-party advertising, including Google AdSense, to keep the Site free. Third-party vendors, including Google, use cookies to serve ads based on your prior visits to this Site or other websites.</p>
<ul><li>Google's use of advertising cookies enables it and its partners to serve ads to you based on your visits to this Site and/or other sites on the internet.</li>
<li>You may opt out of personalised advertising by visiting <a href="https://adssettings.google.com" target="_blank" rel="noopener">Google Ads Settings</a>. You can also opt out of some third-party vendors' use of cookies for personalised advertising at <a href="https://www.aboutads.info/choices/" target="_blank" rel="noopener">www.aboutads.info</a>.</li>
<li>To learn how Google uses information from sites that use its services, see <a href="https://policies.google.com/technologies/partner-sites" target="_blank" rel="noopener">How Google uses information from sites or apps that use our services</a>.</li></ul>
<p>Where required by law, including in the European Economic Area, the United Kingdom and Switzerland, we ask for your consent before non-essential cookies are used. You can change your choice at any time with the <b>Cookie settings</b> link in the footer.</p>
<h3>3. Analytics</h3>
<p>We use <b>Google Analytics 4</b>, a service provided by Google, to count visits and see which pages are popular, so we know what to improve.</p>
<ul><li><b>What it collects.</b> The pages you view and their titles, the site that referred you, approximate location (country and city, worked out from your IP address; Google Analytics 4 does not store IP addresses), device type, browser, operating system, screen size and language, and basic interactions such as scrolling, time on page and clicks on links to other sites. It does not collect your name or email address.</li>
<li><b>Cookies.</b> Google Analytics uses first-party cookies (<span class="mono">_ga</span> and <span class="mono">_ga_*</span>) to tell visits apart. They can last up to two years.</li>
<li><b>Consent.</b> In the European Economic Area, the United Kingdom and Switzerland, analytics cookies are only set if you choose <b>Accept all</b>. Until then, or if you choose <b>Essential only</b>, no analytics cookies are stored; Google may receive limited signals without cookies or identifiers (for example, that a page was viewed), which it uses only in aggregate. Elsewhere, analytics cookies are used by default and you can turn them off by choosing <b>Essential only</b>.</li>
<li><b>Changing your choice.</b> Use the <b>Cookie settings</b> link in the footer of any page at any time.</li>
<li><b>More information and opting out.</b> See <a href="https://policies.google.com/privacy" target="_blank" rel="noopener">Google's Privacy Policy</a> and <a href="https://policies.google.com/technologies/partner-sites" target="_blank" rel="noopener">how Google uses information from sites that use its services</a>. You can also block Google Analytics on every website with the <a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener">Google Analytics opt-out browser add-on</a>.</li></ul>
<h3>4. How we use information</h3>
<p>To operate and improve the Site, keep it secure, show advertising that funds it, and respond to messages. We do not sell your personal information.</p>
<h3>5. Your rights</h3>
<p>Depending on where you live, you may have the right to access, correct or delete personal data we hold about you, to object to or restrict processing, and to withdraw consent. California residents may opt out of the "sale" or "sharing" of personal information for cross-context behavioural advertising. To exercise these rights, contact us at <span class="mono">${SITE.email}</span>.</p>
<h3>6. Children</h3>
<p>The Site is a general-audience sports reference and is not directed at children under 13. We do not knowingly collect personal information from children.</p>
<h3>7. Data retention and security</h3>
<p>We keep emails only as long as needed to respond and for reasonable record keeping. We use reasonable measures to protect information, but no method of transmission over the internet is completely secure.</p>
<h3>8. Changes</h3>
<p>We may update this policy. The date at the top shows when it last changed.</p>
<h3>9. Contact</h3>
<p>Questions about privacy: <span class="mono">${SITE.email}</span>.</p>`},
terms:{t:"Terms of Use",b:`
<p class="meta">Last updated: ${SITE.updated}</p>
<p>By using ${SITE.domain} you agree to these terms. If you do not agree, please do not use the Site.</p>
<h3>1. Use of the Site</h3>
<p>The Site is provided for personal, non-commercial information and entertainment. You agree not to misuse it, including by attempting to disrupt it, scraping it at a volume that degrades service, or using it for unlawful purposes.</p>
<h3>2. Content and copyright</h3>
<p>The design, text, charts, graphics, logo and arrangement of the Site are © ${new Date().getFullYear()} ${SITE.name} unless stated otherwise. Factual sports data such as results and times are not owned by us, but our compilation and presentation of it is. You may share links and quote small extracts with credit to ${SITE.name}. Please do not republish substantial parts of the Site without permission.</p>
<h3>3. Third-party material</h3>
<p>Some material is used under licence or credited to its source, such as circuit geometry from TracingInsights F1 telemetry data (Apache 2.0 licence), with historical results from F1DB (CC BY 4.0). Trademarks belong to their respective owners; see the <a href="${H("disclaimer")}" data-go="disclaimer">disclaimer</a>.</p>
<h3>4. Accuracy</h3>
<p>We aim for accuracy but provide the Site "as is" without warranties of any kind. Results can change after official decisions. Do not rely on the Site for betting or other financial decisions.</p>
<h3>5. Links and advertising</h3>
<p>The Site may contain links to other websites and display third-party advertising. We are not responsible for the content or practices of third-party sites or advertisers.</p>
<h3>6. Limitation of liability</h3>
<p>To the fullest extent permitted by law, ${SITE.name} is not liable for any indirect or consequential loss arising from use of the Site.</p>
<h3>7. Changes</h3>
<p>We may update these terms at any time. Continued use of the Site means you accept the current version.</p>
<h3>8. Contact</h3>
<p><span class="mono">${SITE.email}</span></p>`},
disclaimer:{t:"Disclaimer & Copyright",b:`
<h3>Unofficial site</h3>
<p>${SITE.name} is an unofficial fan website. It is not associated in any way with the Formula 1 companies. F1, FORMULA ONE, FORMULA 1, FIA FORMULA ONE WORLD CHAMPIONSHIP, GRAND PRIX and related marks are trademarks of Formula One Licensing B.V. Team names, driver names and other marks belong to their respective owners and are used only to identify them.</p>
<h3>No official logos or imagery</h3>
<p>We do not use official F1, team or sponsor logos, photographs or broadcast imagery. Team colours are approximations used to tell teams apart in tables and charts. Circuit maps are drawn from open car telemetry data and are not official track maps.</p>
<h3>Data sources and credits</h3>
<ul><li>Race classifications, qualifying, practice, starting grids and session times: compiled from official published results and timing.</li>
<li>Results, qualifying, sprint results, championship standings and the race schedule: Jolpica F1 API (successor to the Ergast API).</li> <li>Lap-by-lap positions: <a href="https://github.com/TracingInsights" target="_blank" rel="noopener">TracingInsights</a> timing data (Apache-2.0), and <a href="https://openf1.org" target="_blank" rel="noopener">OpenF1</a> for new races.</li> <li>Practice and sprint qualifying classifications, lap timing, safety car, virtual safety car and red flag periods, and session times: <a href="https://openf1.org" target="_blank" rel="noopener">OpenF1</a> (openf1.org).</li> <li>Tyre strategy: <a href="https://github.com/TracingInsights" target="_blank" rel="noopener">TracingInsights</a>, from the official F1 timing feed (Apache-2.0).</li>
<li>Circuit maps: drawn from <a href="https://github.com/TracingInsights" target="_blank" rel="noopener">TracingInsights</a> car telemetry (Apache-2.0).</li> <li>Past seasons (archive, 1950–2025): <a href="https://github.com/f1db/f1db" target="_blank" rel="noopener">F1DB</a>, CC BY 4.0.</li> <li>Grand Prix racing 1946–1949: the 1946–1949 Grand Prix season pages on <a href="https://en.wikipedia.org/wiki/1949_Grand_Prix_season" target="_blank" rel="noopener">Wikipedia</a>, CC BY-SA 4.0.</li> <li>Country flags: <a href="https://github.com/lipis/flag-icons" target="_blank" rel="noopener">flag-icons</a>, MIT licence.</li>
<li>Tyre compound selections and weekend forecasts: published team and supplier race previews.</li>
<li>Fonts: Big Shoulders Display, IBM Plex Sans Condensed and IBM Plex Mono via Google Fonts (SIL Open Font Licence).</li></ul>
<h3>Copyright</h3>
<p>© ${new Date().getFullYear()} ${SITE.name}. Original text, design, charts and the ${SITE.name} logo are protected by copyright. If you believe something on the Site infringes your rights, email <span class="mono">${SITE.email}</span> with details and we will review it promptly.</p>
<h3>Accuracy</h3>
<p>Information is provided for general interest and may contain errors or be superseded by official decisions. It should not be used for betting.</p>`},
contact:{t:"Contact",b:`
<p class="lead">Spotted an error, have a suggestion or want to get in touch about the site?</p>
<div class="contact-card"><span class="lbl">Email</span><b class="mono" id="cmail">${SITE.email}</b><button class="navbtn" data-copy="${SITE.email}">Copy address</button></div>
<p>For corrections, please include the round, the session and what you think is wrong. We usually reply within a few days.</p>
<p>For privacy requests, see our <a href="${H("privacy")}" data-go="privacy">Privacy Policy</a>.</p>`},
sitemap:{t:"Site map",b:`
<ul class="smap">
<li><a href="${H("season")}" data-go="season">2026 Season</a> · calendar, next race, standings, race cards</li>
<li><a href="${H("championship")}" data-go="championship">2026 Championship</a> · points progression, results grids, statistics</li>
<li><a href="${H("drivers")}" data-go="drivers">2026 Drivers</a> · ${grid26.map(d=>`<a href="${H("driver-"+bioOf(d[0]).code)}">${esc(sur(d[0]))}</a>`).join(" · ")}</li>
<li><a href="${H("teams")}" data-go="teams">2026 Teams</a> · ${CONSTRUCTORS.map(c=>`<a href="${H("team-"+TEAMBIO[c[0]].key)}">${esc(TEAMBIO[c[0]].name)}</a>`).join(" · ")}</li>
<li>Races: ${RACES.filter(r=>r.res).map(r=>`<a href="${H("detail-"+r.r)}" data-detail="${r.r}">R${r.r} ${esc(r.short.replace(" (Sepang)",""))}</a>`).join(" · ")}</li>
<li><a href="${H("archive")}" data-go="archive">Archive</a>: ${Object.keys(ARCHIVE).sort((a,b)=>b-a).map(y=>`<a href="${H("archive-"+y)}" data-year="${y}">${y}</a>`).join(" · ")}</li>
<li><a href="${H("about")}" data-go="about">About</a> · <a href="${H("contact")}" data-go="contact">Contact</a> · <a href="${H("privacy")}" data-go="privacy">Privacy</a> · <a href="${H("terms")}" data-go="terms">Terms</a> · <a href="${H("disclaimer")}" data-go="disclaimer">Disclaimer &amp; copyright</a></li></ul>`}
};
function viewPage(k){const p=PAGES[k];return `<article class="doc"><span class="lbl">${SITE.name}</span><h1>${p.t}</h1>${p.b}</article>`;}
/* cookie consent (replace with a Google-certified CMP when AdSense is live in EEA/UK) */
function consentBanner(force){let c=null;try{c=localStorage.getItem("ta-consent");}catch(e){}
  if(c&&!force)return;const d=document.createElement("div");d.className="consent";d.setAttribute("role","dialog");d.setAttribute("aria-label","Cookie choices");
  d.innerHTML=`<p>We use cookies for essential features and, with your consent, for advertising and analytics. See our <a href="${H("privacy")}" data-go="privacy">Privacy Policy</a>.</p><div><button class="navbtn" data-consent="reject">Essential only</button><button class="navbtn sig" data-consent="accept">Accept all</button></div>`;
  document.querySelectorAll(".consent").forEach(x=>x.remove());document.body.appendChild(d);}


/* ---------- ROUTER ---------- */
let t=null;
function setNav(k){["season","championship","drivers","teams","archive"].forEach(x=>{const b=$("#n-"+x);if(x===k)b.setAttribute("aria-current","page");else b.removeAttribute("aria-current");});}
/* the race bar and section tabs stay pinned: the tabs sit just under the bar */
function pinSizes(){const p=$(".dnav.pin"),j=$(".jump"),R=document.documentElement.style;R.setProperty("--pinh",(p?p.offsetHeight:0)+"px");R.setProperty("--jumph",(j?j.offsetHeight:0)+"px");}
window.addEventListener("resize",()=>pinSizes());
function route(){const _yr=$(".yrail"),yrX=_yr?_yr.scrollLeft:null;document.body.classList.remove("fs-lock");document.title="Track Almanac · Races. Drivers. Teams. Numbers.";
  document.querySelectorAll("[data-clock]").forEach(b=>b.setAttribute("aria-pressed",b.dataset.clock===CLOCK));
  document.querySelectorAll("[data-unit]").forEach(b=>b.setAttribute("aria-pressed",b.dataset.unit===UNIT));
  document.querySelectorAll("[data-theme-set]").forEach(b=>b.setAttribute("aria-pressed",b.dataset.themeSet===THEME));
  clearInterval(t); closeDrawer();
  const h=curKey();
  if(h==="calendar"){$("#app").innerHTML=viewCalendar();$("#sheetname").textContent="2026 CALENDAR";setNav("");document.title="2026 F1 Calendar · Track Almanac";}
  else if(h==="notfound"){$("#app").innerHTML=viewNotFound();$("#sheetname").textContent="NOT FOUND";setNav("");}
  else if(PAGES[h]){$("#app").innerHTML=viewPage(h);$("#sheetname").textContent=PAGES[h].t.toUpperCase();setNav("");document.title=PAGES[h].t+" · Track Almanac";}
  else if(h==="archive-1946-1949"){$("#app").innerHTML=viewPrewar();centreYrail(yrX);$("#sheetname").textContent="SEASON ARCHIVE";setNav("archive");}
  else if(h.startsWith("archive")){const y=+h.split("-")[1];const ay=ARCHIVE[y]?y:2025;$("#app").innerHTML=viewArchive(ARCHIVE[y]?y:null);drawArchCharts(ay);centreYrail(yrX);if((ARCHIVE[ay]||{}).next)initRoute();
    if(ARCHV[ay]&&!ARCHDATA[ay])loadSeason(ay).then(()=>{if(curKey()===h){const r=$(".yrail"),x=r?r.scrollLeft:null;$("#app").innerHTML=viewArchive(ARCHIVE[y]?y:null);drawArchCharts(ay);const r2=$(".yrail");if(r2&&x!=null)r2.scrollLeft=x;}});$("#sheetname").textContent="SEASON ARCHIVE";setNav("archive");}
  else if(h==="drivers"||h.startsWith("driver-")){$("#app").innerHTML=viewDrivers();$("#sheetname").textContent="2026 DRIVERS";setNav("drivers");document.title="2026 Drivers · Track Almanac";if(h.startsWith("driver-"))openDriver(h.slice(7));}
  else if(h==="teams"||h.startsWith("team-")){$("#app").innerHTML=viewTeams();$("#sheetname").textContent="2026 TEAMS";setNav("teams");document.title="2026 Teams · Track Almanac";if(h.startsWith("team-")){const k=teamByKey(h.slice(5));if(k)openTeam(k);}}
  else if(h==="championship"){$("#app").innerHTML=viewChampionship();drawCharts();$("#sheetname").textContent="2026 CHAMPIONSHIP · POINTS";setNav("championship");}
  else if(h.startsWith("detail-")){const [nn,jk]=h.slice(7).split("-");const n=+nn;lapSel=new Set();$("#app").innerHTML=viewDetail(n);drawLapChart();if(jk)jumpTo(jk);const r=RACES.find(x=>x.r===n);$("#sheetname").textContent=r?`R${n} · ${r.gp.toUpperCase()}`:"";setNav("season");}
  else{$("#app").innerHTML=viewSeason();tower("d");countdown();$("#sheetname").textContent="2026 WORLD CHAMPIONSHIP";setNav("season");
    if(h.startsWith("race-"))openRace(+h.slice(5));}
  {const app=$("#app"),t1=h1Text(h);if(t1&&!app.querySelector("h1"))app.insertAdjacentHTML("afterbegin",`<h1 class="sr">${esc(t1)}</h1>`);}
  if(PATHMODE&&NAVD){document.title=pageTitle(h);const c=document.querySelector('link[rel="canonical"]');if(c)c.href=location.origin+location.pathname;}
  /* GA4: the first load is counted by gtag config; count in-app page changes once the new title is set, only when the address changed */
  if(PATHMODE&&window.TA_GA&&window.gtag){const pv=location.pathname+location.search;if(pv!==window.TA_GA_FIRST){window.TA_GA_FIRST=pv;gtag("event","page_view",{page_location:location.href,page_title:document.title});}}
  pinSizes();
  if(!(PATHMODE&&location.hash&&/^detail-/.test(h)))window.scrollTo(0,0);
}
function cdParts(ms,sm){let s=Math.max(0,Math.floor(ms/1000));const v=[Math.floor(s/86400),Math.floor(s%86400/3600),Math.floor(s%3600/60),s%60];
  return v.map((n,i)=>(sm&&i===0&&!n)?"":`<b>${String(n).padStart(2,"0")}</b><i>${["d","h","m","s"][i]}</i>`).join("");}
function countdown(){const box=$("#cdx");if(!box)return;const S=SCHED[nextRace.r]?SCHED[nextRace.r][1]:[["Grand Prix",nextRace.start,0]];
  const lab=n=>n==="Grand Prix"?"Race":n;
  const tick=()=>{const now=Date.now(),end=x=>Date.parse(x[1])+(x[2]||120)*60000;
    const live=S.find(x=>now>=Date.parse(x[1])&&now<end(x)),nxt=S.find(x=>Date.parse(x[1])>now),gp=S.find(x=>x[0]==="Grand Prix")||S[S.length-1];
    let h="";
    if(live)h+=`<div class="cdrow live"><span class="lbl"><span class="pulse"></span>Live now</span><b class="cdname">${esc(lab(live[0]))}</b><span class="when">Ends about ${tfmt(new Date(end(live)).toISOString(),null,{hour:"2-digit",minute:"2-digit"})} your time</span></div>`;
    if(nxt&&nxt[0]!=="Grand Prix")h+=`<div class="cdrow ses"><span class="lbl">Next session in</span><b class="cdname">${esc(lab(nxt[0]))}</b><div class="cd">${cdParts(Date.parse(nxt[1])-now,true)}</div><span class="when">${tfmt(nxt[1],null)} your time</span></div>`;
    if(now<Date.parse(gp[1]))h+=`<div class="cdrow gp"><span class="lbl">Lights out in</span><div class="cd">${cdParts(Date.parse(gp[1])-now)}</div><span class="when">${tfmt(gp[1],null)} your time</span></div>`;
    else if(!live)h+=`<div class="cdrow gp"><span class="lbl">Grand Prix</span><b class="cdname">Chequered flag</b><span class="when">Results will appear here shortly.</span></div>`;
    box.innerHTML=h;
    document.querySelectorAll(".nxs .nr[data-t]").forEach(r=>{const a=+r.dataset.t,e=a+(+r.dataset.d)*60000;r.classList.toggle("past",now>=e);r.classList.toggle("live",now>=a&&now<e);r.classList.toggle("nextup",!!nxt&&!live&&a===Date.parse(nxt[1]));});};
  tick();t=setInterval(tick,1000);}
document.addEventListener("click",e=>{
  {const A=e.target.closest("a[data-go],a[data-detail],a[data-year],a[data-driver],a[data-team]");if(A){if(e.ctrlKey||e.metaKey||e.shiftKey||e.altKey||e.button>0)return;e.preventDefault();}}
  const mm=$(".moremenu");if(mm&&!mm.hidden&&!e.target.closest(".more")){mm.hidden=true;$(".morebtn").setAttribute("aria-expanded","false");}
  if(e.target.closest("[data-more]")){const open=mm.hidden;mm.hidden=!open;$(".morebtn").setAttribute("aria-expanded",String(open));return;}
  if(e.target.closest(".moremenu")){mm.hidden=true;$(".morebtn").setAttribute("aria-expanded","false");}
  const sv=e.target.closest("[data-sess]");if(sv&&!e.target.closest("[data-detail],[data-quick]")){const [sn,sk]=sv.dataset.sess.split(":");const tgt="detail-"+sn+"-"+sk;if(curKey()===tgt)route();else go(tgt);return;}
  if(RT){const rp=e.target.closest("[data-rplay]");if(rp){RT.playing?RT.pause():RT.play();return;}
    if(e.target.closest("[data-rreset]")){RT.reset();return;}
    const rz=e.target.closest("[data-rzoom]");if(rz){RT.pause();RT.zoom(rz.dataset.rzoom);return;}
    const rs=e.target.closest("[data-rstop],[data-rpin]");if(rs){const i=+(rs.dataset.rstop??rs.dataset.rpin);RT.pause();if(RT.phase==="fly"||RT.phase==="idle")RT.phase="dwell";RT.leg=-1;$("#rplane").style.display="none";RT.select(i);RT.trails();RT.setBtn();RT.show(i);return;}}
  const dc=e.target.closest("[data-dec]");if(dc){scrollDecade(dc.dataset.dec);return;}
  const pj=e.target.closest("[data-pwj]");if(pj){const t=document.getElementById(pj.dataset.pwj);if(t)t.scrollIntoView({behavior:"smooth",block:"start"});return;}
  const sc2=e.target.closest("[data-scroll]");if(sc2){scrollHome(sc2.dataset.scroll);return;}
  if(e.target.closest("[data-lapcharts]")){go("detail-"+done[done.length-1].r+"-chart");return;}
  const mc=e.target.closest("[data-mclose]");if(mc){closeModal(mc.dataset.mclose);return;}
  const dv=e.target.closest("[data-driver]");if(dv){openDriver(dv.dataset.driver);return;}
  const tm=e.target.closest("[data-team]");if(tm){openTeam(tm.dataset.team);return;}
  const ds=e.target.closest("[data-dsort]");if(ds){driverSort=ds.dataset.dsort;try{localStorage.setItem("ta-dsort",driverSort)}catch(err){}const y=window.scrollY;$("#app").innerHTML=viewDrivers();window.scrollTo(0,y);return;}
  if(e.target.closest("[data-close]")){setKey("season");closeDrawer();return;}
  const b=e.target.closest("[data-quick],[data-detail],[data-go],[data-year],[data-fp],[data-chip],[data-jump],[data-order],[data-lap],[data-fs],[data-spd],[data-clock],[data-unit],[data-theme-set],[data-standall],[data-top],[data-consent],[data-cookies],[data-copy],[data-chipset],#t-d,#t-c");if(!b)return;
  if(b.dataset.fs){toggleFS(b.dataset.fs);return;}
  if(b.hasAttribute("data-top")){window.scrollTo({top:0,behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth"});return;}
  if(b.hasAttribute("data-standall")){const st=b.closest(".stand"),on=!st.classList.contains("all");st.classList.toggle("all",on);b.setAttribute("aria-expanded",String(on));
    b.textContent=on?"Show top 10":`Show all ${st.querySelectorAll("tbody")[0].rows.length} drivers`;return;}
  if(b.dataset.themeSet){setTheme(b.dataset.themeSet);const y=window.scrollY;route();window.scrollTo(0,y);return;}
  if(b.dataset.unit){UNIT=b.dataset.unit==="mi"?"mi":"km";try{localStorage.setItem("ta-unit",UNIT)}catch(err){}const y=window.scrollY;route();window.scrollTo(0,y);return;}
  if(b.dataset.clock){CLOCK=b.dataset.clock;try{localStorage.setItem("ta-clock",CLOCK)}catch(err){}const y=window.scrollY,open=$(".drawer")?location.hash:null;route();window.scrollTo(0,y);return;}
  if(b.dataset.consent){try{localStorage.setItem("ta-consent",b.dataset.consent)}catch(err){}if(window.taConsent)window.taConsent(b.dataset.consent);document.querySelectorAll(".consent").forEach(x=>x.remove());return;}
  if(b.dataset.cookies){consentBanner(true);return;}
  if(b.dataset.copy){const v=b.dataset.copy;try{navigator.clipboard.writeText(v).then(()=>{b.textContent="Copied";},()=>{const r=document.createRange();r.selectNodeContents($("#cmail"));getSelection().removeAllRanges();getSelection().addRange(r);});}catch(err){}return;}
  if(b.dataset.spd){ANIM_SPEED=+b.dataset.spd;document.querySelectorAll("[data-spd]").forEach(x=>x.setAttribute("aria-pressed",+x.dataset.spd===ANIM_SPEED));return;}
  if(b.dataset.order){plateOrder=b.dataset.order;try{localStorage.setItem("pa-order2",plateOrder)}catch(err){}const y=window.scrollY;route();window.scrollTo(0,y);return;}
  if(b.dataset.lap){const v=b.dataset.lap;if(v==="clear")lapSel.clear();else{const d=+v;lapSel.has(d)?lapSel.delete(d):lapSel.add(d);}applyLapSel();return;}
  if(b.dataset.chipset){const v=b.dataset.chipset;chartSel=new Set(v==="all"?DRIVERS.map(d=>d[0]):v==="top"?DRIVERS.slice(0,6).map(d=>d[0]):[]);drawCharts();return;}
  if(b.id==="t-d")return tower("d"); if(b.id==="t-c")return tower("c");
  if(b.dataset.jump){e.preventDefault();const s=$("#s-"+b.dataset.jump);if(s)s.scrollIntoView({behavior:"smooth",block:"start"});return;}
  if(b.dataset.fp){const n=parseInt(curKey().slice(7));document.querySelectorAll("[data-fp]").forEach(x=>x.setAttribute("aria-pressed",x===b));$("#fp-out").innerHTML=fpOut(n,b.dataset.fp);return;}
  if(b.dataset.chip){const k=b.dataset.chip;chartSel.has(k)?chartSel.delete(k):chartSel.add(k);drawCharts();return;}
  if(b.dataset.year){e.preventDefault();go("archive-"+b.dataset.year);return;}
  if(b.dataset.go){e.preventDefault();go(b.dataset.go);return;}
  if(b.dataset.detail){e.preventDefault();go("detail-"+b.dataset.detail);return;}
  if(b.dataset.quick){const n=+b.dataset.quick;setKey("race-"+n);if(!$(".home")){route();}else openRace(n);}
});
document.addEventListener("keydown",e=>{if(e.key==="Escape"&&$(".moremenu")&&!$(".moremenu").hidden){$(".moremenu").hidden=true;$(".morebtn").setAttribute("aria-expanded","false");$(".morebtn").focus();return;}if(e.key==="Escape"&&$(".modal")){closeModal(pageBase());return;}if((e.key==="Enter"||e.key===" ")&&e.target.matches&&e.target.matches(".tower li[role=button],[data-sess]")){e.preventDefault();e.target.click();return;}if(e.key==="Escape"&&$(".fsbox.full")){toggleFS($(".fsbox.full").id,false);return;}if((e.key==="Enter"||e.key===" ")&&e.target.matches&&e.target.matches("article[role=button]")){e.preventDefault();e.target.click();return;}if(e.key==="Escape"&&$(".drawer")){setKey("season");closeDrawer();}});
if(PATHMODE){window.addEventListener("popstate",()=>{NAVD=true;route();});window.addEventListener("hashchange",()=>{if(location.pathname==="/"&&isLegacy(location.hash.slice(1)))route();});}else window.addEventListener("hashchange",route);
route();
consentBanner();
