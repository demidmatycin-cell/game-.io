from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import re
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# 🔑 YANDEXGPT API
YANDEX_API_KEY = "AQVNyJjL-slW40rTCEGR8a_O0MfHjNnWEAd5kwmf"
FOLDER_ID = "b1gpc79uc6813e585opd"
YANDEX_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/generator')
def generator():
    return send_from_directory('.', 'generator.html')

@app.route('/gallery')
def gallery():
    return send_from_directory('.', 'gallery.html')

@app.route('/contacts')
def contacts():
    return send_from_directory('.', 'contacts.html')

@app.route('/style.css')
def style_css():
    return send_from_directory('.', 'style.css', mimetype='text/css')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

# 📚 ШАБЛОНЫ ТРЕБОВАНИЙ ДЛЯ РАЗНЫХ ЖАНРОВ
GAME_REQUIREMENTS = {
    'Гонки': """
ТРЕБОВАНИЯ К ГОНКАМ:
1. Используй HTML5 Canvas (800x600) для рендеринга
2. Создай машину игрока (цветная, с деталями)
3. Сделай дорогу с разметкой (асфальт, обочины, полосы)
4. Добавь минимум 3-5 машин-соперников с разным цветом
5. Реализуй управление: стрелки ВВЕРХ/ВНИЗ/ВЛЕВО/ВПРАВО
6. Добавь систему очков (чем дальше едешь, тем больше очков)
7. Сделай столкновения (game over при ударе)
8. Добавь спидометр или индикатор скорости
9. Фон: пустыня/город/космос (в зависимости от темы)
10. Игра должна быть динамичной и интересной!
""",
    'Шутер': """
ТРЕБОВАНИЯ К ШУТЕРУ:
1. HTML5 Canvas (800x600)
2. Игрок (корабль/танк/солдат) с детальной графикой
3. Минимум 5-10 врагов разных типов
4. Стрельба: пробел для выстрела
5. Враги стреляют в ответ
6. Система здоровья (HP бар)
7. Система очков за уничтожение
8. Взрывы (частицы/анимация)
9. Волны врагов (усложнение со временем)
10. Босс в конце (опционально)
""",
    'Аркада': """
ТРЕБОВАНИЯ К АРКАДЕ:
1. HTML5 Canvas (800x600)
2. Главный герой с анимацией
3. Минимум 10-15 объектов для сбора/избегания
4. Управление стрелками или WASD
5. Система очков и рекордов
6. Уровни сложности (ускорение со временем)
7. Бонусы/апгрейды
8. Красочная графика с эффектами
9. Звуковые эффекты (опционально)
10. Экран Game Over с результатом
""",
    'Платформер': """
ТРЕБОВАНИЯ К ПЛАТФОРМЕРУ:
1. HTML5 Canvas (800x600)
2. Игрок с физикой (прыжки, гравитация)
3. Минимум 5-7 платформ разного размера
4. Враги на платформах (2-3 штуки)
5. Сбор монет/предметов (минимум 10)
6. Управление: стрелки + пробел для прыжка
7. Система очков
8. Финиш/цель уровня
9. Анимация персонажа
10. Красочный фон и декорации
""",
    'Головоломка': """
ТРЕБОВАНИЯ К ГОЛОВОЛОМКЕ:
1. HTML5 Canvas или DOM элементы
2. Игровое поле (сетка 5x5 или больше)
3. Минимум 15-20 элементов для взаимодействия
4. Логическая механика (соединение, сортировка,匹配)
5. Система уровней (3-5 уровней)
6. Подсчёт ходов/времени
7. Визуальная обратная связь
8. Кнопка "Рестарт"
9. Красивая графика
10. Постепенное усложнение
""",
    'Стратегия': """
ТРЕБОВАНИЯ К СТРАТЕГИИ:
1. HTML5 Canvas (800x600)
2. Игровая карта с ресурсами
3. База/юниты игрока (минимум 3 типа)
4. Вражеские юниты (2-3 типа)
5. Система ресурсов (золото/энергия)
6. Постройка/создание юнитов
7. Пошаговая или real-time механика
8. Система боя
9. Индикаторы здоровья
10. Интерфейс управления
""",
    'RPG': """
ТРЕБОВАНИЯ К RPG:
1. HTML5 Canvas (800x600)
2. Персонаж с характеристиками (HP, XP, уровень)
3. Мир с локациями (минимум 3 зоны)
4. Враги/монстры (5-7 типов)
5. Система боя (пошаговая или action)
6. Инвентарь/предметы (минимум 5 предметов)
7. Диалоги/NPC (опционально)
8. Квесты/цели
9. Прокачка характеристик
10. Сохранение прогресса (localStorage)
"""
}

def generate_game_code(user_prompt):
    """Генерация кода игры с усиленными требованиями"""
    
    # Определяем жанр из промпта
    genre = None
    for g in GAME_REQUIREMENTS.keys():
        if g.lower() in user_prompt.lower():
            genre = g
            break
    
    # Базовые требования для ВСЕХ игр
    base_requirements = """
ОБЯЗАТЕЛЬНЫЕ ТРЕБОВАНИЯ:
1. Создай ПОЛНОЦЕННУЮ играбельную игру (не демо, не заглушку!)
2. Используй HTML5 Canvas 800x600 для рендеринга
3. Включи ВСЁ в один HTML-файл (CSS в <style>, JS в <script>)
4. Игра должна работать СРАЗУ после открытия файла
5. Добавь красивый визуальный стиль с цветами и эффектами
6. Реализуй плавное управление (60 FPS)
7. Добавь систему очков и рекордов (localStorage)
8. Сделай экран начала игры с кнопкой "НАЧАТЬ"
9. Сделай экран Game Over с кнопкой "ЗАНОВО"
10. Добавь инструкции по управлению на экране
11. Размер файла: не менее 300-500 строк кода
12. Используй современные практики (ES6+, requestAnimationFrame)
13. Добавь звуковые эффекты (Web Audio API, опционально)
14. Сделай адаптацию под window resize
15. Добавь частицы/эффекты для красоты
"""

    # Специфичные требования для жанра
    genre_requirements = GAME_REQUIREMENTS.get(genre, "") if genre else """
ОБЩИЕ ТРЕБОВАНИЯ:
1. Минимум 10-15 интерактивных объектов на экране
2. Динамичный геймплей
3. Красочная графика
4. Плавная анимация
5. Интересная механика
"""

    # Формируем ФИНАЛЬНЫЙ промпт
    full_prompt = f"""Ты ПРОФЕССИОНАЛЬНЫЙ разработчик игр с 15-летним опытом. 
Твоя задача — создать ПОЛНОЦЕННУЮ, ИНТЕРЕСНУЮ и КРАСИВУЮ браузерную игру.

ХАРАКТЕРИСТИКИ:
{user_prompt}

{base_requirements}

{genre_requirements}

ВАЖНО:
- Это должна быть НАСТОЯЩАЯ игра, а не примитивная демонстрация!
- Используй объектно-ориентированный подход (классы для игрока, врагов и т.д.)
- Добавь минимум 5-10 функций для разных механик
- Сделай красивый UI с кнопками и индикаторами
- Используй яркие цвета и градиенты
- Добавь эффекты (свечение, тени, частицы)
- Код должен быть ЧИСТЫМ и хорошо структурированным

КРИТИЧЕСКИ ВАЖНО:
- Верни ТОЛЬКО HTML-код (от <!DOCTYPE html> до </html>)
- БЕЗ пояснений, БЕЗ markdown, БЕЗ комментариев о коде
- Игра должна быть ГОТОВА К ИГРЕ сразу!
- Минимум 400-600 строк кода
- Используй ВСЁ пространство Canvas (800x600)
- Сделай НЕЗАБЫВАЕМЫЙ игровой опыт!"""

    # Запрос к API
    payload = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.9,  # Выше для креативности
            "maxTokens": "8000"  # Ещё больше для большого кода
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты экспертный геймдев-разработчик. Создаёшь сложные, красивые и играбельные HTML5 игры. Отвечаешь ТОЛЬКО кодом."
            },
            {
                "role": "user",
                "text": full_prompt
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "x-folder-id": FOLDER_ID
    }
    
    try:
        print(f"\n{'='*70}")
        print(f"🎮 Генерация игры: {genre or 'Универсальная'}")
        print(f"{'='*70}")
        
        response = requests.post(YANDEX_API_URL, headers=headers, json=payload, timeout=150)
        
        if response.status_code != 200:
            return None, f"API error: {response.status_code}"
        
        data = response.json()
        game_code = data['result']['alternatives'][0]['message']['text']
        
        # Очистка кода
        game_code = clean_game_code(game_code)
        
        if not game_code.lower().strip().startswith('<!doctype'):
            return None, "Invalid response (no <!DOCTYPE>)"
        
        print(f"✅ Сгенерировано: {len(game_code)} символов")
        print(f"{'='*70}\n")
        
        return game_code, None
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None, str(e)

def clean_game_code(code):
    """Очистка кода от markdown и лишних символов"""
    code = re.sub(r'^```\s*html?\s*\n?', '', code, flags=re.IGNORECASE)
    code = re.sub(r'^```\s*\n?', '', code)
    code = re.sub(r'\n?\s*```\s*$', '', code)
    
    doctype_match = re.search(r'<!DOCTYPE\s+html', code, re.IGNORECASE)
    if doctype_match:
        code = code[doctype_match.start():]
    
    html_end_match = re.search(r'</html>', code, re.IGNORECASE)
    if html_end_match:
        code = code[:html_end_match.end()]
    
    return code.strip()

@app.route('/api/generate-game', methods=['POST'])
def api_generate_game():
    if not request.is_json:
        return jsonify({'success': False, 'error': 'JSON required'}), 400
    
    data = request.json
    user_prompt = data.get('prompt', '').strip()
    
    if not user_prompt:
        return jsonify({'success': False, 'error': 'No prompt'}), 400
    
    print(f"\n📋 Запрос: {user_prompt[:200]}...")
    
    game_code, error = generate_game_code(user_prompt)
    
    if error:
        return jsonify({'success': False, 'error': error}), 500
    
    return jsonify({
        'success': True,
        'error': None,
        'game_code': game_code
    })

@app.route('/api/status', methods=['GET'])
def api_status():
    return jsonify({
        'status': 'ok',
        'message': 'GameAI Generator Server v2.0',
        'version': '2.0.0'
    })

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🎮 GAMEAI GENERATOR SERVER v2.0")
    print("="*70)
    print(f"📡 http://localhost:5000")
    print(f"🎮 Генератор: http://localhost:5000/generator")
    print(f"🖼️ Галерея: http://localhost:5000/gallery")
    print(f"📧 Контакты: http://localhost:5000/contacts")
    print("="*70)
    print(f"\n📁 Проект: {os.path.abspath('.')}")
    print("\n⏳ Ожидание запросов...\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)