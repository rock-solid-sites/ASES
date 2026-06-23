---
title: "Beds24 Booking Plugin"
tags: ["beds24", "architecture", "retro"]
sources: []
contributors: ["OL2r"]
created: 2026-06-23
updated: 2026-06-23
---

# Beds24 Booking Plugin: Architecture, Timeline, and Retrospective Findings

Evidence extracted on 2026-06-23 from 50 files in `/home/claude-code/beds24-booking-plugin/`.

## 1. Core Architecture (The Split Boundary)
- **Discovery (WordPress-owned)**: Search form, room results, cart accumulator.
- **Transaction (Beds24 iframe)**: Guest Details form, payments, confirmation (Beds24's `booking3.php`).
- **Data Model**: WP custom post type `beds24_room` mapped to Beds24 Room IDs via post meta. Custom taxonomy `beds24_amenity` for non-OTA variables.

## 2. API Integration Mechanics
- **Token Exchange**: Invite code → Refresh Token → Daily Access Token (24h validity).
- **Undocumented Parameters**: `sr1-{id}=1` and `naa1-1-{id}=N` are used to prepopulate multi-room carts.
- **Pricing**: Queries use `numAdults=1` to handle private flat-pricing and dorm bed-pricing cleanly.

## 3. Styling Contract & theme.json Integration
- Maps theme design tokens to ~30 CSS custom properties (`--beds24-*`).
- Generates paste-ready, static CSS for Beds24's custom CSS field (`bookingcss`) to style the iframe.

## 4. Key Lessons Learned (Retrospective)
- **Knowledge Primacy**: Discarding legacy code but fully retaining the 27 retrospective rules proved that structured system knowledge is more durable and valuable than execution code.
- **Silent Failures**: Web platforms truncate inputs silently (e.g., Beds24's customhead truncates at 2,000 chars; aaPanel's open_basedir fails on symlinks). Verification must check computed styles and actual payloads.
- **Write Up to the Gate**: Pattern for handling secrets; agents code up to execution, operator executes with substituted secret.

See `findings/2026-06-23-beds24-plugin-evidence.md` for the fully detailed findings and EDASES layer mapping.
