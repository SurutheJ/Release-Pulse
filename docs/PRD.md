# Product Requirements Document (PRD)

## ReleasePulse: AI-Powered Feedback Intelligence

**Author:** Suruthe Jayachandran  
**Version:** 1.0  
**Last Updated:** January 2026  
**Status:** MVP Complete

---

## Executive Summary

ReleasePulse is an internal PM tool that transforms unstructured app store reviews into prioritized, actionable product insights. It automates theme discovery, regression detection, and backlog prioritization—reducing manual review analysis time by 80% while improving prioritization consistency.

---

## Problem Statement

### Current State

Product Managers at mobile-first companies face a recurring challenge:

1. **Volume**: Thousands of new reviews per release
2. **Noise**: Mixed feedback (praise, complaints, feature requests, spam)
3. **Manual process**: PMs spend 4-8 hours per release reading and categorizing reviews
4. **Inconsistency**: Different PMs prioritize differently based on intuition
5. **Latency**: Issues discovered days/weeks after release

### Impact

| Problem | Business Impact |
|---------|-----------------|
| Slow issue discovery | Regressions impact users longer |
| Inconsistent prioritization | Suboptimal resource allocation |
| Manual effort | PM time diverted from strategic work |
| No historical tracking | Repeated mistakes, persistent debt ignored |

### Opportunity

Automate the feedback-to-insight pipeline to:
- **Reduce time** spent on manual review analysis
- **Improve consistency** with data-driven prioritization
- **Enable proactive** regression detection
- **Track persistent issues** across releases

---

## Target Users

### Primary Persona: Mobile PM

**Name:** Alex, Product Manager  
**Company:** Mobile-first consumer app (10M+ MAU)  
**Responsibilities:** Feature prioritization, release planning, user feedback synthesis

**Pain Points:**
- Spends 5+ hours per release reading reviews
- Struggles to identify what's new vs. what's persistent
- Has no systematic way to prioritize feedback themes
- Often discovers issues from angry user tweets, not reviews

**Goals:**
- Understand release health within 10 minutes
- Identify regressions before they escalate
- Make defensible prioritization decisions
- Track whether fixes actually improved sentiment

### Secondary Persona: Engineering Manager

**Name:** Jordan, Engineering Manager  
**Responsibilities:** Sprint planning, technical debt management

**Needs from ReleasePulse:**
- Prioritized list of issues with effort estimates
- Evidence (user quotes) to justify investments
- Trend data showing if previous fixes worked

---

## User Stories

### Epic 1: Release Health Monitoring

| ID | User Story | Priority |
|----|------------|----------|
| US-1.1 | As a PM, I want to see an executive summary of the latest release so I can quickly assess health | P0 |
| US-1.2 | As a PM, I want to compare pain distribution across versions so I can identify regressions | P0 |
| US-1.3 | As a PM, I want to filter by version so I can focus on specific releases | P1 |

### Epic 2: Theme Discovery

| ID | User Story | Priority |
|----|------------|----------|
| US-2.1 | As a PM, I want reviews auto-clustered into themes so I don't manually categorize | P0 |
| US-2.2 | As a PM, I want to see representative quotes per theme so I can validate clusters | P0 |
| US-2.3 | As a PM, I want to drill into any theme to see all related reviews | P1 |

### Epic 3: Prioritization

| ID | User Story | Priority |
|----|------------|----------|
| US-3.1 | As a PM, I want a ranked priority backlog so I know what to fix first | P0 |
| US-3.2 | As a PM, I want to see regression flags so I can identify release-critical issues | P0 |
| US-3.3 | As a PM, I want to see persistence flags so I can identify tech debt | P0 |
| US-3.4 | As a PM, I want to export the backlog to CSV so I can import into Jira | P2 |

### Epic 4: Trend Analysis

| ID | User Story | Priority |
|----|------------|----------|
| US-4.1 | As a PM, I want to see theme trends over time so I can track improvement | P1 |
| US-4.2 | As a PM, I want to see version-over-version deltas so I can spot sudden changes | P1 |

---

## Functional Requirements

### FR-1: Data Ingestion

| ID | Requirement | Status |
|----|-------------|--------|
| FR-1.1 | System shall accept CSV files with review data | Complete |
| FR-1.2 | System shall parse review content, score, version, and engagement metrics | Complete |
| FR-1.3 | System shall handle missing or malformed data gracefully | Complete |

### FR-2: Theme Clustering

| ID | Requirement | Status |
|----|-------------|--------|
| FR-2.1 | System shall generate semantic embeddings for each review | Complete |
| FR-2.2 | System shall cluster reviews into 6 product themes | Complete |
| FR-2.3 | System shall support multi-label theme assignment | Complete |
| FR-2.4 | System shall weight reviews by severity, impact, and sample size | Complete |

### FR-3: Signal Analysis

| ID | Requirement | Status |
|----|-------------|--------|
| FR-3.1 | System shall calculate normalized pain signal per theme per version | Complete |
| FR-3.2 | System shall flag regressions (>5% signal increase) | Complete |
| FR-3.3 | System shall flag persistent issues (>15% signal in 3+ releases) | Complete |

### FR-4: Prioritization

| ID | Requirement | Status |
|----|-------------|--------|
| FR-4.1 | System shall calculate RICE score for each theme | ✅ Complete |
| FR-4.2 | System shall rank themes by priority score | ✅ Complete |
| FR-4.3 | System shall display effort estimates | ✅ Complete |

### FR-5: Dashboard

| ID | Requirement | Status |
|----|-------------|--------|
| FR-5.1 | Dashboard shall display executive summary metrics | Complete |
| FR-5.2 | Dashboard shall allow version selection | Complete |
| FR-5.3 | Dashboard shall visualize pain distribution by theme | Complete |
| FR-5.4 | Dashboard shall display priority backlog table | Complete |
| FR-5.5 | Dashboard shall allow drilling into raw reviews | Complete |
| FR-5.6 | Dashboard shall explain methodology to users | In Progress (V2) |

---

## Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | Dashboard shall load within 3 seconds | Met |
| NFR-2 | System shall handle 10,000+ reviews | Met |
| NFR-3 | Dashboard shall be responsive on desktop | Met |
| NFR-4 | System shall be deployable via Streamlit Cloud | Met |

---

## Success Metrics

### Primary Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| **Time to Insight** | Time from release to understanding health | <10 minutes |
| **Prioritization Consistency** | Agreement between tool ranking and PM intuition | >80% |
| **Regression Detection Rate** | % of actual regressions flagged by tool | >90% |

### Secondary Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Theme Accuracy | PM agreement that clusters are meaningful | >85% |
| Dashboard Adoption | Weekly active users (internal) | 5+ PMs |
| Export Usage | % of sessions that export backlog | >30% |

---

## Out of Scope (V1)

The following are explicitly **not** included in V1:

| Feature | Reason | Future Version |
|---------|--------|----------------|
| Real-time ingestion | Requires API integration | V2 |
| Slack/Jira integration | Requires auth setup | V2 |
| LLM-generated summaries | Cost and latency concerns | V2 |
| Multi-app comparison | Scope creep | V3 |
| User authentication | Internal tool, single user | V3 |

---

## Roadmap

### V1 (Current) — MVP
- [x] Batch data processing pipeline
- [x] Theme clustering with weighted embeddings
- [x] Regression and persistence detection
- [x] RICE prioritization
- [x] Interactive Streamlit dashboard

### V2 — Enhanced Intelligence
- [~] Methodology explanation in dashboard (in progress)
- [ ] LLM-generated theme summaries
- [ ] CSV export functionality
- [ ] Improved mobile responsiveness

### V3 — Integration & Scale
- [ ] App Store Connect API integration
- [ ] Slack alerts for regressions
- [ ] Jira ticket auto-creation
- [ ] Multi-app support

### V4 — Agentic Workflows
- [ ] Autonomous monitoring agent
- [ ] Natural language querying
- [ ] Predictive analytics

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Clustering produces non-meaningful themes | Medium | High | Manual validation, adjustable k |
| False positive regressions | Medium | Medium | Tunable thresholds, PM review |
| Effort estimates inaccurate | High | Medium | Treat as relative, not absolute |
| Data quality issues | Low | High | Preprocessing, validation |

---

## Appendix

### A. Theme Definitions

| Theme | Description | Example Reviews |
|-------|-------------|-----------------|
| Playback Reliability | Audio playback issues | "Songs skip randomly", "Music stops when I switch apps" |
| Navigation & Home Feed | UI and recommendation issues | "Can't find my playlists", "Home page is cluttered" |
| Library & Playlist Control | Content management | "Can't sort my library", "Playlist shuffle is broken" |
| Free vs Premium Friction | Monetization concerns | "Too many ads", "Premium features should be free" |
| UI & Content Surfaces | Visual and content issues | "New design is ugly", "Podcast UI is confusing" |
| Performance & Media Issues | Speed and media playback | "App is slow", "Downloads fail" |

### B. RICE Formula Details

```
Priority = (Reach × Impact × Confidence) / Effort

Where:
- Reach = 0.6 × Normalized_Signal + 0.4 × Review_Volume_Ratio
- Impact = (5 - Avg_Rating) / 4 × Regression_Multiplier × Persistence_Multiplier
- Confidence = 0.7 × Review_Volume_Ratio + 0.3 × Is_Persistent
- Effort = Manual estimate (1-5)
```

### C. Glossary

| Term | Definition |
|------|------------|
| Pain Signal | Weighted sum of negative feedback for a theme |
| Normalized Signal | Theme pain as % of total version pain |
| Regression | Significant increase in pain signal vs. previous version |
| Persistence | Theme consistently high across multiple releases |
| RICE | Reach, Impact, Confidence, Effort framework |
