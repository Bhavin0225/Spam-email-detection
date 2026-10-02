import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv

# Add parent directory to path to enable loading app modules if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environmental configurations
load_dotenv()

# MongoDB connection configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27018")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "phishing_detection_db")

@st.cache_resource
def get_db_client():
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2000)
        # Verify connection
        client.admin.command('ping')
        return client
    except Exception as e:
        st.error(f"Failed to connect to MongoDB at {MONGODB_URI}. Error: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="Spam Detection Admin Console",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🛡️ Spam Email Detection Console")
    st.subheader("Operational Analytics & Admin Desk")
    st.markdown("---")

    client = get_db_client()
    if not client:
        st.warning("Database offline. Please check your MongoDB connection settings in .env.")
        st.info("Make sure the MongoDB service is running (e.g. locally or via docker compose).")
        return

    db = client[MONGODB_DATABASE]

    # Sidebar controls
    st.sidebar.header("Configuration")
    st.sidebar.markdown(f"**Database:** `{MONGODB_DATABASE}`")
    st.sidebar.markdown(f"**URI Host:** `{MONGODB_URI.split('@')[-1] if '@' in MONGODB_URI else MONGODB_URI}`")

    refresh = st.sidebar.button("🔄 Refresh Data", use_container_width=True)
    if refresh:
        st.cache_data.clear()

    # Load collections
    predictions_col = db["predictions"]
    feedback_col = db["feedback"]
    model_col = db["model_metadata"]
    emails_col = db["emails"]

    # Calculate high level statistics
    total_predictions = predictions_col.count_documents({})
    total_feedback = feedback_col.count_documents({})
    approved_feedback = feedback_col.count_documents({"status": "approved"})
    pending_feedback = feedback_col.count_documents({"status": "pending"})

    # Fetch active model details
    active_model = model_col.find_one({"deployed": True})
    active_version = active_model["model_version"] if active_model else "N/A"
    active_precision = active_model.get("precision", 0.0) if active_model else 0.0
    active_recall = active_model.get("recall", 0.0) if active_model else 0.0

    # Calculate spam rate
    spam_count = predictions_col.count_documents({"prediction_label": "suspicious"})
    spam_rate = (spam_count / total_predictions * 100) if total_predictions > 0 else 0.0

    # Metrics Layout Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Scanned Volume", f"{total_predictions:,}")
    with col2:
        st.metric("Average Spam Rate", f"{spam_rate:.1f}%")
    with col3:
        st.metric("Active Model Version", active_version)
    with col4:
        st.metric("Model Precision / Recall", f"{active_precision*100:.1f}% / {active_recall*100:.1f}%")

    st.markdown("---")

    # Content Layout Columns
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.subheader("📈 Classification Trends over Time")
        
        # Pull predictions count by date
        pipeline = [
            {
                "$project": {
                    "date": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$created_at"
                        }
                    },
                    "is_spam": {
                        "$cond": [{"$eq": ["$prediction_label", "suspicious"]}, 1, 0]
                    },
                    "is_ham": {
                        "$cond": [{"$eq": ["$prediction_label", "legitimate"]}, 1, 0]
                    }
                }
            },
            {
                "$group": {
                    "_id": "$date",
                    "Spam": {"$sum": "$is_spam"},
                    "Legitimate": {"$sum": "$is_ham"},
                    "Total": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}},
            {"$limit": 30}
        ]
        
        trends = list(predictions_col.aggregate(pipeline))
        if trends:
            df_trends = pd.DataFrame(trends).rename(columns={"_id": "Date"}).set_index("Date")
            st.area_chart(df_trends[["Spam", "Legitimate"]])
        else:
            st.info("No time series prediction logs found.")

        # Flagged Domains Chart
        st.subheader("🚩 Top Flagged Suspicious Domains")
        pipeline_domains = [
            {
                "$lookup": {
                    "from": "emails",
                    "localField": "email_id",
                    "foreignField": "email_id",
                    "as": "email"
                }
            },
            {"$unwind": "$email"},
            {"$match": {"prediction_label": "suspicious"}},
            {
                "$group": {
                    "_id": "$email.sender_domain",
                    "Flagged Scans": {"$sum": 1}
                }
            },
            {"$sort": {"Flagged Scans": -1}},
            {"$limit": 10}
        ]
        
        domains = list(predictions_col.aggregate(pipeline_domains))
        if domains:
            df_domains = pd.DataFrame(domains).rename(columns={"_id": "Domain"}).set_index("Domain")
            st.bar_chart(df_domains)
        else:
            st.info("No flagged domains found in prediction logs.")

    with right_col:
        st.subheader("📝 Correction Feedback Queue")
        
        # Feedback details card
        st.markdown(f"""
        - **Total Corrections Logged:** `{total_feedback}`
        - **Approved corrections (Retraining candidates):** `{approved_feedback}`
        - **Pending reviews:** `{pending_feedback}`
        """)

        # Feedback approval progress bar
        retrain_progress = min(approved_feedback / 10.0, 1.0)
        st.progress(retrain_progress, text=f"Retraining Progress: {approved_feedback}/10 approved corrections")
        if approved_feedback >= 10:
            st.success("🎉 Retraining threshold reached! Automated pipeline triggered in background.")
        
        # Model Registry list
        st.subheader("📦 Model Performance Registry")
        models = list(model_col.find({}).sort("created_at", -1))
        if models:
            for m in models:
                status_icon = "🟢 Deployed" if m.get("deployed") else "⚪ Inactive"
                st.markdown(f"""
                **Version:** `{m['model_version']}` ({status_icon})  
                - **Algorithm:** {m['algorithm']}  
                - **Precision / Recall:** `{m['precision']:.4f}` / `{m['recall']:.4f}`  
                - **F1-Score / AUC:** `{m['f1_score']:.4f}` / `{m['auc_roc']:.4f}`  
                - **Threshold:** `{m['threshold']:.2f}`  
                - **Created:** {m['created_at'].strftime('%Y-%m-%d %H:%M:%S')}  
                ---
                """)
        else:
            st.info("No model metadata registry records found.")

if __name__ == "__main__":
    main()
