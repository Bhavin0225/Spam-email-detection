import os
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, classification_report
import joblib
from app.database.collections import get_collection
from app.ml.feature_engine import FeatureExtractor
from app.utils.logger import logger

def load_splits_data():
    """
    Loads emails from the database emails collection and returns splits
    (train_emails, val_emails, test_emails).
    """
    emails_collection = get_collection("emails")
    
    train_emails = list(emails_collection.find({"split": "train"}))
    val_emails = list(emails_collection.find({"split": "validation"}))
    test_emails = list(emails_collection.find({"split": "test"}))
    
    logger.info(f"Loaded database splits: Train={len(train_emails)}, Val={len(val_emails)}, Test={len(test_emails)}")
    return train_emails, val_emails, test_emails

def optimize_decision_threshold(model, X_val, y_val, default_threshold: float = 0.65) -> float:
    """
    Finds the decision threshold (from 0.30 to 0.90 in step of 0.05) that maximizes
    precision while maintaining recall >= 0.70 on the validation set.
    """
    probs = model.predict_proba(X_val)[:, 1]
    
    best_threshold = default_threshold
    best_precision = 0.0
    
    thresholds = np.arange(0.30, 0.91, 0.05)
    valid_thresholds_found = False
    
    for t in thresholds:
        preds = (probs >= t).astype(int)
        # Handle zero division warnings gracefully
        precision = precision_score(y_val, preds, zero_division=0)
        recall = recall_score(y_val, preds, zero_division=0)
        
        logger.debug(f"Scan Threshold {t:.2f}: Precision = {precision:.4f}, Recall = {recall:.4f}")
        
        if recall >= 0.70:
            valid_thresholds_found = True
            if precision > best_precision:
                best_precision = precision
                best_threshold = float(t)
                
    if not valid_thresholds_found:
        logger.warning("No threshold satisfied the recall >= 0.70 constraint. Optimizing for F1 score instead.")
        best_f1 = 0.0
        for t in thresholds:
            preds = (probs >= t).astype(int)
            f1 = f1_score(y_val, preds, zero_division=0)
            if f1 > best_f1:
                best_f1 = f1
                best_threshold = float(t)
                
    logger.info(f"Optimized Decision Threshold selected: {best_threshold:.2f} (Val Precision: {best_precision:.4f})")
    return best_threshold

def run_training_pipeline(model_version: str = "v1.0.0", models_dir: str = "models"):
    """
    Runs the complete ML training pipeline:
    1. Loads datasets from MongoDB.
    2. Instantiates/loads the FeatureExtractor.
    3. Transforms email splits to feature matrices.
    4. Trains and evaluates Multinomial Naive Bayes (TF-IDF features only).
    5. Trains and evaluates Logistic Regression (All features).
    6. Trains and evaluates XGBoost (All features).
    7. Optimizes decision threshold for XGBoost.
    8. Serializes and saves production XGBoost model to disk.
    9. Logs model metadata statistics in MongoDB.
    """
    # 1. Load Split Data
    train_emails, val_emails, test_emails = load_splits_data()
    
    if len(train_emails) == 0 or len(val_emails) == 0 or len(test_emails) == 0:
        raise ValueError("Cannot train models: one or more dataset splits is empty in the database.")
        
    y_train = np.array([e["label"] for e in train_emails], dtype=np.int32)
    y_val = np.array([e["label"] for e in val_emails], dtype=np.int32)
    y_test = np.array([e["label"] for e in test_emails], dtype=np.int32)
    
    # 2. Setup/Load FeatureExtractor
    extractor_path = os.path.join(models_dir, model_version)
    extractor = FeatureExtractor(max_subject_features=1000, max_body_features=3000)
    
    if os.path.exists(os.path.join(extractor_path, "subject_vectorizer.pkl")):
        logger.info(f"Loading pre-fit FeatureExtractor from: {extractor_path}")
        extractor.load(extractor_path)
    else:
        logger.info("Fitted FeatureExtractor not found on disk. Re-fitting on training split...")
        extractor.fit(train_emails)
        extractor.save(extractor_path)
        
    # 3. Transform Email Data Splits
    logger.info("Transforming email dataset splits to features...")
    X_train = extractor.transform_batch(train_emails)
    X_val = extractor.transform_batch(val_emails)
    X_test = extractor.transform_batch(test_emails)
    
    # Vocabulary sizes
    num_subject_features = len(extractor.subject_vectorizer.vocabulary_)
    num_body_features = len(extractor.body_vectorizer.vocabulary_)
    num_tfidf_features = num_subject_features + num_body_features
    
    logger.info(f"Feature Vector sizes: TF-IDF={num_tfidf_features} (Subject={num_subject_features}, Body={num_body_features}), Handcrafted=16")
    
    # 4. Progressive Baseline 1: Naive Bayes (TF-IDF features only)
    logger.info("Training Baseline 1: Multinomial Naive Bayes (TF-IDF Only)...")
    X_train_tfidf = X_train[:, :num_tfidf_features]
    X_test_tfidf = X_test[:, :num_tfidf_features]
    
    nb_model = MultinomialNB()
    nb_model.fit(X_train_tfidf, y_train)
    nb_preds = nb_model.predict(X_test_tfidf)
    
    nb_precision = precision_score(y_test, nb_preds, zero_division=0)
    nb_recall = recall_score(y_test, nb_preds, zero_division=0)
    nb_f1 = f1_score(y_test, nb_preds, zero_division=0)
    
    logger.info("--- Baseline 1 (Naive Bayes) Test Metrics ---")
    logger.info(f"  Precision: {nb_precision:.4f}, Recall: {nb_recall:.4f}, F1-Score: {nb_f1:.4f}")
    
    # 5. Progressive Baseline 2: Logistic Regression (All features)
    logger.info("Training Baseline 2: Logistic Regression (All features)...")
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train, y_train)
    lr_preds = lr_model.predict(X_test)
    
    lr_precision = precision_score(y_test, lr_preds, zero_division=0)
    lr_recall = recall_score(y_test, lr_preds, zero_division=0)
    lr_f1 = f1_score(y_test, lr_preds, zero_division=0)
    
    logger.info("--- Baseline 2 (Logistic Regression) Test Metrics ---")
    logger.info(f"  Precision: {lr_precision:.4f}, Recall: {lr_recall:.4f}, F1-Score: {lr_f1:.4f}")
    
    # 6. Production Candidate: XGBoost (All features)
    logger.info("Training Production Candidate: XGBoost (All features)...")
    xgb_model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric="logloss"
    )
    xgb_model.fit(X_train, y_train)
    
    # 7. Threshold Tuning for XGBoost on Validation set
    logger.info("Optimizing threshold for XGBoost model on validation split...")
    best_threshold = optimize_decision_threshold(xgb_model, X_val, y_val)
    
    # 8. Evaluate XGBoost on Test Split
    test_probs = xgb_model.predict_proba(X_test)[:, 1]
    xgb_preds = (test_probs >= best_threshold).astype(int)
    
    xgb_precision = float(precision_score(y_test, xgb_preds, zero_division=0))
    xgb_recall = float(recall_score(y_test, xgb_preds, zero_division=0))
    xgb_f1 = float(f1_score(y_test, xgb_preds, zero_division=0))
    try:
        xgb_auc = float(roc_auc_score(y_test, test_probs))
        if np.isnan(xgb_auc):
            logger.warning("AUC-ROC is nan (possibly due to single class). Setting to 0.5.")
            xgb_auc = 0.5
    except ValueError:
        logger.warning("Only one class is present in y_test. AUC-ROC is undefined and will be set to 0.5.")
        xgb_auc = 0.5
    
    logger.info("--- XGBoost (Production Model) Test Metrics ---")
    logger.info(f"  Precision: {xgb_precision:.4f}, Recall: {xgb_recall:.4f}, F1-Score: {xgb_f1:.4f}, AUC-ROC: {xgb_auc:.4f}")
    logger.info(f"  Decision Threshold: {best_threshold:.2f}")
    logger.info("\n" + classification_report(y_test, xgb_preds, zero_division=0))
    
    # 9. Save XGBoost Artifacts
    os.makedirs(extractor_path, exist_ok=True)
    model_save_path = os.path.join(extractor_path, "xgboost_model.pkl")
    joblib.dump(xgb_model, model_save_path)
    logger.info(f"Serialized production XGBoost model to: {model_save_path}")
    
    # 10. Update and Write metadata in MongoDB
    model_metadata_collection = get_collection("model_metadata")
    
    # Mark prior versions as undeployed
    model_metadata_collection.update_many(
        {"model_version": {"$ne": model_version}},
        {"$set": {"deployed": False}}
    )
    
    # Write new metadata registry record
    metadata_doc = {
        "model_version": model_version,
        "algorithm": "XGBoost",
        "precision": xgb_precision,
        "recall": xgb_recall,
        "f1_score": xgb_f1,
        "auc_roc": xgb_auc,
        "threshold": best_threshold,
        "deployed": True,
        "artifact_path": extractor_path + "/",
        "created_at": datetime.now(timezone.utc)
    }
    
    # Check if duplicate version metadata exists and overwrite
    model_metadata_collection.delete_many({"model_version": model_version})
    model_metadata_collection.insert_one(metadata_doc)
    logger.info("Registered production model metrics successfully inside model_metadata collection.")
    
    return {
        "version": model_version,
        "nb": {"precision": nb_precision, "recall": nb_recall, "f1": nb_f1},
        "lr": {"precision": lr_precision, "recall": lr_recall, "f1": lr_f1},
        "xgb": {"precision": xgb_precision, "recall": xgb_recall, "f1": xgb_f1, "auc": xgb_auc, "threshold": best_threshold}
    }

def retrain_model_from_feedback() -> dict:
    """
    Retrains the active XGBoost model by combining the original training dataset
    with approved user correction feedback.
    """
    logger.info("Triggering automated background retraining pipeline...")
    
    # 1. Fetch active deployed model version
    meta_col = get_collection("model_metadata")
    active_meta = meta_col.find_one({"deployed": True})
    active_version = active_meta["model_version"] if active_meta else "v1.0.0"
    
    new_version = "v1.1.0"
    if active_version:
        import re
        match = re.match(r"v?(\d+)\.(\d+)\.(\d+)", active_version)
        if match:
            major, minor, patch = map(int, match.groups())
            new_version = f"v{major}.{minor + 1}.0"
        else:
            new_version = active_version + "_retrained"
            
    logger.info(f"Retraining model from active version {active_version} to new version {new_version}...")
    
    # 2. Load original dataset splits
    train_emails, val_emails, test_emails = load_splits_data()
    
    # 3. Load approved feedback and associate original emails
    feedback_col = get_collection("feedback")
    predictions_col = get_collection("predictions")
    emails_col = get_collection("emails")
    
    approved_feedback = list(feedback_col.find({"status": "approved"}))
    logger.info(f"Loaded {len(approved_feedback)} approved feedback corrections for retraining.")
    
    feedback_emails = []
    for fb in approved_feedback:
        pred = predictions_col.find_one({"prediction_id": fb["prediction_id"]})
        if not pred:
            continue
        email_doc = emails_col.find_one({"email_id": pred["email_id"]})
        if not email_doc:
            continue
            
        # Determine correct label
        label_str = fb["correct_label"].strip().lower()
        label_val = 1 if label_str in {"suspicious", "spam"} else 0
        
        # Create a copy with the updated/corrected label
        corrected_email = dict(email_doc)
        corrected_email["label"] = label_val
        feedback_emails.append(corrected_email)
        
    logger.info(f"Appending {len(feedback_emails)} corrected emails to the training set.")
    
    # Combine original training emails with feedback corrections
    combined_train = train_emails + feedback_emails
    
    if len(combined_train) == 0:
        raise ValueError("Training dataset is empty.")
        
    y_train = np.array([e["label"] for e in combined_train], dtype=np.int32)
    y_val = np.array([e["label"] for e in val_emails], dtype=np.int32)
    y_test = np.array([e["label"] for e in test_emails], dtype=np.int32)
    
    # 4. Fit FeatureExtractor on combined training dataset
    models_dir = "models"
    new_extractor_path = os.path.join(models_dir, new_version)
    os.makedirs(new_extractor_path, exist_ok=True)
    
    extractor = FeatureExtractor(max_subject_features=1000, max_body_features=3000)
    logger.info(f"Fitting new FeatureExtractor for version {new_version}...")
    extractor.fit(combined_train)
    extractor.save(new_extractor_path)
    
    # 5. Transform all splits
    X_train = extractor.transform_batch(combined_train)
    X_val = extractor.transform_batch(val_emails)
    X_test = extractor.transform_batch(test_emails)
    
    # 6. Train XGBoost
    logger.info("Training new XGBoost production model...")
    xgb_model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric="logloss"
    )
    xgb_model.fit(X_train, y_train)
    
    # 7. Optimize threshold
    best_threshold = optimize_decision_threshold(xgb_model, X_val, y_val)
    
    # 8. Evaluate on test split
    test_probs = xgb_model.predict_proba(X_test)[:, 1]
    xgb_preds = (test_probs >= best_threshold).astype(int)
    
    xgb_precision = float(precision_score(y_test, xgb_preds, zero_division=0))
    xgb_recall = float(recall_score(y_test, xgb_preds, zero_division=0))
    xgb_f1 = float(f1_score(y_test, xgb_preds, zero_division=0))
    try:
        xgb_auc = float(roc_auc_score(y_test, test_probs))
    except ValueError:
        xgb_auc = 0.5
        
    logger.info(f"Retrained XGBoost metrics: Precision={xgb_precision:.4f}, Recall={xgb_recall:.4f}, F1={xgb_f1:.4f}, AUC={xgb_auc:.4f}")
    
    # 9. Save artifacts
    model_save_path = os.path.join(new_extractor_path, "xgboost_model.pkl")
    joblib.dump(xgb_model, model_save_path)
    
    # 10. Update database active registries
    # Set all old models to deployed = False
    meta_col.update_many({}, {"$set": {"deployed": False}})
    
    # Insert new deployed metadata
    metadata_doc = {
        "model_version": new_version,
        "algorithm": "XGBoost",
        "precision": xgb_precision,
        "recall": xgb_recall,
        "f1_score": xgb_f1,
        "auc_roc": xgb_auc,
        "threshold": best_threshold,
        "deployed": True,
        "artifact_path": new_extractor_path + "/",
        "created_at": datetime.now(timezone.utc)
    }
    meta_col.delete_many({"model_version": new_version})
    meta_col.insert_one(metadata_doc)
    logger.info(f"New model {new_version} marked as active and deployed in MongoDB.")
    
    # Reset in-memory cache to force reload on next request
    from app.services.model_service import model_service
    model_service._engine = None
    model_service._cached_version = None
    logger.info("Successfully hot-swapped ML model engine cache in memory.")
    
    return {
        "status": "success",
        "old_version": active_version,
        "new_version": new_version,
        "metrics": {"precision": xgb_precision, "recall": xgb_recall, "f1": xgb_f1}
    }

