# Dashboard Đắk Lắk

- Tổng hợp: https://tambabu20-source.github.io/Daklak-DA/
- Tổ 1: https://tambabu20-source.github.io/Daklak-DA/to-1/

Tổ 1 chỉ dùng tab `Báo cáo` (gid `1905427817`) của Google Sheet liên kết trên dashboard. Tổ 2–4 giữ nguyên dữ liệu cũ. Số tiền trong Sheet là triệu đồng, được chia 1.000 để hiển thị tỷ đồng. Tỷ lệ từng dự án giữ nguyên nguồn; tỷ lệ tổng tính từ tổng số tiền và công khai chênh lệch với tỷ lệ dòng tổng nguồn.

`python scripts/sync_to1.py` đọc CSV công khai, kiểm tra cấu trúc, số thứ tự và các tổng tiền trước khi cập nhật hai HTML. Không cần khóa, cookie hay tài khoản Google. Nếu nguồn không còn công khai hoặc cấu trúc thay đổi, tác vụ dừng trước khi ghi/deploy; bản công khai gần nhất vẫn giữ nguyên. Cấu trúc hiện hỗ trợ báo cáo KH 2026/tháng 9; cần rà soát ánh xạ khi đổi kỳ báo cáo.

GitHub Actions chạy lúc 10:00 UTC (17:00 Asia/Ho_Chi_Minh), hoặc chạy thủ công. Lịch GitHub có thể trễ theo hàng đợi. Tác vụ commit dữ liệu thay đổi rồi deploy cả hai trang; không thay đổi automation ChatGPT đã có. Chỉ hai HTML được đưa vào artifact Pages.
