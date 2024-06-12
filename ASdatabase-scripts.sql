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
    FOREIGN KEY (store_id) REFERENCES stores(store_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
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


CREATE TABLE IF NOT EXISTS category (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(255) UNIQUE,
    image VARCHAR(255)
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
    FOREIGN KEY (store_id) REFERENCES stores(store_id),
    FOREIGN KEY (category) REFERENCES category(category)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    store_id INT NOT NULL,
    total_cost DECIMAL(10, 2) NOT NULL,
    tax DECIMAL(10, 2) NOT NULL,
    discount DECIMAL(10, 2) NOT NULL,
    final_price DECIMAL(10, 2) NOT NULL,
    status ENUM ('Pending', 'Ongoing', 'Completed', 'Canceled') NOT NULL,
    creation_date DATE NOT NULL,
    CONSTRAINT orders_ibfk_1 FOREIGN KEY (user_id) REFERENCES user (user_id),
    CONSTRAINT orders_ibfk_2 FOREIGN KEY (store_id) REFERENCES stores (store_id)
);


CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    equipment_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    start_time DATE NOT NULL,
    end_time DATE NOT NULL,
    CONSTRAINT order_items_ibfk_1 FOREIGN KEY (order_id) REFERENCES orders (order_id),
    CONSTRAINT order_items_ibfk_2 FOREIGN KEY (equipment_id) REFERENCES equipment (equipment_id)
);


CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    order_id INT NOT NULL,
    user_id INT NOT NULL,
    payment_type ENUM('Credit Card') NOT NULL,
    payment_status ENUM('Processed', 'Pending', 'Failed', 'Refunded') NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date DATE NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);


CREATE TABLE IF NOT EXISTS discount (
    discount_id INT PRIMARY KEY,
    days INT NOT NULL,
    discount_pricing DECIMAL(5, 2) NOT NULL
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


CREATE TABLE IF NOT EXISTS equipment_repair_history (
    repair_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    equipment_id INT NOT NULL,
    store_id INT NOT NULL,
    status_from ENUM('Available', 'Rented', 'Under Repair', 'Retired') NOT NULL,
    status_to ENUM('Available', 'Rented', 'Under Repair', 'Retired') NOT NULL,
    change_date DATE NOT NULL,
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id)
);


CREATE TABLE IF NOT EXISTS equipment_rental_history (
    rental_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    equipment_id INT NOT NULL,
    store_id INT NOT NULL,
    status_from ENUM('Available', 'Rented', 'Under Repair', 'Retired') NOT NULL,
    status_to ENUM('Available', 'Rented', 'Under Repair', 'Retired') NOT NULL,
    change_date DATE NOT NULL,
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id)
);


CREATE TABLE IF NOT EXISTS reminders (
    reminder_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    sender_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (sender_id) REFERENCES user(user_id)
);


INSERT INTO user (username, email, date_of_birth, password_hash, salt, role) VALUES
-- Admin user
('superadmin', 'admin@agrihire-solutions.com', '1980-01-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'admin'),

-- National Manager
('manager666', 'manager@agrihire-solutions.com', '1980-02-01', "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", 'national_manager'),

-- Local Managers
('lincoln000', 'manager.lincoln@agrihire-solutions.com', '1985-03-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'local_manager'),
('rolleston000', 'manager.rolleston@agrihire-solutions.com', '1985-04-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'local_manager'),
('ashburton000', 'manager.ashburton@agrihire-solutions.com', '1985-05-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'local_manager'),

-- Staff Members
('lincoln001', 'staff1.lincoln@agrihire-solutions.com', '1990-06-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'staff'),
('lincoln002', 'staff2.lincoln@agrihire-solutions.com', '1991-01-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'staff'),
('lincoln003', 'staff3.lincoln@agrihire-solutions.com', '1992-03-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'staff'),
('lincoln004', 'staff4.lincoln@agrihire-solutions.com', '1993-03-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'staff'),
('lincoln005', 'staff5.lincoln@agrihire-solutions.com', '1994-04-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'staff'),
('rolleston1', 'staff1.rolleston@agrihire-solutions.com', '1995-05-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'staff'),
('rolleston2', 'staff2.rolleston@agrihire-solutions.com', '1996-06-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'staff'),
('rolleston3', 'staff3.rolleston@agrihire-solutions.com', '1997-07-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'staff'),
('rolleston4', 'staff4.rolleston@agrihire-solutions.com', '1998-08-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'staff'),
('rolleston5', 'staff5.rolleston@agrihire-solutions.com', '1999-09-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'staff'),
('ashburton1', 'staff1.ashburton@agrihire-solutions.com', '1990-01-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'staff'),
('ashburton2', 'staff2.ashburton@agrihire-solutions.com', '1991-02-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'staff'),
('ashburton3', 'staff3.ashburton@agrihire-solutions.com', '1992-03-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'staff'),
('ashburton4', 'staff4.ashburton@agrihire-solutions.com', '1993-04-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'staff'),
('ashburton5', 'staff5.ashburton@agrihire-solutions.com', '1994-05-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'staff'),

-- Customers
('liam123', 'liam123@gmail.com', '1980-07-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'customer'),
('jameson123', 'jameson123@gmail.com', '1981-07-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'customer'),
('carter123', 'carter123@gmail.com', '1982-07-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'customer'),
('mason123', 'mason123@gmail.com', '1983-07-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'customer'),
('logan123', 'logan123@gmail.com', '1984-07-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'customer'),
('jacob123', 'jacob123@gmail.com', '1985-07-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'customer'),
('michael123', 'michael123@gmail.com', '1986-07-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'customer'),
('tyler123', 'tyler123@gmail.com', '1987-07-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'customer'),
('alexander123', 'alexander123@gmail.com', '1988-07-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'customer'),
('ryan123', 'ryan123@gmail.com', '1989-07-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'customer'),
('daniel123', 'daniel123@gmail.com', '1992-07-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'customer'),
('william123', 'william123@gmail.com', '1991-07-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'customer'),
('mia123', 'mia123@gmail.com', '1990-07-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'customer'),
('amelia123', 'amelia123@gmail.com', '1993-07-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'customer'),
('charlotte123', 'charlotte123@gmail.com', '1994-07-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'customer'),
('evelyn123', 'evelyn123@gmail.com', '1995-07-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'customer'),
('abigail123', 'abigail123@gmail.com', '1996-07-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'customer'),
('harper123', 'harper123@gmail.com', '1997-07-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'customer'),
('emily123', 'emily123@gmail.com', '1998-07-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'customer'),
('zoe123', 'zoe123@gmail.com', '1999-07-01', 'a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609', 'e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff', 'customer')
;

INSERT INTO stores (store_id, store_name, address, phone) VALUES
(1, "Lincoln", "123 Farm Road, Lincoln", "0254258756"),
(2, "Rolleston", "456 Greengrass Road, Rolleston", "02354101456"),
(3, "Ashburton", "789 Harvest Road, Ashuburton", "0262102542")
;

-- Insert data into the admin_national_manager table
INSERT INTO admin_national_manager (user_id, title, first_name, family_name, phone_number) VALUES
(1, "Ms", "Rose", "Dawson", "0225871234"),
(2, "Mr", "Peter", "Collins", "0224859438")
;

-- Insert data into the local_manager table
INSERT INTO local_manager (user_id, store_id, title, first_name, family_name, phone_number) VALUES
(3, 1, "Mr", "John", "Doe", "0255512345"),
(4, 2, "Mr", "James", "Smith", "0226785555"),
(5, 3, "Mr", "Steven", "Johnson", "02368524587")
;

-- Insert data into the staff table
INSERT INTO staff (user_id, store_id, title, first_name, family_name, phone_number) VALUES
(6, 1, "Mr", "Jack", "Jones", "0240012345"),
(7, 1, "Miss", "Mia", "Roberts", "0265754258"),
(8, 1, "Mr", "Daniel", "Harrison", "0262542542"),
(9, 1, "Miss", "Eva", "Parker", "0236542582"),
(10, 1, "Mr", "Henry", "Reed", "0232574580"),
(11, 2, "Miss", "Emily", "Brooks", "0232251545"),
(12, 2, "Mr", "Ethan", "Parker", "0232574581"),
(13, 2, "Miss", "Emma", "Harper", "0232574582"),
(14, 2, "Miss", "Olivia", "Stone", "0232574583"),
(15, 2, "Mr", "Noah", "Flynn", "0225745840"),
(16, 3, "Miss", "Ava", "Turner", "0232574585"),
(17, 3, "Mr", "Oliver", "Mason", "0232574586"),
(18, 3, "Miss", "Sophia", "Carter", "0232574587"),
(19, 3, "Mr", "Aiden", "Ford", "0232574588"),
(20, 3, "Miss", "Isabella", "Pearce", "0232574589")
;

-- Insert data into the customer table
INSERT INTO customer (user_id, title, first_name, family_name, phone_number, address) VALUES
(21, "Mr", "Liam", "Brooks", "0254525411", "11 milkfarm street, greengrass, Canterbury"),
(22, "Mr", "Jameson", "Wilde", "0254525411", "11 milkfarm street, greengrass, Canterbury"),
(23, "Mr", "Carter", "Shaw", "0254525411", "11 milkfarm street, greengrass, Canterbury"),
(24, "Mr", "Mason", "Cole", "0254525411", "11 milkfarm street, greengrass, Canterbury"),
(25, "Mr", "Logan", "Knight", "0254525411", "11 milkfarm street, greengrass, Canterbury"),
(26, "Mr", "Jacob", "Ellis", "0254525411", "11 milkfarm street, greengrass, Canterbury"),
(27, "Mr", "Michael", "Bishop", "0254525411", "11 milkfarm street, greengrass, Canterbury"),
(28, "Mr", "Tyler", "Reed", "0254525411", "11 milkfarm street, greengrass, Canterbury"),
(29, "Mr", "Alexander", "Stone", "0254525411", "11 milkfarm street, greengrass, Canterbury"),
(30, "Mr", "Ryan", "Wolfe", "0254525411", "11 milkfarm street, greengrass, Canterbury"),
(31, "Mr", "Daniel", "Chase", "0254525411", "11 milkfarm street, greengrass, Canterbury"),
(32, "Mr", "William", "Dale", "0254525411", "11 milkfarm street, greengrass, Canterbury"),
(33, "Miss", "Mia", "Clarke", "0254525411", "11 milkfarm street, greengrass, Canterbury"),
(34, "Miss", "Amelia", "Barton", "0254525411", "11 milkfarm street, greengrass, Canterbury"),
(35, "Miss", "Charlotte", "Rose", "0254525411", "11 milkfarm street, greengrass, Canterbury"),
(36, "Miss", "Evelyn", "Blair", "0254525411", "11 milkfarm street, greengrass, Canterbury"),
(37, "Miss", "Abigail", "Wright", "0254525411", "11 milkfarm street, greengrass, Canterbury"),
(38, "Miss", "Harper", "Lee", "0254525411", "11 milkfarm street, greengrass, Canterbury"),
(39, "Miss", "Emily", "Ford", "0254525411", "11 milkfarm street, greengrass, Canterbury"),
(40, "Miss", "Zoe", "Bird", "0254525411", "11 milkfarm street, greengrass, Canterbury")
;


INSERT INTO category (category, image) VALUES
('Tractor', 'Tractor.jpg'),
('Wrapper', 'Wrapper.jpg'),
('Spreader', 'Spreader.jpg'),
('Excavator', 'Excavator.jpg');


INSERT INTO equipment (equipment_id, name, description, category, purchase_date, cost, serial_number, status, store_id, maximum_date, minimum_date, Image) VALUES
(1, "Deutz Fahr", "This 2019 Deutz Fahr 6185 RC shift professional series tractor has only done 2,670 hours and is in great condition and ready to go to work . 50kph front suspension, front linkage and pto, this tractor is a serious contracting machine and with the loader would add incredible versitility to any fleet.", "Tractor", "2015-01-01", 369, "5242875401", "Available", 1, "360", "1", "tractor1.jpg"),
(3, "Amazone", "Amazone UX5201 Super with 30 mtr boom , as new , 5200ltr tank with 580ltr fresh water , twin pumps 520ltrs/min , axle suspension , 9 sections with auto shut off , ISOBUS with Amazone joystick , DUS- Boom recirculation , comfort package , boom auto height control , LED lighting package.", "Spreader", "2015-01-01", 289, "5242875403", "Available", 1, "360", "1", "Spreader1.jpg"),
(4, "McHale/Fusion", "A2020 model. 22,000 bales. 1,000 speed gear box. 6 bar camless pickup. 650 tyres.", "Wrapper", "2015-01-01", 159, "5242875404", "Available", 1, "360", "1", "wrapper1.jpg"),
(5, "AManure Spreader", "*6 tonne super capacity
*4 tonne Urea capacity
*Wide belt to handle organic matter (poultry waste, etc) with ease
*E spreader in cab rate control
*Electronic door actuator", "Spreader", "2015-01-01", 359, "5242875405", "Available", 1, "360", "1", "spreader1.jpg"),
(6, "DX140LCR", "Subtype: Tracked-Excav
Make: Doosan
Model: DX140LCR", "Tractor", "2015-01-01", 169, "5242875406", "Available", 1, "360", "1", "excav1.jpg"),
(7, "JS130", "13.7 tonne operating weight, Long carriage - providing excellent breakout force, 600mm steel tracks, Large air conditioned cabin, Heated seat with air suspension, Hydraulic hitch, High flow hydraulics, 900mm general purpose bucket, Heavy duty X undercarriage, JCB 74kw Tier 3 diesel engine", "Tractor", "2015-01-01", 189, "5242875407", "Available", 1, "360", "1", "good1.png"),
(8, "CASE IH/Maxxum 125", "This Case Maxxum 125 Multi Controller Tractor has a Case LR2100 Self Levelling Loader and Bucket, 125HP Boost to 155HP, Active Drive 8 Speed Power Shift Transmission, Electronic Remotes, Integrated Loader Joystick Control,", "Tractor", "2015-01-01", 255, "5242875408", "Available", 1, "360", "1", "good2.png"),
(9, "Taege/4.8m Triple Box Air Seeder", "Taege 4.8m Air Seeder - triple box drill, 2 x 850L hoppers & 1 x 200L hopper, all three hoppers are electrically driven, all three are very easy to calibrate, Monitor shows fan speed and seeding rate of all hoppers, 4.8m working width and folds to 3.1m for road transport, covering harrows, 121mm tine spacing. Tilth grows seed.", "Tractor", "2015-01-01", 200, "5242875409", "Available", 1, "360", "1", "good3.png"),
(10, "Merlo/P72.10", "With a max of 10 metre reach and 7.2 ton lift it is well suited to construction. The frame levelling and side shift make it ideal for accurate placement of goods on an uneven site and the single joystick makes it easy to control.", "Tractor", "2015-01-01", 260, "5242875410", "Available", 1, "360", "1", "good4.png"),
(11, "Fendt/Rotana 160V", "SOBUS, Also has monitor, bale size 0.9m to 1.60m, workshop checked, finance package available, happy to on farm.", "Tractor", "2015-01-01", 289, "5242875411", "Available", 1, "360", "1", "good5.png"),
(12, "PIUMA", "Only 1400mm wide, 4 Wheel Steering so great turning circle for tight headlands
Cruise Control for steering, 4 Conveyor belts, holds two bins while filling one
Gentle delivery from conveyor to bin, very quiet and economical 25 HP Diesel engine
Four Adjustable Height Platforms while two harvest in front at ground level.", "Tractor", "2015-01-01", 200, "5242875412", "Available", 1, "360", "1", "good6.png"),
(13, "Uni drill", "24 row, 3 metre trailing disc drill.
NZs most cost effective disc direct drill.
Ideal for over sowing, into stubble or cultivated ground.
Fewer moving parts; low ongoing repair and maintenance.
Narrow row spacing but staggered design allows good trash clearance.
Long life Tungsten carbide tipped coulters
Mounted on rubber Duratorque suspension for easy maintenance
Self clean design Guttler roller.
700L capacity hopper for high speed drilling, quick and easy calibration, convenient emptying, and individual row accuracy, with the ability to sow to the last quantity of seed, with all seed types.", "Tractor", "2015-01-01", 180, "5242875413", "Available", 1, "360", "1", "good7.png"),
(14, "Antonio Carraro", "Gearing 16F x 16R
98 hp Kubota engine
R series steering isodiametric tractor
With reversible driving position
Powerful and streamlined
Extremely versatile and ideally suited to a wide range of applications.", "Tractor", "2015-01-01", 300, "5242875414", "Available", 1, "360", "1", "good8.png"),
(15, "Taege/300AS121D", "Brand New Taege 3.1m air seeder, 25 run 121mm row spacing, plastic seed & fert hoppers, both 850L so easy half ton of seed & fert, Taege electric drive, oil cooler for hydraulic fan, Wide tyres, safety rail, small seed inserts, covering harrows, roll top hopper covers, very smart and easy to use. We can add a third hopper for another $13000 + gst which is 200L and set up to broadcast small seeds or slug bait.", "Spreader", "2015-01-01", 289, "5242875415", "Available", 1, "340", "1", "good9.png"),
(16, "Moore/Unidrill", "The most straight forward, easy to use, and functional pasture based drill on the market
* Single discs
*90mm row spacing
*Rear guttler roller - very effective in pugged conditions and consolidating cultivated soil
*Accord metering system and pneumatic hopper is easy to set up and can handle any seed type", "Spreader", "2015-01-01", 270, "5242875416", "Available", 1, "360", "1", "good10.png"),
(17, "Maschio Jumbo 8.0mtr", "Maschio Jumbo 8.0mtr Power Harrow , Farmer owned , very tidy , as new Quickfit Tungsten tines , hydraulic depth control of tooth packer roller and leveling board , contour control , awesome efficient cultivation tool", "Spreader", "2015-01-01", 290, "5242875417", "Available", 1, "360", "1", "good11.png"),
(18, "Kverneland/95130C/Rakes", "The Kverneland 94125 C and 95130 C are targeted at making lighter work of tough and demanding operations. With an impressive capacity of 12.50m working width, straightforward design and the possibility to adjust both work and swath width, they are designed to boost the complete process of collection and pick-up, altering to the changing crop intensity during the season. The Kverneland 12.5m 4-rotor rake is offered with a choice of either ProLine or CompactLine gearbox. Both machines are similar in construction.", "Spreader", "2015-01-01", 260, "5242875418", "Available", 1, "360", "1", "good12.png"),
(19, "McHale/V660", "Single belt
Rotor feed with 15 knives
2m pick up
bale size upto 1.68m", "Spreader", "2015-01-01", 340, "5242875419", "Available", 1, "360", "1", "good13.png"),
(20, "Combi RX148 Multi-feeder", "Hustler Chainless Rear Floor Combi RX148 Multi-feeder with Brakes. 14.2 cube (17 cube heaped). Can handle all bale types and shapes and has awesome stability in rolling country. Can add other spec including scales", "Spreader", "2015-01-01", 310, "5242875420", "Available", 1, "360", "1", "good14.png"),
(21, "300EDBT121SS", "TAEGE 300EDBT 121 3M DRILL, twin box, Stainless steel fert box, 121mm tine spacing, electronic rate control, small seed inserts, Broadcasting system, covering harrows, safety chain, LED tratier lights,Hazard panels, 2.8m drilling width", "Spreader", "2015-01-01", 289, "5242875421", "Available", 1, "360", "1", "good15.png"),
(22, "New Holland T5.120", "A compact tractor ideal for a variety of tasks in any farm setting, equipped with 120HP engine.", "Spreader", "2015-01-01", 350, "5242875422", "Available", 1, "360", "1", "good1.png"),
(23, "John Deere 5075E", "A powerful utility tractor designed for easy operation, offering a 75HP engine and optimal efficiency.", "Spreader", "2015-01-01", 360, "5242875423", "Available", 1, "360", "1", "good2.png"),
(24, "Case IH Magnum 340", "340HP high-efficiency tractor, offers superior performance for large-scale agricultural operations.", "Spreader", "2015-01-01", 380, "5242875424", "Available", 1, "360", "1", "good3.png"),
(25, "Bobcat S770", "Skid-steer loader designed for tough work, yet easy to maneuver and operate in tight spaces.", "Spreader", "2015-01-01", 290, "5242875425", "Available", 1, "360", "1", "excavator1.jpg"),
(26, "Komatsu PC350LC-8", "Robust tracked excavator ideal for heavy-duty tasks, with a powerful lifting capacity and precise control.", "Excavator", "2015-01-01", 410, "5242875426", "Available", 1, "360", "1", "good4.png"),
(27, "Hitachi ZX350LC-6", "Hitachi's medium excavator, perfect for jobs requiring a durable and reliable machine.", "Excavator", "2015-01-01", 395, "5242875427", "Available", 1, "360", "1", "good5.png"),
(28, "Anderson Hybrid X", "A highly efficient bale wrapper, suitable for large and small farms wanting to improve feed quality.", "Excavator", "2015-01-01", 275, "5242875428", "Available", 1, "360", "1", "good6.png"),
(29, "McHale 991BE", "A fully automated bale wrapper providing high-speed operation and precision.", "Excavator", "2015-01-01", 265, "5242875429", "Available", 1, "360", "1", "good7.png"),
(30, "Kuhn SW 4014", "Auto-load bale wrapper with a unique design allowing for non-stop wrapping – high efficiency.", "Excavator", "2015-01-01", 255, "5242875430", "Available", 1, "360", "1", "good8.png"),
(31, "Hardi Navigator 4000", "Spreader with a 4000L tank, designed for large fields, includes advanced tech for precision agriculture.", "Excavator", "2015-01-01", 345, "5242875431", "Available", 1, "360", "1", "good9.png"),
(32, "Berthoud Raptor 4240", "High-capacity field Spreader, offers excellent maneuverability and effective crop protection.", "Excavator", "2015-01-01", 330, "5242875432", "Available", 1, "360", "1", "good10.png"),
(33, "Fendt Rogator 655", "A Spreader known for its robust performance and precision, suitable for all crop types.", "Excavator", "2015-01-01", 320, "5242875433", "Available", 1, "360", "1", "good1.png"),
(34, "CAT 299D3 XE Land Management", "Caterpillar's robust compact track loader designed for land-clearing and forestry management.", "Excavator", "2015-01-01", 405, "5242875434", "Available", 1, "360", "1", "good2.png"),
(35, "John Deere XUV835M", "Gator Utility Vehicle with high-performance features, ideal for rugged landscapes and farming tasks.", "Excavator", "2015-01-01", 310, "5242875435", "Available", 1, "360", "1", "good3.png"),
(36, "Kubota M7060", "70 HP utility tractor, offers hydraulic shuttle shifting for easy operation in a variety of tasks.", "Excavator", "2015-01-01", 298, "5242875436", "Available", 1, "360", "1", "good4.png"),
(37, "CLAAS Axion 950", "Powerful tractor with a 410 HP engine, designed for heavy-duty agricultural tasks.", "Wrapper", "2015-01-01", 420, "5242875437", "Available", 1, "360", "1", "good5.png"),
(38, "Krone Big M 450", "Self-propelled mower conditioner with exceptional area performance, designed for large-scale farming.", "Wrapper", "2015-01-01", 435, "5242875438", "Available", 1, "360", "1", "good7.png"),
(39, "Massey Ferguson 7726", "A reliable tractor with a Dyna-6 transmission and a 255 HP engine suitable for a variety of farm tasks.", "Wrapper", "2015-01-01", 410, "5242875439", "Available", 1, "360", "1", "good2.png"),
(40, "Valtra N174", "Versatile tractor known for its comfort and efficiency, equipped with a 201 HP engine.", "Wrapper", "2015-01-01", 398, "5242875440", "Available", 1, "360", "1", "good1.png"),
(41, "Yanmar VIO80", "An 8-ton class mini excavator with zero tail swing, perfect for tight job sites and urban work.", "Wrapper", "2015-01-01", 380, "5242875441", "Available", 2, "360", "1", "good3.png"),
(42, "Volvo EC250D", "Robust 25-ton crawler excavator, offers high durability and excellent digging capacity.", "Wrapper", "2015-01-01", 410, "5242875442", "Available", 2, "360", "1", "good6.png"),
(43, "Takeuchi TB290", "Compact hydraulic excavator ideal for urban environments, offering a 9-ton operating weight.", "Wrapper", "2015-01-01", 365, "5242875443", "Available", 2, "360", "1", "good7.png"),
(44, "Lemken Sirius 10", "High capacity Spreader with advanced technology for precision application of plant protection products.", "Spreader", "2015-01-01", 350, "5242875444", "Available", 2, "360", "1", "good8.png"),
(45, "Rau Spridotrain 28", "Tractor-pulled Spreader with a 2800 liter tank, ideal for medium to large farms.", "Spreader", "2015-01-01", 340, "5242875445", "Available", 2, "360", "1", "good6.png"),
(46, "Tanco Autowrap 1400 EH", "Bale wrapper capable of handling both round and square bales, enhances forage quality.", "Tractor", "2015-01-01", 325, "5242875446", "Available", 2, "360", "1", "tractor1.jpg"),
(47, "McHale 998", "Square bale wrapper, provides high speed and consistent performance, essential for large operations.", "Tractor", "2015-01-01", 315, "5242875447", "Available", 2, "360", "1", "good1.png"),
(48, "Kuhn SW 4014", "Integrated bale wrapper with a unique auto-loading system, minimizes labor and maximizes efficiency.", "Tractor", "2015-01-01", 305, "5242875448", "Available", 2, "360", "1", "good2.png"),
(49, "Kubota M7-171", "Mid-range tractor with advanced features, providing reliable performance and superior comfort.", "Excavator", "2015-01-01", 420, "5242875449", "Available", 2, "360", "1", "good9.png"),
(50, "New Holland T7.315", "High-power tractor designed for large-scale farming, combines efficiency and durability.", "Tractor", "2015-01-01", 430, "5242875450", "Available", 2, "360", "1", "good4.png"),
(51, "JCB Fastrac 8330", "High-speed tractor offering unique suspension for superior ride quality on and off the field.", "Tractor", "2015-01-01", 440, "5242875451", "Available", 2, "360", "1", "good8.png"),
(52, "Bobcat E85", "Compact excavator that offers impressive digging force and depth, ideal for a variety of tasks.", "Excavator", "2015-01-01", 355, "5242875452", "Available", 2, "360", "1", "good7.png"),
(53, "Caterpillar 308E2 CR", "Mini hydraulic excavator designed for performance and comfort, with reduced tail swing design for tight spaces.", "Excavator", "2015-01-01", 365, "5242875453", "Available", 2, "360", "1", "good5.png"),
(54, "John Deere 345G LC", "Large-scale excavator offering exceptional reach, depth, and lifting capacity, suited for heavy construction.", "Excavator", "2015-01-01", 375, "5242875454", "Available", 2, "360", "1", "good13.png"),
(55, "Fendt Rogator 655", "High-end Spreader with unmatched application precision, built for the most demanding farming tasks.", "Spreader", "2015-01-01", 360, "5242875455", "Available", 2, "360", "1", "good12.png"),
(56, "Challenger RoGator 1300B", "Robust self-propelled Spreader, features a 1300 gallon tank for uninterrupted spraying on large fields.", "Spreader", "2015-01-01", 370, "5242875456", "Available", 2, "360", "1", "good1.png"),
(57, "Anderson RB580", "Versatile bale wrapper, allows for wrapping both round and square bales efficiently.", "Wrapper", "2015-01-01", 290, "5242875457", "Available", 2, "360", "1", "good1.png"),
(58, "Vermeer BW5500", "Premium bale wrapper known for its durability and efficiency, capable of handling extreme conditions.", "Wrapper", "2015-01-01", 300, "5242875458", "Available", 2, "360", "1", "good11.png"),
(59, "Massey Ferguson WR9870", "The swather provides excellent maneuverability and power for efficient cutting and conditioning.", "Spreader", "2015-01-01", 380, "5242875459", "Available", 2, "360", "1", "good2.png"),
(60, "Case IH Patriot 4430", "State-of-the-art Spreader, provides precise application with less waste, suited for all crop types.", "Spreader", "2015-01-01", 390, "5242875460", "Available", 2, "360", "1", "good9.png"),
(61, "Deutz-Fahr 9340 TTV", "High-tech tractor with 336 HP for maximum productivity in larger agricultural operations.", "Tractor", "2015-01-01", 460, "5242875461", "Available", 3, "360", "1", "tractor1.jpg"),
(62, "Zetor Forterra HD", "120 HP tractor with high durability and robust performance, ideal for tough tasks.", "Tractor", "2015-01-01", 445, "5242875462", "Available", 3, "360", "1", "good1.png"),
(63, "McCormick X7.670", "High-performance tractor with a 195 HP engine, designed for efficiency and comfort.", "Tractor", "2015-01-01", 430, "5242875463", "Available", 3, "360", "1", "good7.png"),
(64, "Kubota KX080-4", "Compact excavator with superior lifting capacity and low emission engine, ideal for urban environments.", "Excavator", "2015-01-01", 395, "5242875464", "Available", 3, "360", "1", "good2.png"),
(65, "Liebherr R9800", "One of the worlds largest excavators, designed for professional mining operations.", "Excavator", "2015-01-01", 485, "5242875465", "Available", 3, "360", "1", "good9.png"),
(66, "Hyundai HX220L", "Robust 22-ton excavator with advanced features for enhanced control and efficiency.", "Excavator", "2015-01-01", 410, "5242875466", "Available", 3, "360", "1", "good2.png"),
(67, "Silvan Selecta Gold 2000", "Powerful Spreader with a 2000-liter tank, ideal for large farms requiring efficient crop management.", "Spreader", "2015-01-01", 380, "5242875467", "Available", 3, "360", "1", "good8.png"),
(68, "Gaspardo Manta 12-Row Planter", "Precision planter for high-speed, accurate seed placement, ensuring maximum crop yields.", "Spreader", "2015-01-01", 365, "5242875468", "Available", 3, "360", "1", "good2.png"),
(69, "Amazone UX 11200", "Super high-capacity field Spreader with 12000-liter tank for uninterrupted spraying sessions.", "Spreader", "2015-01-01", 390, "5242875469", "Available", 3, "360", "1", "good6.png"),
(70, "Tanco 1400 EH Autowrap", "Highly efficient square and round bale wrapper, perfect for large-scale operations.", "Wrapper", "2015-01-01", 310, "5242875470", "Available", 3, "360", "1", "good4.png"),
(71, "Lely Tigo XR 75", "Combination loader and silage cutter, offers exceptional cutting and loading capabilities.", "Wrapper", "2015-01-01", 300, "5242875471", "Available", 3, "360", "1", "good1.png"),
(72, "Vicon FastBale", "Dual-purpose bale wrapper capable of wrapping both wet and dry bales efficiently.", "Wrapper", "2015-01-01", 325, "5242875472", "Available", 3, "360", "1", "good2.png"),
(73, "Fiatagri F130", "Powerful tractor with great versatility, ideal for both field and hauling operations.", "Tractor", "2015-01-01", 455, "5242875473", "Available", 3, "360", "1", "tractor1.jpg"),
(74, "Mahindra 2655", "Compact and agile tractor, perfect for small to medium-sized farms or orchards.", "Tractor", "2015-01-01", 420, "5242875474", "Available", 3, "360", "1", "good3.png"),
(75, "David Brown 995", "Classic tractor renowned for its reliability and durability, suitable for all types of agricultural activities.", "Tractor", "2015-01-01", 435, "5242875475", "Available", 3, "360", "1", "good4.png"),
(76, "Caterpillar 336F L XE", "High-efficiency large excavator with integrated technology to save fuel and reduce emissions.", "Excavator", "2015-01-01", 475, "5242875476", "Available", 3, "360", "1", "good5.png"),
(77, "JCB 3CX", "Backhoe loader known for its versatility and performance in urban construction and excavating operations.", "Excavator", "2015-01-01", 460, "5242875477", "Available", 3, "360", "1", "good6.png"),
(78, "Komatsu PC210 LCi-10", "Intelligent Machine Control excavator that offers precision in grading and excavating with minimal operator input.", "Excavator", "2015-01-01", 445, "5242875478", "Available", 3, "360", "1", "good7.png"),
(79, "Hardi Saritor 62 Active", "Self-propelled Spreader with a 6200-liter tank and Active Air suspension for optimal field performance.", "Spreader", "2015-01-01", 360, "5242875479", "Available", 3, "360", "1", "good8.png"),
(80, "Agco RoGator 1300", "Dynamic Spreader designed for large-scale and high-precision chemical applications in modern farming.", "Spreader", "2015-01-01", 370, "5242875480", "Available", 3, "360", "1", "good9.png");


INSERT INTO orders (user_id, store_id, total_cost, tax, discount, final_price, status, creation_date) VALUES
(22, 1, 100, 15, 0, 115, 'Pending', '2024-05-20'),
(23, 1, 120, 18, 0, 138, 'Pending', '2024-05-21'),
(24, 1, 130, 19.5, 0, 149.5, 'Pending', '2024-05-22'),
(25, 1, 140, 21, 0, 161, 'Pending', '2024-05-23'),
(25, 1, 150, 22.5, 0, 172.5, 'Pending', '2024-05-24'),
(26, 1, 160, 24, 0, 184, 'Pending', '2024-05-25'),
(27, 1, 170, 25.5, 0, 195.5, 'Pending', '2024-05-26'),
(28, 1, 180, 27, 0, 207, 'Pending', '2024-05-27'),
(29, 1, 190, 28.5, 0, 218.5, 'Pending', '2024-05-28'),
(30, 1, 200, 30, 0, 230, 'Pending', '2024-05-29'),
(31, 1, 110, 16.5, 0, 126.5, 'Pending', '2024-05-30'),
(32, 1, 120, 18, 0, 138, 'Pending', '2024-05-31'),
(33, 1, 130, 19.5, 0, 149.5, 'Pending', '2024-06-01'),
(34, 1, 140, 21, 0, 161, 'Pending', '2024-06-02'),
(22, 1, 150, 22.5, 0, 172.5, 'Ongoing', '2024-06-03'),
(36, 1, 160, 24, 0, 184, 'Ongoing', '2024-06-04'),
(37, 1, 170, 25.5, 0, 195.5, 'Ongoing', '2024-06-05'),
(38, 1, 180, 27, 0, 207, 'Ongoing', '2024-06-06'),
(39, 1, 190, 28.5, 0, 218.5, 'Ongoing', '2024-06-07'),
(40, 1, 200, 30, 0, 230, 'Ongoing', '2024-06-08'),
(21, 1, 210, 31.5, 0, 241.5, 'Ongoing', '2024-06-09'),
(22, 1, 220, 33, 0, 253, 'Ongoing', '2024-06-10'),
(23, 1, 230, 34.5, 0, 264.5, 'Ongoing', '2024-06-11'),
(24, 1, 240, 36, 0, 276, 'Ongoing', '2024-06-12'),
(25, 1, 250, 37.5, 0, 287.5, 'Ongoing', '2024-06-13'),
(26, 1, 260, 39, 0, 299, 'Ongoing', '2024-06-14'),
(27, 1, 270, 40.5, 0, 310.5, 'Ongoing', '2024-06-15'),
(22, 1, 280, 42, 0, 322, 'Completed', '2024-06-16'),
(29, 1, 290, 43.5, 0, 333.5, 'Completed', '2024-06-17'),
(30, 1, 300, 45, 0, 345, 'Completed', '2024-06-18'),
(22, 2, 105, 15.75, 0, 120.75, 'Pending', '2024-05-20'),
(23, 2, 110, 16.5, 0, 126.5, 'Pending', '2024-05-21'),
(24, 2, 115, 17.25, 0, 132.25, 'Pending', '2024-05-22'),
(25, 2, 120, 18, 0, 138, 'Pending', '2024-05-23'),
(26, 2, 125, 18.75, 0, 143.75, 'Pending', '2024-05-24'),
(27, 2, 130, 19.5, 0, 149.5, 'Pending', '2024-05-25'),
(28, 2, 135, 20.25, 0, 155.25, 'Pending', '2024-05-26'),
(29, 2, 140, 21, 0, 161, 'Pending', '2024-05-27'),
(30, 2, 145, 21.75, 0, 166.75, 'Pending', '2024-05-28'),
(31, 2, 150, 22.5, 0, 172.5, 'Pending', '2024-05-29'),
(32, 2, 155, 23.25, 0, 178.25, 'Ongoing', '2024-06-03'),
(33, 2, 160, 24, 0, 184, 'Ongoing', '2024-06-04'),
(34, 2, 165, 24.75, 0, 189.75, 'Ongoing', '2024-06-05'),
(35, 2, 170, 25.5, 0, 195.5, 'Ongoing', '2024-06-06'),
(36, 2, 175, 26.25, 0, 201.25, 'Ongoing', '2024-06-07'),
(37, 2, 180, 27, 0, 207, 'Completed', '2024-06-08'),
(38, 2, 185, 27.75, 0, 212.75, 'Completed', '2024-06-09'),
(39, 2, 190, 28.5, 0, 218.5, 'Completed', '2024-06-10'),
(40, 2, 195, 29.25, 0, 224.25, 'Completed', '2024-06-11'),
(21, 2, 200, 30, 0, 230, 'Completed', '2024-06-12'),
(22, 3, 205, 30.75, 0, 235.75, 'Pending', '2024-05-20'),
(23, 3, 210, 31.5, 0, 241.5, 'Pending', '2024-05-21'),
(24, 3, 215, 32.25, 0, 247.25, 'Pending', '2024-05-22'),
(25, 3, 220, 33, 0, 253, 'Pending', '2024-05-23'),
(26, 3, 225, 33.75, 0, 258.75, 'Pending', '2024-05-24'),
(27, 3, 230, 34.5, 0, 264.5, 'Pending', '2024-05-25'),
(28, 3, 235, 35.25, 0, 270.25, 'Pending', '2024-05-26'),
(29, 3, 240, 36, 0, 276, 'Pending', '2024-05-27'),
(30, 3, 245, 36.75, 0, 281.75, 'Pending', '2024-05-28'),
(31, 3, 250, 37.5, 0, 287.5, 'Pending', '2024-05-29'),
(32, 3, 255, 38.25, 0, 293.25, 'Ongoing', '2024-06-03'),
(33, 3, 260, 39, 0, 299, 'Ongoing', '2024-06-04'),
(34, 3, 265, 39.75, 0, 304.75, 'Ongoing', '2024-06-05'),
(35, 3, 270, 40.5, 0, 310.5, 'Ongoing', '2024-06-06'),
(36, 3, 275, 41.25, 0, 316.25, 'Ongoing', '2024-06-07'),
(37, 3, 280, 42, 0, 322, 'Completed', '2024-06-08'),
(38, 3, 285, 42.75, 0, 327.75, 'Completed', '2024-06-09'),
(39, 3, 290, 43.5, 0, 333.5, 'Completed', '2024-06-10'),
(40, 3, 295, 44.25, 0, 339.25, 'Completed', '2024-06-11'),
(21, 3, 300, 45, 0, 345, 'Completed', '2024-06-12')
;


INSERT INTO order_items (order_id, equipment_id, quantity, price, start_time, end_time) VALUES
(1, 1, 1, 100, '2024-06-13', '2024-06-15'),
(2, 3, 1, 120, '2024-06-13', '2024-06-16'),
(3, 5, 1, 130, '2024-06-13', '2024-06-17'),
(4, 7, 1, 140, '2024-06-13', '2024-06-18'),
(5, 9, 1, 150, '2024-06-13', '2024-06-19'),
(6, 11, 1, 160, '2024-06-13', '2024-06-20'),
(7, 13, 1, 170, '2024-06-13', '2024-06-21'),
(8, 15, 1, 180, '2024-06-13', '2024-06-22'),
(9, 17, 1, 190, '2024-06-13', '2024-06-23'),
(15, 19, 1, 200, '2024-06-13', '2024-06-24'),
(16, 21, 1, 210, '2024-06-10', '2024-06-13'),
(17, 23, 1, 220, '2024-06-09', '2024-06-13'),
(18, 25, 1, 230, '2024-06-08', '2024-06-13'),
(19, 27, 1, 240, '2024-06-07', '2024-06-13'),
(20, 29, 1, 250, '2024-06-06', '2024-06-13'),
(21, 31, 1, 260, '2024-06-05', '2024-06-13'),
(22, 33, 1, 270, '2024-06-04', '2024-06-13'),
(23, 35, 1, 280, '2024-06-03', '2024-06-13'),
(24, 37, 1, 290, '2024-06-02', '2024-06-13'),
(25, 39, 1, 300, '2024-06-01', '2024-06-13'),
(31, 41, 1, 105, '2024-05-20', '2024-05-27'),
(32, 42, 1, 110, '2024-05-21', '2024-05-28'),
(33, 43, 1, 115, '2024-05-22', '2024-05-29'),
(34, 44, 1, 120, '2024-05-23', '2024-05-30'),
(35, 45, 1, 125, '2024-05-24', '2024-05-31'),
(36, 46, 1, 130, '2024-05-25', '2024-06-01'),
(37, 47, 1, 135, '2024-05-26', '2024-06-02'),
(38, 48, 1, 140, '2024-05-27', '2024-06-03'),
(39, 49, 1, 145, '2024-05-28', '2024-06-04'),
(40, 50, 1, 150, '2024-05-29', '2024-06-05'),
(41, 51, 1, 155, '2024-06-03', '2024-06-10'),
(42, 52, 1, 160, '2024-06-04', '2024-06-11'),
(43, 53, 1, 165, '2024-06-05', '2024-06-12'),
(44, 54, 1, 170, '2024-06-06', '2024-06-13'),
(45, 55, 1, 175, '2024-06-07', '2024-06-14'),
(46, 56, 1, 180, '2024-06-08', '2024-06-15'),
(47, 57, 1, 185, '2024-06-09', '2024-06-16'),
(48, 58, 1, 190, '2024-06-10', '2024-06-17'),
(49, 59, 1, 195, '2024-06-11', '2024-06-18'),
(50, 60, 1, 200, '2024-06-12', '2024-06-19'),
(51, 61, 1, 105, '2024-05-20', '2024-05-27'),
(52, 62, 1, 110, '2024-05-21', '2024-05-28'),
(53, 63, 1, 115, '2024-05-22', '2024-05-29'),
(54, 64, 1, 120, '2024-05-23', '2024-05-30'),
(55, 65, 1, 125, '2024-05-24', '2024-05-31'),
(56, 66, 1, 130, '2024-05-25', '2024-06-01'),
(57, 67, 1, 135, '2024-05-26', '2024-06-02'),
(58, 68, 1, 140, '2024-05-27', '2024-06-03'),
(59, 69, 1, 145, '2024-05-28', '2024-06-04'),
(60, 70, 1, 150, '2024-05-29', '2024-06-05'),
(61, 71, 1, 155, '2024-06-03', '2024-06-10'),
(62, 72, 1, 160, '2024-06-04', '2024-06-11'),
(63, 73, 1, 165, '2024-06-05', '2024-06-12'),
(64, 74, 1, 170, '2024-06-06', '2024-06-13'),
(65, 75, 1, 175, '2024-06-07', '2024-06-14'),
(66, 76, 1, 180, '2024-06-08', '2024-06-15'),
(67, 77, 1, 185, '2024-06-09', '2024-06-16'),
(68, 78, 1, 190, '2024-06-10', '2024-06-17'),
(69, 79, 1, 195, '2024-06-11', '2024-06-18'),
(70, 80, 1, 200, '2024-06-12', '2024-06-19')
;


INSERT INTO payments (order_id, user_id, payment_type, payment_status, amount, payment_date) VALUES
(1, 22, 'Credit Card', 'Processed', 120.75, '2024-05-20'),
(2, 23, 'Credit Card', 'Processed', 126.5, '2024-05-21'),
(3, 24, 'Credit Card', 'Processed', 132.25, '2024-05-22'),
(4, 25, 'Credit Card', 'Processed', 138, '2024-05-23'),
(5, 26, 'Credit Card', 'Processed', 143.75, '2024-05-24'),
(6, 27, 'Credit Card', 'Processed', 149.5, '2024-05-25'),
(7, 28, 'Credit Card', 'Processed', 155.25, '2024-05-26'),
(8, 29, 'Credit Card', 'Processed', 161, '2024-05-27'),
(9, 30, 'Credit Card', 'Processed', 166.75, '2024-05-28'),
(10, 31, 'Credit Card', 'Processed', 172.5, '2024-05-29'),
(11, 32, 'Credit Card', 'Processed', 178.25, '2024-06-03'),
(12, 33, 'Credit Card', 'Processed', 184, '2024-06-04'),
(13, 34, 'Credit Card', 'Processed', 189.75, '2024-06-05'),
(14, 35, 'Credit Card', 'Processed', 195.5, '2024-06-06'),
(15, 36, 'Credit Card', 'Processed', 201.25, '2024-06-07'),
(16, 37, 'Credit Card', 'Processed', 207, '2024-06-08'),
(17, 38, 'Credit Card', 'Processed', 212.75, '2024-06-09'),
(18, 39, 'Credit Card', 'Processed', 218.5, '2024-06-10'),
(19, 40, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(20, 22, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(21, 23, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(22, 24, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(23, 25, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(24, 26, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(25, 27, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(26, 28, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(27, 29, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(28, 30, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(29, 31, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(30, 32, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(31, 33, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(32, 34, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(33, 35, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(34, 36, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(35, 37, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(36, 38, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(37, 39, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(38, 40, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(39, 21, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(40, 22, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(41, 23, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(42, 24, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(43, 25, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(44, 26, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(45, 27, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(46, 28, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(47, 29, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(48, 30, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(49, 31, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(50, 32, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(51, 33, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(52, 34, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(53, 35, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(54, 36, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(55, 37, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(56, 38, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(57, 39, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(58, 40, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(59, 21, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(60, 22, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(61, 23, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(62, 24, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(63, 25, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(64, 26, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(65, 27, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(66, 28, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(67, 29, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(68, 30, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(69, 31, 'Credit Card', 'Processed', 224.25, '2024-06-11'),
(70, 32, 'Credit Card', 'Processed', 224.25, '2024-06-11')
;



INSERT INTO discount (discount_id, days, discount_pricing) VALUES
(1, 0, 0),
(2, 30, 0.05),
(3, 180, 0.1),
(4, 360, 0.15);


INSERT INTO news (title, content, publish_date, creator_id, store_id) VALUES
('New Tractor Models Available', 'We are excited to announce the arrival of the latest tractor models. Visit our store to see them in action!', '2024-06-01', 1, 1),
('Store Renovation Completed', 'The renovation of our Lincoln store is now complete. Come and check out the new look and improved facilities!', '2024-06-02', 3, 1),
('New Spreader Technology', 'Discover the latest advancements in Spreader technology. Our Rolleston store has new models in stock.', '2024-06-03', 4, 2),
('Staff Training Program', 'We have initiated a comprehensive training program for all staff members to enhance service quality.', '2024-06-04', 5, NULL)
;
