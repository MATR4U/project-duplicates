# Matr Project - Kanban Board

## 📝 ToDo
- [ ] Implement Service Class (independence of db instance from the App class and API endpoints)
- [ ] Implement Dynamic Handling of DB connections
- [ ] Implement Config File Handler
- [ ] Implement Thread safety in common classes

## 🚧 In Progress
- [90%] Implement Dynamic Handling of Configuration File changes.
  - [ ] Test Successful

## ✅ Done
- [x] Configuration validation using pydantic model (100% Complete)
- [x] Implement Singletons for App and DB (100% Complete)
- [x] Working Prototype using Backend FastAPI + SQLModel and Database Postgresql (100% Complete)

## 🔙 Backlog
- [ ] Implement Service Discovery
- [ ] Implement Service Broker (MQTT)
- [ ] Implement Dynamic Service Binding (...)
- [ ] Improve API using GraphAPI
- [ ] Implement Circuit Breaker Pattern ([Pybreaker](https://pypi.org/project/pybreaker/))
- [ ] Redis centralised dynamic Config-State cache
- [ ] Implement Base class for easier Inheritance
