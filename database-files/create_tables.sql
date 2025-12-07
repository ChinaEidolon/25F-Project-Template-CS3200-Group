-- part a: creation of the database
DROP DATABASE IF EXISTS gym_management;
CREATE DATABASE gym_management;
USE gym_management;


-- part b: creation of all tables
DROP TABLE IF EXISTS TRAINER;
CREATE TABLE TRAINER (
   trainer_id INT AUTO_INCREMENT PRIMARY KEY,
   first_name VARCHAR(50) NOT NULL,
   last_name VARCHAR(50) NOT NULL
);


DROP TABLE IF EXISTS NUTRITIONIST;
CREATE TABLE NUTRITIONIST (
   nutritionist_id INT AUTO_INCREMENT PRIMARY KEY,
   first_name VARCHAR(50) NOT NULL,
   last_name VARCHAR(50) NOT NULL
);


DROP TABLE IF EXISTS GYM_MEMBER;
CREATE TABLE GYM_MEMBER (
   member_id INT AUTO_INCREMENT PRIMARY KEY,
   first_name VARCHAR(50) NOT NULL,
   last_name VARCHAR(50) NOT NULL,
   trainer_id INT,
   nutritionist_id INT,
   status VARCHAR(20) DEFAULT 'active',
   FOREIGN KEY (trainer_id) REFERENCES TRAINER(trainer_id) ON DELETE SET NULL,
   FOREIGN KEY (nutritionist_id) REFERENCES NUTRITIONIST(nutritionist_id) ON DELETE SET NULL
);


DROP TABLE IF EXISTS MESSAGE;
CREATE TABLE MESSAGE (
   message_id INT AUTO_INCREMENT PRIMARY KEY,
   member_id INT NOT NULL,
   trainer_id INT,
   content TEXT NOT NULL,
   message_timestamp DATETIME NOT NULL,
   read_status VARCHAR(20) DEFAULT 'unread',
   FOREIGN KEY (member_id) REFERENCES GYM_MEMBER(member_id) ON DELETE CASCADE,
   FOREIGN KEY (trainer_id) REFERENCES TRAINER(trainer_id) ON DELETE SET NULL
);

DROP TABLE IF EXISTS PROGRESS;
CREATE TABLE PROGRESS (
   progress_id INT AUTO_INCREMENT PRIMARY KEY,
   member_id INT NOT NULL,
   date DATE NOT NULL,
   weight DECIMAL(5,2),
   body_fat_percentage DECIMAL(4,2),
   measurements VARCHAR(200),
   photos VARCHAR(500),
   FOREIGN KEY (member_id) REFERENCES GYM_MEMBER(member_id) ON DELETE CASCADE
);


DROP TABLE IF EXISTS FOOD_LOG;
CREATE TABLE FOOD_LOG (
   log_id INT AUTO_INCREMENT PRIMARY KEY,
   member_id INT NOT NULL,
   food VARCHAR(100) NOT NULL,
   timestamp DATETIME NOT NULL,
   portion_size VARCHAR(50),
   calories INT,
   proteins DECIMAL(6,2),
   carbs DECIMAL(6,2),
   fats DECIMAL(6,2),
   FOREIGN KEY (member_id) REFERENCES GYM_MEMBER(member_id) ON DELETE CASCADE
);


DROP TABLE IF EXISTS MEAL_PLAN;
CREATE TABLE MEAL_PLAN (
   plan_id INT AUTO_INCREMENT PRIMARY KEY,
   member_id INT NOT NULL,
   calorie_goals INT,
   macro_goals VARCHAR(200),
   date DATE NOT NULL,
   FOREIGN KEY (member_id) REFERENCES GYM_MEMBER(member_id) ON DELETE CASCADE
);


DROP TABLE IF EXISTS WORKOUT_PLAN;
CREATE TABLE WORKOUT_PLAN (
   plan_id INT AUTO_INCREMENT PRIMARY KEY,
   member_id INT NOT NULL,
   goals VARCHAR(500),
   date DATE NOT NULL,
   FOREIGN KEY (member_id) REFERENCES GYM_MEMBER(member_id) ON DELETE CASCADE
);


DROP TABLE IF EXISTS WORKOUT_LOG;
CREATE TABLE WORKOUT_LOG (
   log_id INT AUTO_INCREMENT PRIMARY KEY,
   member_id INT NOT NULL,
   trainer_id INT,
   date DATE NOT NULL,
   notes TEXT,
   sessions INT DEFAULT 1,
   FOREIGN KEY (member_id) REFERENCES GYM_MEMBER(member_id) ON DELETE CASCADE,
   FOREIGN KEY (trainer_id) REFERENCES TRAINER(trainer_id) ON DELETE SET NULL
);


DROP TABLE IF EXISTS EXERCISE;
CREATE TABLE EXERCISE (
   exercise_id INT AUTO_INCREMENT PRIMARY KEY,
   category VARCHAR(50) NOT NULL,
   sets INT,
   reps INT,
   weight DECIMAL(6,2)
);


DROP TABLE IF EXISTS PLAN_EXERCISE;
CREATE TABLE PLAN_EXERCISE (
   plan_exercise_id INT AUTO_INCREMENT PRIMARY KEY,
   plan_id INT NOT NULL,
   exercise_id INT NOT NULL,
   FOREIGN KEY (plan_id) REFERENCES WORKOUT_PLAN(plan_id) ON DELETE CASCADE,
   FOREIGN KEY (exercise_id) REFERENCES EXERCISE(exercise_id) ON DELETE CASCADE
);


DROP TABLE IF EXISTS LOG_EXERCISE;
CREATE TABLE LOG_EXERCISE (
   log_exercise_id INT AUTO_INCREMENT PRIMARY KEY,
   log_id INT NOT NULL,
   exercise_id INT NOT NULL,
   FOREIGN KEY (log_id) REFERENCES WORKOUT_LOG(log_id) ON DELETE CASCADE,
   FOREIGN KEY (exercise_id) REFERENCES EXERCISE(exercise_id) ON DELETE CASCADE
);


DROP TABLE IF EXISTS CLASS_SESSION;
CREATE TABLE CLASS_SESSION (
   session_id INT AUTO_INCREMENT PRIMARY KEY,
   trainer_id INT NOT NULL,
   class_name VARCHAR(100) NOT NULL,
   date DATETIME NOT NULL,
   cost DECIMAL(8,2),
   FOREIGN KEY (trainer_id) REFERENCES TRAINER(trainer_id) ON DELETE CASCADE
);


DROP TABLE IF EXISTS CLASS_ATTENDANCE;
CREATE TABLE CLASS_ATTENDANCE (
   attendance_id INT AUTO_INCREMENT PRIMARY KEY,
   session_id INT NOT NULL,
   member_id INT NOT NULL,
   status VARCHAR(20) DEFAULT 'registered',
   FOREIGN KEY (session_id) REFERENCES CLASS_SESSION(session_id) ON DELETE CASCADE,
   FOREIGN KEY (member_id) REFERENCES GYM_MEMBER(member_id) ON DELETE CASCADE
);


DROP TABLE IF EXISTS INVOICE;
CREATE TABLE INVOICE (
   invoice_id INT AUTO_INCREMENT PRIMARY KEY,
   member_id INT NOT NULL,
   trainer_id INT,
   amount DECIMAL(10,2) NOT NULL,
   date_issued DATE NOT NULL,
   status VARCHAR(20) DEFAULT 'pending',
   category VARCHAR(50),
   date DATE NOT NULL,
   FOREIGN KEY (member_id) REFERENCES GYM_MEMBER(member_id) ON DELETE CASCADE,
   FOREIGN KEY (trainer_id) REFERENCES TRAINER(trainer_id) ON DELETE SET NULL
);


DROP TABLE IF EXISTS PAYMENT;
CREATE TABLE PAYMENT (
   payment_id INT AUTO_INCREMENT PRIMARY KEY,
   invoice_id INT NOT NULL,
   paid_date DATE NOT NULL,
   card_details VARCHAR(100),
   bank_info VARCHAR(100),
   FOREIGN KEY (invoice_id) REFERENCES INVOICE(invoice_id) ON DELETE CASCADE
);


-- part c: creation of a small amount of sample data
INSERT INTO TRAINER (first_name, last_name) VALUES
('John', 'Smith'),
('Sarah', 'Johnson'),
('Mike', 'Williams');


INSERT INTO NUTRITIONIST (first_name, last_name) VALUES
('Emily', 'Brown'),
('David', 'Martinez'),
('Lisa', 'Anderson');


INSERT INTO GYM_MEMBER (first_name, last_name, trainer_id, nutritionist_id, status) VALUES
('Alex', 'Thompson', 1, 1, 'active'),
('Jessica', 'Davis', 2, 1, 'active'),
('Chris', 'Wilson', 1, 2, 'active');


INSERT INTO PROGRESS (member_id, date, weight, body_fat_percentage, measurements, photos) VALUES
(1, '2024-11-01', 180.50, 18.5, 'Chest: 42in, Waist: 34in, Arms: 15in', '/photos/alex_nov.jpg'),
(2, '2024-11-01', 145.00, 22.0, 'Chest: 36in, Waist: 28in, Hips: 38in', '/photos/jessica_nov.jpg'),
(3, '2024-11-01', 195.00, 20.5, 'Chest: 44in, Waist: 36in, Arms: 16in', '/photos/chris_nov.jpg');


INSERT INTO FOOD_LOG (member_id, food, timestamp, portion_size, calories, proteins, carbs, fats) VALUES
(1, 'Grilled Chicken Breast', '2024-11-20 12:30:00', '6 oz', 280, 53.0, 0.0, 6.2),
(1, 'Brown Rice', '2024-11-20 12:30:00', '1 cup', 216, 5.0, 45.0, 1.8),
(2, 'Greek Yogurt', '2024-11-20 08:00:00', '1 cup', 130, 20.0, 9.0, 0.7);


INSERT INTO MEAL_PLAN (member_id, calorie_goals, macro_goals, date) VALUES
(1, 2500, 'Protein: 180g, Carbs: 250g, Fats: 70g', '2024-11-01'),
(2, 1800, 'Protein: 120g, Carbs: 180g, Fats: 50g', '2024-11-01'),
(3, 2800, 'Protein: 200g, Carbs: 280g, Fats: 80g', '2024-11-01');


INSERT INTO WORKOUT_PLAN (member_id, goals, date) VALUES
(1, 'Build muscle mass, increase strength in compound lifts', '2024-11-01'),
(2, 'Tone muscles, improve cardiovascular endurance', '2024-11-01'),
(3, 'Powerlifting focused, increase 1RM on squat, bench, deadlift', '2024-11-01');


INSERT INTO EXERCISE (category, sets, reps, weight) VALUES
('Bench Press', 4, 8, 185.00),
('Squats', 4, 10, 225.00),
('Deadlift', 3, 6, 315.00),
('Pull-ups', 3, 12, 0.00),
('Running', 1, 1, 0.00);


INSERT INTO WORKOUT_LOG (member_id, trainer_id, date, notes, sessions) VALUES
(1, 1, '2024-11-20', 'Great session, hit new PR on bench press', 1),
(2, 2, '2024-11-20', 'Focused on form, cardio endurance improving', 1),
(3, 1, '2024-11-19', 'Heavy deadlift day, feeling strong', 1);


INSERT INTO PLAN_EXERCISE (plan_id, exercise_id) VALUES
(1, 1),
(1, 2),
(2, 4),
(3, 3);


INSERT INTO LOG_EXERCISE (log_id, exercise_id) VALUES
(1, 1),
(1, 2),
(2, 5),
(3, 3);


INSERT INTO CLASS_SESSION (trainer_id, class_name, date, cost) VALUES
(2, 'Yoga Flow', '2024-11-25 09:00:00', 25.00),
(1, 'HIIT Training', '2024-11-25 18:00:00', 30.00),
(3, 'Spin Class', '2024-11-26 07:00:00', 20.00);


INSERT INTO CLASS_ATTENDANCE (session_id, member_id, status) VALUES
(1, 2, 'registered'),
(2, 1, 'attended'),
(2, 3, 'registered');


INSERT INTO INVOICE (member_id, trainer_id, amount, date_issued, status, category, date) VALUES
(1, 1, 150.00, '2024-11-01', 'paid', 'Monthly Membership', '2024-11-01'),
(2, 2, 150.00, '2024-11-01', 'paid', 'Monthly Membership', '2024-11-01'),
(3, 1, 200.00, '2024-11-01', 'pending', 'Personal Training Package', '2024-11-01');


INSERT INTO PAYMENT (invoice_id, paid_date, card_details, bank_info) VALUES
(1, '2024-11-02', 'Visa ending in 1234', NULL),
(2, '2024-11-03', 'Mastercard ending in 5678', NULL);

