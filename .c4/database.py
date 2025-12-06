"""
Database schema and operations for SDG3 game
"""
import sqlite3
from contextlib import contextmanager
from typing import Optional, Dict, List, Tuple
import random
import string

DB_PATH = "sdg3_game.db"

# Updated region names
REGIONS = {
    "Africa": "Africa, South of Sahara",
    "Middle East": "Middle East & North Africa", 
    "Pacific Asia": "Pacific Rim",
    "European Union": "Europe",
    "China": "China",
    "India": "India",
    "Russia": "Russia",
    "USA": "USA",
    "Latin America": "Latin America",
    "South East Asia": "South East Asia"
}

MINISTRIES = ["Poverty", "Inequality", "Empowerment", "Food", "Energy", "Future/Budget"]


@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def generate_game_id() -> str:
    """
    Generate a simple game ID: 3 uppercase letters + dash + 3 digits
    Example: ADJ-932
    """
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    digits = ''.join(random.choices(string.digits, k=3))
    return f"{letters}-{digits}"


def create_unique_game_id() -> str:
    """Generate a unique game_id (check database for uniqueness)"""
    with get_db() as conn:
        while True:
            game_id = generate_game_id()
            cursor = conn.execute("SELECT game_id FROM games WHERE game_id = ?", (game_id,))
            if not cursor.fetchone():
                return game_id


def init_database():
    """Initialize database schema"""
    with get_db() as conn:
        # Games table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS games (
                game_id TEXT PRIMARY KEY,
                gm_username TEXT NOT NULL,
                num_rounds INTEGER NOT NULL,
                current_round INTEGER DEFAULT 0,
                state TEXT DEFAULT 'setup',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Players table - username is UNIQUE across entire database
        conn.execute("""
            CREATE TABLE IF NOT EXISTS players (
                player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                game_id TEXT NOT NULL,
                region TEXT NOT NULL,
                ministry TEXT NOT NULL,
                is_ai BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES games(game_id)
            )
        """)
        
        # Create index on username for fast lookups
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_players_username 
            ON players(username)
        """)
        
        # Policies table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS policies (
                policy_id INTEGER PRIMARY KEY AUTOINCREMENT,
                policy_name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT
            )
        """)
        
        # Policy decisions table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS policy_decisions (
                decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT NOT NULL,
                round INTEGER NOT NULL,
                region TEXT NOT NULL,
                ministry TEXT NOT NULL,
                policy_id INTEGER NOT NULL,
                value REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES games(game_id),
                FOREIGN KEY (policy_id) REFERENCES policies(policy_id),
                UNIQUE(game_id, round, region, ministry, policy_id)
            )
        """)
        
        # Plot variables table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS plot_variables (
                variable_id INTEGER PRIMARY KEY AUTOINCREMENT,
                variable_name TEXT NOT NULL,
                region TEXT NOT NULL,
                description TEXT
            )
        """)
        
        # Plot results table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS plot_results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT NOT NULL,
                round INTEGER NOT NULL,
                region TEXT NOT NULL,
                variable_id INTEGER NOT NULL,
                value REAL NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games(game_id),
                FOREIGN KEY (variable_id) REFERENCES plot_variables(variable_id),
                UNIQUE(game_id, round, region, variable_id)
            )
        """)
        
        conn.commit()


def check_username_available(username: str) -> bool:
    """
    Check if username is available globally (not just within a game)
    Returns True if available, False if taken
    """
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT username FROM players WHERE username = ?",
            (username,)
        )
        return cursor.fetchone() is None


def get_game_by_gm_username(username: str) -> Optional[Dict]:
    """
    Get game information by GM username
    Returns game dict if found, None otherwise
    """
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT game_id, gm_username, num_rounds, current_round, state, 
                   created_at, updated_at
            FROM games 
            WHERE gm_username = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (username,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_available_regions_ministries(game_id: str) -> Dict[str, List[str]]:
    """
    Get available (unclaimed) ministries for each region
    Returns dict: {region_name: [available_ministry1, ministry2, ...]}
    """
    with get_db() as conn:
        # Get all claimed positions
        cursor = conn.execute(
            """
            SELECT region, ministry 
            FROM players 
            WHERE game_id = ? AND is_ai = 0
            """,
            (game_id,)
        )
        claimed = {(row['region'], row['ministry']) for row in cursor.fetchall()}
        
        # Build available positions
        available = {}
        for region in REGIONS.keys():
            available_ministries = [
                ministry for ministry in MINISTRIES 
                if (region, ministry) not in claimed
            ]
            if available_ministries:  # Only include regions with available spots
                available[region] = available_ministries
        
        return available


def create_game(gm_username: str, num_rounds: int) -> str:
    """Create a new game and return game_id"""
    game_id = create_unique_game_id()
    
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO games (game_id, gm_username, num_rounds, current_round, state)
            VALUES (?, ?, ?, 0, 'setup')
            """,
            (game_id, gm_username, num_rounds)
        )
        conn.commit()
    
    return game_id


def add_player(game_id: str, username: str, region: str, ministry: str, is_ai: bool = False) -> bool:
    """
    Add a player to the game
    Returns True if successful, False if username taken or position occupied
    """
    with get_db() as conn:
        try:
            conn.execute(
                """
                INSERT INTO players (username, game_id, region, ministry, is_ai)
                VALUES (?, ?, ?, ?, ?)
                """,
                (username, game_id, region, ministry, is_ai)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Username already exists or other constraint violation
            return False


def get_player_info(username: str) -> Optional[Dict]:
    """
    Get player information by username
    Returns player dict if found, None otherwise
    """
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT p.player_id, p.username, p.game_id, p.region, p.ministry, 
                   p.is_ai, g.num_rounds, g.current_round, g.state
            FROM players p
            JOIN games g ON p.game_id = g.game_id
            WHERE p.username = ?
            """,
            (username,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def save_policy_decision(game_id: str, round_num: int, region: str, 
                        ministry: str, policy_id: int, value: float):
    """Save a policy decision (upsert)"""
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO policy_decisions 
                (game_id, round, region, ministry, policy_id, value)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(game_id, round, region, ministry, policy_id)
            DO UPDATE SET value = excluded.value, timestamp = CURRENT_TIMESTAMP
            """,
            (game_id, round_num, region, ministry, policy_id, value)
        )
        conn.commit()


def get_policy_decisions(game_id: str, round_num: int, region: str, 
                         ministry: str) -> List[Tuple[int, float]]:
    """
    Get policy decisions for a specific player in a round
    Returns list of (policy_id, value) tuples
    """
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT policy_id, value
            FROM policy_decisions
            WHERE game_id = ? AND round = ? AND region = ? AND ministry = ?
            ORDER BY policy_id
            """,
            (game_id, round_num, region, ministry)
        )
        return [(row['policy_id'], row['value']) for row in cursor.fetchall()]


if __name__ == "__main__":
    # Initialize database
    init_database()
    print("Database initialized successfully!")
    
    # Test game_id generation
    print("\nSample game IDs:")
    for _ in range(5):
        print(f"  {generate_game_id()}")
