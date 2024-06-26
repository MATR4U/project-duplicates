# Matr Project - Kanban Board - Backend

## Legend
- **🌟 Feature**: Represents new capabilities or significant improvements.
- **🐞 Bug-fix**: For items related to fixing errors or issues.
- **🔧 Enhancement**: Refers to improvements or upgrades to existing features.
- **📌 Task**: General tasks or activities that need to be completed.

## 📝 ToDo
- [ ] 📌 Implement Dynamic Handling of DB connections
- [ ] 📌 Implement Thread safety
- [ ] 📌 Refactor the handling of _initialized
- [x] 🌟 Implement Service Class (independence of db instance from the App class and API endpoints)
- [x] 🐞 DB health check at startup

## 🚧 In Progress
- [x] 🔧 Implement Dynamic Handling of Configuration File changes.
  - [x] 🌟Implement Traefik using as loadbalancer

## ✅ Done
- [x] 📌 Implement Config File Handler
- [x] 🐞 DB health check at startup
- [x] 🔧 Configuration validation using pydantic model (100% Complete)
- [x] 📌 Implement Singletons for App and DB (100% Complete)
- [x] 🌟 Working Prototype using Backend FastAPI + SQLModel and Database Postgresql (100% Complete)

## 🔙 Backlog
- [ ] 🌟 Implement Service Discovery
- [ ] 🌟 Implement Service Broker (MQTT)
- [ ] 🔧 Implement Dynamic Service Binding (...)
- [ ] 🔧 Improve API using GraphAPI
- [ ] 🔧 Implement Circuit Breaker Pattern ([Pybreaker](https://pypi.org/project/pybreaker/))
- [ ] 🔧 Redis centralised dynamic Config-State cache
- [ ] 📌 Implement Base class for easier Inheritance