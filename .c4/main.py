"""
SDG3 Educational Simulation Game - NiceGUI Implementation
Main application entry point
Phase 1 Complete: Start code, region tags, session state fixed
"""
from nicegui import ui, app
import database as db

# Global state for current user session
session_state = {
    'username': None,
    'game_id': None,
    'role': None,  # 'gm' or 'player'
    'region_tag': None,  # Changed from 'region' to 'region_tag'
    'ministry': None
}


def get_browser_language():
    """Detect browser language (placeholder - NiceGUI handles this)"""
    return 'en'  # Default to English, can be enhanced


# ============================================================================
# ENTRY PAGE
# ============================================================================

@ui.page('/')
def entry_page():
    """Main entry page - start/continue game or join game"""
    
    ui.colors(primary='#1976D2', secondary='#26A69A', accent='#9C27B0')
    
    with ui.column().classes('w-full max-w-2xl mx-auto p-8 gap-6'):
        ui.label('SDG3 Simulation Game').classes('text-4xl font-bold text-center')
        ui.label('Sustainable Development Goals - The Age of Consequences').classes(
            'text-xl text-center text-gray-600'
        )
        
        ui.separator()
        
        # GM Section
        with ui.card().classes('w-full p-6'):
            ui.label('Game Master').classes('text-2xl font-bold mb-4')
            
            with ui.row().classes('w-full gap-4'):
                ui.button('Start New Game', 
                         on_click=lambda: ui.navigate.to('/gm/new'),
                         icon='add_circle').classes('flex-1')
                
                ui.button('Continue Existing Game', 
                         on_click=lambda: ui.navigate.to('/gm/continue'),
                         icon='play_arrow').classes('flex-1')
        
        # Player Section
        with ui.card().classes('w-full p-6'):
            ui.label('Player').classes('text-2xl font-bold mb-4')
            
            with ui.row().classes('w-full gap-4'):
                ui.button('Join New Game', 
                         on_click=lambda: ui.navigate.to('/player/join'),
                         icon='person_add').classes('flex-1')
                
                ui.button('Resume Game', 
                         on_click=lambda: ui.navigate.to('/player/resume'),
                         icon='login').classes('flex-1')


# ============================================================================
# GM - START NEW GAME
# ============================================================================

@ui.page('/gm/new')
def gm_new_game():
    """GM starts a new game - requires start code 'oscar'"""
    
    with ui.column().classes('w-full max-w-2xl mx-auto p-8 gap-6'):
        ui.label('Start New Game').classes('text-3xl font-bold')
        
        with ui.card().classes('w-full p-6'):
            start_code_input = ui.input('Start Code', 
                                       placeholder='Enter start code',
                                       password=True,
                                       password_toggle_button=True).classes('w-full')
            
            username_input = ui.input('Your Username (Game Master)', 
                                     placeholder='Enter your username').classes('w-full')
            
            error_label = ui.label('').classes('text-red-500')
            
            def create_game():
                start_code = start_code_input.value.strip()
                username = username_input.value.strip()
                
                # Validate start code first
                if start_code != db.START_CODE:
                    error_label.text = 'Invalid start code'
                    return
                
                if not username:
                    error_label.text = 'Please enter a username'
                    return
                
                # Check if username is available globally (including as GM)
                player_info = db.get_player_info(username)
                if player_info:
                    error_label.text = 'Username already taken. Please choose another.'
                    return
                
                # Check if username is already a GM
                with db.get_db() as conn:
                    cursor = conn.execute("SELECT game_id FROM games WHERE gm_username = ?", (username,))
                    if cursor.fetchone():
                        error_label.text = 'Username already used as Game Master. Please choose another.'
                        return
                
                # Create game (always 3 rounds)
                game_id = db.create_game(username)
                
                # Update session
                session_state['username'] = username
                session_state['game_id'] = game_id
                session_state['role'] = 'gm'
                
                ui.navigate.to(f'/gm/config')
            
            ui.button('Create Game', on_click=create_game, icon='create').classes('w-full')
        
        ui.button('← Back', on_click=lambda: ui.navigate.to('/'), 
                 icon='arrow_back').classes('mt-4')


# ============================================================================
# GM - CONTINUE EXISTING GAME
# ============================================================================

@ui.page('/gm/continue')
def gm_continue_game():
    """GM continues existing game - only asks for username"""
    
    with ui.column().classes('w-full max-w-2xl mx-auto p-8 gap-6'):
        ui.label('Continue Existing Game').classes('text-3xl font-bold')
        
        with ui.card().classes('w-full p-6'):
            ui.label('Enter your Game Master username to restore your game').classes('mb-4')
            
            username_input = ui.input('Your Username', 
                                     placeholder='Enter your GM username').classes('w-full')
            
            error_label = ui.label('').classes('text-red-500')
            game_info_label = ui.label('').classes('text-blue-600')
            
            def check_and_continue():
                username = username_input.value.strip()
                
                if not username:
                    error_label.text = 'Please enter your username'
                    game_info_label.text = ''
                    return
                
                # Look up game by GM username (GMs are in games table, not players table)
                with db.get_db() as conn:
                    cursor = conn.execute(
                        """
                        SELECT game_id, num_rounds, current_round, state
                        FROM games 
                        WHERE gm_username = ?
                        ORDER BY created_at DESC
                        LIMIT 1
                        """,
                        (username,)
                    )
                    game = cursor.fetchone()
                
                if not game:
                    error_label.text = 'No game found for this username'
                    game_info_label.text = ''
                    return
                
                # Found game - show info
                error_label.text = ''
                game_id = game['game_id']
                game_info_label.text = f"Game found: {game_id} | Rounds: {game['num_rounds']} | Current: {game['current_round']} | State: {game['state']}"
                
                # Update session
                session_state['username'] = username
                session_state['game_id'] = game_id
                session_state['role'] = 'gm'
                
                # Navigate to GM config/dashboard
                ui.navigate.to('/gm/config')
            
            ui.button('Continue Game', on_click=check_and_continue, 
                     icon='play_arrow').classes('w-full mt-4')
        
        ui.button('← Back', on_click=lambda: ui.navigate.to('/'), 
                 icon='arrow_back').classes('mt-4')


# ============================================================================
# GM - CONFIGURATION PAGE
# ============================================================================

@ui.page('/gm/config')
def gm_config_page():
    """GM configuration page - shows game info and AI region selection"""
    
    if not session_state.get('game_id') or session_state.get('role') != 'gm':
        ui.navigate.to('/')
        return
    
    game_id = session_state['game_id']
    username = session_state['username']
    
    # Get game info
    game_info = db.get_game_info(game_id)
    current_round = game_info['current_round']
    
    with ui.column().classes('w-full max-w-4xl mx-auto p-8 gap-6'):
        ui.label(f'Game Master: {username}').classes('text-3xl font-bold')
        ui.label(f'Game ID: {game_id}').classes('text-2xl text-blue-600 font-mono')
        ui.label('Share this Game ID with your players!').classes('text-lg text-gray-600')
        
        ui.separator()
        
        # Show current round
        with ui.card().classes('w-full p-6 bg-blue-50'):
            ui.label(f'Current Round: {current_round} / {game_info["num_rounds"]}').classes('text-xl font-bold')
            ui.label(f'Game State: {game_info["state"]}').classes('text-lg text-gray-700')
        
        # Show AI regions
        ai_regions = db.get_ai_regions(game_id)
        if ai_regions:
            with ui.card().classes('w-full p-6 bg-blue-50'):
                ui.label('AI-Controlled Regions').classes('text-2xl font-bold mb-4')
                for region_tag in sorted(ai_regions):
                    display_name = db.REGION_TAGS[region_tag]
                    ui.label(f'🤖 {display_name}').classes('text-base text-blue-700')
        
        # Show available positions (excluding AI regions)
        with ui.card().classes('w-full p-6'):
            ui.label('Available Positions for Human Players').classes('text-2xl font-bold mb-4')
            
            available = db.get_available_regions_ministries(game_id)
            
            if not available:
                ui.label('All human positions filled!').classes('text-green-600 font-bold')
            else:
                for region_tag, ministries in sorted(available.items()):
                    display_name = db.REGION_TAGS[region_tag]
                    ui.label(f'{display_name}: {", ".join(ministries)}').classes('text-base')
        
        # AI Region Selection (only if round 0)
        if current_round == 0:
            with ui.card().classes('w-full p-6'):
                ui.label('AI Region Control').classes('text-2xl font-bold mb-4')
                ui.label('Select which regions will be controlled by AI:').classes('text-gray-600 mb-4')
                
                # Get current AI regions
                current_ai_regions = db.get_ai_regions(game_id)
                
                # Create checkboxes for each region
                ai_checkboxes = {}
                
                with ui.column().classes('w-full gap-2'):
                    for region_tag, display_name in sorted(db.REGION_TAGS.items(), key=lambda x: x[1]):
                        ai_checkboxes[region_tag] = ui.checkbox(
                            display_name,
                            value=(region_tag in current_ai_regions)
                        ).classes('text-base')
                
                status_label = ui.label('').classes('mt-4')
                
                # def save_ai_regions_OLD():
                #     # Get selected AI regions
                #     selected_ai = [tag for tag, checkbox in ai_checkboxes.items() if checkbox.value]
                    
                #     # Validate: at least 1 region must be human-playable
                #     if len(selected_ai) >= 10:
                #         status_label.text = '❌ Error: At least 1 region must be playable by humans!'
                #         status_label.classes('text-red-600')
                #         return
                    
                #     # Save to database
                #     db.set_ai_regions(game_id, selected_ai)
                    
                #     # Generate AI players and their Round 1 policy decisions
                #     print(f"🤖 Creating AI players...")
                #     for ai_region_tag in selected_ai:
                #         for ministry in db.MINISTRIES:
                #             # Add AI player to database
                #             ai_username = f"AI_{ai_region_tag}_{ministry}"
                #             db.add_player(game_id, ai_username, ai_region_tag, ministry, is_ai=True)
                    
                #     # COMMIT AI PLAYERS BEFORE GENERATING POLICIES
                #     with db.get_db() as conn:
                #         conn.commit()
                #     print(f"✅ AI players committed to database")
                    
                #     # Generate AI policy decisions for Round 1
                #     print(f"🤖 Generating AI policies for game {game_id}, round 1...")
                #     db.generate_ai_policy_decisions(game_id, round_num=1)
                    
                #     # Advance to Round 1
                #     with db.get_db() as conn:
                #         conn.execute(
                #             """
                #             UPDATE games
                #             SET current_round = 1, state = 'playing', updated_at = CURRENT_TIMESTAMP
                #             WHERE game_id = ?
                #             """,
                #             (game_id,)
                #         )
                #         conn.commit()
                    
                #     # Navigate to GM game board
                #     ui.navigate.to('/gm/board') 
                    
                    
                def save_ai_regions():
                    try:
                        # Get selected AI regions
                        selected_ai = [tag for tag, checkbox in ai_checkboxes.items() if checkbox.value]
                        
                        # Validate: at least 1 region must be human-playable
                        if len(selected_ai) >= 10:
                            status_label.text = '❌ Error: At least 1 region must be playable by humans!'
                            status_label.classes('text-red-600')
                            return
                        
                        # Save to database
                        db.set_ai_regions(game_id, selected_ai)                        

                        # USE ONE CONNECTION FOR EVERYTHING
                        with db.get_db() as conn:
                            # First, delete any existing AI players for this game
                            conn.execute(
                                "DELETE FROM players WHERE game_id = ? AND is_ai = 1",
                                (game_id,)
                            )
                            print(f"🧹 Cleared existing AI players for game {game_id}")
                            
                            # Generate AI players directly here
                            print(f"🤖 Creating AI players...")
                            print(f"   Selected AI regions: {selected_ai}")
                            print(f"   Ministries: {db.MINISTRIES}")
                            
                            player_count = 0
                            created_usernames = set()  # Track what we've created
                            
                            for ai_region_tag in selected_ai:
                                for ministry in db.MINISTRIES:
                                    # Make username globally unique by including game_id
                                    ai_username = f"AI_{game_id}_{ai_region_tag}_{ministry}"
                                    
                                    # Check for duplicate before inserting
                                    if ai_username in created_usernames:
                                        print(f"⚠️  DUPLICATE DETECTED: {ai_username}")
                                        continue
                                    
                                    print(f"   Creating: {ai_username}")
                                    created_usernames.add(ai_username)
                                    
                                    conn.execute(
                                        """
                                        INSERT INTO players (username, game_id, region_tag, ministry, is_ai)
                                        VALUES (?, ?, ?, ?, ?)
                                        """,
                                        (ai_username, game_id, ai_region_tag, ministry, True)
                                    )
                                    player_count += 1                                    
                            
                            conn.commit()
                            print(f"✅ Created {player_count} AI players")

                            # Verify immediately on same connection
                            cursor = conn.execute(
                                "SELECT COUNT(*) as count FROM players WHERE game_id = ? AND is_ai = 1",
                                (game_id,)
                            )
                            count = cursor.fetchone()['count']
                            print(f"🔍 Verified: {count} AI players in database")
                        
                        # Now generate policies (in its own connection, after commit)
                        print(f"🤖 Generating AI policies...")
                        db.generate_ai_policy_decisions(game_id, round_num=1)
                        db.generate_ai_policy_decisions(game_id, round_num=2)
                        db.generate_ai_policy_decisions(game_id, round_num=3)
                                                                        
                        # Advance to Round 1
                        with db.get_db() as conn:
                            conn.execute(
                                """
                                UPDATE games
                                SET current_round = 1, state = 'playing', updated_at = CURRENT_TIMESTAMP
                                WHERE game_id = ?
                                """,
                                (game_id,)
                            )
                            conn.commit()
                        
                        print(f"✅ Game advanced to round 1")
                        status_label.text = '✅ AI regions saved and Round 1 started!'
                        status_label.classes('text-green-600')
                        ui.navigate.to(f'/gm/board?game_id={game_id}')
                        
                    except Exception as e:
                        print(f"❌ ERROR: {e}")
                        import traceback
                        traceback.print_exc()
                        status_label.text = f'❌ Error: {str(e)}'
                        status_label.classes('text-red-600')                    
                                    
                
                ui.button('Save AI Region Selection & Start Game', 
                         on_click=save_ai_regions, 
                         icon='play_arrow').classes('w-full mt-4')
        else:
            # Game already started
            ui.button('Go to Game Board', 
                     on_click=lambda: ui.navigate.to('/gm/board'),
                     icon='dashboard').classes('w-full mt-4')
        
        ui.button('← Back to Home', on_click=lambda: ui.navigate.to('/'), 
                 icon='home').classes('mt-4')


# ============================================================================
# GM - GAME BOARD
# ============================================================================

@ui.page('/gm/board')
def gm_game_board():
    """GM game board - monitor player submissions and manage rounds"""
    
    if not session_state.get('game_id') or session_state.get('role') != 'gm':
        ui.navigate.to('/')
        return
    
    game_id = session_state['game_id']
    username = session_state['username']
    
    # Get game info
    game_info = db.get_game_info(game_id)
    current_round = game_info['current_round']
    num_rounds = game_info['num_rounds']
    accept_submissions = game_info['accept_submissions']
    game_state = game_info['state']
    
    with ui.column().classes('w-full max-w-6xl mx-auto p-8 gap-6'):
        # Header
        with ui.row().classes('w-full items-center justify-between'):
            with ui.column():
                ui.label(f'Game Organizer Board').classes('text-3xl font-bold')
                ui.label(f'Game: {game_id} | Round: {current_round}/{num_rounds}').classes('text-xl text-gray-600 font-mono')
            
            ui.button('Player IDs', 
                     on_click=lambda: show_player_ids_dialog(game_id),
                     icon='people').classes('text-lg')
        
        ui.separator()
        
        # Instructions card
        with ui.card().classes('w-full p-6 bg-amber-50'):
            ui.label('Setup Instructions').classes('text-2xl font-bold mb-4 text-gray-900')
            
            if current_round == 1:
                ui.label('All roles have been set up now. Tell your players to log in now, using the Game ID shown above.').classes('text-base mb-2 text-gray-800')
                ui.label('Ask them to look at the state of their region for last 35 years and discuss their decisions to improve the lives of their people.').classes('text-base mb-4 text-gray-800')
            else:
                ui.label(f'Round {current_round} is in progress.').classes('text-base mb-2 text-gray-800')
                ui.label('Monitor player submissions below. When all have submitted, you can advance to the next round.').classes('text-base mb-4 text-gray-800')
            
            ui.label('Check repeatedly if all your players have submitted by clicking the Check Submissions button.').classes('text-base mb-2 text-gray-800')
            ui.label('Once all submitted, you will see a button to accept submissions and advance to the next round.').classes('text-base text-gray-800')
        
        # Check submissions section
        status_container = ui.column().classes('w-full gap-4')
        
        def check_submissions():
            # Clear previous content
            status_container.clear()
            
            with status_container:
                # Get submission status
                status = db.get_submission_status(game_id, current_round)
                
                with ui.card().classes('w-full p-6'):
                    ui.label(f'Submission Status for Round {current_round}').classes('text-2xl font-bold mb-4')
                    
                    # Progress bar
                    total = status['total_human']
                    submitted = status['submitted']
                    
                    if total > 0:
                        progress_pct = (submitted / total) * 100
                        ui.label(f'{submitted} of {total} players have submitted ({progress_pct:.0f}%)').classes('text-lg mb-2')
                        
                        # Linear progress
                        ui.linear_progress(value=submitted / total).classes('w-full')
                    
                    # Show waiting players
                    if status['waiting']:
                        ui.label('').classes('mt-4')  # Spacer
                        ui.label('Still waiting for:').classes('text-lg font-bold mb-2')
                        
                        for region_tag, ministry, player_username in status['waiting']:
                            display_region = db.REGION_TAGS[region_tag]
                            ui.label(f'  • {display_region} - {ministry} ({player_username})').classes('text-base ml-4')
                    
                    # If all submitted, show accept button
                    if status['all_submitted']:
                        ui.label('').classes('mt-4')  # Spacer
                        with ui.card().classes('w-full p-4 bg-green-50'):
                            ui.label('✓ All players have submitted!').classes('text-xl font-bold text-green-700 mb-2')
                            
                            if current_round < num_rounds:
                                ui.label(f'Ready to advance to Round {current_round + 1}?').classes('text-base text-green-600 mb-4')
                                
                                def advance_to_next_round():
                                    # Advance round
                                    db.advance_round(game_id)
                                    # Refresh page
                                    ui.navigate.to('/gm/board')
                                
                                ui.button(f'Advance to Round {current_round + 1}', 
                                         on_click=advance_to_next_round,
                                         icon='arrow_forward').classes('w-full')
                            else:
                                ui.label('This is the final round. Game complete!').classes('text-lg text-green-700 font-bold')
                                ui.button('View Final Results', 
                                         on_click=lambda: ui.notify('Results view coming in Phase 3!'),
                                         icon='assessment').classes('w-full mt-2')
        
        with ui.row().classes('w-full gap-4'):
            ui.button('Check Submissions', 
                     on_click=check_submissions,
                     icon='refresh').classes('text-lg')
        
        status_container
        
        ui.button('← Back to Config', on_click=lambda: ui.navigate.to('/gm/config'), 
                 icon='arrow_back').classes('mt-4')


def show_player_ids_dialog(game_id: str):
    """Show dialog with list of all logged-in players"""
    with ui.dialog() as dialog, ui.card().classes('w-full max-w-2xl'):
        ui.label('Player IDs').classes('text-2xl font-bold mb-4')
        
        # Get all human players
        with db.get_db() as conn:
            cursor = conn.execute(
                """
                SELECT region_tag, ministry, username
                FROM players
                WHERE game_id = ? AND is_ai = 0
                ORDER BY region_tag, ministry
                """,
                (game_id,)
            )
            players = cursor.fetchall()
        
        if not players:
            ui.label('No players have joined yet.').classes('text-gray-600')
        else:
            # Create table
            with ui.card().classes('w-full p-4'):
                columns = [
                    {'name': 'region', 'label': 'Region', 'field': 'region', 'align': 'left'},
                    {'name': 'ministry', 'label': 'Ministry', 'field': 'ministry', 'align': 'left'},
                    {'name': 'username', 'label': 'Login ID', 'field': 'username', 'align': 'left'},
                ]
                
                rows = []
                for player in players:
                    rows.append({
                        'region': db.REGION_TAGS[player['region_tag']],
                        'ministry': player['ministry'],
                        'username': player['username']
                    })
                
                ui.table(columns=columns, rows=rows, row_key='username').classes('w-full')
        
        ui.button('Close', on_click=dialog.close).classes('w-full mt-4')
    
    dialog.open()


# ============================================================================
# PLAYER - JOIN GAME
# ============================================================================

@ui.page('/player/join')
def player_join_game():
    """Player joins a game - needs username and game_id"""
    
    with ui.column().classes('w-full max-w-2xl mx-auto p-8 gap-6'):
        ui.label('Join Game').classes('text-3xl font-bold')
        
        with ui.card().classes('w-full p-6'):
            username_input = ui.input('Your Username', 
                                     placeholder='Choose a unique username').classes('w-full')
            
            game_id_input = ui.input('Game ID', 
                                    placeholder='Enter the game ID from your Game Master').classes('w-full')
            
            error_label = ui.label('').classes('text-red-500')
            
            def verify_and_continue():
                username = username_input.value.strip()
                game_id = game_id_input.value.strip()
                
                if not username:
                    error_label.text = 'Please enter a username'
                    return
                
                if not game_id:
                    error_label.text = 'Please enter a Game ID'
                    return
                
                # Check if username is available
                player_info = db.get_player_info(username)
                if player_info:
                    error_label.text = 'Username already taken. Please choose another.'
                    return
                
                # Check if game exists
                with db.get_db() as conn:
                    cursor = conn.execute("SELECT game_id FROM games WHERE game_id = ?", (game_id,))
                    if not cursor.fetchone():
                        error_label.text = 'Game ID not found'
                        return
                
                # Update session
                session_state['username'] = username
                session_state['game_id'] = game_id
                session_state['role'] = 'player'
                
                # Navigate to region selection
                ui.navigate.to('/player/select_region')
            
            ui.button('Continue', on_click=verify_and_continue, 
                     icon='arrow_forward').classes('w-full')
        
        ui.button('← Back', on_click=lambda: ui.navigate.to('/'), 
                 icon='arrow_back').classes('mt-4')


# ============================================================================
# PLAYER - RESUME GAME
# ============================================================================

@ui.page('/player/resume')
def player_resume_game():
    """Player resumes existing game"""
    
    with ui.column().classes('w-full max-w-2xl mx-auto p-8 gap-6'):
        ui.label('Resume Game').classes('text-3xl font-bold')
        
        with ui.card().classes('w-full p-6'):
            username_input = ui.input('Your Username', 
                                     placeholder='Enter your username').classes('w-full')
            
            error_label = ui.label('').classes('text-red-500')
            info_label = ui.label('').classes('text-blue-600')
            
            def check_and_resume():
                username = username_input.value.strip()
                
                if not username:
                    error_label.text = 'Please enter your username'
                    return
                
                # Look up player
                player = db.get_player_info(username)
                
                if not player:
                    error_label.text = 'Username not found'
                    info_label.text = ''
                    return
                
                # Found player - show info using region_tag
                error_label.text = ''
                region_tag = player['region_tag']
                display_region = db.REGION_TAGS.get(region_tag, region_tag)
                info_label.text = f"Game: {player['game_id']} | Region: {display_region} | Ministry: {player['ministry']}"
                
                # Update session
                session_state['username'] = username
                session_state['game_id'] = player['game_id']
                session_state['role'] = 'player'
                session_state['region_tag'] = region_tag
                session_state['ministry'] = player['ministry']
                
                # Navigate to player dashboard
                ui.navigate.to('/player/dashboard')
            
            ui.button('Resume', on_click=check_and_resume, 
                     icon='login').classes('w-full mt-4')
        
        ui.button('← Back', on_click=lambda: ui.navigate.to('/'), 
                 icon='arrow_back').classes('mt-4')


# ============================================================================
# PLAYER - SELECT REGION
# ============================================================================

@ui.page('/player/select_region')
def player_select_region():
    """Player selects region and ministry"""
    
    if not session_state.get('game_id') or session_state.get('role') != 'player':
        ui.navigate.to('/')
        return
    
    game_id = session_state['game_id']
    username = session_state['username']
    
    with ui.column().classes('w-full max-w-4xl mx-auto p-8 gap-6'):
        ui.label(f'Welcome, {username}!').classes('text-3xl font-bold')
        ui.label(f'Game: {game_id}').classes('text-xl text-blue-600 font-mono')
        
        ui.separator()
        
        ui.label('Select Your Region and Ministry').classes('text-2xl font-bold mb-4')
        ui.label('Choose an available position to begin playing:').classes('text-gray-600 mb-4')
        
        available = db.get_available_regions_ministries(game_id)
        
        if not available:
            ui.label('No positions available - game is full!').classes('text-red-600 font-bold')
            ui.button('← Back', on_click=lambda: ui.navigate.to('/'), 
                     icon='arrow_back').classes('mt-4')
            return
        
        error_label = ui.label('').classes('text-red-500')
        
        # Create selection UI using region_tag
        with ui.column().classes('w-full gap-4'):
            for region_tag, ministries in sorted(available.items()):
                display_name = db.REGION_TAGS[region_tag]
                
                with ui.card().classes('w-full p-4'):
                    ui.label(display_name).classes('text-xl font-bold mb-2')
                    
                    with ui.row().classes('w-full gap-2 flex-wrap'):
                        for ministry in ministries:
                            def make_select_handler(r_tag, m):
                                def handler():
                                    # Try to add player using region_tag
                                    success = db.add_player(game_id, username, r_tag, m, is_ai=False)
                                    
                                    if success:
                                        session_state['region_tag'] = r_tag
                                        session_state['ministry'] = m
                                        ui.navigate.to('/player/dashboard')
                                    else:
                                        error_label.text = 'Position already taken or error occurred. Please try another.'
                                
                                return handler
                            
                            ui.button(ministry, 
                                     on_click=make_select_handler(region_tag, ministry),
                                     icon='check_circle').classes('flex-grow')
        
        ui.button('← Back', on_click=lambda: ui.navigate.to('/'), 
                 icon='arrow_back').classes('mt-4')


# ============================================================================
# PLAYER - DASHBOARD
# ============================================================================

@ui.page('/player/dashboard')
def player_dashboard():
    """Player dashboard - policy management and plot variables"""
    
    if not session_state.get('game_id') or session_state.get('role') != 'player':
        ui.navigate.to('/')
        return
    
    username = session_state['username']
    game_id = session_state['game_id']
    region_tag = session_state['region_tag']
    ministry = session_state['ministry']
    display_region = db.REGION_TAGS.get(region_tag, region_tag)
    
    # Get game info
    game_info = db.get_game_info(game_id)
    current_round = game_info['current_round']
    
    # If round is 0, we're in setup - go to round 1
    if current_round == 0:
        current_round = 1
    
    with ui.column().classes('w-full max-w-6xl mx-auto p-8 gap-6'):
        # Header
        with ui.row().classes('w-full items-center justify-between'):
            with ui.column().classes('gap-1'):
                ui.label(f'{username}').classes('text-3xl font-bold')
                ui.label(f'{display_region} - {ministry}').classes('text-2xl text-blue-600')
                ui.label(f'Game: {game_id} | Round: {current_round}').classes('text-lg text-gray-600 font-mono')
        
        ui.separator()
        
        # Status message
        status_label = ui.label('').classes('text-lg font-bold')
        
        # Get policies for this ministry
        policies = db.get_policies_for_ministry(ministry)
        
        # Get existing decisions for this round
        existing_decisions = dict(db.get_policy_decisions(game_id, current_round, region_tag, ministry))
        
        # Policy Sliders Section
        with ui.card().classes('w-full p-6'):
            ui.label('Policy Decisions').classes('text-2xl font-bold mb-4')
            ui.label(f'Set your policy positions for Round {current_round}').classes('text-gray-600 mb-4')
            
            if not policies:
                ui.label(f'No policies assigned to {ministry}').classes('text-red-600')
            else:
                # Create sliders for each policy
                slider_refs = {}
                
                for policy in policies:
                    pol_id = policy['pol_id']
                    pol_tag = policy['pol_tag']
                    pol_name = policy['pol_name']
                    pol_min = policy['pol_min']
                    pol_max = policy['pol_max']
                    explanation = policy.get('explanation', 'No explanation available')
                    
                    # Get existing value or use middle as default
                    current_value = existing_decisions.get(pol_id, (pol_min + pol_max) / 2)
                    
                    with ui.card().classes('w-full p-4 mb-3 bg-gray-50').tight():
                        # Policy name and explanation
                        with ui.expansion(pol_name, icon='info').classes('w-full'):
                            ui.label(explanation).classes('text-sm text-gray-700')
                        
                        # Slider with value display
                        with ui.row().classes('w-full items-center gap-4'):
                            ui.label(f'{pol_min}').classes('text-sm text-gray-600 w-12 text-right')
                            
                            # Create slider
                            slider = ui.slider(
                                min=pol_min, 
                                max=pol_max, 
                                value=current_value,
                                step=(pol_max - pol_min) / 100  # 100 steps
                            ).classes('flex-grow')
                            
                            # Value display
                            value_label = ui.label(f'{current_value:.2f}').classes('text-lg font-mono w-20')
                            
                            ui.label(f'{pol_max}').classes('text-sm text-gray-600 w-12')
                            
                            # Store reference
                            slider_refs[pol_id] = (slider, value_label, pol_tag)
                            
                            # Update value label on change
                            def make_update_handler(val_label):
                                def handler(e):
                                    val_label.text = f'{e.value:.2f}'
                                return handler
                            
                            slider.on('update:model-value', make_update_handler(value_label))
                            
                            # Save on mouse release
                            def make_save_handler(pol_id_val, s, tag):
                                def handler():
                                    value = s.value
                                    db.save_policy_decision(
                                        game_id, current_round, region_tag, 
                                        ministry, pol_id_val, value
                                    )
                                    status_label.text = f'✓ Saved {tag}: {value:.2f}'
                                    status_label.classes('text-green-600')
                                return handler
                            
                            slider.on('mouseup', make_save_handler(pol_id, slider, pol_tag))
                            slider.on('touchend', make_save_handler(pol_id, slider, pol_tag))
                
                # Submit button
                def submit_policies():
                    # Mark as submitted
                    db.mark_player_submission(game_id, username, current_round)
                    status_label.text = '✓ Policies submitted! You can still adjust them until the GM advances the round.'
                    status_label.classes('text-green-600')
                
                ui.button('Submit Policies for This Round', 
                         on_click=submit_policies,
                         icon='send').classes('w-full mt-4')
        
        # Plot Variables Section
        with ui.card().classes('w-full p-6'):
            ui.label('Your Indicators').classes('text-2xl font-bold mb-4')
            
            # Get plot variables for this ministry
            plot_vars = db.get_plot_variables_for_ministry(ministry)
            
            if not plot_vars:
                ui.label('No indicators assigned to your ministry').classes('text-gray-600')
            else:
                ui.label(f'Monitoring {len(plot_vars)} indicators for {ministry}').classes('text-gray-600 mb-4')
                
                # Display as cards for now (graphs come later with simulation)
                with ui.column().classes('w-full gap-3'):
                    for pv in plot_vars:
                        with ui.card().classes('w-full p-4'):
                            with ui.row().classes('w-full items-center justify-between'):
                                with ui.column().classes('gap-1'):
                                    ui.label(pv['pv_indicator']).classes('text-lg font-bold')
                                    ui.label(pv['pv_subtitle']).classes('text-sm text-gray-600')
                                
                                # Show green/red thresholds if available
                                if pv['pv_green'] is not None and pv['pv_red'] is not None:
                                    with ui.column().classes('gap-1 text-right'):
                                        ui.label(f"🟢 Target: {pv['pv_green']}").classes('text-sm')
                                        ui.label(f"🔴 Threshold: {pv['pv_red']}").classes('text-sm')
                            
                            # Placeholder for graph
                            ui.label('[Graph will appear here after simulation]').classes('text-sm text-gray-400 italic mt-2')
        
        ui.button('← Back to Home', on_click=lambda: ui.navigate.to('/'), 
                 icon='home').classes('mt-4')


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ in {"__main__", "__mp_main__"}:
    # Initialize database
#    db.init_database()
#    db.load_policies_data()
#    db.load_plot_variables_data()
    
    # Run NiceGUI app
    ui.run(
        title='SDG3 Simulation Game',
        favicon='🌍',
        dark=None,  # Auto-detect dark mode
        reload=True,
        show=True,
        port=8888  # Use port 8888 to avoid Windows permission issues
    )
