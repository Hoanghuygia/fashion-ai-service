# Dependency Map

High-level feature relationships for Style Engine AI. Only implemented features
are listed.

- Service Foundation
  - independent
- Data Persistence
  - independent
- Internal Authentication
  - depends on Service Foundation
- Background Removal
  - depends on Internal Authentication
  - depends on Service Foundation
  - depends on Data Persistence
