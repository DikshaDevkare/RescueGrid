import {useEffect,useMemo,useState} from 'react';
import {MapContainer,TileLayer,Marker,Popup,Circle,Tooltip as LeafletTooltip,useMap} from 'react-leaflet';
import {useSearchParams} from 'react-router-dom';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import {Filter,LocateFixed,X} from 'lucide-react';
import type {Incident,Victim,Resource,MapPoint} from './types';
import {useOnline} from './hooks';

const points:MapPoint[]=[
{id:'T1',name:'Team Alpha',kind:'team',latitude:18.532,longitude:73.848,status:'Active',detail:'Search & Rescue · RG-ALPHA-01'},
{id:'T2',name:'Team Beta',kind:'team',latitude:18.546,longitude:73.865,status:'Active',detail:'Medical Response · RG-BETA-02'},
{id:'H1',name:'CityCare Hospital',kind:'hospital',latitude:18.529,longitude:73.874,status:'Open',detail:'Emergency department · 24/7'},
{id:'H2',name:'District Hospital',kind:'hospital',latitude:18.507,longitude:73.842,status:'Open',detail:'Trauma + ambulance support'},
{id:'H3',name:'Municipal Emergency Hospital',kind:'hospital',latitude:18.548,longitude:73.878,status:'Open',detail:'Emergency care · 24/7'},
{id:'RLP1',name:'Relief Water Point A',kind:'relief',latitude:18.523,longitude:73.856,status:'Available',detail:'Drinking water · 1,200 L'},
{id:'RLP2',name:'Food Relief Camp',kind:'relief',latitude:18.516,longitude:73.872,status:'Available',detail:'Food packs · 420'},
{id:'RLP3',name:'Relief Water Point B',kind:'relief',latitude:18.512,longitude:73.861,status:'Available',detail:'Drinking water · 900 L'},
{id:'RLP4',name:'Relief Water Point C',kind:'relief',latitude:18.542,longitude:73.846,status:'Available',detail:'Drinking water · 700 L'},
{id:'S1',name:'Community Safe Zone',kind:'safe',latitude:18.538,longitude:73.882,status:'Open',detail:'Temporary shelter · 250 capacity'},
{id:'S2',name:'Municipal School Safe Zone',kind:'safe',latitude:18.501,longitude:73.864,status:'Open',detail:'Assembly point · 180 capacity'},
{id:'S3',name:'Hillview Safe Zone',kind:'safe',latitude:18.515,longitude:73.895,status:'Open',detail:'Temporary shelter · 320 capacity'}];

const colors:any={team:'#2563eb',hospital:'#15966b',relief:'#e45b20',safe:'#7c5ccf',Critical:'#c62828',High:'#e45b20',Medium:'#f59e0b',Low:'#2563eb',victim:'#f59e0b',resource:'#2563eb',incident:'#c62828'};
const iconLetter:any={team:'T',hospital:'H',relief:'R',safe:'S',victim:'V',resource:'R',incident:'!'};

const pin=(c:string,t:string,label?:string)=>L.divIcon({className:'pin',html:`<div class="pinbody" style="--c:${c}"><span class="pinletter"><span class="pinlettertext">${t}</span></span>${label?`<span class="pinlabel">${label}</span>`:''}</div>`,iconSize:label?[170,46]:[42,42],iconAnchor:label?[21,21]:[21,42]});

function Recenter({center}:{center:[number,number]}){const m=useMap();return <button className="mapcontrol" onClick={()=>m.setView(center,13)}><LocateFixed size={14}/> My area</button>}
function distance(a:number,b:number,c:number,d:number){const R=6371;const p=Math.PI/180;const x=(c-a)*p,y=(d-b)*p;const q=Math.sin(x/2)**2+Math.cos(a*p)*Math.cos(c*p)*Math.sin(y/2)**2;return 2*R*Math.asin(Math.sqrt(q))}

export function MapView({incidents=[],victims=[],resources=[],compact=false,userLocation}:{incidents?:Incident[];victims?:Victim[];resources?:Resource[];compact?:boolean;userLocation?:[number,number]}={}){
 const online=useOnline(); const [searchParams]=useSearchParams(); const center=userLocation||[18.5204,73.8567] as [number,number]; const [filters,setFilters]=useState<Record<string,boolean>>({incidents:true,victims:true,resources:true,team:true,hospital:true,relief:true,safe:true}); const [severity]=useState('All'); const [selected,setSelected]=useState<any>(null);
 const toggle=(k:string)=>setFilters(x=>({...x,[k]:!x[k]}));
 const filteredInc=useMemo(()=>incidents.filter(x=>filters.incidents&&(severity==='All'||x.severity===severity)),[incidents,filters.incidents,severity]);
 useMemo(()=>[...points].sort((a,b)=>distance(center[0],center[1],a.latitude,a.longitude)-distance(center[0],center[1],b.latitude,b.longitude)).slice(0,3),[center]);
 useEffect(()=>{const id=searchParams.get('incident')||searchParams.get('victim')||searchParams.get('resource');if(!id)return;const found=[...incidents.map(x=>({...x,_kind:'incident'})),...victims.map(x=>({...x,_kind:'victim'})),...resources.map(x=>({...x,_kind:'resource'})),...points.map(x=>({...x,_kind:x.kind}))].find(x=>x.id===id);if(found)setSelected(found)},[searchParams,incidents,victims,resources]);
 const renderSelect=(item:any,kind:string,letter:string)=>{const title=String(item.title||item.name||'');const showLabel=kind==='incident'||kind==='hospital'||kind==='team';return <Marker key={kind+item.id} position={[item.latitude,item.longitude]} icon={pin(colors[item.severity||kind]||colors[kind]||'#2563eb',letter,showLabel?title:undefined)} eventHandlers={{click:()=>setSelected({...item,_kind:kind})}}><LeafletTooltip direction="top" offset={[0,-18]} opacity={.98}>{title}</LeafletTooltip><Popup><b>{title}</b><br/>{kind==='incident'?`${item.type} · ${item.severity}`:kind==='victim'?`Victim · ${item.severity}`:item.detail||item.category}<br/><small>{item.status}</small></Popup></Marker>};
 return <div className={'map '+(compact?'compactmap':'')}>
  <div className="maptools"><span className="filterbtn"><Filter size={13}/> Show</span>{['incidents','victims','resources','team','hospital','relief','safe'].map(k=><button key={k} className={filters[k]?'filter on':'filter'} onClick={()=>toggle(k)}>{k==='team'?'Teams':k==='hospital'?'Hospitals':k==='relief'?'Relief':k==='safe'?'Safe zones':k[0].toUpperCase()+k.slice(1)}</button>)}</div>
  <MapContainer center={center} zoom={12} className="leaflet"><TileLayer attribution="&copy; OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/><Recenter center={center}/>
   {filteredInc.map(x=>renderSelect(x,'incident','!'))}
   {filters.victims&&victims.map(x=>renderSelect(x,'victim','V'))}
   {filters.resources&&resources.filter(x=>x.latitude!=null&&x.longitude!=null).map(x=>renderSelect(x,'resource','R'))}
   {points.map(x=>filters[x.kind]&&renderSelect(x,x.kind,iconLetter[x.kind]))}
   {filteredInc.filter(x=>x.severity==='Critical').map(x=><Circle key={'c'+x.id} center={[x.latitude,x.longitude]} radius={650} pathOptions={{color:'#c62828',fillColor:'#c62828',fillOpacity:.09}}/>)}
  </MapContainer>
  <div className="map-note"><span className={online?'dot green':'dot red'}/>{online?'LIVE MAP + OPERATIONAL DATA':'OFFLINE · CACHED OPERATIONAL DATA'} · {new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}</div>
  <div className="legend"><span><i style={{background:'#c62828'}}/>Incidents</span><span><i style={{background:'#f59e0b'}}/>Victims</span><span><i style={{background:'#2563eb'}}/>Teams</span><span><i style={{background:'#15966b'}}/>Hospitals</span><span><i style={{background:'#7c5ccf'}}/>Safe zones</span></div>
  {!compact&&selected&&<aside className="mapdetails show"><button onClick={()=>setSelected(null)} aria-label="Close details"><X size={15}/></button><small>{String(selected._kind).toUpperCase()}</small><h3>{selected.title||selected.name}</h3><p>{selected.description||selected.detail||selected.medical_condition||selected.location||'Operational record'}</p>{selected.type&&<div className="detailrow"><span>Type</span><b>{selected.type}</b></div>}<div className="detailrow"><span>Status</span><b>{selected.status}</b></div>{selected.severity&&<div className="detailrow"><span>Severity</span><b className={'sev '+selected.severity.toLowerCase()}>{selected.severity}</b></div>}{selected.people_affected!=null&&<div className="detailrow"><span>People affected</span><b>{selected.people_affected}</b></div>}{selected.category&&<div className="detailrow"><span>Category</span><b>{selected.category}</b></div>}{selected.available!=null&&<div className="detailrow"><span>Available</span><b>{selected.available} {selected.unit||''}</b></div>}{selected.medical_condition&&<div className="detailrow"><span>Medical note</span><b>{selected.medical_condition}</b></div>}{selected.updated_by&&<div className="detailrow"><span>Updated by</span><b>{selected.updated_by}</b></div>}<div className="detailrow"><span>Coordinates</span><b>{Number(selected.latitude).toFixed(4)}, {Number(selected.longitude).toFixed(4)}</b></div></aside>}
 </div>
}
