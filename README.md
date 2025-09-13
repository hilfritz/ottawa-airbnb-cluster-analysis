# Cluster Analysis of Ottawa Airbnbs

A simple project to showcase Exploratory Data Analysis, Descriptive Analysis Concepts and to demonstrate use of K-Means clustering identify datapoints sharing similar features and group them into clusters.

## Table of Contents
- [Project Overview](#project-overview)
- [Descriptive Analysis](#descriptive-analysis)
  - [Clustering](#clustering)
  - [K-Means Clustering](#k-means-clustering)
  - [Elbow Method](#elbow-method)
  - [Geospatial Visualization](#geospatial-visualization)
- [Data and Sources](#data-and-sources)
- [Data Preparation](#data-preparation)
- [Exploratory Data Analysis (EDA)](#exploratory-data-analysis-eda)
- [Methodology](#methodology)
- [Results](#results)
  - [Visualizations](#visualizations)
    - [Geographical Heatmap of Ottawa Listings](#geographical-heatmap-of-ottawa-listings)
    - [Clustered Listings with Centroids](#clustered-listings-with-centroids)
  - [Findings and Insights](#findings-and-insights)
- [Limitations](#limitations)
- [Next Steps](#next-steps)
- [Reproducibility](#reproducibility)
- [Tools and Libraries](#tools-and-libraries)
- [References and Attribution](#references-and-attribution)
- [Author](#author)



## Project Overview
The goal is to analyze Ottawa Airbnb listings and identify distinct price segments. The workflow covers data collection, cleaning, EDA, clustering, mapping, and interpretation to understand how accommodations are priced across neighborhoods.


## Descriptive Analysis
### Clustering
Unsupervised learning that groups similar observations without predefined labels.

### K-Means Clustering
Iteratively assigns points to **k** centroids and updates centroids by the mean of assigned points, minimizing within-cluster variance.

**Algorithm (high level):**
1. Choose **k** (number of clusters).
2. Initialize centroids.
3. Assign points to nearest centroid.
4. Update centroids as cluster means.
5. Repeat until convergence or iteration limit.

### Elbow Method
Plot **within-cluster sum of squares (WCSS)** vs **k** and choose the “elbow” where marginal gains diminish (bias–variance balance).

### Geospatial Visualization
Mapping latitude/longitude helps interpret whether price segments cluster in specific districts (e.g., downtown premium zones).


## Data and Sources
- Dataset: `DATA AIRBNB.csv` (Ottawa, 2023)
- Source: https://insideairbnb.com/get-the-data/
- Core fields: **price**, **latitude**, **longitude**, plus listing metadata.

---

## Data Preparation
- Removed duplicates and handled missing values.
- Standardized fields (types/formatting) for analysis.
- (Note) Because K-Means is distance-based, feature scaling is important. Price and coordinates should be placed on comparable scales to avoid bias from units.


## Exploratory Data Analysis (EDA)
- **Price distribution:** Assessed central tendency and spread (mean, median, variance).
- **Geography:** Plotted points by latitude/longitude to compare downtown vs. suburban clusters.
- **Outliers:** Flagged unusually high/low prices and addressed them to stabilize clustering.


## Methodology
- **Features:** `price`, `latitude`, `longitude`
- **Clustering:** K-Means (scikit-learn)
- **Model selection:** Elbow Method indicated **k = 3**  
  ![Elbow Method](FIGURES/elbow_method.png)
- **Validation:** Visual inspection on maps and descriptive stats per cluster.


## Results
**Clusters identified:**

| Cluster | Color   | Description                    | Price Range | Avg. Price | Interpretation                                                                 |
|---------|---------|--------------------------------|-------------|------------|---------------------------------------------------------------------------------|
| 2       | 🔴 Red  | High-price accommodations      | $127–$271   | $187.90    | Premium/luxury stays in prime locations; tighter price band                     |
| 1       | 🟡 Yellow | Mid-priced accommodations     | $18–$171    | $86.00     | Broad, heterogeneous segment; mix of budget to moderate options                 |
| 0       | 🟢 Green | Budget accommodations         | $25–$225    | $83.34     | Mostly budget-friendly; includes some higher-priced listings (potential outliers)|

### Visualizations
#### Geographical Heatmap of Ottawa Listings
[Click map to view interactive version](https://hilfritz.github.io/ottawa-airbnb-cluster-analysis/FIGURES/ottawa_airbnb_cluster_heatmap.html)  
[![Geographical Heatmap of the Airbnb listings in Ottawa](SCREENSHOTS/ottawa_listings_heatmap.jpg)](https://hilfritz.github.io/ottawa-airbnb-cluster-analysis/FIGURES/ottawa_airbnb_cluster_heatmap.html)

#### Clustered Listings with Centroids
[Click map to view interactive version](https://hilfritz.github.io/ottawa-airbnb-cluster-analysis/FIGURES/ottawa_clusters_map_with_centroids_legend.html)  
[![Geographical Distribution of Airbnb listings with clusters in Ottawa (with centroids)](SCREENSHOTS/ottawa_clustered_listings.jpg)](https://hilfritz.github.io/ottawa-airbnb-cluster-analysis/FIGURES/ottawa_clusters_map_with_centroids_legend.html)

### Findings and Insights
- **Premium zone (Cluster 2):** Concentrated downtown and high-demand areas; tighter price band suggests consistent product positioning.
- **Mid segment (Cluster 1):** Wide variability implies a mix of room types and locations spanning budget to moderate tiers.
- **Budget segment (Cluster 0):** Broadest range; presence of some higher prices suggests outliers or heterogeneity in listing types.
- **Spatial pattern:** Prices generally increase toward central Ottawa; affordable listings are more dispersed outward.

## Limitations
- **Feature scope:** Only price and coordinates used; omits room type, reviews, availability, etc.
- **Scaling sensitivity:** K-Means is sensitive to feature scaling; improper scaling can bias results.
- **Cluster shape:** K-Means assumes roughly spherical clusters; non-spherical structure may be underfit.
- **Temporal scope:** Single-year snapshot (2023) may not generalize across seasons/years.

## Next Steps
- Add features (room type, number of reviews, availability, minimum nights).
- Try alternative algorithms (DBSCAN, Hierarchical) and compare silhouette scores.
- Build an interactive dashboard for on-the-fly filtering and cluster comparison.
- Conduct temporal analysis (seasonality, events) and pricing elasticity studies.


## Reproducibility
- The **Jupyter Notebook** in the repository contains full EDA, modeling steps, additional figures, and diagnostics supporting this report.
- Ensure Python environment with: `pandas`, `numpy`, `matplotlib`, `seaborn`, `folium`, `scikit-learn`.
- Run notebook cells in order; confirm dataset path to `DATA AIRBNB.csv`.


## Tools and Libraries
- **Python:** pandas, numpy, matplotlib, seaborn, folium, scikit-learn  
- **Environment:** Jupyter Notebook


## References and Attribution
- Data: Inside Airbnb — https://insideairbnb.com/get-the-data/  
- Methodology references: standard clustering/K-Means literature and scikit-learn documentation.


<br/></br></br>
📓 *Note:* The **Jupyter Notebook (`notebook.ipynb`)** contains the full result outputs, including figures, and other supporting analysis.

## Author
**Hilfritz Camallere**  
This project showcases EDA and K-Means clustering to group listings with similar characteristics and interpret spatial pricing patterns in Ottawa.
