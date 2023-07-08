-- Create the Users table
CREATE TABLE Users (
  user_id SERIAL PRIMARY KEY,
  username VARCHAR(50) NOT NULL,
  password VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL,
  role VARCHAR(10) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login TIMESTAMP
);

-- Create the UserSessions table
CREATE TABLE UserSessions (
  session_id SERIAL PRIMARY KEY,
  user_id INT NOT NULL,
  session_token VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_accessed TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Add a random user
INSERT INTO Users (username, password, email, role)
VALUES ('joe', 'joe', 'john.doe@example.com', 'guest');

-- Add a user session
--INSERT INTO UserSessions (user_id, session_token)
--VALUES (1, 'abc123xyz');
