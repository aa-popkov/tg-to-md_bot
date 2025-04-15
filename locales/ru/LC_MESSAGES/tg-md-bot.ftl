hello = Привет, <b>{ $user }</b>!

cur-lang = Текущий язык: <i>Русский 🇷🇺</i>
    Ты можешь поменять язык с помощью команды:
    /language_en

    И выполнить - /help команду

help-message = <b>📄 Markdown Converter Bot</b>

    <i>Превращай Telegram-посты в красивые Markdown-файлы!</i>

    ✨ <b>Что умеет этот бот?</b> ✨

    🔹 <b>Конвертирует</b> текст со стилями Telegram (<b>жирный</b>, <i>курсив</i>, <code>моноширинный</code> и др.) в Markdown-разметку.
    🔹 <b>Сохраняет</b> форматирование: заголовки, списки, ссылки и даже <code>код</code>!
    🔹 <b>Добавляет картинки</b> 🖼️ – если в посте есть изображения, они встроятся в файл.
    🔹 <b>Отправляет готовый файл</b> 📂 – скачивай и используй в своих проектах!

    💡 <b>Как использовать?</b>
    Просто <b>перешли</b> боту любой пост или сообщение – и получи <u>Markdown-документ</u> в ответ!

    🚀 <i>Идеально для:</i>
    • 📝 Конспектирования полезных постов
    • 📚 Создания документации
    • 💾 Сохранения красивого форматирования

    OpenSource - https://github.com/aa-popkov/tg-to-md_bot

    { cur-lang }

    <b>Попробуй прямо сейчас!</b>

example-message = <b>🔶 Жирный текст 🔶</b>

    <i>🌀 Курсив 🌀</i>

    <s>❌ Зачеркнутый ❌</s>

    <a href="https://google.com/">🌐 Ссылка 🌐</a>

    <code>💻 код в строку 💻</code>

    <pre><code class="language-python">
    # 🐍 Python code block 🐍
    print('Блок кода с подсветкой синтаксиса!')
    </code></pre>

    <pre>
    📜 Блок кода 📜
    </pre>

start-message = 🌟 <b>Привет, { $user }!</b> 👋
    Рад тебя видеть! Немного информации обо мне:

    { help-message }

some-problem = 😱 Упс, Что-то не так
    Похоже, я не могу обработать твой запрос. Попробуй чуть позже 😪

change-lang = Ты успешно установил русский язык 🇷🇺

unsupported-message = Такой тип сообщений пока не поддерживается.
