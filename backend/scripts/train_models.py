import os
import sys
from app.database.connection import db_manager
from app.ml.training import run_training_pipeline
from app.utils.logger import logger

def main():
    """
    Main entry script to run the model training pipeline.
    Connects to database, runs progressive fit and evaluate steps,
    saves artifacts, and exits.
    """
    logger.info("Initializing database connection for model training...")
    try:
        db_manager.connect()
    except Exception as e:
        logger.critical(f"Failed to connect to database: {str(e)}")
        sys.exit(1)
        
    try:
        results = run_training_pipeline(model_version="v1.0.0", models_dir="models")
        logger.info(f"Model Training pipeline run succeeded for version {results['version']}!")
        
        print("\n==================================================")
        print("          TRAINING PIPELINE SUMMARY")
        print("==================================================")
        print("Baseline 1 (Multinomial Naive Bayes - TF-IDF only):")
        print(f"  Precision : {results['nb']['precision']:.4f}")
        print(f"  Recall    : {results['nb']['recall']:.4f}")
        print(f"  F1-Score  : {results['nb']['f1']:.4f}")
        print("\nBaseline 2 (Logistic Regression - All features):")
        print(f"  Precision : {results['lr']['precision']:.4f}")
        print(f"  Recall    : {results['lr']['recall']:.4f}")
        print(f"  F1-Score  : {results['lr']['f1']:.4f}")
        print("\nProduction Model (XGBoost - All features):")
        print(f"  Precision : {results['xgb']['precision']:.4f}")
        print(f"  Recall    : {results['xgb']['recall']:.4f}")
        print(f"  F1-Score  : {results['xgb']['f1']:.4f}")
        print(f"  AUC-ROC   : {results['xgb']['auc']:.4f}")
        print(f"  Threshold : {results['xgb']['threshold']:.2f}")
        print("==================================================\n")
    except Exception as e:
        logger.exception(f"Exception during training pipeline run: {str(e)}")
        sys.exit(1)
    finally:
        db_manager.close()

if __name__ == "__main__":
    main()
