# 📦 Amazon India E-Commerce Retail & Fulfilment Optimization

> **Author:** Pankaj Kumar | IBM SkillsBuild Internship  
> **Domain:** E-Commerce Analytics · Retail Intelligence · Supply-Chain Optimization  
> **Dataset:** Amazon India Sales Report — 128,975 transactions (Mar – Jun 2022)

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Dataset Overview](#2-dataset-overview)
3. [Analytical Findings & Key Metrics](#3-analytical-findings--key-metrics)
4. [Repository Architecture](#4-repository-architecture)
5. [Setup & Execution Guide](#5-setup--execution-guide)
6. [Interactive Streamlit Dashboard](#6-interactive-streamlit-dashboard)
7. [Business Recommendations](#7-business-recommendations)
8. [Conclusions](#8-conclusions)

---

## 1. Problem Statement

Amazon India's apparel category operates across a diverse, high-velocity order pipeline spanning multiple fulfilment channels, product categories, and geographies. Actionable intelligence is critical to:

- **Reducing revenue leakage** from a 14.2% cancellation rate (≈ ₹69.19 L in gross transaction value).
- **Optimising fulfilment mix** between Amazon Easy Ship (69.5%) and Merchant-fulfilled (30.5%) channels.
- **Identifying geographic and product concentration risks** to inform inventory placement and promotional marketing spend.
- **Unlocking the B2B segment's premium spend potential** (₹768.41 AOV vs ₹694.03 B2C baseline).

This project delivers an end-to-end data analytics pipeline — from raw data hygiene to a full-featured interactive executive BI dashboard and academic report.

---

## 2. Dataset Overview

| Attribute | Detail |
|---|---|
| **Source** | Amazon India Sales Report (Kaggle) |
| **Period** | 31 March 2022 – 29 June 2022 |
| **Total Records** | 128,975 transactions |
| **Features** | 21 analytical columns (post-cleaning) |
| **Geography** | Pan-India — 39 States & Union Territories |
| **Currency** | Indian Rupee (INR) |

### Key Columns

| Column | Description |
|---|---|
| `Order ID` | Unique transaction identifier |
| `Date` | Order placement date (ISO 8601 standardized) |
| `Status` | Order pipeline state (Shipped, Delivered, Cancelled, etc.)[cite: 3] |
| `Fulfilment` | Channel — `Amazon` (Easy Ship) or `Merchant`[cite: 3] |
| `Category` | Product category (Set, Kurta, Western Dress, etc.)[cite: 3] |
| `Qty` | Units ordered[cite: 3] |
| `Amount` | Net transaction value in INR[cite: 3] |
| `ship-state` | Delivery state (standardised across 39 States/UTs)[cite: 3] |
| `B2B` | Boolean indicator for Enterprise vs Consumer buyers[cite: 3] |

---

## 3. Analytical Findings & Key Metrics

### 3.1 Revenue & Pipeline Summary

| Metric | Value |
|---|---|
| **Gross Transaction Volume (GTV)** | ₹785.93 L[cite: 3] |
| **Cancelled Order Value** | ₹69.19 L (14.2% leakage)[cite: 3] |
| **Net Fulfilled Revenue** | ₹716.73 L[cite: 3] |
| **Total Fulfilled Orders** | 1,03,193[cite: 3] |
| **Total Units Sold** | 1,10,992[cite: 3] |
| **Average Order Value (AOV)** | ₹694.56[cite: 3] |

### 3.2 Product Category Performance

| Rank | Category | Net Revenue | Share |
|---|---|---|---|
| 1 | Set | ₹357.32 L | 49.9%[cite: 3] |
| 2 | Kurta | ₹194.26 L | 27.1%[cite: 3] |
| 3 | Western Dress | ₹102.10 L | 14.2%[cite: 3] |
| 4 | Top | ₹49.04 L | 6.8%[cite: 3] |
| 5 | Ethnic Dress | ₹7.33 L | 1.0%[cite: 3] |

> **Insight:** *Set* and *Kurta* collectively drive **~77% of all net revenue**, indicating high single-category concentration risk[cite: 3].

### 3.3 Geographic Distribution — Top 5 States

| Rank | State | Net Revenue | Share |
|---|---|---|---|
| 1 | Maharashtra | ₹122.25 L | 17.1%[cite: 3] |
| 2 | Karnataka | ₹96.50 L | 13.5%[cite: 3] |
| 3 | Telangana | ₹62.90 L | 8.8%[cite: 3] |
| 4 | Uttar Pradesh | ₹61.87 L | 8.6%[cite: 3] |
| 5 | Tamil Nadu | ₹59.54 L | 8.3%[cite: 3] |

> **Insight:** The top 5 states generate **over 58%** of net revenue, reflecting a strong Western–Southern urban metro cluster[cite: 3].

### 3.4 Fulfilment & Customer Segment Dynamics

| Metric / Dimension | Primary Segment | Secondary Segment | Key Variance |
|---|---|---|---|
| **Fulfilment Method** | Amazon Easy Ship (69.5% \| 89,698 orders)[cite: 3] | Merchant Fulfilled (30.5% \| 39,277 orders)[cite: 3] | Easy Ship exhibits higher SLA consistency[cite: 3] |
| **Buyer Segmentation** | B2C Consumer (AOV ₹694.03)[cite: 3] | B2B Enterprise (AOV ₹768.41)[cite: 3] | **+10.7% Basket Value Premium** in B2B[cite: 3] |

---

## 4. Repository Architecture

```text
Amazon_Sales_Project/
│
├── Amazon Sale Report.csv          # Raw source dataset (128,975 transactions)
├── cleaned_sales_data.csv          # Processed, standardized & imputed analytical dataset
│
├── data_cleaning.py                # Step 1: Automated 5-stage cleaning & 39-state mapping
├── sales_summary.py                # Step 2: Terminal executive summary & ratio computation
├── generate_charts.py              # Step 3: Generates 6 high-res analytical figures (300 DPI)
├── Pankaj_AmazonSales.py           # Step 4: Full interactive Streamlit & Plotly BI application
│
├── Pankaj_ProjectReport.docx       # Formal academic project report with embedded charts & tables
│
├── project_charts/                 # High-resolution visual artifacts
│   ├── chart1_categories.png       # Figure 1: Revenue contribution by category
│   ├── chart2_states.png           # Figure 2: Top shipping states by revenue
│   ├── chart3_fulfilment.png       # Figure 3: Fulfilment channel distribution
│   ├── chart4_status.png           # Figure 4: Order lifecycle & pipeline progression
│   ├── chart5_b2b.png              # Figure 5: B2B vs B2C average order value
│   └── chart6_courier.png          # Figure 6: Logistics carrier dispatch status
│
├── requirements.txt                # Python runtime dependencies
└── README.md                       # Comprehensive project documentation