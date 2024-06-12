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

CREATE INDEX store_id
    ON orders (store_id);

CREATE INDEX user_id
    ON orders (user_id);


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

CREATE INDEX equipment_id
    ON order_items (equipment_id);

CREATE INDEX order_id
    ON order_items (order_id);


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


-- To be updated -- We will use data from 3-5 stores, each with 1 local manager, 5 staff members, 4 equipment categories with 10 equipments each, additionally with 20 customers, 1 admin and 1 national manager for presentation.

INSERT INTO user (username, email, password_hash, salt, role, date_of_birth) VALUES
-- Admin user
("superadmin", "rose123@agrihire-solutions.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "admin", "1977-12-12"),
-- National Manager
("manager666", "peter123@agrihire-solutions.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "national_manager", "1980-10-10"),
-- Customer user
("farmer007", "tim123@gmail.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "customer", "1975-02-02"),
-- Store 1 users
("lincoln000", "john123@agrihire-solutions.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "local_manager", "1985-05-05"),
("lincoln001", "jack123@agrihire-solutions.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "staff", "1990-01-01"),
("lincoln002", "mia123@agrihire-solutions.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "staff", "1998-06-06"),
-- Store 2 users
("rolleston000", "james123@agrihire-solutions.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "local_manager", "1980-09-09"),
("rolleston001", "daniel123@agrihire-solutions.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "staff", "1993-07-07"),
("rolleston002", "eva123@agrihire-solutions.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "staff", "1999-08-08"),
-- Store 3 users
("ashburton000", "steven123@agrihire-solutions.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "local_manager", "1983-07-20"),
("ashburton001", "henry123@agrihire-solutions.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "staff", "2000-10-10"),
("ashburton002", "emily123@agrihire-solutions.com", "a5a65903076850e9555dd57a46232f4cafa42b92b2b75cd987d601ef3396e609", "e7289be420cba78b9e9338db0c49d98140af341bf524291a205b63253ff5d8ff", "staff", "1997-11-11")
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
(4, 1, "Mr", "John", "Doe", "0255512345"),
(7, 2, "Mr", "James", "Smith", "0226785555"),
(10, 3, "Mr", "Steven", "Johnson", "02368524587")
;

-- Insert data into the staff table
INSERT INTO staff (user_id, store_id, title, first_name, family_name, phone_number) VALUES
(5, 1, "Mr", "Jack", "Jones", "0240012345"),
(6, 1, "Miss", "Mia", "Roberts", "0265754258"),
(8, 2, "Mr", "Daniel", "Harrison", "0262542542"),
(9, 2, "Miss", "Eva", "Parker", "0236542582"),
(11, 3, "Mr", "Henry", "Reed", "0232574580"),
(12, 3, "Miss", "Emily", "Brooks", "0232251545")
;

-- Insert data into the customer table
INSERT INTO customer (user_id, title, first_name, family_name, phone_number, address) VALUES
(3, "Mr", "Tim", "Doe", "0254525411", "11 milkfarm street, greengrass, Canterbury")
;


INSERT INTO equipment (equipment_id, name, description, category, purchase_date, cost, serial_number, status, store_id, maximum_date, minimum_date, Image) VALUES
(1, "Deutz Fahr", "This 2019 Deutz Fahr 6185 RC shift professional series tractor has only done 2,670 hours and is in great condition and ready to go to work . 50kph front suspension, front linkage and pto, this tractor is a serious contracting machine and with the loader would add incredible versitility to any fleet.", "Tractor", "2015-01-01", 369, "5242875401", "Available", 1, "360", "1", "tractor1.jpg"),
(3, "Amazone", "Amazone UX5201 Super with 30 mtr boom , as new , 5200ltr tank with 580ltr fresh water , twin pumps 520ltrs/min , axle suspension , 9 sections with auto shut off , ISOBUS with Amazone joystick , DUS- Boom recirculation , comfort package , boom auto height control , LED lighting package.", "Sprayer", "2015-01-01", 289, "5242875403", "Available", 1, "360", "1", "sprayer1.jpg"),
(4, "McHale/Fusion", "A2020 model. 22,000 bales. 1,000 speed gear box. 6 bar camless pickup. 650 tyres.", "Bale Wrapper", "2015-01-01", 159, "5242875404", "Available", 1, "360", "1", "wrapper1.jpg"),
(5, "AManure Spreader", "*6 tonne super capacity
*4 tonne Urea capacity
*Wide belt to handle organic matter (poultry waste, etc) with ease
*E spreader in cab rate control
*Electronic door actuator", "Spreader", "2015-01-01", 359, "5242875405", "Available", 1, "360", "1", "spreader1.jpg"),
(6, "DX140LCR", "Subtype: Tracked-Excav
Make: Doosan
Model: DX140LCR", "Tracked-Excav", "2015-01-01", 169, "5242875406", "Available", 1, "360", "1", "excav1.jpg"),
(7, "JS130", "13.7 tonne operating weight, Long carriage - providing excellent breakout force, 600mm steel tracks, Large air conditioned cabin, Heated seat with air suspension, Hydraulic hitch, High flow hydraulics, 900mm general purpose bucket, Heavy duty X undercarriage, JCB 74kw Tier 3 diesel engine", "Tracked-Excav", "2015-01-01", 189, "5242875407", "Available", 1, "360", "1", "good1.png"),
(8, "CASE IH/Maxxum 125", "This Case Maxxum 125 Multi Controller Tractor has a Case LR2100 Self Levelling Loader and Bucket, 125HP Boost to 155HP, Active Drive 8 Speed Power Shift Transmission, Electronic Remotes, Integrated Loader Joystick Control,", "Tractor", "2015-01-01", 255, "5242875408", "Available", 1, "360", "1", "good2.png"),
(9, "Taege/4.8m Triple Box Air Seeder", "Taege 4.8m Air Seeder - triple box drill, 2 x 850L hoppers & 1 x 200L hopper, all three hoppers are electrically driven, all three are very easy to calibrate, Monitor shows fan speed and seeding rate of all hoppers, 4.8m working width and folds to 3.1m for road transport, covering harrows, 121mm tine spacing. Tilth grows seed.", "Seed Drills", "2015-01-01", 200, "5242875409", "Available", 1, "360", "1", "good3.png"),
(10, "Merlo/P72.10", "With a max of 10 metre reach and 7.2 ton lift it is well suited to construction. The frame levelling and side shift make it ideal for accurate placement of goods on an uneven site and the single joystick makes it easy to control.", "Telescopic Handler", "2015-01-01", 260, "5242875410", "Available", 1, "360", "1", "good4.png"),
(11, "Fendt/Rotana 160V", "SOBUS, Also has monitor, bale size 0.9m to 1.60m, workshop checked, finance package available, happy to on farm.", "Round Baler", "2015-01-01", 289, "5242875411", "Available", 1, "360", "1", "good5.png"),
(12, "PIUMA", "Only 1400mm wide, 4 Wheel Steering so great turning circle for tight headlands
Cruise Control for steering, 4 Conveyor belts, holds two bins while filling one
Gentle delivery from conveyor to bin, very quiet and economical 25 HP Diesel engine
Four Adjustable Height Platforms while two harvest in front at ground level.", "Horticulture Harvester", "2015-01-01", 200, "5242875412", "Available", 1, "360", "1", "good6.png"),
(13, "Uni drill", "24 row, 3 metre trailing disc drill.
NZs most cost effective disc direct drill.
Ideal for over sowing, into stubble or cultivated ground.
Fewer moving parts; low ongoing repair and maintenance.
Narrow row spacing but staggered design allows good trash clearance.
Long life Tungsten carbide tipped coulters
Mounted on rubber Duratorque suspension for easy maintenance
Self clean design Guttler roller.
700L capacity hopper for high speed drilling, quick and easy calibration, convenient emptying, and individual row accuracy, with the ability to sow to the last quantity of seed, with all seed types.", "Disc Seeder", "2015-01-01", 180, "5242875413", "Available", 1, "360", "1", "good7.png"),
(14, "Antonio Carraro", "Gearing 16F x 16R
98 hp Kubota engine
R series steering isodiametric tractor
With reversible driving position
Powerful and streamlined
Extremely versatile and ideally suited to a wide range of applications.", "Tractor", "2015-01-01", 300, "5242875414", "Available", 1, "360", "1", "good8.png"),
(15, "Taege/300AS121D", "Brand New Taege 3.1m air seeder, 25 run 121mm row spacing, plastic seed & fert hoppers, both 850L so easy half ton of seed & fert, Taege electric drive, oil cooler for hydraulic fan, Wide tyres, safety rail, small seed inserts, covering harrows, roll top hopper covers, very smart and easy to use. We can add a third hopper for another $13000 + gst which is 200L and set up to broadcast small seeds or slug bait.", "Seed Drills", "2015-01-01", 289, "5242875415", "Available", 1, "340", "1", "good9.png"),
(16, "Moore/Unidrill", "The most straight forward, easy to use, and functional pasture based drill on the market
* Single discs
*90mm row spacing
*Rear guttler roller - very effective in pugged conditions and consolidating cultivated soil
*Accord metering system and pneumatic hopper is easy to set up and can handle any seed type", "Seed Drills", "2015-01-01", 270, "5242875416", "Available", 2, "360", "1", "good10.png"),
(17, "Maschio Jumbo 8.0mtr", "Maschio Jumbo 8.0mtr Power Harrow , Farmer owned , very tidy , as new Quickfit Tungsten tines , hydraulic depth control of tooth packer roller and leveling board , contour control , awesome efficient cultivation tool", "Power Harrows", "2015-01-01", 290, "5242875417", "Available", 2, "360", "1", "good11.png"),
(18, "Kverneland/95130C/Rakes", "The Kverneland 94125 C and 95130 C are targeted at making lighter work of tough and demanding operations. With an impressive capacity of 12.50m working width, straightforward design and the possibility to adjust both work and swath width, they are designed to boost the complete process of collection and pick-up, altering to the changing crop intensity during the season. The Kverneland 12.5m 4-rotor rake is offered with a choice of either ProLine or CompactLine gearbox. Both machines are similar in construction.", "Tedder", "2015-01-01", 260, "5242875418", "Available", 2, "360", "1", "good12.png"),
(19, "McHale/V660", "Single belt
Rotor feed with 15 knives
2m pick up
bale size upto 1.68m", "Round Baler", "2015-01-01", 340, "5242875419", "Available", 3, "360", "1", "good13.png"),
(20, "Combi RX148 Multi-feeder", "Hustler Chainless Rear Floor Combi RX148 Multi-feeder with Brakes. 14.2 cube (17 cube heaped). Can handle all bale types and shapes and has awesome stability in rolling country. Can add other spec including scales", "Feedout", "2015-01-01", 310, "5242875420", "Available", 3, "360", "1", "good14.png"),
(21, "300EDBT121SS", "TAEGE 300EDBT 121 3M DRILL, twin box, Stainless steel fert box, 121mm tine spacing, electronic rate control, small seed inserts, Broadcasting system, covering harrows, safety chain, LED tratier lights,Hazard panels, 2.8m drilling width", "Seed Drills", "2015-01-01", 289, "5242875421", "Available", 3, "360", "1", "good15.png")
;

-- login password: A12345678

INSERT INTO discount (discount_id, days, discount_pricing) VALUES
(1, 0, 0),
(2, 30, 0.05),
(3, 180, 0.1),
(4, 360, 0.15);



