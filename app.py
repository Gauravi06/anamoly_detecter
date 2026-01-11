import streamlit as st
import pandas as pd
import plotly.express as px
from modules.rule_engine import detect_fraud_rules
from modules.ml_detector import detect_fraud_ml, combine_detections

# Page config
st.set_page_config(
    page_title="Fake Transaction Detector",
    page_icon="🔍",
    layout="wide"
)

# Title
st.title("🔍 Fake Transaction Detector")
st.markdown("**Team BetaDrift** | Techfiesta'26 | Problem Statement FD003")

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📁 Upload Data")
    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
    
    if st.button("🎲 Use Sample Data"):
        uploaded_file = "sample"
    
    st.markdown("---")
    st.markdown("### 🎯 Detection Settings")
    threshold_amount = st.slider("High Amount Threshold (₹)", 1000, 50000, 10000)
    threshold_frequency = st.slider("High Frequency (txns/hour)", 1, 20, 5)

# Main content
if uploaded_file is not None:
    # Load data
    if uploaded_file == "sample":
        df = pd.read_csv("data/sample_transactions.csv")
    else:
        df = pd.read_csv(uploaded_file)
    
    st.success(f"✅ Loaded {len(df)} transactions")
    
    # Run fraud detection
    with st.spinner('🔍 Analyzing transactions...'):
        # Rule-based detection
        df_rules = detect_fraud_rules(df)
        
        # ML-based detection
        df_ml = detect_fraud_ml(df)
        
        # Combine both methods
        df_analyzed = combine_detections(df_rules, df_ml)
    
    st.success('✅ Analysis complete!')
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Transactions", len(df_analyzed))
    with col2:
        suspicious_count = df_analyzed['is_suspicious'].sum()
        st.metric("🚨 Suspicious", suspicious_count, 
                 delta=f"{(suspicious_count/len(df_analyzed)*100):.1f}%")
    with col3:
        st.metric("Total Amount", f"₹{df_analyzed['amount'].sum():,.2f}")
    with col4:
        high_risk = (df_analyzed['final_risk_level'] == 'High').sum()
        st.metric("⚠️ High Risk", high_risk)
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 All Transactions", "🚨 Suspicious Only", "📈 Analytics"])
    
    with tab1:
        st.subheader("All Transactions")
        st.dataframe(
            df_analyzed[['transaction_id', 'user_id', 'amount', 'timestamp', 
                        'location', 'merchant', 'final_risk_level', 'combined_risk_score', 'fraud_reasons']],
            use_container_width=True
        )
    
    with tab2:
        st.subheader("Suspicious Transactions")
        suspicious_df = df_analyzed[df_analyzed['is_suspicious']]
        
        if len(suspicious_df) > 0:
            st.dataframe(
                suspicious_df[['transaction_id', 'user_id', 'amount', 
                              'location', 'merchant', 'final_risk_level', 'combined_risk_score', 'fraud_reasons']],
                use_container_width=True
            )
        else:
            st.success("✅ No suspicious transactions detected!")
    
    with tab3:
        st.subheader("Risk Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk level pie chart
            risk_counts = df_analyzed['final_risk_level'].value_counts()
            fig_pie = px.pie(
                values=risk_counts.values,
                names=risk_counts.index,
                title='Risk Level Distribution',
                color_discrete_map={'Low': 'green', 'Medium': 'orange', 'High': 'red'}
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Amount distribution
            fig_box = px.box(
                df_analyzed,
                y='amount',
                color='final_risk_level',
                title='Transaction Amounts by Risk Level',
                color_discrete_map={'Low': 'green', 'Medium': 'orange', 'High': 'red'}
            )
            st.plotly_chart(fig_box, use_container_width=True)
        
        # Timeline
        st.subheader("Transaction Timeline")
        fig_timeline = px.scatter(
            df_analyzed,
            x='timestamp',
            y='amount',
            color='final_risk_level',
            size='combined_risk_score',
            hover_data=['transaction_id', 'merchant', 'fraud_reasons'],
            title='Transactions Over Time',
            color_discrete_map={'Low': 'green', 'Medium': 'orange', 'High': 'red'}
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    
else:
    st.info("👆 Upload a CSV file or click 'Use Sample Data' to get started")