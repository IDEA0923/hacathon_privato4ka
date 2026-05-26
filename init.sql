CREATE TABLE IF NOT EXISTS users (
                                id SERIAL PRIMARY KEY, 
                                tg_id BIGINT ,
                                subjects VARCHAR(255),
                                class INT, 
                                region INT
                                );

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
                                )
CREATE TABLE IF NOT EXISTS registered_events (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL,
    tg_id BIGINT NOT NULL,
    event_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
);
