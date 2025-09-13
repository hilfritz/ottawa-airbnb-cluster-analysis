# Cluster Analysis of Ottawa Airbnbs
A simple project to showcase Exploratory Data Analysis and to demonstrate use of K-Means clustering identify datapoints sharing similar features and group them into clusters.

## Table of Contents
- [Project Overview](#project-overview)
- [Data Collection](#data-collection)
- [Exploratory Data Analysis (EDA)](#exploratory-data-analysis-eda)
- [Background Concepts](#background-concepts)
- [Clustering](#clustering)
- [Visualization](#visualization-plots-and-heatmaps-showing-geographic-distribution-of-clusters)
- [Findings & Insights](#findings--insights)
- [Tools & Libraries Used](#tools--libraries-used)
- [Next Steps](#next-steps)
- [Author](#author)

---

## Project Overview
This project analyzes Airbnb listings in Ottawa to identify distinct price clusters using data science techniques. 
The workflow covers data collection, cleaning, exploratory data analysis (EDA), clustering, and final insights. 
It aims to provide a clear picture of how Airbnb accommodations are priced across different neighborhoods in Ottawa.

---

## Data Collection
- Dataset: `DATA AIRBNB.csv` (Airbnb listings in Ottawa in 2023).
  - Dataset taken from : https://insideairbnb.com/get-the-data/
- Key variables include **price**, **latitude**, **longitude**, and other listing details.
- Data cleaning was performed to handle missing values, remove duplicates, and standardize formats.

---

## Exploratory Data Analysis (EDA)
- **Price distribution** was examined to understand the spread of Airbnb rates across Ottawa.
- **Geographical visualization**: Plotted listings on a map to see price concentration in downtown vs suburban areas.
- **Outlier detection**: Identified unusually high/low listings and treated them accordingly.
- **Descriptive statistics**: Mean, median, and variance of prices across the dataset.

---

## Background Concepts

### What is Clustering?
Clustering is an **unsupervised machine learning technique** used to group data points that share similar characteristics. Unlike supervised learning, it does not rely on predefined labels; instead, it identifies natural groupings within the data.

### K-Means Clustering
K-Means is one of the most widely used clustering algorithms.  
- **How it works**:  
  1. Choose the number of clusters (**k**).  
  2. Randomly initialize cluster centers (called centroids).  
  3. Assign each data point to the nearest centroid.  
  4. Recalculate centroids as the mean of assigned points.  
  5. Repeat until centroids stabilize or a maximum number of iterations is reached.  
- **Goal**: Minimize the **within-cluster variance** (distance between points and their cluster center).  

It’s especially effective when clusters are roughly spherical and well-separated, as in geographical pricing data.

### Elbow Method
The **elbow method** is a heuristic to determine the optimal number of clusters (**k**).  
- Plot the **within-cluster sum of squares (WCSS)** against the number of clusters.  
- The point where the curve bends (like an "elbow") suggests the best value for k, balancing accuracy with simplicity.

### Outlier Detection
Outliers are data points that deviate significantly from others. Detecting and handling outliers ensures that clustering results are not skewed by unusual values (e.g., a single Airbnb priced at $5,000 per night).

### Geographical Visualization
By plotting **latitude and longitude**, you can overlay clusters on a city map. This makes it easier to interpret whether certain price segments are concentrated in specific neighborhoods (e.g., luxury stays in downtown Ottawa).

---

## Clustering
- **Methodology**: Applied K-Means clustering using **price, latitude, and longitude** as features.
- **Number of clusters**: Determined optimal clusters using the **elbow method** and selected **3 clusters**.
  - ![Elbow Method](FIGURES/elbow_method.png)
- **Clusters identified**:
    | Cluster | Color  | Description                   | Price Range | Avg. Price | Interpretation |
    |---------|--------|-------------------------------|-------------|------------|----------------|
    | 2       | 🔴 Red   | High Price accommodations     | $127 – $271 | $187.9     | Narrow range → Premium or luxury stays, entire homes/apartments in prime locations |
    | 1       | 🟡 Yellow | Mid Priced accommodations     | $18 – $171  | $86.0      | Wide range → Mix of budget-friendly & moderately priced stays, some very affordable options |
    | 0       | 🟢 Green  | Cheap / Budget accommodations | $25 – $225  | $83.34     | Very wide range → Mostly budget-friendly stays, but includes some higher-priced listings |

---

## Visualization: Plots and heatmaps showing geographic distribution of clusters.

### Geographical Heatmap of the Airbnb listings in Ottawa
[Click map to view interactive version](https://hilfritz.github.io/ottawa-airbnb-cluster-analysis/FIGURES/ottawa_airbnb_cluster_heatmap.html)  
[![Geographical Heatmap of the Airbnb listings in Ottawa](SCREENSHOTS/ottawa_listings_heatmap.jpg)](https://hilfritz.github.io/ottawa-airbnb-cluster-analysis/FIGURES/ottawa_airbnb_cluster_heatmap.html)

### Geographical Distribution of Airbnb listings with clusters in Ottawa (with centroids)
[Click map to view interactive version](https://hilfritz.github.io/ottawa-airbnb-cluster-analysis/FIGURES/ottawa_clusters_map_with_centroids_legend.html)  
[![Geographical Distribution of Airbnb listings with clusters in Ottawa (with centroids)](SCREENSHOTS/ottawa_clustered_listings.jpg)](https://hilfritz.github.io/ottawa-airbnb-cluster-analysis/FIGURES/ottawa_clusters_map_with_centroids_legend.html)

---

## Findings & Insights
- **Cluster 2 (High Price)**: Concentrated in prime locations, likely luxury homes/apartments.
- **Cluster 1 (Mid Price)**: Represents a mix of budget and moderately priced listings with wide variability.
- **Cluster 0 (Low Price)**: Surprisingly includes some higher-priced outliers, possibly due to irregularities in listing descriptions or cleaning steps.
- **Overall trend**: Prices increase towards central/downtown Ottawa, while affordable listings are more scattered in outer neighborhoods.

---

## Tools & Libraries Used
- **Python**: Pandas, NumPy, Matplotlib, Seaborn, Folium, Scikit-learn.
- **Notebook Environment**: Jupyter Notebook.

---

## Next Steps
- Enhance dataset with more features (room type, number of reviews, availability).
- Experiment with other clustering algorithms (DBSCAN, Hierarchical Clustering).
- Build an interactive dashboard for users to explore clusters dynamically.

---

## Author
Hilfritz Camallere  
A simple project to showcase Exploratory Data Analysis and to demonstrate use of K-Means clustering identify datapoints sharing similar features and group them into clusters.
