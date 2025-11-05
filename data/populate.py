import sqlite3
import json
import sys
import os

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(__file__)
DB_NAME = os.path.join(SCRIPT_DIR, "dnd_srd.db")
SCHEMA_FILE = os.path.join(SCRIPT_DIR, "schema.sql")
MODULES_DIR = os.path.join(SCRIPT_DIR, "modules")

# --- Database Functions ---

def connect_db(db_name):
    """Connects to the SQLite DB and returns connection and cursor."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.executescript("PRAGMA foreign_keys = ON;")
    return conn, cursor

def create_tables(cursor):
    """Creates all tables from the schema.sql file."""
    print(f"Reading schema from {SCHEMA_FILE}...")
    try:
        with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        cursor.executescript(schema_sql)
        print("Tables created successfully.")
    except FileNotFoundError:
        print(f"ERROR: '{SCHEMA_FILE}' not found.", file=sys.stderr)
        raise
    except sqlite3.Error as e:
        print(f"An error occurred while creating tables: {e}", file=sys.stderr)
        raise

# --- Data Loading Function ---

def load_json(file_path):
    """Loads and parses JSON data from a local file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            print(f"  Loading data from: {file_path}")
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}", file=sys.stderr)
        return None
    except FileNotFoundError:
        print(f"Error: File not found. Make sure '{file_path}' exists.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error loading file {file_path}: {e}", file=sys.stderr)
        return None

# --- Population Functions ---

def populate_reference_tables(cursor, file_paths):
    """Populates all independent reference tables from their JSON files."""
    print("Populating reference tables...")
    
    try:
        ability_scores = load_json(file_paths['ability_scores'])
        if ability_scores:
            cursor.executemany(
                "INSERT OR IGNORE INTO AbilityScore (\"index\", name, full_name, description) VALUES (?, ?, ?, ?)",
                [(s['index'], s['name'], s.get('full_name'), '\n'.join(s.get('desc', []))) for s in ability_scores]
            )

        damage_types = load_json(file_paths['damage_types'])
        if damage_types:
            cursor.executemany(
                "INSERT OR IGNORE INTO DamageType (\"index\", name, description) VALUES (?, ?, ?)",
                [(d['index'], d['name'], '\n'.join(d.get('desc', []))) for d in damage_types]
            )

        magic_schools = load_json(file_paths['magic_schools'])
        if magic_schools:
            cursor.executemany(
                "INSERT OR IGNORE INTO MagicSchool (\"index\", name, description) VALUES (?, ?, ?)",
                [(s['index'], s['name'], s.get('desc')) for s in magic_schools]
            )

        prof_data = load_json(file_paths['proficiencies'])
        if prof_data:
            cursor.executemany(
                "INSERT OR IGNORE INTO Proficiency (\"index\", name, type) VALUES (?, ?, ?)",
                [(p['index'], p['name'], p['type']) for p in prof_data]
            )

        cat_data = load_json(file_paths['equipment_categories'])
        if cat_data:
            cursor.executemany(
                "INSERT OR IGNORE INTO EquipmentCategory (\"index\", name) VALUES (?, ?)",
                [(c['index'], c['name']) for c in cat_data]
            )
        
        prop_data = load_json(file_paths['weapon_properties'])
        if prop_data:
            cursor.executemany(
                "INSERT OR IGNORE INTO WeaponProperty (\"index\", name, description) VALUES (?, ?, ?)",
                [(p['index'], p['name'], '\n'.join(p.get('desc', []))) for p in prop_data]
            )
        
        # NEW: Load Languages
        languages = load_json(file_paths['languages'])
        if languages:
            cursor.executemany(
                "INSERT OR IGNORE INTO Language (\"index\", name, type) VALUES (?, ?, ?)",
                [(l['index'], l['name'], l.get('type')) for l in languages]
            )

        print("Reference tables populated.")
    except sqlite3.Error as e:
        print(f"Error populating reference tables: {e}", file=sys.stderr)
        raise

def populate_class_tables(cursor, file_paths):
    """Populates all tables related to Classes."""
    print("Populating Class tables...")
    classes_data = load_json(file_paths['classes'])
    if not classes_data:
        print("  Skipping class tables, file not loaded.")
        return

    try:
        for char_class in classes_data:
            spellcasting = char_class.get('spellcasting', {})
            spellcasting_lvl = spellcasting.get('level')
            spellcasting_abil = spellcasting.get('spellcasting_ability', {}).get('index')
            
            cursor.execute(
                """INSERT OR IGNORE INTO Class ("index", name, hit_die, spellcasting_level, spellcasting_ability_index) 
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    char_class['index'], char_class['name'], char_class['hit_die'],
                    spellcasting_lvl, spellcasting_abil
                )
            )
            
            for subclass in char_class.get('subclasses', []):
                cursor.execute(
                    "INSERT OR IGNORE INTO Subclass (\"index\", name, class_index) VALUES (?, ?, ?)",
                    (subclass['index'], subclass['name'], char_class['index'])
                )
            
            for prof in char_class.get('proficiencies', []):
                cursor.execute(
                    "INSERT OR IGNORE INTO ClassProficiency (class_index, proficiency_index) VALUES (?, ?)",
                    (char_class['index'], prof['index'])
                )
                                  
            for choice in char_class.get('proficiency_choices', []):
                cursor.execute(
                    "INSERT INTO ClassProficiencyChoice (class_index, description, choose, type) VALUES (?, ?, ?, ?)",
                    (char_class['index'], choice.get('desc'), choice['choose'], choice['type'])
                )
                choice_id = cursor.lastrowid
                
                choice_from = choice.get('from', {})
                if not choice_from: continue

                options = choice_from.get('options', [])
                for option in options:
                    if isinstance(option, dict) and option.get('option_type') == 'reference':
                        cursor.execute(
                            "INSERT OR IGNORE INTO ClassProficiencyChoiceOption (choice_id, proficiency_index) VALUES (?, ?)",
                            (choice_id, option['item']['index'])
                        )
                    elif isinstance(option, dict) and option.get('option_type') == 'choice':
                        nested_choice_from = option.get('choice', {}).get('from', {})
                        nested_options = nested_choice_from.get('options', [])
                        for nested_option in nested_options:
                             if isinstance(nested_option, dict) and nested_option.get('option_type') == 'reference':
                                cursor.execute(
                                    "INSERT OR IGNORE INTO ClassProficiencyChoiceOption (choice_id, proficiency_index) VALUES (?, ?)",
                                    (choice_id, nested_option['item']['index'])
                                )

        print("Class tables populated.")
    except sqlite3.Error as e:
        print(f"Error populating class tables: {e}", file=sys.stderr)
        raise

def populate_subclass_details(cursor, file_paths):
    """Parses 5e-SRD-Subclasses.json to add descriptions and flavors to the Subclass table."""
    print("Populating subclass details...")
    subclass_data = load_json(file_paths['subclasses'])
    if not subclass_data:
        print("  Skipping subclass details, file not loaded.")
        return
        
    try:
        for subclass in subclass_data:
            cursor.execute(
                """UPDATE Subclass SET desc = ?, subclass_flavor = ? WHERE "index" = ?""",
                (
                    '\n'.join(subclass.get('desc', [])),
                    subclass.get('subclass_flavor'),
                    subclass['index']
                )
            )
        print("Subclass details populated.")
    except sqlite3.Error as e:
        print(f"Error populating subclass details: {e}", file=sys.stderr)
        raise

def populate_spell_tables(cursor, file_paths):
    """Populates all tables related to Spells."""
    print("Populating Spell tables...")
    spells_data = load_json(file_paths['spells'])
    if not spells_data:
        print("  Skipping spells, file not loaded.")
        return

    try:
        for spell in spells_data:
            cursor.execute(
                """INSERT OR IGNORE INTO Spell ("index", name, description, higher_level_desc, range, components, material, ritual, 
                   duration, concentration, casting_time, level, attack_type, damage_type_index, dc_type_index, 
                   dc_success, area_of_effect_type, area_of_effect_size, school_index) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    spell['index'], spell['name'], '\n'.join(spell.get('desc', [])),
                    '\n'.join(spell.get('higher_level', [])), spell.get('range'),
                    ','.join(spell.get('components', [])), spell.get('material'),
                    spell.get('ritual', False), spell.get('duration'),
                    spell.get('concentration', False), spell.get('casting_time'),
                    spell['level'], spell.get('attack_type'),
                    spell.get('damage', {}).get('damage_type', {}).get('index'),
                    spell.get('dc', {}).get('dc_type', {}).get('index'),
                    spell.get('dc', {}).get('dc_success'),
                    spell.get('area_of_effect', {}).get('type'),
                    spell.get('area_of_effect', {}).get('size'),
                    spell.get('school', {}).get('index')
                )
            )
            
            for char_class in spell.get('classes', []):
                cursor.execute(
                    "INSERT OR IGNORE INTO SpellClass (spell_index, class_index) VALUES (?, ?)",
                    (spell['index'], char_class['index'])
                )

            for subclass in spell.get('subclasses', []):
                cursor.execute(
                    "INSERT OR IGNORE INTO SpellSubclass (spell_index, subclass_index) VALUES (?, ?)",
                    (spell['index'], subclass['index'])
                )
        
        print("Spell tables populated.")
    except sqlite3.Error as e:
        print(f"Error populating spell tables: {e}", file=sys.stderr)
        raise

def populate_equipment_tables(cursor, file_paths):
    """Populates all tables related to Equipment."""
    print("Populating Equipment tables...")
    equipment_data = load_json(file_paths['equipment'])
    if not equipment_data:
        print("  Skipping equipment, file not loaded.")
        return
        
    try:
        for item in equipment_data:
            cursor.execute(
                """INSERT OR IGNORE INTO Equipment ("index", name, equipment_category_index, cost_quantity, cost_unit, weight, 
                   description, weapon_category, weapon_range, category_range, damage_dice, damage_type_index, 
                   range_normal, range_long, throw_range_normal, throw_range_long, two_handed_damage_dice, 
                   two_handed_damage_type_index, armor_category, armor_class_base, armor_class_dex_bonus, 
                   armor_class_max_bonus, str_minimum, stealth_disadvantage, gear_category_index, tool_category, 
                   vehicle_category, speed_quantity, speed_unit, capacity) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    item.get('index'), item.get('name'),
                    item.get('equipment_category', {}).get('index'),
                    item.get('cost', {}).get('quantity'), item.get('cost', {}).get('unit'),
                    item.get('weight'), '\n'.join(item.get('desc', [])) if item.get('desc') else None,
                    item.get('weapon_category'), item.get('weapon_range'), item.get('category_range'),
                    item.get('damage', {}).get('damage_dice'),
                    item.get('damage', {}).get('damage_type', {}).get('index'),
                    item.get('range', {}).get('normal'), item.get('range', {}).get('long'),
                    item.get('throw_range', {}).get('normal'), item.get('throw_range', {}).get('long'),
                    item.get('two_handed_damage', {}).get('damage_dice'),
                    item.get('two_handed_damage', {}).get('damage_type', {}).get('index'),
                    item.get('armor_category'), item.get('armor_class', {}).get('base'),
                    item.get('armor_class', {}).get('dex_bonus'),
                    item.get('armor_class', {}).get('max_bonus'),
                    item.get('str_minimum', 0), item.get('stealth_disadvantage', False),
                    item.get('gear_category', {}).get('index'), item.get('tool_category'),
                    item.get('vehicle_category'), item.get('speed', {}).get('quantity'),
                    item.get('speed', {}).get('unit'), item.get('capacity')
                )
            )
            
            for prop in item.get('properties', []):
                cursor.execute(
                    "INSERT OR IGNORE INTO EquipmentProperty (equipment_index, property_index) VALUES (?, ?)",
                    (item['index'], prop['index'])
                )
                                  
            for content in item.get('contents', []):
                cursor.execute("SELECT 1 FROM Equipment WHERE \"index\" = ?", (content['item']['index'],))
                if cursor.fetchone():
                    cursor.execute(
                        "INSERT OR IGNORE INTO EquipmentContent (pack_equipment_index, content_equipment_index, quantity) VALUES (?, ?, ?)",
                        (item['index'], content['item']['index'], content['quantity'])
                    )

        print("Equipment tables populated.")
    except sqlite3.Error as e:
        print(f"Error populating equipment tables: {e}", file=sys.stderr)
        raise

def populate_levels_tables(cursor, file_paths):
    """Populates all tables related to class and subclass level progression."""
    print("Populating level progression tables...")
    
    # We must load features first to populate the Feature table
    features_data = load_json(file_paths['features'])
    if features_data:
        try:
            for feature in features_data:
                cursor.execute(
                    "INSERT OR IGNORE INTO Feature (\"index\", name, description) VALUES (?, ?, ?)",
                    (
                        feature['index'], feature['name'],
                        '\n'.join(feature.get('desc', []))
                    )
                )
            print("  Feature table populated.")
        except sqlite3.Error as e:
            print(f"Error populating Feature table: {e}", file=sys.stderr)
            raise
    else:
        print("  Skipping Feature table, file not loaded.")

    levels_data = load_json(file_paths['levels'])
    if not levels_data:
        print("  Skipping level progression, file not loaded.")
        return

    try:
        for level_entry in levels_data:
            # Add any features *also* defined in this file (some are)
            for feature in level_entry.get('features', []):
                cursor.execute(
                    "INSERT OR IGNORE INTO Feature (\"index\", name) VALUES (?, ?)",
                    (feature['index'], feature['name'])
                )
            
            if 'subclass' in level_entry:
                cursor.execute(
                    """INSERT INTO SubclassLevel (subclass_index, level, subclass_specific_json) 
                       VALUES (?, ?, ?)""",
                    (
                        level_entry['subclass']['index'],
                        level_entry['level'],
                        json.dumps(level_entry.get('subclass_specific'))
                    )
                )
                subclass_level_id = cursor.lastrowid
                
                for feature in level_entry.get('features', []):
                    cursor.execute(
                        "INSERT OR IGNORE INTO SubclassLevel_Feature (subclass_level_id, feature_index) VALUES (?, ?)",
                        (subclass_level_id, feature['index'])
                    )
            
            elif 'class' in level_entry:
                cursor.execute(
                    """INSERT INTO ClassLevel (class_index, level, prof_bonus, ability_score_bonuses, class_specific_json) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        level_entry['class']['index'],
                        level_entry['level'],
                        level_entry.get('prof_bonus'),
                        level_entry.get('ability_score_bonuses'),
                        json.dumps(level_entry.get('class_specific'))
                    )
                )
                class_level_id = cursor.lastrowid
                
                for feature in level_entry.get('features', []):
                    cursor.execute(
                        "INSERT OR IGNORE INTO ClassLevel_Feature (class_level_id, feature_index) VALUES (?, ?)",
                        (class_level_id, feature['index'])
                    )
                
                if 'spellcasting' in level_entry:
                    sc = level_entry['spellcasting']
                    cursor.execute(
                        """INSERT OR IGNORE INTO ClassLevel_Spellcasting 
                           (class_level_id, cantrips_known, spells_known, spell_slots_level_1, spell_slots_level_2, 
                           spell_slots_level_3, spell_slots_level_4, spell_slots_level_5, spell_slots_level_6, 
                           spell_slots_level_7, spell_slots_level_8, spell_slots_level_9) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            class_level_id,
                            sc.get('cantrips_known'), sc.get('spells_known'),
                            sc.get('spell_slots_level_1'), sc.get('spell_slots_level_2'),
                            sc.get('spell_slots_level_3'), sc.get('spell_slots_level_4'),
                            sc.get('spell_slots_level_5'), sc.get('spell_slots_level_6'),
                            sc.get('spell_slots_level_7'), sc.get('spell_slots_level_8'),
                            sc.get('spell_slots_level_9')
                        )
                    )
        print("Level progression tables populated.")
    except sqlite3.Error as e:
        print(f"Error populating level tables: {e}", file=sys.stderr)
        raise

# ---------- NEW: Feat Population Function ----------
def populate_feat_table(cursor, file_paths):
    """Populates the Feat table."""
    print("Populating Feat table...")
    feats_data = load_json(file_paths['feats'])
    if not feats_data:
        print("  Skipping Feats, file not loaded.")
        return
    
    try:
        for feat in feats_data:
            prereqs = feat.get('prerequisites', [])
            prereqs_json = json.dumps(prereqs) if prereqs else None
            
            cursor.execute(
                """INSERT OR IGNORE INTO Feat ("index", name, prerequisites_json, description) 
                   VALUES (?, ?, ?, ?)""",
                (
                    feat['index'], feat['name'],
                    prereqs_json,
                    '\n'.join(feat.get('desc', []))
                )
            )
        print("Feat table populated.")
    except sqlite3.Error as e:
        print(f"Error populating Feat table: {e}", file=sys.stderr)
        raise

# ---------- NEW: Race Population Function ----------
def populate_race_tables(cursor, file_paths):
    """Populates all tables related to Races."""
    print("Populating Race tables...")
    races_data = load_json(file_paths['races'])
    if not races_data:
        print("  Skipping Race tables, file not loaded.")
        return

    try:
        for race in races_data:
            cursor.execute(
                """INSERT OR IGNORE INTO Race ("index", name, speed, alignment, age, size, size_description, language_desc) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    race['index'], race['name'], race['speed'],
                    race.get('alignment'), race.get('age'), race.get('size'),
                    race.get('size_description'), race.get('language_desc')
                )
            )
            race_index = race['index']

            # Ability Bonuses
            for bonus in race.get('ability_bonuses', []):
                cursor.execute(
                    "INSERT OR IGNORE INTO RaceAbilityBonus (race_index, ability_score_index, bonus) VALUES (?, ?, ?)",
                    (race_index, bonus['ability_score']['index'], bonus['bonus'])
                )
            
            # Starting Proficiencies
            for prof in race.get('starting_proficiencies', []):
                cursor.execute(
                    "INSERT OR IGNORE INTO RaceProficiency (race_index, proficiency_index) VALUES (?, ?)",
                    (race_index, prof['index'])
                )

            # Languages
            for lang in race.get('languages', []):
                cursor.execute(
                    "INSERT OR IGNORE INTO RaceLanguage (race_index, language_index) VALUES (?, ?)",
                    (race_index, lang['index'])
                )
            
            # Traits (Features)
            for trait in race.get('traits', []):
                # Ensure feature exists in Feature table first
                cursor.execute("INSERT OR IGNORE INTO Feature (\"index\", name) VALUES (?, ?)", (trait['index'], trait['name']))
                cursor.execute(
                    "INSERT OR IGNORE INTO RaceFeature (race_index, feature_index) VALUES (?, ?)",
                    (race_index, trait['index'])
                )

            # Proficiency Choices (modeled after class choices)
            for choice in race.get('starting_proficiency_options', []):
                # --- START FIX ---
                # Check if choice is a dictionary before trying to access keys
                if not isinstance(choice, dict):
                    print(f"  Skipping non-dict proficiency choice for race {race_index}: {choice}")
                    continue
                # --- END FIX ---

                cursor.execute(
                    "INSERT INTO RaceProficiencyChoice (race_index, description, choose, type) VALUES (?, ?, ?, ?)",
                    (race_index, choice.get('desc'), choice['choose'], choice['type'])
                )
                choice_id = cursor.lastrowid
                choice_from = choice.get('from', {})
                if not choice_from: continue
                
                options = choice_from.get('options', [])
                for option in options:
                    if isinstance(option, dict) and option.get('option_type') == 'reference':
                        cursor.execute(
                            "INSERT OR IGNORE INTO RaceProficiencyChoiceOption (choice_id, proficiency_index) VALUES (?, ?)",
                            (choice_id, option['item']['index'])
                        )
                    elif isinstance(option, dict) and option.get('option_type') == 'choice':
                        nested_choice_from = option.get('choice', {}).get('from', {})
                        nested_options = nested_choice_from.get('options', [])
                        for nested_option in nested_options:
                             if isinstance(nested_option, dict) and nested_option.get('option_type') == 'reference':
                                cursor.execute(
                                    "INSERT OR IGNORE INTO RaceProficiencyChoiceOption (choice_id, proficiency_index) VALUES (?, ?)",
                                    (choice_id, nested_option['item']['index'])
                                )

            # Language Choices
            for choice in race.get('language_options', []):
                # --- START FIX ---
                # Check if choice is a dictionary before trying to access keys
                if not isinstance(choice, dict):
                    print(f"  Skipping non-dict language choice for race {race_index}: {choice}")
                    continue
                # --- END FIX ---

                cursor.execute(
                    "INSERT INTO RaceLanguageChoice (race_index, description, choose, type) VALUES (?, ?, ?, ?)",
                    (race_index, choice.get('desc'), choice['choose'], choice['type'])
                )
                choice_id = cursor.lastrowid
                choice_from = choice.get('from', {})
                if not choice_from: continue
                
                options = choice_from.get('options', [])
                for option in options:
                     if isinstance(option, dict) and option.get('option_type') == 'reference':
                        cursor.execute(
                            "INSERT OR IGNORE INTO RaceLanguageChoiceOption (choice_id, language_index) VALUES (?, ?)",
                            (choice_id, option['item']['index'])
                        )
                     elif isinstance(option, dict) and option.get('option_type') == 'choice':
                        nested_choice_from = option.get('choice', {}).get('from', {})
                        nested_options = nested_choice_from.get('options', [])
                        for nested_option in nested_options:
                             if isinstance(nested_option, dict) and nested_option.get('option_type') == 'reference':
                                cursor.execute(
                                    "INSERT OR IGNORE INTO RaceLanguageChoiceOption (choice_id, language_index) VALUES (?, ?)",
                                    (choice_id, nested_option['item']['index'])
                                )
        
        print("Race tables populated.")
    except sqlite3.Error as e:
        print(f"Error populating race tables: {e}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"A general error occurred in populate_race_tables: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        raise

# ---------- NEW: Subrace Population Function ----------
def populate_subrace_tables(cursor, file_paths):
    """Populates all tables related to Subraces."""
    print("Populating Subrace tables...")
    subraces_data = load_json(file_paths['subraces'])
    if not subraces_data:
        print("  Skipping Subrace tables, file not loaded.")
        return

    try:
        for subrace in subraces_data:
            cursor.execute(
                """INSERT OR IGNORE INTO Subrace ("index", name, race_index, description) 
                   VALUES (?, ?, ?, ?)""",
                (
                    subrace['index'], subrace['name'], subrace['race']['index'],
                    '\n'.join(subrace.get('desc', []))
                )
            )
            subrace_index = subrace['index']

            # Ability Bonuses
            for bonus in subrace.get('ability_bonuses', []):
                cursor.execute(
                    "INSERT OR IGNORE INTO SubraceAbilityBonus (subrace_index, ability_score_index, bonus) VALUES (?, ?, ?)",
                    (subrace_index, bonus['ability_score']['index'], bonus['bonus'])
                )
            
            # Starting Proficiencies
            for prof in subrace.get('starting_proficiencies', []):
                cursor.execute(
                    "INSERT OR IGNORE INTO SubraceProficiency (subrace_index, proficiency_index) VALUES (?, ?)",
                    (subrace_index, prof['index'])
                )

            # Languages
            for lang in subrace.get('languages', []):
                cursor.execute(
                    "INSERT OR IGWE IGNORE INTO SubraceLanguage (subrace_index, language_index) VALUES (?, ?)",
                    (subrace_index, lang['index'])
                )
            
            # Traits (Features) - Note: key is 'racial_traits' in subrace json
            for trait in subrace.get('racial_traits', []): 
                cursor.execute("INSERT OR IGNORE INTO Feature (\"index\", name) VALUES (?, ?)", (trait['index'], trait['name']))
                cursor.execute(
                    "INSERT OR IGNORE INTO SubraceFeature (subrace_index, feature_index) VALUES (?, ?)",
                    (subrace_index, trait['index'])
                )

            # Language Choices
            for choice in subrace.get('language_options', []):
                # --- START FIX ---
                # Check if choice is a dictionary before trying to access keys
                if not isinstance(choice, dict):
                    print(f"  Skipping non-dict language choice for subrace {subrace_index}: {choice}")
                    continue
                # --- END FIX ---

                cursor.execute(
                    "INSERT INTO SubraceLanguageChoice (subrace_index, description, choose, type) VALUES (?, ?, ?, ?)",
                    (subrace_index, choice.get('desc'), choice['choose'], choice['type'])
                )
                choice_id = cursor.lastrowid
                choice_from = choice.get('from', {})
                if not choice_from: continue
                
                options = choice_from.get('options', [])
                for option in options:
                     if isinstance(option, dict) and option.get('option_type') == 'reference':
                        cursor.execute(
                            "INSERT OR IGNORE INTO SubraceLanguageChoiceOption (choice_id, language_index) VALUES (?, ?)",
                            (choice_id, option['item']['index'])
                        )
                     elif isinstance(option, dict) and option.get('option_type') == 'choice':
                        nested_choice_from = option.get('choice', {}).get('from', {})
                        nested_options = nested_choice_from.get('options', [])
                        for nested_option in nested_options:
                             if isinstance(nested_option, dict) and nested_option.get('option_type') == 'reference':
                                cursor.execute(
                                    "INSERT OR IGNORE INTO SubraceLanguageChoiceOption (choice_id, language_index) VALUES (?, ?)",
                                    (choice_id, nested_option['item']['index'])
                                )
        
        print("Subrace tables populated.")
    except sqlite3.Error as e:
        print(f"Error populating subrace tables: {e}", file=sys.stderr)
        raise

# --- Main Execution ---

def main():
    """Main function to create and populate the database."""
    
    # This script assumes all these JSON files are in the 'modules' subdirectory.
    file_paths = {
        'classes': os.path.join(MODULES_DIR, '5e-SRD-Classes.json'),
        'levels': os.path.join(MODULES_DIR, '5e-SRD-Levels.json'),
        'subclasses': os.path.join(MODULES_DIR, '5e-SRD-Subclasses.json'),
        'features': os.path.join(MODULES_DIR, '5e-SRD-Features.json'),
        'spells': os.path.join(MODULES_DIR, '5e-SRD-Spells.json'),
        'equipment': os.path.join(MODULES_DIR, '5e-SRD-Equipment.json'),
        'proficiencies': os.path.join(MODULES_DIR, '5e-SRD-Proficiencies.json'),
        'equipment_categories': os.path.join(MODULES_DIR, '5e-SRD-Equipment-Categories.json'),
        'weapon_properties': os.path.join(MODULES_DIR, '5e-SRD-Weapon-Properties.json'),
        'ability_scores': os.path.join(MODULES_DIR, '5e-SRD-Ability-Scores.json'),
        'damage_types': os.path.join(MODULES_DIR, '5e-SRD-Damage-Types.json'),
        'magic_schools': os.path.join(MODULES_DIR, '5e-SRD-Magic-Schools.json'),
        # NEWLY ADDED
        'races': os.path.join(MODULES_DIR, '5e-SRD-Races.json'),
        'subraces': os.path.join(MODULES_DIR, '5e-SRD-Subraces.json'),
        'languages': os.path.join(MODULES_DIR, '5e-SRD-Languages.json'),
        'feats': os.path.join(MODULES_DIR, '5e-SRD-Feats.json'),
    }
    
    # Check if DB already exists and delete it for a clean build
    if os.path.exists(DB_NAME):
        print(f"Removing old database '{DB_NAME}'...")
        os.remove(DB_NAME)

    conn = None
    try:
        conn, cursor = connect_db(DB_NAME)
        
        # Create all the tables
        create_tables(cursor)
        
        # Populate tables in order of dependency
        populate_reference_tables(cursor, file_paths) # Now includes Languages
        
        populate_class_tables(cursor, file_paths) 
        
        populate_subclass_details(cursor, file_paths) 
        
        populate_spell_tables(cursor, file_paths)
        populate_equipment_tables(cursor, file_paths)
        
        populate_levels_tables(cursor, file_paths) # Populates Features, which Races depend on
        
        # NEWLY ADDED
        populate_race_tables(cursor, file_paths)
        populate_subrace_tables(cursor, file_paths)
        populate_feat_table(cursor, file_paths)
        
        # Save changes
        conn.commit()
        print(f"\nSuccessfully created and populated '{DB_NAME}'!")

    except Exception as e:
        print(f"\nAn error occurred: {e}", file=sys.stderr)
        if conn:
            conn.rollback()
            print("Database transaction rolled back.")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()