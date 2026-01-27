# ReleasePulse

**AI-Powered Feedback Intelligence for Product Roadmaps**

> Transform noisy app store reviews into actionable release insights and prioritized roadmap decisions.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## Problem Statement

Product Managers spend **hours manually reading app reviews** to understand user sentiment, identify regressions, and prioritize fixes. This process is:
- **Time-consuming**: Thousands of reviews per release
- **Subjective**: Different PMs may interpret feedback differently
- **Reactive**: Issues are often discovered too late

**ReleasePulse automates this entire workflow.**

---

## Solution Overview

ReleasePulse is an end-to-end ML pipeline that:

1. **Clusters user feedback** into meaningful product themes using NLP embeddings
2. **Detects regressions** by tracking theme signals across releases
3. **Identifies persistent pain** that spans multiple versions
4. **Generates a prioritized backlog** using RICE-style scoring

### Key Features

| Feature | Description |
|---------|-------------|
| **Theme Discovery** | Automatically clusters reviews into 6 product areas using sentence embeddings |
| **Regression Detection** | Flags themes with 5%+ increase in pain share between releases |
| **Persistence Tracking** | Identifies issues appearing in 3+ consecutive releases |
| **RICE Prioritization** | Ranks themes by Reach × Impact × Confidence ÷ Effort |
| **Interactive Dashboard** | Explore data by version, theme, and drill into raw reviews |

---

## Screenshots

### Executive Summary
High-level view of the latest release with key pain metrics.

### Priority Roadmap
RICE-scored backlog with regression and persistence flags.

### Theme Deep Dive
Explore raw user feedback with weighted impact scores.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| **NLP Embeddings** | `sentence-transformers` (all-MiniLM-L6-v2) |
| **Clustering** | Weighted KMeans |
| **Data Processing** | Pandas, NumPy, scikit-learn |
| **Visualization** | Plotly, Streamlit |
| **Dashboard** | Streamlit |

---

## Project Structure

```
ReleasePulse/
├── README.md                 # You are here
├── Dashboard.py              # Main Streamlit dashboard
├── Dashboard_v2.py           # Enhanced dashboard with methodology
├── requirements.txt          # Python dependencies
│
├── docs/
│   ├── METHODOLOGY.md        # Technical approach & PM reasoning
│   └── PRD.md                # Product Requirements Document
│
├── notebooks/
│   ├── Step1_Data collection.ipynb
│   ├── Step2_Text Preparation & Weighting.ipynb
│   ├── Step3_Embedding & Clustering.ipynb
│   ├── Step4_Theme-Level Regression & Persistence Detection.ipynb
│   └── Step5_Prioritization Agent.ipynb
│
└── data/
    ├── UserFeedbackData.csv
    ├── spotify_prepared_for_agents.csv
    ├── spotify_reviews_multilabel.csv
    ├── spotify_reviews_with_base_themes.csv
    ├── priority_backlog.csv
    ├── theme_persistence.csv
    └── theme_version_signal.csv
```

---

## Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/SurutheJ/Projects.git
cd ReleasePulse

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run Dashboard.py

# Or run the enhanced version
streamlit run Dashboard_v2.py
```

---

## Methodology Highlights

### 1. Weighted Feedback Scoring
Each review is weighted by:
- **Severity** (5 - star rating): Low ratings = higher pain
- **Social validation** (thumbs up count): Liked reviews matter more
- **Sample size** (version review count): Normalize across releases

### 2. Theme Clustering
- Generate embeddings using `all-MiniLM-L6-v2`
- Apply weights before clustering for pain-focused themes
- Use cosine similarity for multi-label assignment

### 3. Regression & Persistence Detection
- **Regression**: Theme's pain share increases >5% vs. previous release
- **Persistence**: Theme exceeds 15% pain share in 3+ releases

### 4. RICE Prioritization
```
Priority Score = (Reach × Impact × Confidence) / Effort
```

See [METHODOLOGY.md](docs/METHODOLOGY.md) for detailed technical documentation.

---

## Sample Insights

From analyzing 1,000+ Spotify app reviews:

| Finding | Recommendation |
|---------|----------------|
| **Playback Reliability** is persistent across 4 releases | Prioritize core audio infrastructure |
| **Navigation & Home Feed** shows regression in v8.9.x | Investigate recent UI changes |
| **Free vs Premium Friction** has low effort, high reach | Quick win for conversion optimization |

---

## 🗺️ Future Roadmap

- [ ] **LLM-generated summaries** for each theme
- [ ] **Slack/Jira integration** for automated ticket creation
- [ ] **Real-time ingestion** from App Store Connect API
- [ ] **Competitive analysis** comparing sentiment across apps
- [ ] **Agentic workflows** for autonomous monitoring and alerts

---

## Documentation

- [Methodology & Technical Decisions](docs/METHODOLOGY.md)
- [Product Requirements Document](docs/PRD.md)

---

## Author

**Suruthe Jayachandran**

This project demonstrates PM-minded thinking through technical execution—combining NLP, data science, and product intuition to solve a real workflow problem.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
