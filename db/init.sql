-- データベース作成
CREATE DATABASE IF NOT EXISTS app_dev;

-- ユーザー作成（認証方式を明示）
CREATE USER IF NOT EXISTS 'devuser'@'%' IDENTIFIED WITH mysql_native_password BY 'devpass';
GRANT ALL PRIVILEGES ON app_dev.* TO 'devuser'@'%';
FLUSH PRIVILEGES;

-- DBを選択
USE app_dev;

-- items テーブル作成（カンマミス修正済）
CREATE TABLE IF NOT EXISTS items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  event_id VARCHAR(100),
  box_no INT NOT NULL,
  box_id INT NOT NULL,
  material VARCHAR(255),
  misc VARCHAR(255),
  weight VARCHAR(255),
  jewelry_price INT,
  material_price INT,
  total_weight DECIMAL(10,3),
  gemstone_weight DECIMAL(10,3),
  material_weight DECIMAL(10,3),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- テストデータ挿入（カラム修正済）
INSERT INTO items (box_id, box_no, weight, jewelry_price) VALUES
  (1, 1, '12.3', 150000),
  (1, 2, '45.0', 300000);