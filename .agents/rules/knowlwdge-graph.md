---
trigger: always_on
---

**System Role & Objective:**
You are operating within the Google Anti-Gravity framework. To drastically reduce token consumption, increase response speed, and maintain an accurate understanding of the entire system architecture, you must strictly follow these Knowledge Graph directives.

---

## 1. The Core Source of Truth Directive
- **Mandate:** You must maintain and strictly adhere to a `knowledge_graph.md` file located in the root directory. 
- **Purpose:** This file is the absolute source of truth for the system's architecture, data flow, component relationships, and current state. 
- **Constraint:** Do NOT scan the entire codebase or read unprompted files to build context. Rely entirely on `knowledge_graph.md` as your primary map to conserve token consumption.

## 2. The Initialization (Quick Load) Rule
- **Mandate:** At the beginning of *every* new task, conversation, or session, your first action must be to read the `knowledge_graph.md`.
- **Action:** Use this file to understand the current system structure, dependencies, and active processes *before* writing any code, planning steps, or executing commands.

## 3. The Continuous Update Mechanism
- **Mandate:** Upon completing any task, modifying a component, or altering the system's logic, you must immediately update `knowledge_graph.md`.
- **Action:** Add new components, define their relationships to existing ones, and briefly note their core functionality. 
- **Constraint:** Never mark a task as complete or end a session without syncing the graph to match the exact current state of the codebase.

## 4. Format & Optimization Constraints
- **Mandate:** Keep the `knowledge_graph.md` highly condensed and strictly structured.
- **Action:** Only document high-level component functions, data flows, API endpoints, and critical state interactions.
- **Constraint:** Exclude implementation details, boilerplate code, inner-function logic, or minor styling rules. The graph must remain lightweight.

---

### Example `knowledge_graph.md` Structure to Maintain: