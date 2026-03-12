# Transaction Anomaly Detector

A hybrid financial fraud detection system that combines rule-based logic with machine learning to flag suspicious transactions efficiently.

#Features

Upload a CSV file of transactions or use the built-in sample dataset.

Rule-based detection flags transactions based on:

Unusually high amounts (configurable threshold) 

Micro-transactions (< ₹1) 

High-risk merchant categories (e.g., Online Gambling, Cryptocurrency) 
High transaction frequency per user (configurable threshold) 

ML-based detection using Isolation Forest to identify anomalies based on:

Amount

Time of day

Day of week

User transaction count

Combined risk scoring from both methods for more accurate detection. 

Interactive Streamlit dashboard with visualizations for easy insights. 

🛠 Tech Stack

Python 

Streamlit for interactive dashboards

Scikit-learn (Isolation Forest)

Pandas & NumPy for data manipulation

Plotly for visualizations

How to Run
# Clone the repository
git clone https://github.com/Gauravi06/anamoly_detecter.git
cd anamoly_detecter

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py

Tip: Before pushing to GitHub, remove the venv/ folder to avoid bloating the repo:

git rm -r --cached venv
Input Format

Upload a CSV with the following columns:

user_id, timestamp, amount, merchant, category

A sample dataset is included at: data/sample_transactions.csv.

Project Status

Functional — developed as part of Techfiesta'26 (Problem Statement FD003).

