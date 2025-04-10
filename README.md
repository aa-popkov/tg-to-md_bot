# 📄 Telegram Markdown Converter Bot

_Converts Telegram messages into Markdown files while preserving formatting and images._

## 🌟 Key Features

- Converts messages to Markdown while preserving:
    - **Text formatting** (**bold**, _italic_, `code`, etc.)
    - **Images** 🖼️ (embedded as base64)
    - **Lists and links**
- Easy to use—no complicated commands!

## 📋 Roadmap

- [x] Basic message processing
- [x] Processing messages without a media group (_single image in a message_)
- [x] Processing messages with a media group (_multiple images in a message_)
- [ ] Processing messages with video
- [x] Add multilingual support (i18n)
  - [x] 🇷🇺
  - [x] 🇬🇧

## 🚀 Quick Start

### 🧑‍💻 Development

1. **Clone the repository:**
   ```shell 
   git clone https://github.com/aa-popkov/tg-to-md_bot.git
   ```
2. **Install dependencies:**
    ```shell
    pip install -r requirements.txt
    ```
3. **Set up environment variables:**
    ```shell
    cp .env.example .env  
    ```
4. **Run the bot:**
    ```shell
    python main.py  
    ```

### 🌎 Deployment

1. **Clone the repository:**  
   ```shell  
   git clone https://github.com/aa-popkov/tg-to-md_bot.git && cd tg-to-md_bot
   ```
2. **Set up environment variables:**  
   ```shell  
   cp .env.example .env
   ``` 
3. **Run the Docker container:**  
   ```shell  
   docker compose up -d --build
   ```