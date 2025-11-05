PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Class (
    "index" VARCHAR(100) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    hit_die INT NOT NULL,
    spellcasting_level INT,
    spellcasting_ability_index VARCHAR(10),
    FOREIGN KEY (spellcasting_ability_index) REFERENCES AbilityScore("index")
);

CREATE TABLE IF NOT EXISTS Spell (
    "index" VARCHAR(100) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    higher_level_desc TEXT,
    range VARCHAR(100),
    components VARCHAR(20),
    material TEXT,
    ritual BOOLEAN NOT NULL,
    duration VARCHAR(100),
    concentration BOOLEAN NOT NULL,
    casting_time VARCHAR(100),
    level INT NOT NULL,
    attack_type VARCHAR(50),
    damage_type_index VARCHAR(50),
    dc_type_index VARCHAR(10),
    dc_success VARCHAR(50),
    area_of_effect_type VARCHAR(50),
    area_of_effect_size INT,
    school_index VARCHAR(50) NOT NULL,
    FOREIGN KEY (damage_type_index) REFERENCES DamageType("index"),
    FOREIGN KEY (dc_type_index) REFERENCES AbilityScore("index"),
    FOREIGN KEY (school_index) REFERENCES MagicSchool("index")
);

CREATE TABLE IF NOT EXISTS Equipment (
    "index" VARCHAR(100) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    equipment_category_index VARCHAR(100) NOT NULL,
    cost_quantity DECIMAL(10, 2),
    cost_unit VARCHAR(10),
    weight FLOAT,
    description TEXT,
    weapon_category VARCHAR(50),
    weapon_range VARCHAR(50),
    category_range VARCHAR(50),
    damage_dice VARCHAR(20),
    damage_type_index VARCHAR(50),
    range_normal INT,
    range_long INT,
    throw_range_normal INT,
    throw_range_long INT,
    two_handed_damage_dice VARCHAR(20),
    two_handed_damage_type_index VARCHAR(50),
    armor_category VARCHAR(50),
    armor_class_base INT,
    armor_class_dex_bonus BOOLEAN,
    armor_class_max_bonus INT,
    str_minimum INT,
    stealth_disadvantage BOOLEAN,
    gear_category_index VARCHAR(100),
    tool_category VARCHAR(100),
    vehicle_category VARCHAR(100),
    speed_quantity FLOAT,
    speed_unit VARCHAR(50),
    capacity VARCHAR(100),
    FOREIGN KEY (equipment_category_index) REFERENCES EquipmentCategory("index"),
    FOREIGN KEY (damage_type_index) REFERENCES DamageType("index"),
    FOREIGN KEY (two_handed_damage_type_index) REFERENCES DamageType("index"),
    FOREIGN KEY (gear_category_index) REFERENCES EquipmentCategory("index")
);

CREATE TABLE IF NOT EXISTS AbilityScore (
    "index" VARCHAR(10) PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    full_name VARCHAR(50),
    description TEXT
);

CREATE TABLE IF NOT EXISTS DamageType (
    "index" VARCHAR(50) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS MagicSchool (
    "index" VARCHAR(50) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS EquipmentCategory (
    "index" VARCHAR(100) PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS WeaponProperty (
    "index" VARCHAR(50) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS Proficiency (
    "index" VARCHAR(100) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS Subclass (
    "index" VARCHAR(100) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    class_index VARCHAR(100) NOT NULL,
    desc TEXT,
    subclass_flavor TEXT,
    FOREIGN KEY (class_index) REFERENCES Class("index")
);

CREATE TABLE IF NOT EXISTS ClassProficiency (
    class_index VARCHAR(100),
    proficiency_index VARCHAR(100),
    PRIMARY KEY (class_index, proficiency_index),
    FOREIGN KEY (class_index) REFERENCES Class("index"),
    FOREIGN KEY (proficiency_index) REFERENCES Proficiency("index")
);

CREATE TABLE IF NOT EXISTS ClassProficiencyChoice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_index VARCHAR(100) NOT NULL,
    description TEXT,
    choose INT NOT NULL,
    type VARCHAR(50) NOT NULL,
    FOREIGN KEY (class_index) REFERENCES Class("index")
);

CREATE TABLE IF NOT EXISTS ClassProficiencyChoiceOption (
    choice_id INT,
    proficiency_index VARCHAR(100),
    PRIMARY KEY (choice_id, proficiency_index),
    FOREIGN KEY (choice_id) REFERENCES ClassProficiencyChoice(id),
    FOREIGN KEY (proficiency_index) REFERENCES Proficiency("index")
);

CREATE TABLE IF NOT EXISTS SpellClass (
    spell_index VARCHAR(100),
    class_index VARCHAR(100),
    PRIMARY KEY (spell_index, class_index),
    FOREIGN KEY (spell_index) REFERENCES Spell("index"),
    FOREIGN KEY (class_index) REFERENCES Class("index")
);

CREATE TABLE IF NOT EXISTS SpellSubclass (
    spell_index VARCHAR(100),
    subclass_index VARCHAR(100),
    PRIMARY KEY (spell_index, subclass_index),
    FOREIGN KEY (spell_index) REFERENCES Spell("index"),
    FOREIGN KEY (subclass_index) REFERENCES Subclass("index")
);

CREATE TABLE IF NOT EXISTS EquipmentProperty (
    equipment_index VARCHAR(100),
    property_index VARCHAR(50),
    PRIMARY KEY (equipment_index, property_index),
    FOREIGN KEY (equipment_index) REFERENCES Equipment("index"),
    FOREIGN KEY (property_index) REFERENCES WeaponProperty("index")
);

CREATE TABLE IF NOT EXISTS EquipmentContent (
    pack_equipment_index VARCHAR(100),
    content_equipment_index VARCHAR(100),
    quantity INT NOT NULL,
    PRIMARY KEY (pack_equipment_index, content_equipment_index),
    FOREIGN KEY (pack_equipment_index) REFERENCES Equipment("index"),
    FOREIGN KEY (content_equipment_index) REFERENCES Equipment("index")
);

CREATE TABLE IF NOT EXISTS ClassLevel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_index VARCHAR(100) NOT NULL,
    level INT NOT NULL,
    prof_bonus INT,
    ability_score_bonuses INT,
    class_specific_json TEXT,
    FOREIGN KEY (class_index) REFERENCES Class("index")
);

CREATE TABLE IF NOT EXISTS ClassLevel_Spellcasting (
    class_level_id INTEGER PRIMARY KEY,
    cantrips_known INT,
    spells_known INT,
    spell_slots_level_1 INT,
    spell_slots_level_2 INT,
    spell_slots_level_3 INT,
    spell_slots_level_4 INT,
    spell_slots_level_5 INT,
    spell_slots_level_6 INT,
    spell_slots_level_7 INT,
    spell_slots_level_8 INT,
    spell_slots_level_9 INT,
    FOREIGN KEY (class_level_id) REFERENCES ClassLevel(id)
);

CREATE TABLE IF NOT EXISTS SubclassLevel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subclass_index VARCHAR(100) NOT NULL,
    level INT NOT NULL,
    subclass_specific_json TEXT,
    FOREIGN KEY (subclass_index) REFERENCES Subclass("index")
);

CREATE TABLE IF NOT EXISTS Feature (
    "index" VARCHAR(100) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS ClassLevel_Feature (
    class_level_id INT,
    feature_index VARCHAR(100),
    PRIMARY KEY (class_level_id, feature_index),
    FOREIGN KEY (class_level_id) REFERENCES ClassLevel(id),
    FOREIGN KEY (feature_index) REFERENCES Feature("index")
);

CREATE TABLE IF NOT EXISTS SubclassLevel_Feature (
    subclass_level_id INT,
    feature_index VARCHAR(100),
    PRIMARY KEY (subclass_level_id, feature_index),
    FOREIGN KEY (subclass_level_id) REFERENCES SubclassLevel(id),
    FOREIGN KEY (feature_index) REFERENCES Feature("index")
);

CREATE TABLE IF NOT EXISTS Feat (
    "index" VARCHAR(100) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    prerequisites_json TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS Language (
    "index" VARCHAR(100) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS Race (
    "index" VARCHAR(100) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    speed INT,
    alignment TEXT,
    age TEXT,
    size VARCHAR(50),
    size_description TEXT,
    language_desc TEXT
);

CREATE TABLE IF NOT EXISTS RaceAbilityBonus (
    race_index VARCHAR(100),
    ability_score_index VARCHAR(10),
    bonus INT NOT NULL,
    PRIMARY KEY (race_index, ability_score_index),
    FOREIGN KEY (race_index) REFERENCES Race("index"),
    FOREIGN KEY (ability_score_index) REFERENCES AbilityScore("index")
);

CREATE TABLE IF NOT EXISTS RaceProficiency (
    race_index VARCHAR(100),
    proficiency_index VARCHAR(100),
    PRIMARY KEY (race_index, proficiency_index),
    FOREIGN KEY (race_index) REFERENCES Race("index"),
    FOREIGN KEY (proficiency_index) REFERENCES Proficiency("index")
);

CREATE TABLE IF NOT EXISTS RaceLanguage (
    race_index VARCHAR(100),
    language_index VARCHAR(100),
    PRIMARY KEY (race_index, language_index),
    FOREIGN KEY (race_index) REFERENCES Race("index"),
    FOREIGN KEY (language_index) REFERENCES Language("index")
);

CREATE TABLE IF NOT EXISTS RaceFeature (
    race_index VARCHAR(100),
    feature_index VARCHAR(100),
    PRIMARY KEY (race_index, feature_index),
    FOREIGN KEY (race_index) REFERENCES Race("index"),
    FOREIGN KEY (feature_index) REFERENCES Feature("index")
);

CREATE TABLE IF NOT EXISTS RaceProficiencyChoice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    race_index VARCHAR(100) NOT NULL,
    description TEXT,
    choose INT NOT NULL,
    type VARCHAR(50) NOT NULL,
    FOREIGN KEY (race_index) REFERENCES Race("index")
);

CREATE TABLE IF NOT EXISTS RaceProficiencyChoiceOption (
    choice_id INT,
    proficiency_index VARCHAR(100),
    PRIMARY KEY (choice_id, proficiency_index),
    FOREIGN KEY (choice_id) REFERENCES RaceProficiencyChoice(id),
    FOREIGN KEY (proficiency_index) REFERENCES Proficiency("index")
);

CREATE TABLE IF NOT EXISTS RaceLanguageChoice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    race_index VARCHAR(100) NOT NULL,
    description TEXT,
    choose INT NOT NULL,
    type VARCHAR(50) NOT NULL,
    FOREIGN KEY (race_index) REFERENCES Race("index")
);

CREATE TABLE IF NOT EXISTS RaceLanguageChoiceOption (
    choice_id INT,
    language_index VARCHAR(100),
    PRIMARY KEY (choice_id, language_index),
    FOREIGN KEY (choice_id) REFERENCES RaceLanguageChoice(id),
    FOREIGN KEY (language_index) REFERENCES Language("index")
);

CREATE TABLE IF NOT EXISTS Subrace (
    "index" VARCHAR(100) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    race_index VARCHAR(100) NOT NULL,
    description TEXT,
    FOREIGN KEY (race_index) REFERENCES Race("index")
);

CREATE TABLE IF NOT EXISTS SubraceAbilityBonus (
    subrace_index VARCHAR(100),
    ability_score_index VARCHAR(10),
    bonus INT NOT NULL,
    PRIMARY KEY (subrace_index, ability_score_index),
    FOREIGN KEY (subrace_index) REFERENCES Subrace("index"),
    FOREIGN KEY (ability_score_index) REFERENCES AbilityScore("index")
);

CREATE TABLE IF NOT EXISTS SubraceProficiency (
    subrace_index VARCHAR(100),
    proficiency_index VARCHAR(100),
    PRIMARY KEY (subrace_index, proficiency_index),
    FOREIGN KEY (subrace_index) REFERENCES Subrace("index"),
    FOREIGN KEY (proficiency_index) REFERENCES Proficiency("index")
);

CREATE TABLE IF NOT EXISTS SubraceLanguage (
    subrace_index VARCHAR(100),
    language_index VARCHAR(100),
    PRIMARY KEY (subrace_index, language_index),
    FOREIGN KEY (subrace_index) REFERENCES Subrace("index"),
    FOREIGN KEY (language_index) REFERENCES Language("index")
);

CREATE TABLE IF NOT EXISTS SubraceFeature (
    subrace_index VARCHAR(100),
    feature_index VARCHAR(100),
    PRIMARY KEY (subrace_index, feature_index),
    FOREIGN KEY (subrace_index) REFERENCES Subrace("index"),
    FOREIGN KEY (feature_index) REFERENCES Feature("index")
);

CREATE TABLE IF NOT EXISTS SubraceLanguageChoice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subrace_index VARCHAR(100) NOT NULL,
    description TEXT,
    choose INT NOT NULL,
    type VARCHAR(50) NOT NULL,
    FOREIGN KEY (subrace_index) REFERENCES Subrace("index")
);

CREATE TABLE IF NOT EXISTS SubraceLanguageChoiceOption (
    choice_id INT,
    language_index VARCHAR(100),
    PRIMARY KEY (choice_id, language_index),
    FOREIGN KEY (choice_id) REFERENCES SubraceLanguageChoice(id),
    FOREIGN KEY (language_index) REFERENCES Language("index")
);