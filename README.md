# 📄 Telegram Markdown Converter Bot  
_Превращает Telegram-сообщения в Markdown-файлы с сохранением форматирования и картинок._  
Было написано за пару часов, для решения конкртеной задачи, структура проекта полное 💩, будет исправлено в будущем(_возможно_)

## 🌟 Основные возможности
- Конвертация сообщений в Markdown с сохранением:
  - **Текстового форматирования** (**жирный**, _курсив_, `код`)
  - **Изображений** 🖼️ (встраиваются как base64)
  - **Списков и ссылок**
- Простота использования - никаких сложных команд!

## 📋 Roadmap

- [x] Обработка простых сообщений
- [x] Обработка сообщений без медиа-группы(_одна картинка в сообщении_)
- [ ] Обработка сообщений с медиа-группой(_нескроткр картинок в сообщении_)
- [ ] Обработка сообщений с видео

## 🚀 Быстрый старт

### 🧑‍💻 Разработка

1. **Клонируйте репозиторий:**  
   ```bash  
   git clone https://github.com/aa-popkov/tg-to-md_bot.git
   ```
2. **Установите зависимости:**  
   ```bash  
   pip install -r requirements.txt
   ```
3. **Настройте переменные окружения:**  
   ```bash  
   cp .env.example .env
   ``` 
4. **Запустите бота:**  
   ```bash  
   python main.py
   ```

### 🌎 Публикация

1. **Клонируйте репозиторий:**  
   ```bash  
   git clone https://github.com/aa-popkov/tg-to-md_bot.git && cd tg-to-md_bot
   ```
2. **Настройте переменные окружения:**  
   ```bash  
   cp .env.example .env
   ``` 
3. **Запустите Docker-контейнер:**  
   ```bash  
   docker compose up -d --build
   ```
