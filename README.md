# RunBash:
Tên: RunBash.  
Phiên bản: 1.8 (Chính thức).  
Nền tảng: Windows.  
RunBash là một công cụ dòng lệnh viết bằng Python, giúp chạy Bash script (.sh, .bash) trên Windows một cách nhanh gọn mà không cần mở Git Bash thủ công.  
Chương trình tự động tìm Bash (Git Bash), hỗ trợ login shell, truyền tham số cho script, và cho phép chỉ định đường dẫn Bash bằng biến môi trường RUNBASH_BASH.  
Lưu ý: Chương trình này phụ thuộc vào tệp "Git_Folder\bin\Bash.EXE" đi kèm trong gói Git For Windows.
## Mô tả:
RunBash là một CLI tool dành cho Windows,
cho phép chạy Bash script (.sh, .bash) trực tiếp
thông qua Command Prompt hoặc PowerShell.
## Tính năng chính:
- Tự động phát hiện Bash (Git Bash) trên hệ thống.
- Hỗ trợ chạy Bash với login shell (-l).
- Truyền tham số cho Bash script.
- Cho phép chỉ định Bash thủ công bằng biến môi trường RUNBASH_BASH.
- Trả đúng exit code của Bash script.
- Không phụ thuộc GUI, nhẹ và đơn giản.
- Ưu tiên cách gọi trực tiếp Bash script để giữ hành vi tương tự Git Bash.
- Tối ưu trải nghiệm người dùng để có trải nghiệm tốt nhất có thể.
## Yêu cầu:
- Git For Windows.  
  Tải tại:
  (https://git-scm.com/download/win)
## Tải xuống RunBash:
Tải xuống tại:
(https://github.com/NguyenVuHoangLong2012/RunBash/releases/latest)
## Cách cài đặt:
Sau khi tải xuống tệp RunBash.EXE hãy đưa nó vào System32 hoặc thêm nó vào Path để bạn có thể gọi RunBash.EXE ở bất kì đâu.  
- Nếu bạn muốn đưa tệp RunBash.EXE vào System32 hãy copy RunBash.EXE và duyệt theo đường dẫn sau:  
C:\Windows\System32  
Sau khi vào System32 hãy gián RunBash.EXE vào.
- Nếu bạn muốn thêm RunBash.EXE vào biến môi trường Path hãy làm theo các bước sau:  
Nhấn Windows + R > Gõ sysdm.cpl.  
Sau khi hộp thoại System Properties mở ra hãy chuyển sang tab Advanced.  
Tiếp theo hãy chọn tùy chọn Environment Variables... để mở hộp thoại Environment Variables.  
Ở khung System Variables bên phải, hãy kéo xuống cho tới khi thấy Path, sau khi thấy nhấn Edit.  
Sau khi nhấn Edit bạn sẽ thấy một danh sách đường dẫn hiện ra, nhấn new và nhập đường dẫn của thư mục mà bạn đang đặt tệp RunBash.EXE.  
Sau khi nhập xong hãy nhấn Enter > OK để đóng hộp thoại Environment variables.  
- Nếu bạn sử dụng Git For Windows portable hoặc muốn sử dụng một bản Bash.EXE khác ở bước này hãy nhấn vào New ở một trong hai khung User variables hoặc System variables, ở ô Variable name hãy nhập tên biến môi trường này là RUNBASH_BASH và ở ô Variable value hãy nhập đường dẫn tới tệp "Git_Folder\bin\Bash.EXE" mà bạn muốn chương trình sử dụng mặc định hoặc nhấn vào Browse File... để duyệt tới file đó.  
 Chẳng hạn như trong ví dụ này là "C:\Tool\Git\bin\Bash.EXE".  
Sau khi chọn xong file hãy nhấn OK để Windows tạo biến môi trường RUNBASH_BASH..  
Nếu bạn sử dụng Git For Windows chuẩn hãy bỏ qua bước này.  
Cuối cùng hãy nhấn OK > OK để đóng tất cả các hộp thoại hiện tại đang mở..  
Vậy đã xong.
  ## Hướng dẫn sử dụng:
- Sử dụng "runbash.exe đường_dẫn\script.sh [tham_số...]" hoặc "runbash.exe đường_dẫn\script.bash [tham_số...]" để chạy một Bash script.
- Sử dụng "runbash.exe --login đường_dẫn\script.sh [tham_số...]" hoặc "runbash.exe --login đường_dẫn\script.bash [tham_số...]" để chạy Bash với login shell.
- Sử dụng "runbash.exe --bash-using" để kiểm tra đường dẫn Bash đang được sử dụng.
- Sử dụng "runbash.exe --environment-variables" để hiển thị các biến môi trường bạn đã thiết lập.
- Sử dụng "runbash.exe --version" để kiểm tra phiên bản RunBash.
- Sử dụng "runbash.exe --help" để hiển thị trợ giúp này.
- Sử dụng "runbash.exe --about" để hiển thị toàn bộ thông tin.
- Biến môi trường: RUNBASH_BASH – dùng để chỉ định đường dẫn Bash tùy chỉnh thay vì tự động dò tìm.
## Lưu ý về dự án:
Dự án này được cá nhân tôi phát triển và có thể không còn được phát triển trong tương lai.  
Chương trình này theo giấy phép Mit, xem giấy phép tại:
(https://github.com/NguyenVuHoangLong2012/RunBash/blob/main/LICENSE)
