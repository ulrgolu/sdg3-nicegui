"""
SDG3 Educational Simulation Game - NiceGUI Implementation
Main application entry point
"""
from nicegui import ui, app
import database as db

# Global state for current user session
session_state = {
    'username': None,
    'game_id': None,
    'role': None,  # 'gm' or 'player'
    'region': None,
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
    """GM starts a new game"""
    
    with ui.column().classes('w-full max-w-2xl mx-auto p-8 gap-6'):
        ui.label('Start New Game').classes('text-3xl font-bold')
        
        with ui.card().classes('w-full p-6'):
            username_input = ui.input('Your Username (Game Master)', 
                                     placeholder='Enter your username').classes('w-full')
            
            rounds_input = ui.number('Number of Rounds', value=3, min=1, max=10,
                                    step=1).classes('w-full')
            
            error_label = ui.label('').classes('text-red-500')
            
            def create_game():
                username = username_input.value.strip()
                
                if not username:
                    error_label.text = 'Please enter a username'
                    return
                
                # Check if username is available globally
                if not db.check_username_available(username):
                    error_label.text = 'Username already taken. Please choose another.'
                    return
                
                num_rounds = int(rounds_input.value)
                
                # Create game
                game_id = db.create_game(username, num_rounds)
                
                # Add GM as a player (special role)
                db.add_player(game_id, username, 'GM', 'GameMaster', is_ai=False)
                
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
                
                # Look up game by GM username
                game = db.get_game_by_gm_username(username)
                
                if not game:
                    error_label.text = 'No game found for this username'
                    game_info_label.text = ''
                    return
                
                # Found game - show info and allow continue
                error_label.text = ''
                game_id = game['game_id']
                game_info_label.text = f"Game found: {game_id} | Rounds: {game['num_rounds']} | Current: {game['current_round']}"
                
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
    """GM configuration page - shows game info and available regions/ministries"""
    
    if not session_state.get('game_id') or session_state.get('role') != 'gm':
        ui.navigate.to('/')
        return
    
    game_id = session_state['game_id']
    username = session_state['username']
    
    with ui.column().classes('w-full max-w-4xl mx-auto p-8 gap-6'):
        ui.label(f'Game Master: {username}').classes('text-3xl font-bold')
        ui.label(f'Game ID: {game_id}').classes('text-2xl text-blue-600 font-mono')
        
        ui.separator()
        
        # Show available regions and ministries
        with ui.card().classes('w-full p-6'):
            ui.label('Available Regions & Ministries').classes('text-2xl font-bold mb-4')
            ui.label('Players can join any of these positions:').classes('text-gray-600 mb-4')
            
            available = db.get_available_regions_ministries(game_id)
            
            if not available:
                ui.label('All positions filled!').classes('text-green-600 font-bold')
            else:
                with ui.column().classes('w-full gap-2'):
                    for region, ministries in sorted(available.items()):
                        # Use display name from REGIONS dict
                        display_name = db.REGIONS[region]
                        with ui.expansion(f'{display_name} ({len(ministries)} available)', 
                                        icon='public').classes('w-full'):
                            with ui.column().classes('pl-4 gap-1'):
                                for ministry in ministries:
                                    ui.label(f'• {ministry}').classes('text-gray-700')
        
        # Game controls
        with ui.card().classes('w-full p-6'):
            ui.label('Game Controls').classes('text-2xl font-bold mb-4')
            
            with ui.row().classes('w-full gap-4'):
                ui.button('Manage Players', icon='people').classes('flex-1')
                ui.button('Start Round', icon='play_circle').classes('flex-1')
                ui.button('View Results', icon='assessment').classes('flex-1')
        
        ui.button('← Back to Home', on_click=lambda: ui.navigate.to('/'), 
                 icon='home').classes('mt-4')


# ============================================================================
# PLAYER - JOIN NEW GAME
# ============================================================================

@ui.page('/player/join')
def player_join_game():
    """Player joins a new game"""
    
    with ui.column().classes('w-full max-w-2xl mx-auto p-8 gap-6'):
        ui.label('Join Game').classes('text-3xl font-bold')
        
        with ui.card().classes('w-full p-6'):
            game_id_input = ui.input('Game ID', 
                                    placeholder='e.g., ADJ-932').classes('w-full')
            
            username_input = ui.input('Your Username', 
                                     placeholder='Choose a unique username').classes('w-full')
            
            error_label = ui.label('').classes('text-red-500')
            
            def verify_and_continue():
                game_id = game_id_input.value.strip().upper()
                username = username_input.value.strip()
                
                if not game_id or not username:
                    error_label.text = 'Please enter both Game ID and Username'
                    return
                
                # Check if username is available globally
                if not db.check_username_available(username):
                    error_label.text = 'Username already taken. Please choose another.'
                    return
                
                # Check if game exists
                with db.get_db() as conn:
                    cursor = conn.execute("SELECT game_id FROM games WHERE game_id = ?", 
                                        (game_id,))
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
                
                # Found player - show info
                error_label.text = ''
                info_label.text = f"Game: {player['game_id']} | Region: {player['region']} | Ministry: {player['ministry']}"
                
                # Update session
                session_state['username'] = username
                session_state['game_id'] = player['game_id']
                session_state['role'] = 'player'
                session_state['region'] = player['region']
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
        
        # Create selection UI
        selected_region = {'value': None}
        selected_ministry = {'value': None}
        
        with ui.column().classes('w-full gap-4'):
            for region, ministries in sorted(available.items()):
                display_name = db.REGIONS[region]
                
                with ui.card().classes('w-full p-4'):
                    ui.label(display_name).classes('text-xl font-bold mb-2')
                    
                    with ui.row().classes('w-full gap-2 flex-wrap'):
                        for ministry in ministries:
                            def make_select_handler(r, m):
                                def handler():
                                    # Try to add player
                                    success = db.add_player(game_id, username, r, m, is_ai=False)
                                    
                                    if success:
                                        session_state['region'] = r
                                        session_state['ministry'] = m
                                        ui.navigate.to('/player/dashboard')
                                    else:
                                        error_label.text = 'Position already taken or error occurred. Please try another.'
                                
                                return handler
                            
                            ui.button(ministry, 
                                     on_click=make_select_handler(region, ministry),
                                     icon='check_circle').classes('flex-grow')
        
        ui.button('← Back', on_click=lambda: ui.navigate.to('/'), 
                 icon='arrow_back').classes('mt-4')


# ============================================================================
# PLAYER - DASHBOARD
# ============================================================================

@ui.page('/player/dashboard')
def player_dashboard():
    """Player dashboard - policy management"""
    
    if not session_state.get('game_id') or session_state.get('role') != 'player':
        ui.navigate.to('/')
        return
    
    username = session_state['username']
    game_id = session_state['game_id']
    region = session_state['region']
    ministry = session_state['ministry']
    display_region = db.REGIONS.get(region, region)
    
    with ui.column().classes('w-full max-w-4xl mx-auto p-8 gap-6'):
        ui.label(f'{username}').classes('text-3xl font-bold')
        ui.label(f'{display_region} - {ministry}').classes('text-2xl text-blue-600')
        ui.label(f'Game: {game_id}').classes('text-lg text-gray-600 font-mono')
        
        ui.separator()
        
        # Placeholder for policy management
        with ui.card().classes('w-full p-6'):
            ui.label('Policy Management').classes('text-2xl font-bold mb-4')
            ui.label('Policy sliders will appear here...').classes('text-gray-600')
        
        ui.button('← Back to Home', on_click=lambda: ui.navigate.to('/'), 
                 icon='home').classes('mt-4')


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ in {"__main__", "__mp_main__"}:
    # Initialize database
    db.init_database()
    
    # Run NiceGUI app
    ui.run(
        title='SDG3 Simulation Game',
        favicon='🌍',
        dark=None,  # Auto-detect dark mode
        reload=True,
        show=True,
        port=8888  # Use port 8888 to avoid Windows permission issues
    )
