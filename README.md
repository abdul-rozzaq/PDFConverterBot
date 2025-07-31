# Telegram Document Converter Bot

A powerful, production-ready Telegram bot for document and image conversion built with FastAPI and aiogram 3.x.

## Features

### Document Conversions

- 📄 PDF ↔ Word (.docx)
- 🖼 PDF ↔ Images (PNG, JPG)
- 📝 PDF → Text extraction
- 📊 Excel ↔ PDF

### Image Processing

- 🗜 Image compression
- ⚫ Convert to grayscale
- 📏 Resize/crop images
- 🔄 Format conversion (PNG ↔ JPG ↔ WebP)

### AI Features

- 🔍 OCR: Extract text from images (EasyOCR/Tesseract)
- 📊 Usage statistics and analytics
- 🌐 Multilingual support (English, Uzbek, Russian)

### Technical Features

- ⚡ Async FastAPI backend with webhook
- 🗄️ SQLite/PostgreSQL database support
- 📦 ZIP archives for multiple files
- 🔒 Admin panel and user management
- 🎯 Production-ready with Docker support

## Quick Start

1. **Clone the repository**

```bash
git clone <repository-url>
cd telegram_converter_bot
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up environment**

```bash
cp .env.example .env
# Edit .env with your bot token and settings
```

4. **Run the application**

```bash
python -m app.main
```

### Using Docker

1. **Build and run with Docker Compose**

```bash
docker-compose up -d
```

## Configuration

Create a `.env` file with the following variables:

```env# Telegram Document Converter Bot - Production Ready

## Project Structure
```

telegram_converter_bot/
├── app/
│ ├── **init**.py
│ ├── main.py
│ ├── bot/
│ │ ├── **init**.py
│ │ ├── handlers/
│ │ │ ├── **init**.py
│ │ │ ├── start.py
│ │ │ ├── convert.py
│ │ │ └── admin.py
│ │ ├── keyboards/
│ │ │ ├── **init**.py
│ │ │ └── inline.py
│ │ ├── middlewares/
│ │ │ ├── **init**.py
│ │ │ └── lang.py
│ │ └── utils/
│ │ ├── **init**.py
│ │ ├── converters.py
│ │ └── helpers.py
│ ├── core/
│ │ ├── **init**.py
│ │ ├── config.py
│ │ ├── database.py
│ │ └── storage.py
│ ├── models/
│ │ ├── **init**.py
│ │ └── user.py
│ └── locales/
│ ├── en.json
│ ├── uz.json
│ └── ru.json
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md

```

```
