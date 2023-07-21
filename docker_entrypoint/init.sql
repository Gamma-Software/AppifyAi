-- Create the Users table
CREATE TABLE Users (
  user_id SERIAL PRIMARY KEY,
  username VARCHAR(50) NOT NULL,
  password BYTEA NOT NULL,
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

-- Create the UserData table
CREATE TABLE UserData (
  user_id INT NOT NULL,
  source_code TEXT,
  message_history JSONB,
  tries INT NOT NULL DEFAULT 0,
  openai_key TEXT,
  FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Add the first user
INSERT INTO Users (username, password, email, role) VALUES ('admin', 'admin', 'admin@localhost.com', 'guest');