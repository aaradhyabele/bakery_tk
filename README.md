<<<<<<< HEAD
# SWEETS 'N JOY - Bakery Management System

A professional, feature-rich Bakery Management System built during my early journey with Python. This application demonstrates the integration of a Tkinter-based desktop interface with a MySQL backend, featuring real-time inventory management, sales tracking, and machine-learning-based sales forecasting.

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Tkinter](https://img.shields.io/badge/UI-Tkinter-orange.svg)
![MySQL](https://img.shields.io/badge/Database-MySQL-lightblue.svg)
![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-green.svg)

## 🌟 Key Features

- **Inventory Dashboard**: Real-time tracking of bakery items, flavors, and stock levels.
- **Dynamic Point of Sale (POS)**: Interactive shopping cart system with automated stock validation and checkout.
- **Sales Intelligence**:
  - Automated revenue calculation.
  - Identification of top-selling items and flavors via MySQL stored procedures.
  - **Machine Learning Integration**: 7-day sales forecasting using Random Forest Regression (via Scikit-Learn).
- **Data Visualization**: Interactive sales trend graphs powered by Matplotlib.
- **Administrative Control**: Secure employee login system for accessing sensitive sales reports.
- **Feedback System**: Integrated customer feedback gathering.

## 🛠️ Technology Stack

- **Frontend**: Python Tkinter (with custom styling and themes)
- **Data Handling**: Pandas
- **Database**: MySQL (using `mysql-connector-python`)
- **Machine Learning**: Scikit-Learn (RandomForestRegressor)
- **Visualization**: Matplotlib
- **Reporting**: Pandas & Matplotlib

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- MySQL Server

### Database Setup

1. Open your MySQL terminal or workbench.
2. Create a database named `bakery1`:
   ```sql
   CREATE DATABASE bakery1;
   ```
3. Run the provided `database_setup.sql` script to initialize the tables and stored procedures.

### Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd bakery_tk
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Update the database credentials in `bakery_mgmt.py`:
   ```python
   self.mydb = mysql.connector.connect(
       host="localhost",
       user="your_username",
       password="your_password",
       database="bakery1"
   )
   ```

## 📈 ML Forecasting Logic

The system analyzes historical sales data to predict future demand. It uses `RandomForestRegressor` to map days of the week to historical sales volume, providing a rolling 7-day forecast to help manage bakery production more efficiently.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Note: This project was created as a learning milestone in Python development.*
=======
# Bakery_management
SWEETS’n JOY is a Python-based Bakery Management System with a Tkinter GUI and MySQL database. It handles inventory, billing, customer feedback, and employee sales reports. The system also integrates machine learning using Random Forest to predict future sales and support data-driven business decisions.
>>>>>>> 039d75ade1cd658b8cc90d728939aab52233835b
