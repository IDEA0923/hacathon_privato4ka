CREATE TABLE IF NOT EXISTS users (
                                id SERIAL PRIMARY KEY, 
                                tg_id BIGINT ,
                                subjects VARCHAR(20),
                                class INT, 
                                region VARCHAR(3)
                                );

CREATE TABLE IF NOT EXISTS  events(
                                id SERIAL PRIMARY KEY,
                                name_1 VARCHAR(20),
                                date_of_event TIMESTAMP DEFAULT NOW() + INTERVAL '3 days',
                                subjects VARCHAR(20),
                                description_1 VARCHAR(500)
                                )
