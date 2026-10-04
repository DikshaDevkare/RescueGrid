import json, os, uuid, hashlib, secrets
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
import jwt
from .db import Base, engine, get_db
from .models import User, RescueTeam, Victim, Incident, Resource, Conflict, Activity

Base.metadata.create_all(bind=engine)

def migrate():
    # Small SQLite-safe additive migration for local hackathon databases created by earlier builds.
    with engine.begin() as conn:
        tables = {r[0] for r in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))}
        columns = {r[1] for r in conn.execute(text("PRAGMA table_info(users)"))} if 'users' in tables else set()
        for name, typ in [('latitude','REAL'),('longitude','REAL')]:
            if name not in columns: conn.execute(text(f'ALTER TABLE users ADD COLUMN {name} {typ}'))
        columns = {r[1] for r in conn.execute(text("PRAGMA table_info(resources)"))} if 'resources' in tables else set()
        for name, typ in [('latitude','REAL'),('longitude','REAL'),('device_id','TEXT')]:
            if name not in columns: conn.execute(text(f'ALTER TABLE resources ADD COLUMN {name} {typ}'))
        columns = {r[1] for r in conn.execute(text("PRAGMA table_info(incidents)"))} if 'incidents' in tables else set()
        for name, typ in [('location','TEXT'),('device_id','TEXT')]:
            if name not in columns: conn.execute(text(f'ALTER TABLE incidents ADD COLUMN {name} {typ}'))
        columns = {r[1] for r in conn.execute(text("PRAGMA table_info(victims)"))} if 'victims' in tables else set()
        if 'device_id' not in columns and 'victims' in tables: conn.execute(text('ALTER TABLE victims ADD COLUMN device_id TEXT'))

migrate()
app=FastAPI(title='RESCUEGRID API',version='4.0')
origins=[x.strip() for x in os.getenv('RESCUEGRID_CORS','http://127.0.0.1:5173,http://localhost:5173').split(',') if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_origin_regex=r'https://([a-z0-9-]+\.)?vercel\.app',allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
SECRET=os.getenv('RESCUEGRID_SECRET','rescuegrid-dev-secret-change-me-32-bytes')
bearer=HTTPBearer(auto_error=False)

def now(): return datetime.now(timezone.utc)
def ser(x):
    d={c.name:getattr(x,c.name) for c in x.__table__.columns}
    return {k:(v.isoformat() if isinstance(v,datetime) else v) for k,v in d.items()}
def userpub(u):
    return {'id':u.id,'full_name':u.full_name,'email':u.email,'role':u.role,'mobile':u.mobile,'area':u.area,'latitude':u.latitude,'longitude':u.longitude,'team_name':u.team_name,'team_id':u.team_id,'designation':u.designation,'team_type':u.team_type}
def hp(p):
    salt=secrets.token_bytes(16); digest=hashlib.pbkdf2_hmac('sha256',p.encode(),salt,210000); return 'pbkdf2$'+salt.hex()+'$'+digest.hex()
def vp(p,h):
    try:
        _,s,d=h.split('$',2); return secrets.compare_digest(hashlib.pbkdf2_hmac('sha256',p.encode(),bytes.fromhex(s),210000).hex(),d)
    except Exception:return False
def tok(u): return jwt.encode({'sub':u.id,'exp':now()+timedelta(hours=12)},SECRET,algorithm='HS256')
def me(c:HTTPAuthorizationCredentials=Depends(bearer),db:Session=Depends(get_db)):
    if not c: raise HTTPException(401,'Authentication required')
    try: uid=jwt.decode(c.credentials,SECRET,algorithms=['HS256'])['sub']
    except Exception: raise HTTPException(401,'Invalid session')
    u=db.get(User,uid)
    if not u: raise HTTPException(401,'User not found')
    return u
def role(*roles):
    def d(u=Depends(me)):
        if u.role not in roles: raise HTTPException(403,'Insufficient permissions')
        return u
    return d
def act(db,text_,typ='info'): db.add(Activity(text=text_,type=typ)); db.commit()

@app.get('/api/health')
def health(): return {'status':'ok','service':'RESCUEGRID','version':'4.0'}
@app.get('/')
def root(): return {'service':'RESCUEGRID','status':'ok','version':'4.0'}

class Reg(BaseModel):
    role:str; full_name:str; email:str; mobile:str=''; area:str=''; latitude:float|None=None; longitude:float|None=None
    password:str; confirm_password:str; team_name:str=''; team_id:str=''; designation:str=''; team_type:str=''; verification_id:str=''
class Login(BaseModel): email:str; password:str; role:str

@app.post('/api/auth/register')
def register(b:Reg,db:Session=Depends(get_db)):
    if b.role not in ['community','rescue']: raise HTTPException(400,'Administrator registration is controlled.')
    if b.password!=b.confirm_password: raise HTTPException(400,'Passwords do not match')
    if len(b.password)<6: raise HTTPException(400,'Password must contain at least 6 characters')
    email=b.email.lower().strip()
    if db.query(User).filter_by(email=email).first(): raise HTTPException(409,'Email already registered')
    u=User(id=str(uuid.uuid4()),full_name=b.full_name.strip(),email=email,password_hash=hp(b.password),role=b.role,mobile=b.mobile,area=b.area,latitude=b.latitude,longitude=b.longitude,team_name=b.team_name,team_id=b.team_id,designation=b.designation,team_type=b.team_type,verification_id=b.verification_id)
    db.add(u)
    if b.role=='rescue':
        if not b.team_id or not b.team_name: raise HTTPException(400,'Team name and team ID are required')
        if db.query(RescueTeam).filter_by(team_id=b.team_id).first(): raise HTTPException(409,'Team ID already registered')
        db.add(RescueTeam(id=str(uuid.uuid4()),team_name=b.team_name,team_id=b.team_id,leader_name=b.full_name,designation=b.designation,mobile=b.mobile,email=email,operational_area=b.area,team_type=b.team_type,verification_id=b.verification_id,latitude=b.latitude,longitude=b.longitude,status='Pending Verification'))
    db.commit(); act(db,f'{b.role.title()} account registered: {u.full_name}','auth'); return {'user':userpub(u)}

@app.post('/api/auth/login')
def login(b:Login,db:Session=Depends(get_db)):
    u=db.query(User).filter_by(email=b.email.lower().strip()).first()
    if not u or u.role!=b.role or not vp(b.password,u.password_hash): raise HTTPException(401,'Invalid email, password or role')
    return {'access_token':tok(u),'user':userpub(u)}
@app.get('/api/auth/me')
def authme(u=Depends(me)): return userpub(u)

ENTITY={'victim':Victim,'incident':Incident,'resource':Resource}
for path,Model in [('/api/victims',Victim),('/api/incidents',Incident),('/api/resources',Resource)]:
    def make(M):
        def get(db:Session=Depends(get_db),u=Depends(me),q:str|None=Query(None)):
            rows=db.query(M).all()
            if q: rows=[x for x in rows if q.lower() in json.dumps(ser(x)).lower()]
            return [ser(x) for x in rows]
        return get
    app.add_api_route(path,make(Model),methods=['GET'])

@app.get('/api/summary')
def summary(db:Session=Depends(get_db),u=Depends(me)):
    return {'active_teams':db.query(RescueTeam).filter(RescueTeam.status=='Active').count(),'incidents':db.query(Incident).count(),'critical_incidents':db.query(Incident).filter(Incident.severity=='Critical').count(),'resources':db.query(Resource).count(),'victims':db.query(Victim).count()}

@app.get('/api/admin/users')
def admin_users(db:Session=Depends(get_db),u=Depends(role('admin'))): return [userpub(x) for x in db.query(User).order_by(User.created_at.desc()).all()]
@app.get('/api/admin/teams')
def admin_teams(db:Session=Depends(get_db),u=Depends(role('admin'))): return [ser(x) for x in db.query(RescueTeam).order_by(RescueTeam.created_at.desc()).all()]
@app.get('/api/admin/activities')
def admin_activities(db:Session=Depends(get_db),u=Depends(role('admin'))): return [ser(x) for x in db.query(Activity).order_by(Activity.created_at.desc()).limit(100).all()]
@app.get('/api/admin/stats')
def admin_stats(db:Session=Depends(get_db),u=Depends(role('admin'))):
    return {'users':db.query(User).count(),'community':db.query(User).filter_by(role='community').count(),'teams':db.query(User).filter_by(role='rescue').count(),'incidents':db.query(Incident).count(),'victims':db.query(Victim).count(),'resources':db.query(Resource).count(),'open_conflicts':db.query(Conflict).filter_by(resolved=False).count()}
@app.get('/api/admin/overview')
def admin_overview(db:Session=Depends(get_db),u=Depends(role('admin'))):
    return {'stats':admin_stats(db,u),'recent_incidents':[ser(x) for x in db.query(Incident).order_by(Incident.updated_at.desc()).limit(6).all()], 'recent_activities':[ser(x) for x in db.query(Activity).order_by(Activity.created_at.desc()).limit(8).all()]}

class Sync(BaseModel): id:str; entity:str; entity_id:str; operation:str; payload:dict; base_version:int=0; device_id:str
@app.post('/api/sync')
def sync(b:Sync,db:Session=Depends(get_db),u=Depends(me)):
    M=ENTITY.get(b.entity)
    if not M: raise HTTPException(400,'Unsupported entity')
    old=db.get(M,b.entity_id)
    if b.operation not in ['CREATE','UPDATE','DELETE']: raise HTTPException(400,'Unsupported operation')
    if b.operation=='CREATE' and old:
        c=Conflict(id=str(uuid.uuid4()),entity=b.entity,entity_id=b.entity_id,operation=b.operation,local_payload=json.dumps(b.payload),server_payload=json.dumps(ser(old)),base_version=b.base_version,server_version=old.version,device_id=b.device_id); db.add(c); db.commit(); return {'conflict':ser(c)}
    if b.operation!='CREATE' and not old: raise HTTPException(404,'Server record not found')
    if b.operation!='CREATE' and b.base_version!=old.version:
        c=Conflict(id=str(uuid.uuid4()),entity=b.entity,entity_id=b.entity_id,operation=b.operation,local_payload=json.dumps(b.payload),server_payload=json.dumps(ser(old)),base_version=b.base_version,server_version=old.version,device_id=b.device_id); db.add(c); db.commit(); return {'conflict':ser(c)}
    if b.operation=='CREATE':
        data={k:v for k,v in b.payload.items() if hasattr(M,k) and k not in ['version','updated_at','updated_by','device_id']}
        o=M(**data,version=1,updated_by=u.full_name)
        if hasattr(o,'device_id'): o.device_id=b.device_id
        db.add(o); db.commit(); act(db,f'CREATE {b.entity} synchronized','sync'); return {'record':ser(o)}
    if b.operation=='DELETE': db.delete(old); db.commit(); act(db,f'DELETE {b.entity} synchronized','sync'); return {'record':None}
    for k,v in b.payload.items():
        if hasattr(old,k) and k not in ['id','version','updated_at','updated_by','device_id']: setattr(old,k,v)
    old.version+=1; old.updated_by=u.full_name; old.updated_at=now()
    if hasattr(old,'device_id'): old.device_id=b.device_id
    db.commit(); act(db,f'{b.operation} {b.entity} synchronized','sync'); return {'record':ser(old)}

class Resolve(BaseModel): choice:str
@app.get('/api/conflicts')
def getconf(db:Session=Depends(get_db),u=Depends(me)): return [ser(x) for x in db.query(Conflict).filter_by(resolved=False).order_by(Conflict.created_at.desc()).all()]
@app.post('/api/conflicts/{cid}/resolve')
def resolve(cid:str,b:Resolve,db:Session=Depends(get_db),u=Depends(me)):
    if b.choice not in ['local','server','merge']: raise HTTPException(400,'Invalid choice')
    c=db.get(Conflict,cid)
    if not c: raise HTTPException(404,'Conflict not found')
    M=ENTITY[c.entity]; s=db.get(M,c.entity_id)
    local=json.loads(c.local_payload); remote=json.loads(c.server_payload)
    if not s and b.choice=='server': c.resolved=True; db.commit(); act(db,f'Conflict resolved using server for {c.entity} {c.entity_id}','conflict'); return {'record':None}
    if not s: raise HTTPException(404,'Server record not found')
    if b.choice=='local' and c.operation=='DELETE': db.delete(s); c.resolved=True; db.commit(); act(db,f'Conflict resolved using local delete for {c.entity} {c.entity_id}','conflict'); return {'record':None}
    if b.choice!='server':
        merged=dict(remote)
        if b.choice=='local': merged.update(local)
        else:
            for k,v in local.items():
                if k in ['description','medical_condition'] and v: merged[k]=(remote.get(k,'')+' | '+v).strip(' |')
                elif k not in ['id','version','updated_at']: merged[k]=v
        for k,v in merged.items():
            if hasattr(s,k) and k not in ['id','version','updated_at']: setattr(s,k,v)
        s.version+=1; s.updated_by=u.full_name; s.updated_at=now()
    c.resolved=True; db.commit(); act(db,f'Conflict resolved using {b.choice} for {c.entity} {c.entity_id}','conflict'); return {'record':ser(s) if s else None}

@app.on_event('startup')
def seed():
    db=next(get_db())
    if not db.query(User).filter_by(email='community@rescuegrid.demo').first():
        db.add_all([
            User(id='uc',full_name='Aarav Community',email='community@rescuegrid.demo',password_hash=hp('demo123'),role='community',area='Shivaji Nagar, Pune',latitude=18.531,longitude=73.855),
            User(id='ur',full_name='Team Alpha',email='rescue@rescuegrid.demo',password_hash=hp('demo123'),role='rescue',area='Pune',latitude=18.532,longitude=73.848,team_name='Team Alpha',team_id='RG-ALPHA-01',designation='Field Lead',team_type='Search & Rescue',verification_id='DEMO-VERIFIED'),
            User(id='ua',full_name='RESCUEGRID Admin',email='admin@rescuegrid.demo',password_hash=hp('demo123'),role='admin',area='Pune')])
    if db.query(RescueTeam).count()==0:
        db.add_all([
            RescueTeam(id='T1',team_name='Team Alpha',team_id='RG-ALPHA-01',leader_name='Team Alpha',designation='Field Lead',mobile='9999999999',email='rescue@rescuegrid.demo',operational_area='Pune',team_type='Search & Rescue',verification_id='DEMO-VERIFIED',latitude=18.532,longitude=73.848,status='Active'),
            RescueTeam(id='T2',team_name='Team Beta',team_id='RG-BETA-02',leader_name='Team Beta',designation='Medical Lead',mobile='9999999998',email='beta@rescuegrid.demo',operational_area='Pune',team_type='Medical Response',verification_id='DEMO-VERIFIED',latitude=18.546,longitude=73.865,status='Active')])
    if db.query(Victim).count()==0:
        db.add_all([Victim(id='V104',name='Rahul Sharma',age=31,severity='Critical',medical_condition='Possible fracture',latitude=18.531,longitude=73.855,status='Pending',version=3,updated_by='Team Alpha'),Victim(id='V103',name='Priya Desai',age=42,severity='High',medical_condition='Dehydration',latitude=18.526,longitude=73.862,status='Rescued',version=2,updated_by='Team Beta')])
    if db.query(Incident).count()==0:
        db.add_all([Incident(id='I001',title='Flood in Shivaji Nagar',type='Flood',severity='High',description='Waterlogging affecting residential lanes.',latitude=18.531,longitude=73.855,location='Shivaji Nagar, Pune',people_affected=12,status='Responding',version=2,updated_by='Team Alpha'),Incident(id='I002',title='Road Accident — NH48',type='Accident',severity='Medium',description='Multi-vehicle collision.',latitude=18.497,longitude=73.91,location='NH48, Pune',people_affected=4,status='Reported',version=1,updated_by='Community'),Incident(id='I003',title='Building Collapse Alert',type='Collapse',severity='Critical',description='Structural collapse reported.',latitude=18.544,longitude=73.83,location='Pune City',people_affected=8,status='Responding',version=4,updated_by='Team Beta')])
    if db.query(Resource).count()==0:
        db.add_all([Resource(id='R001',name='Ambulance Fleet',category='Ambulance',available=12,allocated=8,unit='vehicles',location='Central Response Hub',latitude=18.520,longitude=73.850,status='Available',version=1,updated_by='Admin'),Resource(id='R002',name='Medical Kits',category='Medical',available=85,allocated=42,unit='kits',location='District Depot',latitude=18.508,longitude=73.845,status='Available',version=1,updated_by='Admin'),Resource(id='R003',name='Relief Water Point A',category='Water',available=1200,allocated=650,unit='litres',location='Shivaji Nagar Relief Camp',latitude=18.523,longitude=73.856,status='Limited',version=1,updated_by='Admin'),Resource(id='R004',name='Food Relief Stock',category='Food',available=420,allocated=180,unit='packs',location='Relief Camp North',latitude=18.516,longitude=73.872,status='Available',version=1,updated_by='Admin'),Resource(id='R005',name='Rescue Equipment',category='Equipment',available=16,allocated=11,unit='sets',location='Central Response Hub',latitude=18.520,longitude=73.850,status='Limited',version=1,updated_by='Admin')])
    if db.query(Activity).count()==0: db.add(Activity(text='RESCUEGRID operational database initialized',type='system'))
    db.commit(); db.close()
