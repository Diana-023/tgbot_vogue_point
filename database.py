import sqlite3
from config import DATABASE_NAME


class DatabaseManager:
    """Класс для управления базой данных магазина одежды"""
    
    def __init__(self):
        """Инициализация менеджера БД"""
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Установка соединения с БД"""
        try:
            self.connection = sqlite3.connect(DATABASE_NAME)
            self.cursor = self.connection.cursor()
            print("✓ Подключение к базе данных установлено")
            return True
        except Exception as e:
            print(f"✗ Ошибка подключения к БД: {e}")
            return False
    
    def disconnect(self):
        """Закрытие соединения с БД"""
        if self.connection:
            self.connection.close()
            print("✓ Соединение с БД закрыто")
    
    def create_tables(self):
        """Создание всех необходимых таблиц"""
        print("Создание таблиц...")
        
        # Таблица категорий
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )
        ''')
        print("  - Таблица 'categories' создана")
        
        # Таблица товаров
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                category_id INTEGER,
                stock INTEGER DEFAULT 0,
                size TEXT,
                color TEXT,
                image_url TEXT,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        print("  - Таблица 'products' создана")
        
        self.connection.commit()
        print("✓ Все таблицы успешно созданы")
    
    def add_sample_data(self):
        """Добавление тестовых данных"""
        print("Добавление тестовых данных...")
        
        # Проверяем, есть ли уже категории
        self.cursor.execute("SELECT COUNT(*) FROM categories")
        if self.cursor.fetchone()[0] == 0:
            # Добавляем категории
            categories = [
                ("Футболки", "Удобные и стильные футболки из хлопка"),
                ("Джинсы", "Классические и современные джинсы"),
                ("Платья", "Элегантные платья на любой случай"),
                ("Куртки", "Сезонные куртки и пуховики"),
                ("Свитера", "Теплые и уютные свитера")
            ]
            self.cursor.executemany(
                "INSERT INTO categories (name, description) VALUES (?, ?)", 
                categories
            )
            print("  - Добавлены категории")
            
            # Добавляем товары
            products = [
                # Футболки (category_id = 1)
                ("Белая футболка", "Хлопковая футболка классического кроя", 
                 19.99, 1, 50, "M", "Белый", ""),
                ("Черная футболка", "Базовый предмет гардероба", 
                 19.99, 1, 45, "L", "Черный", ""),
                ("Синяя футболка", "Футболка оверсайз", 
                 24.99, 1, 30, "XL", "Синий", ""),
                
                # Джинсы (category_id = 2)
                ("Слим джинсы", "Узкие джинсы из денима", 
                 59.99, 2, 30, "32", "Синий", ""),
                ("Классик джинсы", "Прямые джинсы", 
                 64.99, 2, 25, "34", "Темно-синий", ""),
                ("Скинни джинсы", "Обтягивающие джинсы", 
                 69.99, 2, 20, "30", "Черный", ""),
                
                # Платья (category_id = 3)
                ("Платье-футляр", "Элегантное повседневное платье", 
                 89.99, 3, 15, "S", "Красный", ""),
                ("Платье-миди", "Платье с цветочным принтом", 
                 79.99, 3, 12, "M", "Розовый", ""),
                
                # Куртки (category_id = 4)
                ("Кожаная куртка", "Натуральная кожа", 
                 199.99, 4, 10, "M", "Черный", ""),
                ("Пуховик", "Теплый зимний пуховик", 
                 149.99, 4, 8, "L", "Синий", ""),
                
                # Свитера (category_id = 5)
                ("Шерстяной свитер", "Теплый свитер из мериноса", 
                 79.99, 5, 20, "M", "Серый", ""),
                ("Хлопковый свитер", "Легкий свитер с узором", 
                 59.99, 5, 25, "L", "Зеленый", "")
            ]
            self.cursor.executemany('''
                INSERT INTO products (name, description, price, category_id, stock, size, color, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', products)
            print("  - Добавлены товары")
            
            self.connection.commit()
            print("✓ Тестовые данные добавлены")
        else:
            print("  - Данные уже существуют, пропускаем")
    
    def get_categories(self):
        """Получение списка всех категорий"""
        try:
            self.cursor.execute("SELECT id, name, description FROM categories")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения категорий: {e}")
            return []
    
    def get_products_by_category(self, category_id):
        """Получение товаров по категории"""
        try:
            self.cursor.execute('''
                SELECT id, name, price, size, color, stock 
                FROM products 
                WHERE category_id = ?
            ''', (category_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения товаров: {e}")
            return []
    
    def get_product_details(self, product_id):
        """Получение детальной информации о товаре"""
        try:
            self.cursor.execute('''
                SELECT p.id, p.name, p.description, p.price, p.stock, p.size, p.color, c.name
                FROM products p
                JOIN categories c ON p.category_id = c.id
                WHERE p.id = ?
            ''', (product_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Ошибка получения деталей товара: {e}")
            return None
    
    def filter_products_by_size(self, size):
        """Фильтрация товаров по размеру"""
        try:
            self.cursor.execute('''
                SELECT id, name, price, size, color, stock
                FROM products 
                WHERE size = ? AND stock > 0
            ''', (size,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка фильтрации по размеру: {e}")
            return []
    
    def filter_products_by_color(self, color):
        """Фильтрация товаров по цвету"""
        try:
            self.cursor.execute('''
                SELECT id, name, price, size, color, stock
                FROM products 
                WHERE color = ? AND stock > 0
            ''', (color,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка фильтрации по цвету: {e}")
            return []
    
    def search_products(self, keyword):
        """Поиск товаров по ключевому слову"""
        try:
            query = "%{}%".format(keyword.lower())
            self.cursor.execute('''
                SELECT id, name, price, size, color, stock
                FROM products 
                WHERE LOWER(name) LIKE ? OR LOWER(description) LIKE ?
            ''', (query, query))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка поиска товаров: {e}")
            return []
    
    def get_stock_info(self, product_id):
        """Получение информации о наличии"""
        try:
            self.cursor.execute('''
                SELECT name, stock FROM products WHERE id = ?
            ''', (product_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Ошибка получения наличия: {e}")
            return None


# Функции для обратной совместимости и простого использования
def init_database():
    """Инициализация базы данных с тестовыми данными"""
    db = DatabaseManager()
    if db.connect():
        db.create_tables()
        db.add_sample_data()
        db.disconnect()
        print("База данных готова к использованию")
        return True
    else:
        print("Ошибка инициализации базы данных")
        return False


def get_categories():
    """Получение всех категорий (упрощенная функция)"""
    db = DatabaseManager()
    db.connect()
    categories = db.get_categories()
    db.disconnect()
    return categories


def get_products_by_category(category_id):
    """Получение товаров по категории (упрощенная функция)"""
    db = DatabaseManager()
    db.connect()
    products = db.get_products_by_category(category_id)
    db.disconnect()
    return products


def get_product_details(product_id):
    """Получение деталей товара (упрощенная функция)"""
    db = DatabaseManager()
    db.connect()
    product = db.get_product_details(product_id)
    db.disconnect()
    return product


# Тестирование при запуске файла
if __name__ == "__main__":
    print("=" * 50)
    print("ТЕСТИРОВАНИЕ МОДУЛЯ БАЗЫ ДАННЫХ")
    print("=" * 50)
    
    # Тест инициализации
    print("\n[1] Инициализация БД...")
    init_database()
    
    # Тест подключения
    print("\n[2] Проверка подключения...")
    db = DatabaseManager()
    if db.connect():
        print("✓ Подключение успешно")
        
        # Тест получения категорий
        print("\n[3] Получение категорий:")
        categories = db.get_categories()
        for cat_id, name, desc in categories:
            print(f"   - {name}: {desc}")
        
        # Тест получения товаров
        if categories:
            print(f"\n[4] Товары в категории '{categories[0][1]}':")
            products = db.get_products_by_category(categories[0][0])
            for prod in products:
                print(f"   - {prod[1]} (${prod[2]}) - Размер: {prod[3]}, Цвет: {prod[4]}, В наличии: {prod[5]}")
            
            # Тест детальной информации
            if products:
                print(f"\n[5] Детальная информация о товаре '{products[0][1]}':")
                details = db.get_product_details(products[0][0])
                if details:
                    print(f"   - Название: {details[1]}")
                    print(f"   - Описание: {details[2]}")
                    print(f"   - Цена: ${details[3]}")
                    print(f"   - В наличии: {details[4]} шт.")
                    print(f"   - Размер: {details[5]}")
                    print(f"   - Цвет: {details[6]}")
        
        # Тест фильтрации
        print("\n[6] Фильтрация по размеру 'M':")
        size_products = db.filter_products_by_size("M")
        for prod in size_products:
            print(f"   - {prod[1]} (${prod[2]}) - {prod[3]}, {prod[4]}")
        
        print("\n[7] Фильтрация по цвету 'Черный':")
        color_products = db.filter_products_by_color("Черный")
        for prod in color_products:
            print(f"   - {prod[1]} (${prod[2]}) - {prod[3]}, {prod[4]}")
        
        db.disconnect()
    
    print("\n" + "=" * 50)
    print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    print("=" * 50)