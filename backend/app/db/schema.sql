CREATE TABLE IF NOT EXISTS app_users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'ANALYST',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS revoked_tokens (
    jti VARCHAR(36) NOT NULL PRIMARY KEY,
    expires_at DATETIME NOT NULL,
    INDEX idx_revoked_tokens_expires_at (expires_at)
);