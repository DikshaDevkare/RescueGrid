# 🚨 RESCUEGRID

### Offline-First Disaster Response & Emergency Coordination Platform

RESCUEGRID is an offline-first web platform designed to support emergency and disaster-response operations in situations where internet connectivity may be unreliable or temporarily unavailable.

The platform allows users to continue creating, editing, and managing critical emergency information while offline. Changes are stored locally and placed into a persistent synchronization queue. Once connectivity is restored, the system automatically synchronizes pending changes with the backend.

RESCUEGRID also provides conflict detection to prevent offline updates from silently overwriting newer server data.

---

## 🎯 Problem Statement

During disasters and emergency situations, internet connectivity can be unstable or completely unavailable. Conventional web applications often depend on continuous connectivity, making it difficult for rescue teams and communities to record and update critical information.

RESCUEGRID addresses this problem using an offline-first architecture that allows essential operations to continue even without an active internet connection.

---

## 💡 Our Solution

RESCUEGRID provides:

- 📡 Offline-first operation
- 💾 Local data storage using IndexedDB
- ➕ Offline create operations
- ✏️ Offline editing
- 🗑️ Offline deletion
- 📋 Persistent pending-change queue
- 🔄 Automatic synchronization when connectivity returns
- ⚠️ Conflict detection for concurrent offline edits
- 🛡️ Conflict resolution options
- 🗺️ Emergency map
- 🚑 Victim and incident management
- 📦 Resource management
- 📊 Emergency analytics
- 👥 Role-based dashboards
- 🔐 Authentication and authorization
- 📱 Responsive public-service oriented interface
- 📜 Activity and synchronization monitoring

---

# 👥 User Roles

## 1. Community User

Community users can:

- Report emergencies
- View emergency information
- View the emergency map
- Track their submitted reports
- Access safety information
- Continue submitting information while offline

## 2. Rescue / Security Team

Rescue teams can:

- Monitor victims
- Manage incidents
- Track emergency resources
- View the emergency map
- Update operational information
- Work with emergency data while offline
- Synchronize pending changes when connectivity returns

## 3. Administrator

Administrators can:

- Monitor overall emergency operations
- Manage users
- Monitor rescue teams
- Manage incidents and victims
- View analytics
- Monitor synchronization
- Monitor system activity
- Access emergency mapping

  # 🔄 Offline-First Workflow

RESCUEGRID follows an offline-first approach:

```text
             ┌─────────────────────┐
             │     User Action     │
             │ Create / Edit / Delete│
             └──────────┬──────────┘
                        │
                        ▼
             ┌─────────────────────┐
             │   Local Database    │
             │     IndexedDB       │
             └──────────┬──────────┘
                        │
                 Internet Status
                   /           \
                Online        Offline
                  │              │
                  ▼              ▼
          ┌──────────────┐   ┌──────────────┐
          │ Synchronize  │   │ Pending Queue│
          │ with Backend │   │   Persistent │
          └──────┬───────┘   └──────┬───────┘
                 │                  │
                 │          Connectivity Returns
                 │                  │
                 └──────────┬───────┘
                            ▼
                    ┌───────────────┐
                    │ Sync Engine   │
                    └───────┬───────┘
                            │
                     Version Check
                       /        \
                    Valid      Conflict
                      │           │
                      ▼           ▼
                  Server      Conflict
                  Update      Resolution


---

# 5. Conflict Detection

This is your **innovation/bonus feature**, so definitely mention it.

```markdown
# ⚠️ Conflict Detection & Resolution

RESCUEGRID uses version-based conflict detection.

When an offline device modifies a record, it stores the version of the record that it originally worked with.

When synchronization occurs:

- The client sends the original/base version.
- The backend compares it with the current server version.
- If the versions match, the update is accepted.
- If the server contains a newer version, a conflict is detected.
- The system does not silently overwrite the newer server data.

### Conflict Resolution Options

Users can resolve conflicts using:

- 🟢 Keep Local
- 🔵 Keep Server
- 🟡 Merge

This helps protect critical emergency information from accidental data loss.

# 🧩 Key Modules

### 🔐 Authentication
- Login
- Registration
- Role-based access
- Community, Rescue Team and Administrator roles

### 🚨 Emergency Management
- Emergency reporting
- Incident management
- Victim management
- Emergency status tracking

### 📦 Resource Management
- Resource monitoring
- Availability tracking
- Operational resource information

### 🗺️ Emergency Map
- Incident locations
- Victim locations
- Resource locations
- Emergency markers
- Cached operational information

### 🔄 Sync Center
- Online/offline status
- Pending changes
- Synchronization status
- Failed operations
- Conflict management

### 📊 Analytics
- Incident statistics
- Victim severity distribution
- Operational activity
- Emergency overview

### 📜 Activity Monitoring
- User/system activities
- Synchronization events
- Operational updates

# 🛠️ Technology Stack

## Frontend

- React
- TypeScript
- Vite
- React Router
- Dexie.js
- IndexedDB
- Axios
- Recharts
- React Leaflet
- Leaflet
- Lucide React
- vite-plugin-pwa

## Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- JWT Authentication
- Pydantic

## Architecture

- Progressive Web App (PWA)
- Offline-first architecture
- REST APIs
- Local-first data handling
- Persistent synchronization queue
- Version-based conflict detection


# 🏗️ System Architecture

```text
┌─────────────────────────────┐
│          Users              │
│ Community / Rescue / Admin  │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       React Frontend        │
│     TypeScript + Vite       │
└──────────────┬──────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌─────────────┐   ┌───────────────┐
│ IndexedDB   │   │ Backend API   │
│  + Dexie    │   │   FastAPI     │
└──────┬──────┘   └───────┬───────┘
       │                  │
       │                  ▼
       │           ┌─────────────┐
       │           │ SQLAlchemy  │
       │           │   + SQLite  │
       │           └─────────────┘
       │
       ▼
┌──────────────────────┐
│ Pending Sync Queue   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Synchronization      │
│ Engine               │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Version Validation   │
└──────────┬───────────┘
           │
      ┌────┴─────┐
      ▼          ▼
   Success     Conflict
                 │
                 ▼
        Conflict Resolution

        # ⭐ Project Highlights

- Works even when internet connectivity is unavailable
- Local-first emergency data operations
- Persistent synchronization queue
- Automatic synchronization after reconnection
- Conflict-aware data synchronization
- Role-based emergency management
- Emergency mapping
- Victim, incident and resource tracking
- Operational analytics
- Public-service focused UI
- Progressive Web App architecture

# 🔮 Future Scope

- PostgreSQL deployment for production-scale data
- Advanced disaster prediction
- AI-assisted emergency prioritization
- Intelligent resource allocation
- Advanced offline map caching
- Store-and-forward communication between nearby devices
- Push notifications
- Real-time multi-team coordination when connectivity is available
- Advanced audit and reporting
- Deployment with scalable cloud infrastructure
