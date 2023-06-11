
--  Creating Database
CREATE DATABASE newsx_local CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- Creating User
CREATE USER 'newsxUser'@'localhost' IDENTIFIED BY 'upcoming_unicorn';
GRANT ALL PRIVILEGES ON *.* TO 'newsxUser'@'localhost';
FLUSH PRIVILEGES;



-- DO NOT RUN
-- Creating Table (DO NOT RUN - Not required to run just for Schema editing) (All tentative - Actual table names and structures are different)
-- USE newsx_local;

-- CREATE TABLE raw_news (
--     id VARCHAR(1024) NOT NULL PRIMARY KEY,
--     article MEDIUMTEXT NOT NULL,
--     title TEXT(65535),
--     date date,
--     time time,
--     source_url TEXT(65535),
--     source VARCHAR(1024),
--     original_source VARCHAR(1024),
--     image_url TEXT(65535),
--     author VARCHAR(1024),
--     category VARCHAR(1024),
-- );

-- CREATE TABLE translated_news (
--     id VARCHAR(1024) NOT NULL PRIMARY KEY,
--     summarized_article MEDIUMTEXT NOT NULL,
--     bengali_article MEDIUMTEXT,
--     hindi_article MEDIUMTEXT,
--     hindi_article MEDIUMTEXT,
--     tamil_article MEDIUMTEXT,
--     telugu_article MEDIUMTEXT,
--     kannada_article MEDIUMTEXT,
--     gujarati_article MEDIUMTEXT
-- )