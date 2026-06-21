# Hospitality Management Suite Specification

## Purpose

The Hospitality Management Suite is an integrated operations platform for hospitality businesses, initially focused on hostel operations.

Its purpose is to consolidate operational workflows currently distributed across multiple disconnected systems into a unified platform supporting guest management, reservations, occupancy management, staff coordination, scheduling, communications, operational documentation, and financial tracking.

The system is designed to serve as the primary operational interface for day-to-day hospitality management, reducing reliance on fragmented tools, duplicated data entry, and manual coordination processes.

The Hospitality Management Suite is intended to support real-world operational workflows through a practical, workflow-driven design that prioritizes reliability, clarity, and ease of use over feature completeness.

All requirements, workflows, and architectural decisions defined within this specification shall be evaluated against a single guiding principle:

**Does this improve the ability of staff to perform operational work safely, efficiently, and reliably?**

---

# Operational Context

Current hostel operations are distributed across multiple independent systems, including:

* Beds24
* WhatsApp
* Gmail
* Zoho Mail
* Notion
* Worldpackers
* Google Sheets
* Google Docs

These systems collectively support reservations, guest communications, volunteer management, scheduling, operational documentation, financial tracking, and daily operational coordination.

While functional, the current environment creates several operational problems:

* Information is fragmented across multiple platforms.
* Data must be entered or referenced in multiple places.
* Operational context is frequently lost between systems.
* Staff must switch between tools to complete common tasks.
* Institutional knowledge is difficult to maintain and discover.
* Operational reporting relies heavily on manual processes.

The objective of the Hospitality Management Suite is not to replicate every feature of the systems currently in use. Its objective is to provide a unified operational environment that improves upon the current workflow.

---

# Product Principles

## Workflow First

The system shall be designed around observed operational workflows rather than abstract feature sets.

## Operational Improvement Over Perfection

Version 1 is intended to improve existing workflows, not replace them with theoretically ideal solutions.

A simpler workflow that is consistently used is preferable to a comprehensive workflow that creates operational friction.

## Incremental Adoption

Modules shall provide value independently and may be adopted incrementally without requiring complete organizational migration.

## Single Source of Truth

Where practical, operational data shall have a clearly defined authoritative source.

## Explicit State

Operationally significant actions shall result in visible and understandable state changes.

## Human-Centered Operations

The system shall prioritize clarity, usability, and operational reliability over technical sophistication.

---

# System Scope

The Hospitality Management Suite consists of a collection of operational modules sharing a common authentication, authorization, notification, and data platform.

Core modules include:

1. Reservations & Occupancy
2. Guest Ledger
3. Staff Scheduling
4. Volunteer Management
5. Communications
6. Knowledge Base
7. Reporting & Operations Dashboard
8. Administration & Configuration

Additional modules may be introduced as operational needs are validated.

---

# Version 1 Objectives

The primary objective of Version 1 is successful operational adoption.

Success is measured by:

* Daily use by operational staff.
* Reduced dependence on fragmented external tools.
* Improved visibility of operational information.
* Reduction in duplicate data entry.
* Improved consistency of operational processes.

Version 1 is not required to completely eliminate all external systems.

It is required to provide measurable operational improvements over the current workflow.

---

# Core Architectural Decisions

* Rust is the primary implementation language.
* SQLite is the primary data store.
* The platform is deployed as a single-node application.
* Mobile and desktop clients operate against a shared platform.
* Local operation and reliability take precedence over horizontal scalability.
* Real-time updates shall be provided where operationally beneficial.
* Authorization shall be enforced server-side for all protected operations.

Further architectural decisions are defined within module specifications.

---

# Module Definitions

## Reservations & Occupancy

Purpose:

Provide operational visibility and management of reservations, arrivals, departures, occupancy, room allocation, and guest placement.

Primary capabilities:

* Reservation synchronization
* Occupancy calendar
* Check-in
* Check-out
* Bed assignment
* Group management
* Arrival and departure tracking

Reservation data may be synchronized from external booking systems where required.

---

## Guest Ledger

Purpose:

Provide operational tracking of guest financial activity.

Primary capabilities:

* Payment recording
* Balance tracking
* Multi-currency support
* Operational adjustments
* Transaction history
* Daily reconciliation support

The Guest Ledger is an operational tracking system and is not intended to function as a full accounting platform.

---

## Staff Scheduling

Purpose:

Coordinate staff availability, assignments, recurring shifts, and schedule visibility.

Primary capabilities:

* Shift creation
* Recurring schedules
* Availability tracking
* Assignment management
* Schedule notifications

---

## Volunteer Management

Purpose:

Manage volunteer recruitment, placement, scheduling, and participation.

Primary capabilities:

* Application tracking
* Placement management
* Schedule assignment
* Participation records
* Status tracking

---

## Communications

Purpose:

Centralize operational communication and notification workflows.

Primary capabilities:

* Internal messaging
* Operational notifications
* Communication records
* Context-linked discussions

---

## Knowledge Base

Purpose:

Provide a centralized repository for operational knowledge and documentation.

Primary capabilities:

* SOP management
* Operational documentation
* Search
* Training resources

---

## Reporting & Operations Dashboard

Purpose:

Provide visibility into operational performance and current operational state.

Primary capabilities:

* Occupancy reporting
* Financial summaries
* Schedule visibility
* Operational alerts
* Administrative dashboards

---

# Out of Scope

The Hospitality Management Suite is not intended to be:

* A general accounting platform.
* A public booking engine.
* A replacement for specialized property management allocation algorithms.
* A generalized workflow automation platform.
* A customer relationship management platform.
* A business intelligence platform.

Future versions may expand functionality, but these concerns are outside the scope of the current specification.

---

# Rollout Strategy

Initial deployment targets a three-location hostel operation.

Deployment shall proceed incrementally, with modules introduced individually and evaluated through operational use before wider adoption.

Each module must demonstrate measurable operational value before subsequent expansion.

The long-term objective is a unified hospitality operations platform capable of supporting wider adoption across hospitality organizations.
