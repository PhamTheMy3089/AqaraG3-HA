# Aqara Camera G3 Integration for Home Assistant

[Tiếng Việt](README.md) | [English](README_EN.md)

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

Sau khi cài đặt, bạn chỉ cần đăng nhập tài khoản Aqara:

- **Tài khoản**: Email/phone đăng nhập Aqara
- **Mật khẩu**: Mật khẩu Aqara
- **Khu vực (Area)**: CN/EU/US/HMT/OTHER...

Integration sẽ tự lấy **Token**, **App ID**, **User ID** và danh sách thiết bị để bạn chọn **Subject ID**.
## Lấy thông tin xác thực

Không cần lấy thủ công. Integration tự đăng nhập và lấy thông tin cần thiết.

## Tính năng

- Sensor hiển thị trạng thái các tính năng phát hiện (Motion, Face, Pets, Human)
- Sensor hiển thị WiFi RSSI
- Sensor hiển thị trạng thái báo động

## Hỗ trợ

Nếu gặp vấn đề, vui lòng tạo issue trên GitHub repository.

## Cảm ơn

Dự án này tham khảo và chỉnh sửa dựa trên: https://github.com/sdavides/AqaraPOST-Homeassistant
