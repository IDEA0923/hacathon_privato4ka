CREATE TABLE IF NOT EXISTS users (
                                id SERIAL PRIMARY KEY, 
                                tg_id BIGINT ,
                                subjects VARCHAR(255),
                                class INT, 
                                region INT
                                );

CREATE INDEX IF NOT EXISTS idx_users_tg_id ON users(tg_id);

CREATE TABLE IF NOT EXISTS  events(
                                id SERIAL PRIMARY KEY,
                                name_1 VARCHAR(100),
                                date_start TIMESTAMP DEFAULT NOW() + INTERVAL '3 days',
                                date_end TIMESTAMP DEFAULT NOW() + INTERVAL '4 days',
                                class_start INT DEFAULT 0, 
                                class_end INT DEFAULT 11, 
                                lvl VARCHAR(100),
                                frm VARCHAR(100),
                                lnk VARCHAR(100),
                                subjects VARCHAR(255),
                                description_1 VARCHAR(500),
                                region INT
                                );

CREATE INDEX IF NOT EXISTS idx_events_region ON events(region);
CREATE INDEX IF NOT EXISTS idx_events_class ON events(class_start, class_end);
CREATE INDEX IF NOT EXISTS idx_events_date ON events(date_start);
