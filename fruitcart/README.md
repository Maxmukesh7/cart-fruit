# FruitCart 🍎🛒

FruitCart is a fully featured, responsive e-commerce web application built with Django. It allows users to browse farm-fresh fruits, add them to a session-based cart, manage their orders, and securely check out.

## 🚀 Features
- **User Authentication:** Secure registration, login, and logout.
- **Product Catalog:** Browse fresh fruits with category filtering, search, sorting, and pagination.
- **Shopping Cart:** Session-based cart with dynamic quantity updates and validation.
- **Order Management:** Secure checkout, atomic stock reduction, and complete order history.
- **Responsive UI:** Beautiful, responsive design built with Vanilla HTML/CSS/JS (No Bootstrap/React).
- **Admin Dashboard:** Full Django admin integration to manage inventory, categories, and track order statuses.

## 🛠️ Tech Stack
- **Backend:** Python, Django 5.x
- **Database:** SQLite (default, easily swappable to PostgreSQL)
- **Frontend:** HTML5, CSS3 (Custom Design System), Vanilla JavaScript

## 📦 Installation & Setup

1. **Clone the repository:**
   `ash
   git clone https://github.com/yourusername/fruitcart.git
   cd fruitcart
   `

2. **Create a virtual environment:**
   `ash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   `

3. **Install dependencies:**
   `ash
   pip install -r requirements.txt
   `

4. **Run migrations:**
   `ash
   python manage.py migrate
   `

5. **Create a superuser (for admin access):**
   `ash
   python manage.py createsuperuser
   `

6. **Run the development server:**
   `ash
   python manage.py runserver
   `
   Open http://localhost:8000/ in your browser.

## ⚙️ Environment Variables
For production, you should use a .env file to securely store settings like SECRET_KEY, DEBUG, and database credentials. Currently, the project runs out-of-the-box using development defaults.

## 📸 Screenshots

| Home Page | Store Catalog |
| :---: | :---: |
| *(Add screenshot here)* | *(Add screenshot here)* |

| Shopping Cart | User Dashboard |
| :---: | :---: |
| *(Add screenshot here)* | *(Add screenshot here)* |

## 🔮 Future Improvements
- [ ] Integrate Stripe for online payments.
- [ ] Add PostgreSQL for production database.
- [ ] Implement email notifications for order confirmations.
