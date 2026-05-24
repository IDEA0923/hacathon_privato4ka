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
                                date_start TIMESTAMP DEFAULT NOW() + INTERVAL '3 days',
                                date_end TIMESTAMP DEFAULT NOW() + INTERVAL '4 days',
                                class_start INT DEFAULT 0, 
                                class_end INT DEFAULT 11, 
                                lvl VARCHAR(20),    #@level
                                frm VARCHAR(20),    #@from / source
                                lnk VARCHAR(40)
                                subjects VARCHAR(20),
                                description_1 VARCHAR(500)
                                )
