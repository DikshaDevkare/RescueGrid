"""API regression tests for the core ALG-WEB-02 workflow.
Run from backend/: pytest -q
"""
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.db import SessionLocal
from app.models import User, RescueTeam, Victim, Incident, Conflict

@pytest.fixture(autouse=True)
def clean_test_records():
    db=SessionLocal()
    try:
        db.query(Conflict).delete(synchronize_session=False)
        db.query(Victim).filter(Victim.id.like('TEST-%')).delete(synchronize_session=False)
        db.query(Incident).filter(Incident.id.like('TEST-%')).delete(synchronize_session=False)
        db.query(RescueTeam).filter(RescueTeam.team_id=='RG-TEST-99').delete(synchronize_session=False)
        db.query(User).filter(User.email=='new-team@example.com').delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()

@pytest.fixture(scope='module')
def client():
    with TestClient(app) as c:
        yield c

def token(client, role='rescue'):
    email = {'community':'community@rescuegrid.demo','rescue':'rescue@rescuegrid.demo','admin':'admin@rescuegrid.demo'}[role]
    r = client.post('/api/auth/login', json={'email':email,'password':'demo123','role':role})
    assert r.status_code == 200
    return r.json()['access_token']

def headers(client, role='rescue'):
    return {'Authorization': f'Bearer {token(client, role)}'}

def test_health(client):
    assert client.get('/api/health').status_code == 200

def test_auth_and_role_access(client):
    h = headers(client,'rescue')
    assert client.get('/api/auth/me', headers=h).status_code == 200
    assert client.get('/api/admin/users', headers=h).status_code == 403
    assert client.get('/api/admin/users', headers=headers(client,'admin')).status_code == 200

def test_victim_read_and_sync_create_update_delete(client):
    h = headers(client,'rescue')
    assert client.get('/api/victims', headers=h).status_code == 200
    vid='TEST-VICTIM-ALG'
    payload={'id':vid,'name':'Test Victim','age':29,'severity':'High','medical_condition':'Test','latitude':18.52,'longitude':73.86,'status':'Pending','version':0,'updated_by':'Test'}
    r=client.post('/api/sync',headers=h,json={'id':'op-create-v','entity':'victim','entity_id':vid,'operation':'CREATE','payload':payload,'base_version':0,'device_id':'test-device'})
    assert r.status_code==200 and r.json().get('record')
    created=r.json()['record']; assert created['version']==1
    updated=dict(payload); updated['status']='Rescued'; updated['version']=1
    r=client.post('/api/sync',headers=h,json={'id':'op-update-v','entity':'victim','entity_id':vid,'operation':'UPDATE','payload':updated,'base_version':1,'device_id':'test-device'})
    assert r.status_code==200 and r.json()['record']['version']==2
    r=client.post('/api/sync',headers=h,json={'id':'op-delete-v','entity':'victim','entity_id':vid,'operation':'DELETE','payload':updated,'base_version':2,'device_id':'test-device'})
    assert r.status_code==200 and r.json()['record'] is None

def test_incident_sync_create(client):
    h=headers(client,'rescue'); iid='TEST-INCIDENT-ALG'; payload={'id':iid,'title':'Test Fire','type':'Fire','severity':'High','description':'Test','latitude':18.52,'longitude':73.86,'people_affected':2,'status':'Reported','version':0,'updated_by':'Test'}
    r=client.post('/api/sync',headers=h,json={'id':'op-inc','entity':'incident','entity_id':iid,'operation':'CREATE','payload':payload,'base_version':0,'device_id':'test-device'})
    assert r.status_code==200 and r.json()['record']['id']==iid

def test_version_conflict_and_resolution(client):
    h=headers(client,'rescue'); vid='TEST-CONFLICT-V'
    base={'id':vid,'name':'Conflict Victim','age':31,'severity':'High','medical_condition':'Initial','latitude':18.531,'longitude':73.855,'status':'Pending','version':0,'updated_by':'Device A'}
    r=client.post('/api/sync',headers=h,json={'id':'op-c-create','entity':'victim','entity_id':vid,'operation':'CREATE','payload':base,'base_version':0,'device_id':'device-A'})
    assert r.status_code==200 and r.json()['record']['version']==1
    latest=dict(base); latest['status']='In Progress'; latest['version']=1
    r=client.post('/api/sync',headers=h,json={'id':'op-c-update','entity':'victim','entity_id':vid,'operation':'UPDATE','payload':latest,'base_version':1,'device_id':'device-A'})
    assert r.status_code==200 and r.json()['record']['version']==2
    stale=dict(base); stale['medical_condition']='Offline edit'; stale['status']='Rescued'; stale['version']=1
    r=client.post('/api/sync',headers=h,json={'id':'op-conflict','entity':'victim','entity_id':vid,'operation':'UPDATE','payload':stale,'base_version':1,'device_id':'device-B'})
    assert r.status_code==200 and r.json().get('conflict')
    cid=r.json()['conflict']['id']
    r=client.post(f'/api/conflicts/{cid}/resolve',headers=h,json={'choice':'merge'})
    assert r.status_code==200 and r.json().get('record')
    r=client.post('/api/sync',headers=h,json={'id':'op-c-delete','entity':'victim','entity_id':vid,'operation':'DELETE','payload':stale,'base_version':r.json()['record']['version'],'device_id':'device-A'})
    assert r.status_code==200


def test_summary_and_rescue_team_registration(client):
    h=headers(client,'community')
    r=client.get('/api/summary',headers=h)
    assert r.status_code==200 and 'active_teams' in r.json()
    email='new-team@example.com'; payload={'role':'rescue','full_name':'New Team Lead','email':email,'mobile':'9000000000','area':'Pune','latitude':18.52,'longitude':73.85,'password':'secret123','confirm_password':'secret123','team_name':'New Response Team','team_id':'RG-TEST-99','designation':'Field Lead','team_type':'Search & Rescue','verification_id':'VERIFY-99'}
    r=client.post('/api/auth/register',json=payload); assert r.status_code==200
    h=headers(client,'admin'); teams=client.get('/api/admin/teams',headers=h)
    assert teams.status_code==200 and any(x['team_id']=='RG-TEST-99' for x in teams.json())
