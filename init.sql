CREATE TABLE IF NOT EXISTS users (
                                id SERIAL PRIMARY KEY, 
                                tg_id BIGINT ,
                                subjects VARCHAR(20),
                                class INT, 
                                region INT
                                );

CREATE TABLE IF NOT EXISTS  events(
                                id SERIAL PRIMARY KEY,
                                name_1 VARCHAR(20),
                                date_start TIMESTAMP DEFAULT NOW() + INTERVAL '3 days',
                                date_end TIMESTAMP DEFAULT NOW() + INTERVAL '4 days',
                                class_start INT DEFAULT 0, 
                                class_end INT DEFAULT 11, 
                                lvl VARCHAR(20),
                                frm VARCHAR(20),
                                lnk VARCHAR(40),
                                subjects VARCHAR(20),
                                description_1 VARCHAR(500),
                                region INT
                                )
