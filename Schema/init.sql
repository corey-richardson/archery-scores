DROP TABLE IF EXISTS "Archer";
CREATE TABLE IF NOT EXISTS "Archer" (
    "archer_id" INTEGER PRIMARY KEY,
    "first_name" TEXT NOT NULL,
    "last_name" TEXT NOT NULL,
    "username" TEXT NOT NULL UNIQUE,
    "password" TEXT NOT NULL,
    "birth_date" TEXT NOT NULL,
    "default_category" INT NOT NULL REFERENCES "Categories.category_id",
    "default_bowstyle" INT NOT NULL REFERENCES "Bowstyles.bowstyle_id"
);

DROP TABLE IF EXISTS "ArcherAwards";
CREATE TABLE IF NOT EXISTS "ArcherAwards" (
    "archer_id" INTEGER PRIMARY KEY REFERENCES "Archer.archer_id",
    "handicap" INTEGER,
    "classification" INTEGER REFERENCES "Classifications.classification_id",
    "classification_badge" INTEGER REFERENCES "Classifications.classification_id",
    "portsmouth_badge" INTEGER,
    "worcester_badge" INTEGER,
    "frostbite_badge" INTEGER, 

    CHECK ("handicap" BETWEEN -1 AND 150)
);


DROP TABLE IF EXISTS "EventType";
CREATE TABLE IF NOT EXISTS "EventType" (
    "event_type_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "event_type_name" TEXT NOT NULL
);


DROP TABLE IF EXISTS "Bowstyles";
CREATE TABLE IF NOT EXISTS "Bowstyles" (
    "bowstyle_id" INTEGER PRIMARY KEY,
    "bowstyle_name" TEXT NOT NULL UNIQUE
);


DROP TABLE IF EXISTS "Categories";
CREATE TABLE IF NOT EXISTS "Categories" (
    "category_id" INTEGER PRIMARY KEY,
    "category_name" TEXT NOT NULL UNIQUE
);


DROP TABLE IF EXISTS "Classifications";
CREATE TABLE IF NOT EXISTS "Classifications" (
    "classification_id" INTEGER PRIMARY KEY,
    "classification_string" TEXT NOT NULL UNIQUE
);


DROP TABLE IF EXISTS "Record";
CREATE TABLE IF NOT EXISTS "Record" (
    "record_id" INTEGER PRIMARY KEY,
    "archer_id" INTEGER REFERENCES "Archer.archer_id",
    "round_name" TEXT NOT NULL,
    "date_shot" TEXT NOT NULL,
    "event_name" TEXT,
    "event_type" REFERENCES "EventType.event_type_id",
    "round_handicap" INTEGER DEFAULT -1,
    "round_classification" INTEGER REFERENCES "Classifications.classification_id",
    "notes" TEXT,
    CHECK ("round_handicap" BETWEEN -1 AND 150)
);


DROP TABLE IF EXISTS "RecordDetails";
CREATE TABLE IF NOT EXISTS "RecordDetails" (
    "record_id" PRIMARY KEY REFERENCES "Record.record_id",
    "dozens" REAL NOT NULL,
    "cumulative_dozens" REAL,
    "score" INTEGER NOT NULL,
    "xs" INTEGER DEFAULT 0,
    "tens" INTEGER DEFAULT 0,
    "golds" INTEGER DEFAULT 0,
    "hits" INTEGER DEFAULT 0
);

-- SEED

INSERT INTO "EventType" ("event_type_name")
VALUES 
    ('Club Practice Session'), 
    ('Club Target Day'), 
    ('Club Competition'),
    ('Open Competition'),
    ('Open Competition UKRS'),
    ('Open Competition WRS');


INSERT INTO "Bowstyles" ("bowstyle_name")
VALUES 
    ('Barebow'), 
    ('Compound'), 
    ('Longbow'),
    ('Recurve');


INSERT INTO "Categories" ("category_name")
VALUES 
    ('Male'), 
    ('Male U21'), 
    ('Female'),
    ('Female U21');


INSERT INTO "Classifications" ("classification_string")
VALUES
    ('Indoor Archer 3rd Class'),
    ('Indoor Archer 2nd Class'),
    ('Indoor Archer 1st Class'),
    ('Indoor Bowman 3rd Class'),
    ('Indoor Bowman 2nd Class'),
    ('Indoor Bowman 1st Class'),
    ('Indoor Master Bowman'),
    ('Indoor Grand Master Bowman');
    -- OUTDOOR CLASSIFICATIONS
