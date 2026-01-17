# Aqara Camera G3 Integration for Home Assistant

Integration cho Aqara Camera G3 trong Home Assistant, có thể cài đặt qua HACS.

## Cài đặt

### Qua HACS (Khuyến nghị)

1. Mở HACS trong Home Assistant
2. Vào tab "Integrations"
3. Click vào menu 3 chấm ở góc trên bên phải
4. Chọn "Custom repositories"
5. Thêm repository URL và chọn category "Integration"
6. Tìm "Aqara Camera G3" và click "Install"
7. Restart Home Assistant

### Cài đặt thủ công

1. Copy thư mục `custom_components/aqara_g3` vào thư mục `custom_components` của Home Assistant
2. Restart Home Assistant
3. Vào Settings > Devices & Services > Add Integration
4. Tìm "Aqara Camera G3" và làm theo hướng dẫn

## Cấu hình

Sau khi cài đặt, bạn cần cấu hình integration với các thông tin sau:

- **Aqara URL**: URL của Aqara API (mặc định: `open-cn.aqara.com`)
- **Token**: Token xác thực từ Aqara
- **App ID**: App ID từ Aqara
- **User ID**: User ID từ Aqara
- **Subject ID**: Device ID của camera G3

## Lấy thông tin xác thực

Bạn cần lấy các thông tin xác thực từ Aqara API. Tham khảo file `AqaraG3.json` để biết cách lấy các thông tin này.

## Tính năng

- Sensor hiển thị trạng thái các tính năng phát hiện (Motion, Face, Pets, Human)
- Sensor hiển thị WiFi RSSI
- Sensor hiển thị trạng thái báo động

## Hỗ trợ

Nếu gặp vấn đề, vui lòng tạo issue trên GitHub repository.

