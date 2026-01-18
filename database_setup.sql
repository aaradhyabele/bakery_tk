-- Database Setup for SWEETS 'N JOY Bakery Management System

CREATE DATABASE IF NOT EXISTS bakery1;
USE bakery1;

-- Table: inventory12
CREATE TABLE IF NOT EXISTS inventory12 (
    item VARCHAR(100),
    flavour VARCHAR(100),
    price DOUBLE,
    stock INT,
    PRIMARY KEY (item, flavour)
);

-- Table: employee
CREATE TABLE IF NOT EXISTS employee (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    pass VARCHAR(100)
);

-- Table: td_sale1 (Unified Sales Record)
CREATE TABLE IF NOT EXISTS td_sale1 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item VARCHAR(100),
    flavour VARCHAR(100),
    price DOUBLE, -- This stored the total in original code logic snippets
    stock INT,    -- This stored the quantity in original code logic snippets
    date_ DATE
);

-- Table: bill (Recent Transaction Cache)
CREATE TABLE IF NOT EXISTS bill (
    sr INT AUTO_INCREMENT PRIMARY KEY,
    item VARCHAR(100),
    flavour VARCHAR(100),
    quantity INT,
    total DOUBLE
);

-- Table: feedback
CREATE TABLE IF NOT EXISTS feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    text TEXT,
    date_ DATE
);

-- Initial Data (Optional Sample Data)
INSERT INTO employee (id, name, pass) VALUES (101, 'Admin', 'Aaradhya4252');

-- Stored Procedure: top_item1 (Most sold item)
DELIMITER //
CREATE PROCEDURE top_item1(OUT name_out VARCHAR(100), OUT qty_out INT)
BEGIN
    SELECT item, SUM(stock) INTO name_out, qty_out 
    FROM td_sale1 
    GROUP BY item 
    ORDER BY qty_out DESC 
    LIMIT 1;
END //
DELIMITER ;

-- Stored Procedure: top_item4 (Most sold flavour)
DELIMITER //
CREATE PROCEDURE top_item4(OUT name_out VARCHAR(100), OUT qty_out INT)
BEGIN
    SELECT flavour, SUM(stock) INTO name_out, qty_out 
    FROM td_sale1 
    GROUP BY flavour 
    ORDER BY qty_out DESC 
    LIMIT 1;
END //
DELIMITER ;
