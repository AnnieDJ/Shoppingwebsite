CREATE TABLE IF NOT EXISTS user (
 user_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
 username VARCHAR(255) NOT NULL UNIQUE,
 email VARCHAR(255) NOT NULL UNIQUE,
 date_of_birth DATE,
 password_hash VARCHAR(255) NOT NULL,
 salt VARCHAR(255) NOT NULL,
 role ENUM('customer', 'local_manager','national_manager', 'staff', 'admin') NOT NULL
);

CREATE TABLE IF NOT EXISTS customer (
 customer_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
 user_id INT NOT NULL,
 title VARCHAR(255),
 first_name VARCHAR(255),
 family_name VARCHAR(255),
 phone_number VARCHAR(20),
 address VARCHAR(255),
 FOREIGN KEY (user_id) REFERENCES user(user_id)
);
    
CREATE TABLE IF NOT EXISTS stores (
 store_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
 store_name VARCHAR(255) NOT NULL,
 address VARCHAR(255) NOT NULL,
 phone VARCHAR(20) NOT NULL
);
		
CREATE TABLE IF NOT EXISTS staff (
 staff_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
 user_id INT NOT NULL,
 title VARCHAR(255),
 first_name VARCHAR(255),
 family_name VARCHAR(255),
 phone_number VARCHAR(20),
 store_id INT,
 FOREIGN KEY (store_id) REFERENCES stores(store_id),
 FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE IF NOT EXISTS local_manager (
    local_manager_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    user_id INT NOT NULL,
    store_id INT NOT NULL,
    title VARCHAR(255),
    first_name VARCHAR(255),
    family_name VARCHAR(255),
    username VARCHAR(255),
    phone_number VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id)
);
    
CREATE TABLE IF NOT EXISTS admin_national_manager (
    admin_manager_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    user_id INT NOT NULL,
    title VARCHAR(255),
    first_name VARCHAR(255),
    family_name VARCHAR(255),
    username VARCHAR(255),
    phone_number VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
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
    
CREATE TABLE IF NOT EXISTS rentals (
 rental_id INT AUTO_INCREMENT PRIMARY KEY,
 user_id INT NOT NULL,
 equipment_id INT NOT NULL,
 start_date DATE NOT NULL,
 end_date DATE NOT NULL,
 status ENUM('Pending', 'Completed', 'Canceled') NOT NULL,
 FOREIGN KEY (user_id) REFERENCES user(user_id),
 FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
);
    
CREATE TABLE IF NOT EXISTS orders (
 order_id INT AUTO_INCREMENT PRIMARY KEY,
 user_id INT NOT NULL,
 store_id INT NOT NULL,
 total_cost DECIMAL(10, 2) NOT NULL,
 tax DECIMAL(10, 2) NOT NULL,
 discount DECIMAL(10, 2) NOT NULL,
 final_price DECIMAL(10, 2) NOT NULL,
 status ENUM('Pending', 'Completed', 'Canceled') NOT NULL,
 creation_date DATE NOT NULL,
 FOREIGN KEY (user_id) REFERENCES user(user_id),
 FOREIGN KEY (store_id) REFERENCES stores(store_id)
);
    
CREATE TABLE IF NOT EXISTS order_items (
 order_item_id INT AUTO_INCREMENT PRIMARY KEY,
 order_id INT NOT NULL,
 equipment_id INT NOT NULL,
 quantity INT NOT NULL,
 price DECIMAL(10, 2) NOT NULL,
 FOREIGN KEY (order_id) REFERENCES orders(order_id),
 FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
);
    
CREATE TABLE IF NOT EXISTS payments (
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
 FOREIGN KEY (creator_id) REFERENCES user(user_id),
 FOREIGN KEY (store_id) REFERENCES stores(store_id)
);
    
CREATE TABLE IF NOT EXISTS news (
 news_id INT AUTO_INCREMENT PRIMARY KEY,
 title VARCHAR(255) NOT NULL,
 content TEXT NOT NULL,
 publish_date DATE NOT NULL,
 creator_id INT NOT NULL,
 store_id INT,
 FOREIGN KEY (creator_id) REFERENCES user(user_id),
 FOREIGN KEY (store_id) REFERENCES stores(store_id)
);
    
CREATE TABLE IF NOT EXISTS messages (
 message_id INT AUTO_INCREMENT PRIMARY KEY,
 sender_id INT NOT NULL,
 receiver_id INT NOT NULL,
 content TEXT NOT NULL,
 timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 status ENUM('Sent', 'Received', 'Read') NOT NULL,
 FOREIGN KEY (sender_id) REFERENCES user(user_id),
 FOREIGN KEY (receiver_id) REFERENCES user(user_id)
);

INSERT INTO user (username, email, password_hash, salt, role, date_of_birth) 
VALUES 
('jack', 'jack@gmail.com', 'jack123', 'c4091291e1643d0b66f1d030fe8623f3ca482296576628ff7c71f6a7ec5a0981', 'staff', '1990-01-01'),
('join', 'join@gmail.com', 'join123', 'e55bfbe6d7e7dc1367637333d76bbc9987db2e18273d156b81c013d5ff2dc171', 'local_manager', '1985-05-05'),
('peter', 'peter@gmail.com', 'peter123','359ef946d0f504b5781c8c8917df88a5cae74d83c65d52497b6c895c8fa6adca', 'national_manager', '1980-10-10'),
('rose', 'rose@gmail.com', 'rose123','7e1eb7985b3fc64f5e2248f6bd3bc33695b65d5d813ae5b90278b7573aaa4cf9', 'admin', '1975-12-12');