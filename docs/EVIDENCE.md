# Minh Chứng Thực Hành LAB 16 (Evidence Logs)

Tài liệu này tổng hợp toàn bộ output và bằng chứng thực tế từ quá trình chạy Lab 16 trên **Google Cloud Platform (GCP)**.

---

## 1. Minh Chứng 1: Terraform Apply & Outputs
```text
Apply complete! Resources: 16 added, 0 changed, 0 destroyed.

Outputs:

api_endpoint = "http://8.232.105.161/v1"
gpu_node_name = "ai-gpu-node"
gpu_node_zone = "us-central1-a"
iap_ssh_command = "gcloud compute ssh ai-gpu-node --zone=us-central1-a --tunnel-through-iap"
load_balancer_ip = "8.232.105.161"
```

---

## 2. Minh Chứng 2: Kết Nối IAP & Bootstrap Kiểm Tra Môi Trường ML
```bash
$ gcloud compute ssh ai-gpu-node --zone=us-central1-a --tunnel-through-iap --project=resolute-sky-505509-e7 --command="python3 -c \"import lightgbm, sklearn, pandas, numpy; print('OK')\""

# Output:
OK
```

---

## 3. Minh Chứng 3: Terminal Chạy `python3 benchmark.py`
```text
$ python3 benchmark.py

============================================================
  LIGHTGBM BENCHMARK ON GOOGLE CLOUD COMPUTE ENGINE (CPU)
============================================================
Local creditcard.csv not found. Attempting to fetch CreditCardFraudDetection via OpenML...
Dataset successfully fetched from OpenML: shape (284807, 31)
[*] Dataset Shape: (284807, 31)
[*] Class Distribution: {0.0: 284315, 1.0: 492}
[*] Data Loading Time: 36.6627 s
[*] Train set size: (227845, 30), Test set size: (56962, 30)

[*] Training LightGBM Classifier...
[*] Training finished in: 1.2730 s (Best iteration: 1)

[*] Evaluating model on test set...

[*] Measuring Inference Latency & Throughput...

============================================================
                    BENCHMARK RESULTS
============================================================
| Metric                              | Kết quả            |
|-------------------------------------|--------------------|
| Thời gian load data                 | 36.6627 s          |
| Thời gian training                  | 1.2730 s           |
| Best iteration                      | 1                  |
| AUC-ROC                             | 0.951654           |
| Accuracy                            | 0.998947           |
| F1-Score                            | 0.727273           |
| Precision                           | 0.655738           |
| Recall                              | 0.816327           |
| Inference latency (1 row)           | 0.9158 ms          |
| Inference throughput (1000 rows)    | 912093.02 rows/s   |
============================================================

[+] Full results saved to: benchmark_result.json
```

---

## 4. Minh Chứng 4: Đo Đạc Tài Nguyên (RAM & Network Usage)

### RAM Usage (`free -h`):
```text
$ free -h
               total        used        free      shared  buff/cache   available
Mem:           3.8Gi       480Mi       1.8Gi       456Ki       1.8Gi       3.4Gi
Swap:             0B          0B          0B
```

### Network Traffic (`ip -s link`):
```text
$ ip -s link
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    RX:  bytes packets errors dropped  missed   mcast           
             0       0      0       0       0       0 
    TX:  bytes packets errors dropped carrier collsns           
             0       0      0       0       0       0 
2: ens4: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1460 qdisc mq state UP mode DEFAULT group default qlen 1000
    link/ether 42:01:0a:00:00:02 brd ff:ff:ff:ff:ff:ff
    RX:  bytes packets errors dropped  missed   mcast           
     258553375   44037      0       0       0       0 
    TX:  bytes packets errors dropped carrier collsns           
       1895905   23993      0       0       0       0 
    altname enp0s4
```

---

## 5. Minh Chứng 5: Dọn Dẹp Tài Nguyên (Terraform Destroy & Verification)
```text
$ terraform destroy -auto-approve

google_project_iam_member.gpu_node_log_writer: Destruction complete after 10s
google_project_iam_member.gpu_node_metric_writer: Destruction complete after 10s
google_compute_firewall.allow_lb_healthcheck: Destruction complete after 12s
google_compute_firewall.allow_iap_ssh: Destruction complete after 12s
google_compute_global_forwarding_rule.vllm_fwd: Destruction complete after 22s
google_compute_target_http_proxy.vllm_proxy: Destruction complete after 12s
google_compute_url_map.vllm_url_map: Destruction complete after 11s
google_compute_backend_service.vllm_backend: Destruction complete after 1m14s
google_compute_health_check.vllm_hc: Destruction complete after 12s
google_compute_instance_group.gpu_group: Destruction complete after 14s
google_compute_instance.gpu_node: Destruction complete after 57s
google_service_account.gpu_node_sa: Destruction complete after 2s
google_compute_router_nat.nat: Destruction complete after 4s
google_compute_router.router: Destruction complete after 13s
google_compute_subnetwork.private: Destruction complete after 14s
google_compute_network.ai_vpc: Destruction complete after 22s

Destroy complete! Resources: 16 destroyed.
```

### Xác minh không còn VM nào hoạt động:
```text
$ gcloud compute instances list --project=resolute-sky-505509-e7
Listed 0 items.
```
