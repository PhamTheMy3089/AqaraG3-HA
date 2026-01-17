# Hướng dẫn cài đặt Aqara Camera G3 Integration

## Yêu cầu

- Home Assistant phiên bản 2023.1.0 trở lên
- HACS đã được cài đặt (nếu cài qua HACS)

## Cài đặt qua HACS

### Bước 1: Thêm Custom Repository

1. Mở Home Assistant
2. Vào **HACS** (Home Assistant Community Store)
3. Click vào menu **3 chấm** ở góc trên bên phải
4. Chọn **Custom repositories**
5. Thêm thông tin:
   - **Repository**: URL của repository GitHub này
   - **Category**: Chọn **Integration**
6. Click **Add**

### Bước 2: Cài đặt Integration

1. Trong HACS, vào tab **Integrations**
2. Tìm **Aqara Camera G3**
3. Click vào integration
4. Click **Download**
5. Chọn **Restart Home Assistant** khi được hỏi

### Bước 3: Cấu hình Integration

1. Sau khi Home Assistant khởi động lại, vào **Settings** > **Devices & Services**
2. Click **Add Integration**
3. Tìm và chọn **Aqara Camera G3**
4. Điền thông tin:
   - **Aqara URL**: URL của Aqara API (mặc định: `open-cn.aqara.com`)
   - **Token**: Token xác thực từ Aqara
   - **App ID**: App ID từ Aqara
   - **User ID**: User ID từ Aqara
   - **Subject ID**: Device ID của camera G3 (có thể tìm trong Node-RED flow)
5. Click **Submit**

## Cài đặt thủ công

### Bước 1: Copy files

1. Copy toàn bộ thư mục `custom_components/aqara_g3` vào thư mục `custom_components` của Home Assistant
2. Cấu trúc sẽ là: `config/custom_components/aqara_g3/`

### Bước 2: Restart Home Assistant

1. Vào **Developer Tools** > **YAML**
2. Click **Restart** hoặc restart Home Assistant qua Settings

### Bước 3: Cấu hình Integration

Làm theo các bước tương tự như phần "Cài đặt qua HACS" - Bước 3

## Lấy thông tin xác thực

Các thông tin xác thực cần thiết có thể được lấy từ:

1. **Node-RED Flow**: Trong file `AqaraG3.json`, tìm các global variables:
   - `subjectId`: Device ID của camera
   - `token`: Token xác thực
   - `appid`: App ID
   - `userid`: User ID
   - `aqara_url`: URL của Aqara API

2. **Aqara App**: Đăng nhập vào Aqara app và kiểm tra thông tin API trong developer settings

## Kiểm tra cài đặt

Sau khi cấu hình xong, bạn sẽ thấy:

- Các sensor mới trong **Developer Tools** > **States**:
  - `sensor.aqara_g3_motion_detect`
  - `sensor.aqara_g3_face_detect`
  - `sensor.aqara_g3_pets_detect`
  - `sensor.aqara_g3_human_detect`
  - `sensor.aqara_g3_wifi_rssi`
  - `sensor.aqara_g3_alarm_status`

## Xử lý lỗi

### Lỗi "Cannot connect"
- Kiểm tra kết nối internet
- Kiểm tra Aqara URL có đúng không
- Kiểm tra firewall có chặn kết nối không

### Lỗi "Invalid auth"
- Kiểm tra lại Token, App ID, User ID
- Đảm bảo các thông tin này còn hiệu lực

### Sensor không hiển thị dữ liệu
- Kiểm tra logs trong **Settings** > **System** > **Logs**
- Tìm các dòng có chứa `aqara_g3` để xem lỗi chi tiết

## Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra logs trong Home Assistant
2. Tạo issue trên GitHub repository với thông tin lỗi

