/* Pure recalculation: never mutates the live classifications or standings. */
function withoutAntonelli(season=SEASON,races=RACES,drivers=DRIVERS,schedule=SCHED){
  const key=s=>String(s).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const people=new Map(drivers.map(d=>[key(d[0].split(' ').pop()),{name:d[0],team:d[2],actual:0,points:0,wins:0,finishes:[],actualFinishes:[]}]));
  const person=s=>{const k=key(s);if(!people.has(k))people.set(k,{name:s,team:'',actual:0,points:0,wins:0,finishes:[],actualFinishes:[]});return people.get(k);};
  const classified=row=>/^\d+$/.test(String(row[0]))&&Number(row[0])>0;
  const gpPoints=[25,18,15,12,10,8,6,4,2,1],sprintPoints=[8,7,6,5,4,3,2,1];
  const winners=[];let gp=0,sprints=0,remaining=0,latest=null;
  for(const r of [...races].sort((a,b)=>a.r-b.r)){
    const s=season[String(r.r)]||{},hasGP=!!s.race?.length,hasSprint=!!s.sprint?.length;
    const sprintScheduled=!!r.sprint||(schedule[String(r.r)]?.[1]||[]).some(x=>x[0]==='Sprint');
    if(!hasGP)remaining+=25;if(sprintScheduled&&!hasSprint)remaining+=8;
    for(const [type,points] of [['race',gpPoints],['sprint',sprintPoints]]){
      if(!s[type]?.length)continue;
      if(type==='race'){gp++;latest=r;}else sprints++;
      const rows=s[type].filter(classified).slice().sort((a,b)=>Number(a[0])-Number(b[0]));
      const antonelli=rows.find(row=>key(row[2])==='antonelli');
      for(const row of rows){
        const p=person(row[2]),pos=Number(row[0]);p.actual+=Number(row[5])||0;
        if(type==='race')p.actualFinishes[pos]=(p.actualFinishes[pos]||0)+1;
        if(key(row[2])==='antonelli')continue;
        const promoted=pos-(antonelli&&pos>Number(antonelli[0])?1:0);
        p.points+=points[promoted-1]||0;
        if(type==='race'){p.finishes[promoted]=(p.finishes[promoted]||0)+1;if(promoted===1)p.wins++;}
      }
      if(type==='race'){
        const original=rows.find(row=>Number(row[0])===1),winner=rows.find(row=>key(row[2])!=='antonelli'&&Number(row[0])-(antonelli&&Number(row[0])>Number(antonelli[0])?1:0)===1);
        if(winner)winners.push({round:r.r,race:r.short,name:person(winner[2]).name,changed:original!==winner});
      }
    }
  }
  const compare=(a,b,actual=false)=>{
    const diff=actual?b.actual-a.actual:b.points-a.points;if(diff)return diff;
    const af=actual?a.actualFinishes:a.finishes,bf=actual?b.actualFinishes:b.finishes;
    for(let i=1;i<Math.max(af.length,bf.length);i++){const n=(bf[i]||0)-(af[i]||0);if(n)return n;}return 0;
  };
  const rank=(rows,actual=false)=>{const sorted=rows.sort((a,b)=>compare(a,b,actual)||a.name.localeCompare(b.name));let rank=1;return sorted.map((p,i)=>{if(i&&compare(sorted[i-1],p,actual))rank=i+1;return {...p,rank};});};
  const all=[...people.entries()],revised=rank(all.filter(([k])=>k!=='antonelli').map(([,p])=>p)),actual=rank([...people.values()],true);
  return {revised,actual,winners,gp,sprints,remaining,latest,compare};
}
function viewWithoutAntonelli(){return WHATIF_HTML;}
function initWithoutAntonelli(){
  const host=document.getElementById('wi-live');if(!host)return;
  const result=withoutAntonelli(),{revised,latest,remaining,winners}=result,lead=revised[0];
  const contenders=lead?revised.filter(p=>lead.points-p.points<=remaining):[];
  const transferred=winners.filter(w=>w.changed),gain=revised.reduce((best,p)=>p.points-p.actual>best.points-best.actual?p:best,revised[0]);
  const teams=CONSTRUCTORS.map(c=>({name:c[0],points:revised.filter(d=>d.team===c[0]).reduce((n,d)=>n+d.points,0)})).sort((a,b)=>b.points-a.points);
  host.innerHTML=`<p class="lbl">${latest?`After round ${latest.r} · ${esc(latest.gp)}`:'No finished Grand Prix yet'} · ${result.gp} Grands Prix + ${result.sprints} Sprints</p>
    <div class="wi-cards">${[['Scenario leader',lead?.name||'—',`${lead?.points||0} points`],['Largest gain',gain?`+${gain.points-gain.actual}`:'0',gain?.name||'—'],['Wins reassigned',transferred.length,'Grand Prix victories'],['Points remaining',remaining,`${contenders.length} drivers can catch or tie the lead`]].map(([label,value,note])=>`<div class="wi-card"><span class="lbl">${label}</span><b class="${typeof value==='string'&&!/^[+0-9]+$/.test(value)?'wi-name':''}">${esc(value)}</b><small>${esc(note)}</small></div>`).join('')}</div>
    <section class="dsec"><div class="sec"><h2>The championship rewritten</h2></div>
    <div class="wi-controls"><label>Table <select id="wi-mode"><option value="revised">Without Antonelli</option><option value="actual">Actual standings</option></select></label><label>Find a driver <input id="wi-search" type="search" placeholder="Driver name"></label><label><input id="wi-all" type="checkbox"> Full field</label></div>
    <p class="note2">Select a driver to compare points. Actual points are summed from the same completed session tables.</p>
    <div id="wi-table"></div><div id="wi-spotlight" class="wi-spotlight" aria-live="polite"></div></section>
    <section class="dsec"><div class="sec"><h2>The winners change</h2><span class="lbl">${transferred.length} inherited victories</span></div><p>Grand Prix winners in this scenario. Marked victories pass to the next classified finisher.</p><ol class="wi-wins">${winners.map(w=>`<li><small>Round ${w.round} · ${esc(w.race)}</small><b>${esc(w.name)}</b>${w.changed?'<small>Inherited victory</small>':''}</li>`).join('')}</ol></section>
    <section class="dsec"><div class="sec"><h2>The title picture</h2></div><p>${lead?`${esc(lead.name)} leads with ${lead.points} points. ${revised[1]?`${esc(revised[1].name)} is ${lead.points-revised[1].points} points behind.`:''}`:'Awaiting results.'} There are ${remaining} points still available per driver.</p><p>Within reach on points: ${contenders.map(p=>`${esc(p.name)} (${p.points}, ${p.wins} GP wins)`).join('; ')||'—'}.</p>
    <ul class="wi-next">${RACES.filter(r=>!(SEASON[r.r]?.race?.length)).map(r=>`<li>Round ${r.r} · ${esc(r.gp)} · ${esc(r.date)}</li>`).join('')||'<li>All Grands Prix completed.</li>'}</ul></section>
    <section class="dsec"><div class="sec"><h2>Constructors in this scenario</h2></div><p>Points attributed using each driver's team in the site's current driver list.</p><ol>${teams.map(t=>`<li>${esc(t.name)} · ${t.points} points</li>`).join('')}</ol></section>`;
  const spotlight=p=>{document.getElementById('wi-spotlight').innerHTML=`<span class="lbl">Driver spotlight</span><p><b>${esc(p.name)}</b> · Actual: ${p.actual} · Without Antonelli: ${p.points} · GP wins: ${p.wins}</p>`;};
  function refresh(){
    const actual=document.getElementById('wi-mode').value==='actual',query=document.getElementById('wi-search').value.toLowerCase();
    const list=actual?result.actual:revised,filtered=list.filter(p=>p.name.toLowerCase().includes(query)),shown=document.getElementById('wi-all').checked||query?filtered:filtered.slice(0,10);
    document.getElementById('wi-table').innerHTML=`<table class="t wi-table"><caption>${actual?'Actual standings':'Hypothetical standings without Antonelli'}</caption><thead><tr><th scope="col" class="n">Pos</th><th scope="col">Driver / team</th><th scope="col" class="n">Actual</th><th scope="col" class="n">Gain</th><th scope="col" class="n">Revised</th><th scope="col" class="n">Wins</th></tr></thead><tbody>${shown.map(p=>`<tr><td class="n">${p.rank}</td><td><div class="wi-driver"><span class="sw" style="background:${tcol(p.team)}" aria-hidden="true"></span><div><button type="button" data-wi-driver="${esc(p.name)}">${esc(p.name)}</button><small>${esc(p.team)}</small></div></div></td><td class="n">${p.actual}</td><td class="n">${p.name==='Kimi Antonelli'?'—':`+${p.points-p.actual}`}</td><td class="n">${p.name==='Kimi Antonelli'?'—':p.points}</td><td class="n">${p.name==='Kimi Antonelli'?'—':p.wins}</td></tr>`).join('')||'<tr><td colspan="6">No matching drivers found.</td></tr>'}</tbody></table>`;
  }
  host.querySelectorAll('select,input').forEach(el=>el.addEventListener('input',refresh));
  host.addEventListener('click',e=>{const b=e.target.closest('[data-wi-driver]');if(b){const p=result.actual.find(p=>p.name===b.dataset.wiDriver);if(p)spotlight(p);}});
  refresh();if(lead)spotlight(lead);
}
