dndice/
├── main.py                     # Entry point: CLI menu, command handling
│
├── core/
│   ├── database.py              # SQLite connection, schema setup, query helpers
│   ├── dice.py                  # Dice-rolling utilities (1d20, 3d6, etc.)
│   ├── character.py             # Character class, stats logic, creation flow
│   └── io_utils.py              # JSON import/export, file handling
│
├── data/
|   ├── modules/
│   ├── dnd.db                   # SQLite database (auto-created)
│   └── schema.sql               # Database schema definition

│
├── saves/
│   ├── my_character.json        # Saved character sheets (exported)
│   └── party/                   # Optional folder for grouped saves
│
├── .env                         # config
├── requirements.txt             # Dependencies
├── README.md                    # Project overview, setup instructions
└── LICENSE                      # License (MIT, GPL, etc.)
