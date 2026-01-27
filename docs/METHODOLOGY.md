# Methodology & Technical Decisions

This document explains the technical approach, PM reasoning, and key decisions behind ReleasePulse.

---

## Table of Contents

1. [Overview](#overview)
2. [Data Pipeline](#data-pipeline)
3. [Weighting System](#weighting-system)
4. [Theme Clustering](#theme-clustering)
5. [Regression & Persistence Detection](#regression--persistence-detection)
6. [RICE Prioritization](#rice-prioritization)
7. [Key Decisions & Trade-offs](#key-decisions--trade-offs)

---

## Overview

ReleasePulse answers three core PM questions:

| Question | How ReleasePulse Answers It |
|----------|----------------------------|
| Where is user pain coming from? | Theme clustering with weighted embeddings |
| Is this a new regression or persistent debt? | Version-over-version signal tracking |
| What should we fix next? | RICE-style prioritization scoring |

---

## Data Pipeline

### Step 1: Data Collection
- Source: App store reviews (Google Play)
- Scope: Spotify app reviews across multiple release versions
- Fields: `content`, `score`, `thumbsUpCount`, `reviewCreatedVersion`

### Step 2: Text Preparation
- Lowercase normalization
- URL removal
- Whitespace normalization
- No aggressive stemming (preserves semantic meaning for embeddings)

### Step 3: Embedding & Clustering
- Generate dense vector representations
- Cluster into product themes
- Assign multi-label themes via cosine similarity

### Step 4: Signal Analysis
- Track theme signals across versions
- Detect regressions and persistence

### Step 5: Prioritization
- Calculate RICE scores
- Generate ranked backlog

---

## Weighting System

### Why Weight Reviews?

Not all reviews are equal. A 1-star review with 50 thumbs-up from the latest version carries more signal than a 3-star review with no engagement from an old release.

### Weight Components

#### 1. Severity Weight
```python
severity_weight = 6 - score  # Range: 1-5
```
- 1-star review → weight of 5
- 5-star review → weight of 1
- **Rationale**: Low ratings indicate pain; we want pain-focused clustering

#### 2. Impact Weight (Social Validation)
```python
impact_weight = 1 + (thumbs_up / max_thumbs_up)  # Range: 1-2
```
- Reviews with more "helpful" votes get higher weight
- **Rationale**: Community-validated feedback is more representative

#### 3. Version Weight (Sample Size Normalization)
```python
version_weight = version_count / max_version_count  # Range: 0-1
```
- Versions with more reviews get higher weight
- **Rationale**: Prevents over-indexing on low-sample releases

#### 4. Final Weight
```python
final_weight = severity_weight × impact_weight × version_weight
```

### Trade-off Considered
- **Alternative**: Use only severity weight
- **Decision**: Multiplicative weights because we want reviews that are severe AND validated AND from well-sampled releases

---

## Theme Clustering

### Approach: Weighted Embedding Clustering

#### Step 1: Generate Embeddings
```python
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(reviews)
```

**Why all-MiniLM-L6-v2?**
- Fast inference (384 dimensions)
- Strong semantic similarity performance
- Well-suited for short text (reviews average 50-100 words)

#### Step 2: Apply Weights Before Clustering
```python
X_weighted = embeddings * final_weight.reshape(-1, 1)
X_normalized = normalize(X_weighted)
```

**Why weight before clustering?**
- Ensures high-pain reviews "pull" cluster centroids toward pain topics
- Without weighting, neutral 5-star reviews dilute theme focus

#### Step 3: KMeans Clustering
```python
kmeans = KMeans(n_clusters=6, random_state=42)
theme_ids = kmeans.fit_predict(X_weighted)
```

**Why 6 clusters?**
- Empirically tested 4, 6, 8, 10 clusters
- 6 provided the best balance of:
  - **Interpretability**: Each theme maps to a clear product area
  - **Distinctiveness**: Minimal overlap between themes
  - **Coverage**: All major pain areas represented

#### Step 4: Multi-Label Assignment
```python
def assign_themes(embedding, centroids, threshold=0.35):
    labels = []
    for theme, centroid in centroids.items():
        similarity = cosine_similarity(embedding, centroid)
        if similarity >= threshold:
            labels.append(theme)
    return labels
```

**Why multi-label?**
- Reviews often mention multiple issues ("app crashes AND ads are annoying")
- Single-label assignment loses this signal
- Threshold of 0.35 balances precision/recall

### Resulting Themes

| Theme ID | Label | Description |
|----------|-------|-------------|
| 0 | Playback Reliability | Crashes, buffering, songs not playing |
| 1 | Navigation & Home Feed | UI navigation, homepage recommendations |
| 2 | Library & Playlist Control | Playlist management, library organization |
| 3 | Free vs Premium Friction | Ads, premium features, upgrade prompts |
| 4 | UI & Content Surfaces | Visual design, content discovery |
| 5 | Performance & Media Issues | App speed, downloads, offline mode |

---

## Regression & Persistence Detection

### Regression Detection

**Definition**: A theme is flagged as a regression if its pain share increases significantly in the latest release.

```python
REGRESSION_THRESHOLD = 0.05  # 5% increase

normalized_signal = theme_weight / version_total_weight
delta = current_signal - previous_signal
is_regression = delta > REGRESSION_THRESHOLD
```

**Why 5%?**
- Sensitive enough to catch meaningful shifts
- Not so sensitive that noise triggers false alarms
- Based on observed variance in historical data

### Persistence Detection

**Definition**: A theme is persistent if it consistently represents a large share of user pain across multiple releases.

```python
PERSISTENCE_THRESHOLD = 0.15  # 15% of version pain
MIN_RELEASES = 3

high_signal_count = sum(signal > PERSISTENCE_THRESHOLD for each release)
is_persistent = high_signal_count >= MIN_RELEASES
```

**Why these thresholds?**
- **15%**: A theme capturing 1/6+ of pain is significant
- **3 releases**: Rules out one-time spikes; indicates systemic issue

### PM Interpretation

| Flag | What It Means | Recommended Action |
|------|---------------|-------------------|
| Regression Only | New issue introduced in latest release | Investigate recent changes; potential hotfix |
| Persistent Only | Long-standing tech debt | Plan for larger investment; not urgent |
| Both | Worsening chronic issue | High priority; requires immediate attention |

---

## RICE Prioritization

### Formula

```python
Priority_Score = (Reach × Impact × Confidence) / Effort
```

### Component Definitions

#### Reach (0-1)
How many users are affected?

```python
Reach = 0.6 × Normalized_Signal + 0.4 × (Review_Count / Max_Review_Count)
```

- Combines pain share (signal) with volume (count)
- 60/40 weighting favors intensity over volume

#### Impact (0-1.44)
How severe is the pain?

```python
Impact = (5 - Avg_Rating) / 4

# Multipliers for special cases
if is_regression: Impact *= 1.2
if is_persistent: Impact *= 1.2
```

- Base: Inverted average rating (lower = more impact)
- Boosted 20% for regressions (release risk)
- Boosted 20% for persistence (accumulated debt)

#### Confidence (0-1)
How reliable is this signal?

```python
Confidence = 0.7 × (Review_Count / Max_Count) + 0.3 × Is_Persistent
```

- More reviews = higher confidence
- Persistent issues have validated signal

#### Effort (1-5)
Estimated implementation effort (manually assigned)

| Effort | Description |
|--------|-------------|
| 1 | Quick fix, config change |
| 2 | Small feature, UI tweak |
| 3 | Medium feature, backend change |
| 4 | Large feature, infrastructure |
| 5 | Major initiative, architecture |

### Effort Estimation Rationale

| Theme | Effort | Reasoning |
|-------|--------|-----------|
| Playback Reliability | 4 | Core audio infrastructure is complex |
| Navigation & Home Feed | 3 | UI changes, A/B testing required |
| Library & Playlist Control | 3 | Database and sync considerations |
| Free vs Premium Friction | 2 | Mostly copy/UX changes |
| UI & Content Surfaces | 2 | Frontend-focused changes |
| Performance & Media Issues | 4 | Optimization requires deep profiling |

---

## Key Decisions & Trade-offs

### Decision 1: Weighted vs. Unweighted Clustering

| Option | Pros | Cons |
|--------|------|------|
| **Unweighted** | Simpler, all reviews equal | 5-star reviews dilute pain signal |
| **Weighted** (chosen) | Pain-focused themes | Complexity, potential bias |

**Choice**: Weighted clustering because the goal is pain identification, not general sentiment.

### Decision 2: KMeans vs. Hierarchical Clustering

| Option | Pros | Cons |
|--------|------|------|
| **KMeans** (chosen) | Fast, interpretable, stable | Requires pre-specifying k |
| **Hierarchical** | No k needed, dendrogram | Slower, harder to interpret |

**Choice**: KMeans for speed and PM-friendly outputs. The fixed k=6 was validated empirically.

### Decision 3: Single-Label vs. Multi-Label Themes

| Option | Pros | Cons |
|--------|------|------|
| **Single-label** | Simpler analysis | Loses multi-issue reviews |
| **Multi-label** (chosen) | Captures complexity | Slightly inflated counts |

**Choice**: Multi-label because user complaints often span multiple areas.

### Decision 4: Regression Threshold (5%)

| Threshold | Sensitivity | False Positive Risk |
|-----------|-------------|---------------------|
| 3% | High | High |
| **5%** (chosen) | Balanced | Moderate |
| 10% | Low | Low |

**Choice**: 5% balances catching real regressions without noise.

---

## Limitations & Future Improvements

### Current Limitations
1. **Manual effort estimation**: Could be automated with historical ticket data
2. **Static analysis**: No real-time monitoring
3. **English only**: Embeddings trained primarily on English text
4. **No causal analysis**: Correlation, not causation

### Planned Improvements
1. **LLM-generated theme summaries**: Auto-generate human-readable descriptions
2. **Automated effort estimation**: Train on historical Jira data
3. **Anomaly detection**: Real-time alerts for sudden sentiment shifts
4. **Multi-language support**: Use multilingual embeddings

---

## References

- Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks
- RICE Scoring Framework: Intercom Product Management
- App Review Analysis: Academic literature on mobile app feedback mining
