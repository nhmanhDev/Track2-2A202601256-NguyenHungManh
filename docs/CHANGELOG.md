# Changelog

| Ngày | Thay đổi / Lỗi | Nguyên nhân | Giải pháp |
|---|---|---|---|
| 2026-08-14 | Triển khai Lab 16 GCP & Chạy benchmark LightGBM | Yêu cầu hoàn thành toàn bộ Lab 16 Cloud AI Setup trên GCP | Khởi tạo hạ tầng Terraform (VPC, Private Subnet, Cloud NAT, IAP, Compute Node `e2-medium`, LB), cài đặt môi trường ML, cấu hình script benchmark dataset Credit Card Fraud Detection (284k dòng), thu thập metric và lưu kết quả ra `benchmark_result.json` & `docs/LAB16_REPORT.md`. |
| 2026-08-14 | Lỗi gcloud/IAP API & Project ID không tìm thấy | gcloud config lưu Project ID cũ `aithucchien01256` và API `iap.googleapis.com` chưa kích hoạt | Cập nhật project ID sang `resolute-sky-505509-e7`, kích hoạt `iap.googleapis.com` và `compute.googleapis.com` thành công. |
