# Checklist Test Integration Aqara Camera G3

## Trước khi test

- [ ] Đã copy thư mục `custom_components/aqara_g3` vào Home Assistant
- [ ] Đã có thông tin API: Token, App ID, User ID, Subject ID, Aqara URL
- [ ] Home Assistant đã được restart sau khi copy files

## Test Config Flow

1. **Vào Settings > Devices & Services > Add Integration**
   - [ ] Tìm thấy "Aqara Camera G3 via Cloud API" trong danh sách
   - [ ] Click vào integration và form hiển thị đúng

2. **Điền thông tin đăng nhập**
   - [ ] Tài khoản: Email/phone Aqara
   - [ ] Mật khẩu: Mật khẩu Aqara
   - [ ] Khu vực (Area): CN/EU/US/HMT/OTHER...
3. **Chọn thiết bị**
   - [ ] Danh sách thiết bị hiển thị
   - [ ] Chọn đúng Subject ID (Device ID) của camera

4. **Test Validation**
   - [ ] Với thông tin đúng: Integration được tạo thành công
   - [ ] Với thông tin sai: Hiển thị lỗi "cannot_connect" hoặc "invalid_auth"
   - [ ] Không có thiết bị: Hiển thị lỗi "no_devices"

## Test Sensors

Sau khi integration được cấu hình:

1. **Kiểm tra sensors được tạo**
   - [ ] Vào Developer Tools > States
   - [ ] Tìm các sensor:
     - `sensor.aqara_g3_motion_detect`
     - `sensor.aqara_g3_face_detect`
     - `sensor.aqara_g3_pets_detect`
     - `sensor.aqara_g3_human_detect`
     - `sensor.aqara_g3_wifi_rssi`
     - `sensor.aqara_g3_alarm_status`

2. **Kiểm tra dữ liệu**
   - [ ] Sensors có giá trị (không phải "unknown")
   - [ ] Dữ liệu được cập nhật mỗi 30 giây
   - [ ] Giá trị hiển thị đúng với trạng thái thực tế của camera

## Test Logs

1. **Kiểm tra logs**
   - [ ] Vào Settings > System > Logs
   - [ ] Tìm các dòng có chứa `aqara_g3`
   - [ ] Không có lỗi nghiêm trọng (ERROR)
   - [ ] Có thể có warning (WARNING) nếu API trả về dữ liệu không đúng format

## Test Error Handling

1. **Test với thông tin sai**
   - [ ] User/Pass sai → Hiển thị lỗi "invalid_auth"
   - [ ] Khu vực sai → Có thể báo "cannot_connect" hoặc "invalid_auth"
   - [ ] Subject ID sai → Có thể không có dữ liệu nhưng không crash

2. **Test khi API không khả dụng**
   - [ ] Integration vẫn hoạt động
   - [ ] Sensors hiển thị "unavailable" hoặc giá trị cũ
   - [ ] Logs ghi lại lỗi nhưng không crash

## Test Unload/Reload

1. **Test unload integration**
   - [ ] Vào Settings > Devices & Services
   - [ ] Tìm integration "Aqara Camera G3 via Cloud API"
   - [ ] Click vào và chọn "Delete"
   - [ ] Integration được xóa thành công
   - [ ] Sensors biến mất

2. **Test reload integration**
   - [ ] Sau khi unload, add lại integration
   - [ ] Integration hoạt động bình thường

## Các vấn đề thường gặp

### Integration không xuất hiện trong danh sách
- Kiểm tra file `manifest.json` có đúng format không
- Kiểm tra thư mục `custom_components/aqara_g3` có đúng vị trí không
- Restart Home Assistant

### Lỗi "Cannot connect"
- Kiểm tra kết nối internet
- Kiểm tra Aqara URL có đúng không
- Kiểm tra firewall có chặn không

### Lỗi "Invalid auth"
- Kiểm tra Token, App ID, User ID có đúng không
- Kiểm tra các thông tin này còn hiệu lực không

### Sensors không có dữ liệu
- Kiểm tra Subject ID có đúng không
- Kiểm tra logs để xem lỗi chi tiết
- Kiểm tra API response structure có đúng không

## Ghi chú

- Integration sử dụng polling mỗi 30 giây
- Nếu API trả về lỗi, sensors sẽ giữ giá trị cũ
- Cần có kết nối internet để integration hoạt động
