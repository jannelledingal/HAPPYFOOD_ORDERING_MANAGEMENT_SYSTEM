# 🍔 HAPPYFOOD Ordering Management System

**A Python-based Food Ordering and Management System**  
Developed as a final project to simulate a real-world restaurant ordering workflow — from customer orders to admin management — all in one application.

---

## 📋 Table of Contents
- [About the Project](#about-the-project)
- [Features](#features)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Installation & Setup](#installation--setup)
- [Usage Guide](#usage-guide)
- [Screenshots (Optional)](#screenshots-optional)
- [Contributors](#contributors)
- [License](#license)

---

## 🧩 About the Project
**HAPPYFOOD Ordering Management System** allows users (customers) to browse a restaurant menu, add items to a cart, and place orders.  
Admins can view and manage orders, update the menu, track sales, and maintain order history.

This project demonstrates core programming concepts including:
- Python GUI design
- File and database handling
- Modular programming
- CRUD operations (Create, Read, Update, Delete)

---

## 🚀 Features

### 👨‍🍳 Admin Features
- Login authentication  
- Manage food menu (add, update, delete items)  
- View and manage all customer orders  
- Access sales and order history  

### 🧑‍💻 Customer Features
- Browse food menu  
- Add to cart and checkout  
- View order history and receipts  

### 💾 System Features
- SQLite-based storage (`foodSQL` folder)  
- GUI interface using `tkinter`  
- Modular file structure for scalability  
- Automatic receipt generation (`receipt.py`)  

---

## 🗂️ Project Structure

```

FINAL PROJECT/
├── admin_history.py         # Admin order history page
├── admin_menu.py            # Admin menu interface
├── admin_menu_manage.py     # Manage menu items
├── admin_orders.py          # Handle customer orders
├── assets/                  # Images, icons, and UI resources
├── colors.py                # UI color configuration
├── customer_cart.py         # Customer cart system
├── customer_menu.py         # Customer-facing menu
├── customer_orders.py       # Customer order tracking
├── db.py                    # Database connection and queries
├── foodSQL/                 # Contains SQLite database files
├── main.py                  # Main launcher / entry point
├── receipt.py               # Receipt generator
└── **pycache**/             # Cached Python files

````

---

## 🧠 Technologies Used
| Component | Technology |
|------------|------------|
| Language | Python 3.x |
| GUI Library | Tkinter |
| Database | SQLite |
| Styling | Custom `colors.py` configuration |
| Tools | Python file handling, OOP design |

---

## ⚙️ Installation & Setup

### Prerequisites
- **Python 3.8 or higher**
- Basic knowledge of Python environment setup

### Steps
1. **Clone or Download** this repository:
   ```bash
   git clone https://github.com/jannelledingal/HAPPYFOOD_ORDERING_MANAGEMENT_SYSTEM.git

2. **Navigate** to the project folder:

   ```bash
   cd HAPPYFOOD_ORDERING_MANAGEMENT_SYSTEM/FINAL PROJECT
   ```
3. **Run the application**:

   ```bash
   python main.py
   ```
4. The GUI should appear — start by navigating through the admin or customer modules.

---

## 🖱️ Usage Guide

* **Customers** can view the food menu, add items to their cart, and place an order.
* **Admins** can log in, edit the menu, check orders, and view transaction history.
* All data (orders, menu items, receipts) are stored in the **`foodSQL`** database.

---

## 🖼️ Screenshots 


---

## 👩‍💻 Contributors

**Developed by:**

* Jannelle Jean R. Dingal
  

---

> **Note:**
> This project was created for academic purposes as part of an IT final requirement.
> It demonstrates functional modular programming, UI design, and database integration using Python(VS Code as IDE).
