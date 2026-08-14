import os
import time
import json
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score, precision_score, recall_score
from sklearn.datasets import fetch_openml

def get_dataset():
    data_paths = [
        os.path.expanduser('~/ml-benchmark/creditcard.csv'),
        'creditcard.csv',
        os.path.expanduser('~/.kaggle/creditcard.csv')
    ]
    for path in data_paths:
        if os.path.exists(path):
            print(f"Loading local dataset from: {path}")
            return pd.read_csv(path)
    
    print("Local creditcard.csv not found. Attempting to fetch CreditCardFraudDetection via OpenML...")
    try:
        data = fetch_openml('CreditCardFraudDetection', version=1, as_frame=True, parser='auto')
        df = data.frame
        if 'Class' not in df.columns and 'target' in df.columns:
            df.rename(columns={'target': 'Class'}, inplace=True)
        # Convert Class to numeric if needed
        df['Class'] = pd.to_numeric(df['Class'])
        print(f"Dataset successfully fetched from OpenML: shape {df.shape}")
        # Cache locally
        os.makedirs(os.path.expanduser('~/ml-benchmark'), exist_ok=True)
        df.to_csv(os.path.expanduser('~/ml-benchmark/creditcard.csv'), index=False)
        return df
    except Exception as e:
        print(f"Could not fetch from OpenML: {e}")
        print("Generating synthetic CreditCard benchmark dataset (284,807 rows, 30 features)...")
        np.random.seed(42)
        n_samples = 284807
        n_features = 30
        X_synth = np.random.randn(n_samples, n_features).astype(np.float32)
        # Fraud rate ~ 0.172%
        y_synth = (np.random.rand(n_samples) < 0.00172).astype(int)
        columns = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount']
        df = pd.DataFrame(X_synth, columns=columns)
        df['Class'] = y_synth
        return df

def run_benchmark():
    print("=" * 60)
    print("  LIGHTGBM BENCHMARK ON GOOGLE CLOUD COMPUTE ENGINE (CPU)")
    print("=" * 60)

    # 1. Load Data
    t0 = time.perf_counter()
    df = get_dataset()
    data_load_time = round(time.perf_counter() - t0, 4)
    print(f"[*] Dataset Shape: {df.shape}")
    print(f"[*] Class Distribution: {df['Class'].value_counts().to_dict()}")
    print(f"[*] Data Loading Time: {data_load_time:.4f} s")

    # Prepare features and target
    X = df.drop(columns=['Class'])
    y = df['Class'].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"[*] Train set size: {X_train.shape}, Test set size: {X_test.shape}")

    # 2. Train LightGBM Model
    print("\n[*] Training LightGBM Classifier...")
    model = lgb.LGBMClassifier(
        n_estimators=100,
        learning_rate=0.05,
        num_leaves=31,
        max_depth=-1,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )

    t_train_start = time.perf_counter()
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        callbacks=[lgb.early_stopping(stopping_rounds=10, verbose=False)]
    )
    training_time = round(time.perf_counter() - t_train_start, 4)
    best_iteration = int(model.best_iteration_) if model.best_iteration_ is not None else 100
    print(f"[*] Training finished in: {training_time:.4f} s (Best iteration: {best_iteration})")

    # 3. Model Evaluation
    print("\n[*] Evaluating model on test set...")
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_pred_proba >= 0.5).astype(int)

    auc_roc = round(float(roc_auc_score(y_test, y_pred_proba)), 6)
    accuracy = round(float(accuracy_score(y_test, y_pred)), 6)
    f1 = round(float(f1_score(y_test, y_pred, zero_division=0)), 6)
    precision = round(float(precision_score(y_test, y_pred, zero_division=0)), 6)
    recall = round(float(recall_score(y_test, y_pred, zero_division=0)), 6)

    # 4. Latency & Throughput Benchmark
    print("\n[*] Measuring Inference Latency & Throughput...")
    # Warmup
    sample_1 = X_test.iloc[:1]
    for _ in range(10):
        _ = model.predict_proba(sample_1)

    # Single-row latency (100 runs)
    latencies = []
    for _ in range(100):
        idx = np.random.randint(0, len(X_test))
        single_row = X_test.iloc[idx:idx+1]
        t_start = time.perf_counter()
        _ = model.predict_proba(single_row)
        latencies.append((time.perf_counter() - t_start) * 1000.0) # in ms

    inference_latency_ms = round(float(np.mean(latencies)), 4)

    # 1000-rows throughput
    sample_1000 = X_test.iloc[:1000]
    t_tp_start = time.perf_counter()
    for _ in range(10):
        _ = model.predict_proba(sample_1000)
    total_tp_time = time.perf_counter() - t_tp_start
    throughput_rows_per_sec = round((1000 * 10) / total_tp_time, 2)
    throughput_1000_time_ms = round((total_tp_time / 10) * 1000.0, 4)

    # 5. Output Summary Table
    results = {
        "dataset_shape": list(df.shape),
        "data_load_time_seconds": data_load_time,
        "training_time_seconds": training_time,
        "best_iteration": best_iteration,
        "auc_roc": auc_roc,
        "accuracy": accuracy,
        "f1_score": f1,
        "precision": precision,
        "recall": recall,
        "inference_latency_ms_per_row": inference_latency_ms,
        "inference_throughput_rows_per_sec": throughput_rows_per_sec,
        "inference_time_1000_rows_ms": throughput_1000_time_ms
    }

    print("\n" + "=" * 60)
    print("                    BENCHMARK RESULTS")
    print("=" * 60)
    print(f"| {'Metric':<35} | {'Kết quả':<18} |")
    print("|" + "-" * 37 + "|" + "-" * 20 + "|")
    print(f"| {'Thời gian load data':<35} | {f'{data_load_time:.4f} s':<18} |")
    print(f"| {'Thời gian training':<35} | {f'{training_time:.4f} s':<18} |")
    print(f"| {'Best iteration':<35} | {best_iteration:<18} |")
    print(f"| {'AUC-ROC':<35} | {auc_roc:<18} |")
    print(f"| {'Accuracy':<35} | {accuracy:<18} |")
    print(f"| {'F1-Score':<35} | {f1:<18} |")
    print(f"| {'Precision':<35} | {precision:<18} |")
    print(f"| {'Recall':<35} | {recall:<18} |")
    print(f"| {'Inference latency (1 row)':<35} | {f'{inference_latency_ms:.4f} ms':<18} |")
    print(f"| {'Inference throughput (1000 rows)':<35} | {f'{throughput_rows_per_sec} rows/s':<18} |")
    print("=" * 60)

    # 6. Save JSON
    output_json_path = os.path.expanduser('benchmark_result.json')
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\n[+] Full results saved to: {output_json_path}")

if __name__ == '__main__':
    run_benchmark()
