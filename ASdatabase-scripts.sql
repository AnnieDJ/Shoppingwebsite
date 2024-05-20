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
    store_id INT NOT NULL,
    title VARCHAR(255),
    first_name VARCHAR(255),
    family_name VARCHAR(255),
    phone_number VARCHAR(20),
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

-- not sure how many groups of data the tutor is expecting to see at the presentation, for now we will use data from 3 stores, each with 1 local manager, 2 staff members and a few items (to be updated), additionally with 1 customer, 1 admin and 1 national manager for testing and PO meeting.

INSERT INTO user (username, email, password_hash, salt, role, date_of_birth)
VALUES
-- Admin user
("rose123", "rose123@gmail.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "admin", "1977-12-12"),
-- National Manager
("peter123", "peter123@gmail.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "national_manager", "1980-10-10"),
-- Customer user
("tim123", "tim123@gmail.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "customer", "1975-02-02"),
-- Store 1 users
("jack123", "jack123@gmail.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "staff", "1990-01-01"),
("mia123", "mia123@gmail.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "staff", "1998-06-06"),
("john123", "john123@gmail.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "local_manager", "1985-05-05"),
-- Store 2 users
("daniel123", "daniel123@gmail.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "staff", "1993-07-07"),
("eva123", "eva123@gmail.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "staff", "1999-08-08"),
("james123", "james123@gmail.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "local_manager", "1980-09-09"),
-- Store 3 users
("henry123", "henry123@gmail.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "staff", "2000-10-10"),
("emily123", "emily123@gmail.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "staff", "1997-11-11"),
("steven123", "steven123@gmail.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "local_manager", "1983-07-20")
;

-- Insert data into the admin_national_manager table
INSERT INTO admin_national_manager (user_id, title, first_name, family_name, phone_number)
VALUES
(1, "Ms", "Rose", "Dawson", "0225871234"),
(2, "Mr", "Peter", "Collins", "0224859438")
;

-- Insert data into the local_manager table
INSERT INTO local_manager (user_id, store_id, title, first_name, family_name, phone_number)
VALUES
(6, 1, "Mr", "John", "Doe", "0255512345"),
(9, 2, "Mr", "James", "Smith", "0226785555"),
(12, 3, "Mr", "Steven", "Johnson", "02368524587")
;

-- Insert data into the staff table
INSERT INTO staff (user_id, store_id, title, first_name, family_name, phone_number)
VALUES
(4, 1, "Mr", "Jack", "Jones", "0240012345"),
(5, 1, "Miss", "Mia", "Roberts", "0265754258"),
(7, 2, "Mr", "Daniel", "Harrison", "0262542542"),
(8, 2, "Miss", "Eva", "Parker", "0236542582"),
(10, 3, "Mr", "Henry", "Reed", "0232574580"),
(11, 3, "Miss", "Emily", "Brooks", "0232251545")
;

-- Insert data into the customer table
INSERT INTO customer (user_id, title, first_name, family_name, phone_number, address)
VALUES
(3, "Mr", "Tim", "Doe", "0254525411", "11 milkfarm street, greengrass, Canterbury");

-- login password: A12345678