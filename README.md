# 🛒 Amazon Product Review Video Creator

Tạo review video Amazon chuyên nghiệp từ ảnh/video sẵn có + AI voiceover Inworld TTS.

---

## 🚀 Deploy lên Streamlit Cloud (Miễn phí)

1. Upload `app.py` + `requirements.txt` lên GitHub repo
2. Vào [share.streamlit.io](https://share.streamlit.io) → New app → chọn repo → Deploy

## 💻 Chạy local

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 🔑 Lấy Inworld API Key

1. Đăng ký tại [platform.inworld.ai](https://platform.inworld.ai/signup)
2. API Keys → Generate new key
3. Copy **Basic (Base64)**

---

## 📋 5-Step Workflow

| Bước | Nội dung |
|------|----------|
| **① Product** | Tên sản phẩm, ASIN, thời gian test, rating, pros/cons |
| **② Media** | Dán link ảnh & video (JPG/PNG/MP4/MOV/WebM) |
| **③ Script** | Auto-gen script, chỉnh sửa tự do |
| **④ Voiceover** | Tạo AI audio từng scene, nghe preview, tải MP3 |
| **⑤ Render** | Ghép ảnh/video + audio + nhạc nền → tải MP4 |

---

## 🖼️ Các loại link media được hỗ trợ

- **Amazon listing images** — copy link ảnh từ trang product
- **Google Drive** — share → "Anyone with link" → copy direct link
- **Imgur** — link direct `.jpg`
- **Cloudinary / S3 / CDN** — bất kỳ direct URL nào
- **Video**: `.mp4`, `.mov`, `.webm`, `.avi`

---

## 🎬 Review Templates

| Template | Mục đích |
|----------|----------|
| ⭐⭐⭐⭐⭐ 5-Star Glowing | Sản phẩm tuyệt vời, review nhiệt tình |
| ⭐⭐⭐⭐ 4-Star Balanced | Honest, cân bằng pros/cons |
| ⭐⭐⭐ 3-Star Honest | Trung thực về hạn chế |
| 🔍 Detailed Tech Review | Review kỹ thuật chuyên sâu |
| ✍️ Custom | Tự viết toàn bộ |
