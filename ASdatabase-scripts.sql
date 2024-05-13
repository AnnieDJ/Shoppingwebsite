CREATE TABLE IF NOT EXISTS user (
 user_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
 username VARCHAR(255) NOT NULL UNIQUE,
 email VARCHAR(255) NOT NULL UNIQUE,
 password_hash VARCHAR(255) NOT NULL,
 salt VARCHAR(255) NOT NULL,
 role ENUM('customer', 'manager', 'staff', 'admin') NOT NULL,
);
CREATE TABLE IF NOT EXISTS customer (
 customer_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
 user_id INT NOT NULL,
 title VARCHAR(255),
 first_name VARCHAR(255),
 family_name VARCHAR(255),
 phone_number VARCHAR(20),
 address VARCHAR(255),
 date_of_birth DATE,
 FOREIGN KEY (user_id) REFERENCES user(user_id)
);
CREATE TABLE IF NOT EXISTS staff (
 staff_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
 user_id INT NOT NULL,
 title VARCHAR(255),
 first_name VARCHAR(255),
 family_name VARCHAR(255),
 phone_number VARCHAR(20),
 FOREIGN KEY (user_id) REFERENCES user(user_id)
);
CREATE TABLE IF NOT EXISTS manager (
 manager_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
 user_id INT NOT NULL,
 title VARCHAR(255),
 first_name VARCHAR(255),
 family_name VARCHAR(255),
 position VARCHAR(255),
 phone_number VARCHAR(20),
 FOREIGN KEY (user_id) REFERENCES user(user_id)
);
CREATE TABLE IF NOT EXISTS stores (
 store_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
 store_name VARCHAR(255) NOT NULL,
 address VARCHAR(255) NOT NULL,
 phone VARCHAR(20) NOT NULL,
 manager_id INT,
 FOREIGN KEY (manager_id) REFERENCES manager(manager_id)
);
CREATE TABLE IF NOT EXISTS equipment (
 equipment_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
 name VARCHAR(255) NOT NULL,
 description TEXT,
 category VARCHAR(255),
 purchase_date DATE,
 cost DECIMAL(10, 2),
 serial_number VARCHAR(255) UNIQUE NOT NULL,
 status ENUM('Available', 'Rented', 'Under Repair', 'Retired') NOT NULL,
 store_id INT NOT NULL,
 maximum_date INT,
 minimum_date INT,
 Image VARCHAR(255),
 FOREIGN KEY (store_id) REFERENCES stores(store_id)
);
CREATE TABLE IF NOT EXISTS Rentals (
 rental_id INT AUTO_INCREMENT PRIMARY KEY,
 user_id INT NOT NULL,
 equipment_id INT NOT NULL,
 start_date DATE NOT NULL,
 end_date DATE NOT NULL,
 status ENUM('Pending', 'Completed', 'Canceled') NOT NULL,
 FOREIGN KEY (user_id) REFERENCES Users(user_id),
 FOREIGN KEY (equipment_id) REFERENCES Equipment(equipment_id)
);
CREATE TABLE IF NOT EXISTS Orders (
 order_id INT AUTO_INCREMENT PRIMARY KEY,
 user_id INT NOT NULL,
 store_id INT NOT NULL,
 total_cost DECIMAL(10, 2) NOT NULL,
 tax DECIMAL(10, 2) NOT NULL,
 discount DECIMAL(10, 2) NOT NULL,
 final_price DECIMAL(10, 2) NOT NULL,
 status ENUM('Pending', 'Completed', 'Canceled') NOT NULL,
 creation_date DATE NOT NULL,
 FOREIGN KEY (user_id) REFERENCES Users(user_id),
 FOREIGN KEY (store_id) REFERENCES Stores(store_id)
);
CREATE TABLE IF NOT EXISTS Order_Items (
 order_item_id INT AUTO_INCREMENT PRIMARY KEY,
 order_id INT NOT NULL,
 equipment_id INT NOT NULL,
 quantity INT NOT NULL,
 price DECIMAL(10, 2) NOT NULL,
 FOREIGN KEY (order_id) REFERENCES Orders(order_id),
 FOREIGN KEY (equipment_id) REFERENCES Equipment(equipment_id)
);
CREATE TABLE IF NOT EXISTS Payments (
 payment_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
 order_id INT NOT NULL,
 user_id INT NOT NULL,
 payment_type ENUM('Credit Card', 'Debit Card', 'PayPal', 'Other') NOT NULL,
 payment_status ENUM('Processed', 'Pending', 'Failed', 'Refunded') NOT NULL,
 amount DECIMAL(10, 2) NOT NULL,
 payment_date DATE NOT NULL,
 FOREIGN KEY (order_id) REFERENCES orders(order_id),
 FOREIGN KEY (user_id) REFERENCES user(user_id)
);
CREATE TABLE IF NOT EXISTS promotions (
 promotion_id INT AUTO_INCREMENT PRIMARY KEY,
 title VARCHAR(255) NOT NULL,
 description TEXT,
 start_date DATE NOT NULL,
 end_date DATE NOT NULL,
 creator_id INT NOT NULL,
 store_id INT,
 FOREIGN KEY (creator_id) REFERENCES users(user_id),
 FOREIGN KEY (store_id) REFERENCES stores(store_id)
);
CREATE TABLE IF NOT EXISTS news (
 news_id INT AUTO_INCREMENT PRIMARY KEY,
 title VARCHAR(255) NOT NULL,
 content TEXT NOT NULL,
 publish_date DATE NOT NULL,
 creator_id INT NOT NULL,
 store_id INT,
 FOREIGN KEY (creator_id) REFERENCES users(user_id),
 FOREIGN KEY (store_id) REFERENCES stores(store_id)
);
CREATE TABLE IF NOT EXISTS messages (
 message_id INT AUTO_INCREMENT PRIMARY KEY,
 sender_id INT NOT NULL,
 receiver_id INT NOT NULL,
 content TEXT NOT NULL,
 timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 status ENUM('Sent', 'Received', 'Read') NOT NULL,
 FOREIGN KEY (sender_id) REFERENCES users(user_id),
 FOREIGN KEY (receiver_id) REFERENCES users(user_id)