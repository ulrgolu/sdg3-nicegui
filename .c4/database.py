"""
Database schema and operations for SDG3 game
Phase 1 Update: Correct regions, policies, plot variables, AI support
"""
import sqlite3
from contextlib import contextmanager
from typing import Optional, Dict, List, Tuple
import random
import string

DB_PATH = "sdg3_game.db"

# Start code for game creation
START_CODE = "oscar"

# Corrected region list with tags (internal keys)
REGION_TAGS = {
    "us": "USA",
    "af": "Africa South of Sahara",
    "cn": "China",
    "me": "Middle East and North Africa",
    "sa": "South Asia",
    "la": "Latin America",
    "pa": "Pacific Rim",
    "ec": "East Europe and Central Asia",
    "eu": "Europe",
    "se": "Southeast Asia"
}

REGION_ABBR = ['us', 'af', 'cn', 'me', 'sa', 'la', 'pa', 'ec', 'eu', 'se']

MINISTRIES = ["Poverty", "Inequality", "Empowerment", "Food", "Energy", "Future"]


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
        # Games table - always 3 rounds, added accept_submissions
        conn.execute("""
            CREATE TABLE IF NOT EXISTS games (
                game_id TEXT PRIMARY KEY,
                gm_username TEXT NOT NULL,
                num_rounds INTEGER DEFAULT 3,
                current_round INTEGER DEFAULT 0,
                state TEXT DEFAULT 'setup',
                accept_submissions BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # AI regions table - track which regions are AI-controlled
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ai_regions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT NOT NULL,
                region_tag TEXT NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games(game_id),
                UNIQUE(game_id, region_tag)
            )
        """)
        
        # Players table - username UNIQUE, changed to region_tag, added submission tracking
        conn.execute("""
            CREATE TABLE IF NOT EXISTS players (
                player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                game_id TEXT NOT NULL,
                region_tag TEXT NOT NULL,
                ministry TEXT NOT NULL,
                is_ai BOOLEAN DEFAULT 0,
                has_submitted_round1 BOOLEAN DEFAULT 0,
                has_submitted_round2 BOOLEAN DEFAULT 0,
                has_submitted_round3 BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES games(game_id)
            )
        """)
        
        # Create index on username for fast lookups
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_players_username 
            ON players(username)
        """)
        
        # Policies table - loaded from JSON with full structure
        conn.execute("""
            CREATE TABLE IF NOT EXISTS policies (
                pol_id INTEGER PRIMARY KEY,
                pol_tag TEXT NOT NULL UNIQUE,
                pol_name TEXT NOT NULL,
                pol_min REAL NOT NULL,
                pol_max REAL NOT NULL,
                pol_ministry TEXT NOT NULL,
                pol_ministry_tag TEXT NOT NULL
            )
        """)
        
        # Policy explanations table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS policy_explanations (
                pol_tag TEXT PRIMARY KEY,
                explanation TEXT NOT NULL,
                FOREIGN KEY (pol_tag) REFERENCES policies(pol_tag)
            )
        """)
        
        # Policy decisions table - changed to region_tag
        conn.execute("""
            CREATE TABLE IF NOT EXISTS policy_decisions (
                decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT NOT NULL,
                round INTEGER NOT NULL,
                region_tag TEXT NOT NULL,
                ministry TEXT NOT NULL,
                pol_id INTEGER NOT NULL,
                value REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES games(game_id),
                FOREIGN KEY (pol_id) REFERENCES policies(pol_id),
                UNIQUE(game_id, round, region_tag, ministry, pol_id)
            )
        """)
        
        # Plot variables table - loaded from JSON with full structure
        conn.execute("""
            CREATE TABLE IF NOT EXISTS plot_variables (
                pv_id INTEGER PRIMARY KEY,
                pv_sdg_nbr INTEGER,
                pv_indicator TEXT NOT NULL,
                pv_vensim_name TEXT NOT NULL,
                pv_green REAL,
                pv_red REAL,
                pv_lowerbetter INTEGER,
                pv_ymin REAL,
                pv_ymax REAL,
                pv_subtitle TEXT,
                pv_ministry TEXT NOT NULL,
                pv_pct INTEGER,
                pv_sdg TEXT
            )
        """)
        
        # Plot results table - changed to region_tag
        conn.execute("""
            CREATE TABLE IF NOT EXISTS plot_results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT NOT NULL,
                round INTEGER NOT NULL,
                region_tag TEXT NOT NULL,
                pv_id INTEGER NOT NULL,
                value REAL NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games(game_id),
                FOREIGN KEY (pv_id) REFERENCES plot_variables(pv_id),
                UNIQUE(game_id, round, region_tag, pv_id)
            )
        """)
        
        conn.commit()


def load_policies_data():
    """Load 32 policies and explanations from JSON data"""
    policies_json = [{"pol_id":1,"pol_tag":"ExPS","pol_name":"Expand policy space","pol_min":0.0,"pol_max":100.0,"pol_ministry":"Poverty","pol_ministry_tag":"pov"},{"pol_id":2,"pol_tag":"LPB","pol_name":"Lending from public bodies (LPB)","pol_min":0.0,"pol_max":30.0,"pol_ministry":"Poverty","pol_ministry_tag":"pov"},{"pol_id":3,"pol_tag":"LPBsplit","pol_name":"LPB: Split the use of funds from public lenders","pol_min":0.0,"pol_max":100.0,"pol_ministry":"Poverty","pol_ministry_tag":"pov"},{"pol_id":4,"pol_tag":"LPBgrant","pol_name":"LPB: funds given as loans or grants","pol_min":0.0,"pol_max":100.0,"pol_ministry":"Poverty","pol_ministry_tag":"pov"},{"pol_id":5,"pol_tag":"FMPLDD","pol_name":"Fraction of credit with private lenders NOT drawn down per y","pol_min":0.0,"pol_max":90.0,"pol_ministry":"Poverty","pol_ministry_tag":"pov"},{"pol_id":6,"pol_tag":"TOW","pol_name":"Taxing Owners Wealth","pol_min":0.0,"pol_max":80.0,"pol_ministry":"Poverty","pol_ministry_tag":"pov"},{"pol_id":7,"pol_tag":"FPGDC","pol_name":"Cancel debt from public lenders","pol_min":0.0,"pol_max":100.0,"pol_ministry":"Poverty","pol_ministry_tag":"pov"},{"pol_id":8,"pol_tag":"Lfrac","pol_name":"Leakage fraction reduction","pol_min":0.0,"pol_max":100.0,"pol_ministry":"Poverty","pol_ministry_tag":"pov"},{"pol_id":9,"pol_tag":"SSGDR","pol_name":"Stretch repayment","pol_min":1.0,"pol_max":5.0,"pol_ministry":"Poverty","pol_ministry_tag":"pov"},{"pol_id":10,"pol_tag":"XtaxFrac","pol_name":"Extra taxes paid by the super rich","pol_min":50.0,"pol_max":90.0,"pol_ministry":"Inequality","pol_ministry_tag":"ineq"},{"pol_id":11,"pol_tag":"StrUP","pol_name":"Strengthen Unions","pol_min":0.0,"pol_max":3.0,"pol_ministry":"Inequality","pol_ministry_tag":"ineq"},{"pol_id":12,"pol_tag":"Wreaction","pol_name":"Worker reaction","pol_min":0.0,"pol_max":3.0,"pol_ministry":"Inequality","pol_ministry_tag":"ineq"},{"pol_id":13,"pol_tag":"XtaxCom","pol_name":"Introduce a Universal basic dividend","pol_min":0.0,"pol_max":5.0,"pol_ministry":"Inequality","pol_ministry_tag":"ineq"},{"pol_id":14,"pol_tag":"ICTR","pol_name":"Increase consumption tax rate","pol_min":0.0,"pol_max":10.0,"pol_ministry":"Inequality","pol_ministry_tag":"ineq"},{"pol_id":15,"pol_tag":"IOITR","pol_name":"Increase owner income tax rate","pol_min":0.0,"pol_max":10.0,"pol_ministry":"Inequality","pol_ministry_tag":"ineq"},{"pol_id":16,"pol_tag":"IWITR","pol_name":"Increase worker income tax rate","pol_min":0.0,"pol_max":10.0,"pol_ministry":"Inequality","pol_ministry_tag":"ineq"},{"pol_id":17,"pol_tag":"Ctax","pol_name":"Introduce a Carbon tax","pol_min":0.0,"pol_max":100.0,"pol_ministry":"Inequality","pol_ministry_tag":"ineq"},{"pol_id":18,"pol_tag":"SGRPI","pol_name":"Shift govt spending to investment","pol_min":0.0,"pol_max":50.0,"pol_ministry":"Inequality","pol_ministry_tag":"ineq"},{"pol_id":19,"pol_tag":"FEHC","pol_name":"Education to all","pol_min":0.0,"pol_max":10.0,"pol_ministry":"Empowerment","pol_ministry_tag":"emp"},{"pol_id":20,"pol_tag":"XtaxRateEmp","pol_name":"Female leadership","pol_min":0.0,"pol_max":5.0,"pol_ministry":"Empowerment","pol_ministry_tag":"emp"},{"pol_id":21,"pol_tag":"SGMP","pol_name":"Pensions to all","pol_min":0.0,"pol_max":10.0,"pol_ministry":"Empowerment","pol_ministry_tag":"emp"},{"pol_id":22,"pol_tag":"FWRP","pol_name":"Food waste reduction","pol_min":0.0,"pol_max":90.0,"pol_ministry":"Food","pol_ministry_tag":"food"},{"pol_id":23,"pol_tag":"FLWR","pol_name":"Regenerative agriculture","pol_min":0.0,"pol_max":95.0,"pol_ministry":"Food","pol_ministry_tag":"food"},{"pol_id":24,"pol_tag":"RMDR","pol_name":"Change diets","pol_min":0.0,"pol_max":95.0,"pol_ministry":"Food","pol_ministry_tag":"food"},{"pol_id":25,"pol_tag":"RIPLGF","pol_name":"Reduce food imports","pol_min":0.0,"pol_max":50.0,"pol_ministry":"Food","pol_ministry_tag":"food"},{"pol_id":26,"pol_tag":"FC","pol_name":"Max forest cutting","pol_min":0.0,"pol_max":90.0,"pol_ministry":"Food","pol_ministry_tag":"food"},{"pol_id":27,"pol_tag":"REFOREST","pol_name":"Reforestation","pol_min":0.0,"pol_max":3.0,"pol_ministry":"Food","pol_ministry_tag":"food"},{"pol_id":28,"pol_tag":"FTPEE","pol_name":"Energy system efficiency","pol_min":1.0,"pol_max":2.5,"pol_ministry":"Energy","pol_ministry_tag":"ener"},{"pol_id":29,"pol_tag":"NEP","pol_name":"Electrify everything","pol_min":0.0,"pol_max":95.0,"pol_ministry":"Energy","pol_ministry_tag":"ener"},{"pol_id":30,"pol_tag":"ISPV","pol_name":"Invest in Renewables","pol_min":50.0,"pol_max":95.0,"pol_ministry":"Energy","pol_ministry_tag":"ener"},{"pol_id":31,"pol_tag":"CCS","pol_name":"CCS: Carbon capture and storage at source","pol_min":0.0,"pol_max":80.0,"pol_ministry":"Energy","pol_ministry_tag":"ener"},{"pol_id":32,"pol_tag":"DAC","pol_name":"Direct air capture","pol_min":0.0,"pol_max":1.5,"pol_ministry":"Energy","pol_ministry_tag":"ener"}]
    
    explanations_json = [{"pol_tag":"CCS","explanation":"Percent of fossil use to be equipped with carbon capture and storage (CCS) at source.  This means that you still emit CO2 but it does not get to the atmosphere, where it causes warming,  because you capture it and store it underground."},{"pol_tag":"TOW","explanation":"0 means no wealth tax,  80 means 80% of accrued owners wealth is taxed away each year,  50: half of it"},{"pol_tag":"FPGDC","explanation":"Cancels a percentage of Govt debt outstanding to public lenders. 0 means nothing is cancelled,  100 all is cancelled,  50 half is cancelled --- in the policy start year"},{"pol_tag":"RMDR","explanation":"Change in diet, esp. a reduction in red meat consumption. 0 means red meat is consumed as before, 50 means 50% is replaced with lab meat, 100 means 100% is replaced with lab meat  i.e. no more red meat is 'produced' by intensive livestock farming  aka factory farming."},{"pol_tag":"REFOREST","explanation":"Policy to reforest land, i.e. plant new trees. 0 means no reforestation, 1 means you increase the forest area by 1‰ / yr (that is 1 promille), 3 = you increase the forest area by 3‰ / yr"},{"pol_tag":"FTPEE","explanation":"Annual percentage increase in energy efficiency; 1% per yr is the historical value over the last 40 years. Beware of the power of compound interest!"},{"pol_tag":"LPBsplit","explanation":"0 means all LBP funding goes to consumption (eg child support,  subsidies for food or energy,  etc.)  100 means all goes to public investment like infrastructure,  security,  etc. NOTE This only has an effect if LPB is NOT set to zero"},{"pol_tag":"ExPS","explanation":"Cancels a percentage of Govt debt outstanding to private lenders --- in the policy start year"},{"pol_tag":"FMPLDD","explanation":"Given your credit worthiness  you have an amount you you can borrow from private lenders. Here you choose the fraction of credit you actually draw down each year."},{"pol_tag":"StrUP","explanation":"In any economy, the national income is shared between owners and workers. This policy changes the share going to workers. 1 multiplies the share with 1%,  2 with 2%,  etc "},{"pol_tag":"Wreaction","explanation":"In any economy, there is a power struggle between workers and owners about the share of national income each gets. This policy strenghtens the workers negotiation position. 1 by 1%,  2 by 2%,  etc. "},{"pol_tag":"SGMP","explanation":"To fight poverty in old age  you can introduce pensions for all. The size of the pension is expressed as the percent of the GDP you want to invest. 0 means you invest nothing and leave things as they are. 5 means you invest 5 % of GDP; 10 = 10 % of GDP  money is transferred to workers and paid for by owners"},{"pol_tag":"FWRP","explanation":"Here you decide how much the percentage of 'normal' waste, which is 30%, is to be reduced. I.e. 100 means  no more waste! 50 means waste is reduced by 50 %,  0 means waste continues as always"},{"pol_tag":"ICTR","explanation":"This policy is an increase in the consumption tax (aka sales tax, value added tax (VAT),  etc. 0 means no increase, 10 means an increase by 10 percentage points, 5 by 5 percentage points; the money raised goes to general govt revenue."},{"pol_tag":"XtaxCom","explanation":"A universal basic dividend is created when a state taxes common goods  like fishing rights, mining rights, the right to use airwaves  etc. This policy sets this tax as a percent of GDP  i.e.  0 = 0 % of GDP  i.e. nothing; 5 = 5 % of GDP; 3 = 3 % of GDP  money is transferred to general govt tax revenue."},{"pol_tag":"Lfrac","explanation":"Leakage describes the use of money for illicit purposes: Corruption,  bribery,  etc. The normal leakage is 20%  - so a value of 0 reduction means that those 20% do in fact disappear - a 50 % reduction means 10% disappear and 100% reduction means nothing disappears and everyone in your region is totally honest!"},{"pol_tag":"IOITR","explanation":"This is an increase in the income tax paid by owners. 0 means no increase,  10 means an increase by 10 percentage points, 5 by 5 percentage points; the money raised goes to general govt revenue."},{"pol_tag":"IWITR","explanation":"This is an increase in the income tax paid by workers. 0 means no increase, 10 means an increase by 10 percentage points, 5 by 5 percentage points; the money raised goes to general govt revenue."},{"pol_tag":"SGRPI","explanation":"Governments choose how to use their spending: primarily for consumption (eg child support, subsidies for food or energy, etc.) or for public investment (education, health care, infrastructure  etc.) This policy shifts spending from consumption to investment. 0 means no shift, 10= 10% of consumption shifted to investment, 25 = 25 % of consumption shifted to investment, etc"},{"pol_tag":"FEHC","explanation":"The higher the level of education  esp. of women,  in a society,  the lower the birth rate. Thus  education for all lowers the birth rate. By how much? You make an educated guess: 0 means no effect, 10 means a 10% reduction, 5 means a 5% reduction, etc."},{"pol_tag":"XtaxRateEmp","explanation":"To support women to reach equality costs some money, esp. to close the pay gender gap. How much do you want to spend  as a pct of GDP? 0 means you spend nothing and leave things as they are; 5 means you spend= 5 % of GDP; 3 = 3 % of GDP. Money is transferred to general govt tax revenue"},{"pol_tag":"FLWR","explanation":"Here you decide the percentage of your cropland that is worked regeneratively (low or no tillage,  low or no fertilizers and pesticides  etc.)  50 means 50 % cropland worked is regeneratively, 100 = 100 % of cropland is worked regeneratively, etc. 0 leaves things as they are."},{"pol_tag":"RIPLGF","explanation":"Reduction in food imports. 0 means no reduction,  10=10% reduction, 50=50% reduction This policy reduces food available from elsewhere but strenghtens local producers"},{"pol_tag":"FC","explanation":"Policy to limit forest cutting. 0 means no limitation on cutting,  10=10% reduction in the maximum amount that can be cut,  50=50% reduction in max cut, etc. all the way to 90 % reduction which is practically a ban on cutting"},{"pol_tag":"NEP","explanation":"Percent of fossil fuel (oil, gas, and coal) *not* used for electricity generation (mobility,  heating,  industrial use  etc.) that you want to electrify."},{"pol_tag":"Ctax","explanation":"This is the carbon emission tax. 0 means no carbon tax,  25 = 25 $/ton of CO2 emitted  etc."},{"pol_tag":"DAC","explanation":"Capturing CO2 that is already in the atmosphere and storing it underground   - in GtCO2/yr (Giga tons -  giga is 10^9); In 2020  regional emissions were roughly: USA 5,  Africa  south of Sahara 1,  China 12,  the rest all between 2 and 3 GtCO2/yr. You can capture more than you emit."},{"pol_tag":"XtaxFrac","explanation":"The percentage of *extra* taxes paid by owners (owners pay 50% of extra taxes even under TLTL)  I.e. 90 means owners pay 90 % of extra taxes,  70 means owners pay 70 % of extra taxes, etc. Extra taxes are those for empowerment and to give women equal pay."},{"pol_tag":"LPBgrant","explanation":"0 means all LPB funding is given as loans that must be repaid,  100 means all is given as grants that carry no interest and must not be repaid. NOTE This only has an effect if LPB is NOT set to zero"},{"pol_tag":"LPB","explanation":"The percentage of your GDP made available as financing from public bodies (WorldBank,  IMF,  off-balance funding) LPB= Lending from Public Bodies"},{"pol_tag":"SSGDR","explanation":"You can stretch repayment into the future  so that each year you pay less,  but you do have to pay for a longer time. 1 means no stretching - 2 doubles repayment time  - 3 trebles repayment time - and so on"},{"pol_tag":"ISPV","explanation":"Percent of electricity generation from renewable sources (40% is what we managed to achieve in the past)"}]
    
    with get_db() as conn:
        # Check if already loaded
        cursor = conn.execute("SELECT COUNT(*) as count FROM policies")
        if cursor.fetchone()['count'] > 0:
            return  # Already loaded
        
        # Insert policies
        for policy in policies_json:
            conn.execute("""
                INSERT INTO policies (pol_id, pol_tag, pol_name, pol_min, pol_max, pol_ministry, pol_ministry_tag)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (policy['pol_id'], policy['pol_tag'], policy['pol_name'], policy['pol_min'], 
                  policy['pol_max'], policy['pol_ministry'], policy['pol_ministry_tag']))
        
        # Insert explanations
        for exp in explanations_json:
            conn.execute("""
                INSERT INTO policy_explanations (pol_tag, explanation)
                VALUES (?, ?)
            """, (exp['pol_tag'], exp['explanation']))
        
        conn.commit()


def load_plot_variables_data():
    """Load 48 plot variables from JSON data"""
    plot_vars_json = [{"pv_id":1,"pv_sdg_nbr":1,"pv_indicator":"Poverty rate","pv_vensim_name":"Fraction of population below existential minimum","pv_green":5.0,"pv_red":13.0,"pv_lowerbetter":1,"pv_ymin":0.0,"pv_ymax":65.0,"pv_subtitle":"Fraction of population living below $6.85 per day (%)","pv_ministry":"Poverty","pv_pct":100,"pv_sdg":"No poverty"},{"pv_id":2,"pv_sdg_nbr":2,"pv_indicator":"Undernourished fraction","pv_vensim_name":"Fraction of population undernourished","pv_green":3.0,"pv_red":7.0,"pv_lowerbetter":1,"pv_ymin":0.0,"pv_ymax":30.0,"pv_subtitle":"Fraction of population undernourished (%)","pv_ministry":"Poverty","pv_pct":100,"pv_sdg":"No hunger"},{"pv_id":3,"pv_sdg_nbr":2,"pv_indicator":"Regenerative agriculture","pv_vensim_name":"Regenerative cropland fraction","pv_green":70.0,"pv_red":30.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":100.0,"pv_subtitle":"Proportion of agricultural area worked regeneratively (%)","pv_ministry":"Food","pv_pct":100,"pv_sdg":"No hunger"},{"pv_id":4,"pv_sdg_nbr":3,"pv_indicator":"Average wellbeing index","pv_vensim_name":"Average wellbeing index","pv_green":1.8,"pv_red":1.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":3.0,"pv_subtitle":"Average wellbeing index","pv_ministry":"Future","pv_pct":1,"pv_sdg":"Good health and wellbeing"},{"pv_id":5,"pv_sdg_nbr":3,"pv_indicator":"Life expectancy","pv_vensim_name":"Life expectancy at birth","pv_green":80.0,"pv_red":60.0,"pv_lowerbetter":0,"pv_ymin":30.0,"pv_ymax":110.0,"pv_subtitle":"Life expectancy (years)","pv_ministry":"Inequality","pv_pct":1,"pv_sdg":"Good health and wellbeing"},{"pv_id":6,"pv_sdg_nbr":4,"pv_indicator":"Years in school","pv_vensim_name":"Years of schooling","pv_green":15.0,"pv_red":13.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":18.0,"pv_subtitle":"Years in school","pv_ministry":"Empowerment","pv_pct":1,"pv_sdg":"Quality education"},{"pv_id":7,"pv_sdg_nbr":5,"pv_indicator":"Female labor income share","pv_vensim_name":"GenderEquality","pv_green":48.0,"pv_red":40.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":60.0,"pv_subtitle":"Female pre-tax labor income share (%)","pv_ministry":"Empowerment","pv_pct":100,"pv_sdg":"Gender equality"},{"pv_id":8,"pv_sdg_nbr":6,"pv_indicator":"Safe water access","pv_vensim_name":"Safe water","pv_green":95.0,"pv_red":80.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":100.0,"pv_subtitle":"Fraction of population with access to safe water (%)","pv_ministry":"Poverty","pv_pct":100,"pv_sdg":"Access to clean water"},{"pv_id":9,"pv_sdg_nbr":6,"pv_indicator":"Safe sanitation access","pv_vensim_name":"Safe sanitation","pv_green":90.0,"pv_red":65.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":100.0,"pv_subtitle":"Fraction of population with access to safe sanitation (%)","pv_ministry":"Poverty","pv_pct":100,"pv_sdg":"Access to clean sanitation"},{"pv_id":10,"pv_sdg_nbr":7,"pv_indicator":"Electricity access","pv_vensim_name":"Access to electricity","pv_green":98.0,"pv_red":90.0,"pv_lowerbetter":0,"pv_ymin":10.0,"pv_ymax":100.0,"pv_subtitle":"Fraction of population with access to electricity (%)","pv_ministry":"Empowerment","pv_pct":100,"pv_sdg":"Affordable and clean energy"},{"pv_id":11,"pv_sdg_nbr":7,"pv_indicator":"Renewable energy share","pv_vensim_name":"Renewable energy share in the total final energy consumption","pv_green":80.0,"pv_red":50.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":100.0,"pv_subtitle":"Wind and PV energy share in total energy consumption (%)","pv_ministry":"Energy","pv_pct":100,"pv_sdg":"Affordable and clean energy"},{"pv_id":12,"pv_sdg_nbr":7,"pv_indicator":"Energy intensity","pv_vensim_name":"Total energy use per GDP","pv_green":0.1,"pv_red":0.5,"pv_lowerbetter":1,"pv_ymin":0.0,"pv_ymax":2.0,"pv_subtitle":"Energy intensity in terms of primary energy and GDP (kWh/$)","pv_ministry":"Energy","pv_pct":1,"pv_sdg":"Affordable and clean energy"},{"pv_id":13,"pv_sdg_nbr":8,"pv_indicator":"Worker disposable income","pv_vensim_name":"Disposable income pp post tax pre loan impact","pv_green":25.0,"pv_red":15.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":50.0,"pv_subtitle":"Worker disposable income (1000 $/person-year)","pv_ministry":"Inequality","pv_pct":1,"pv_sdg":"Decent work and economic growth"},{"pv_id":16,"pv_sdg_nbr":8,"pv_indicator":"GDP growth rate","pv_vensim_name":"Smoothed RoC in GDPpp","pv_green":4.0,"pv_red":2.0,"pv_lowerbetter":0,"pv_ymin":-5.0,"pv_ymax":10.0,"pv_subtitle":"Growth rate of GDP per capita (%/yr)","pv_ministry":"Poverty","pv_pct":100,"pv_sdg":"Decent work and economic growth"},{"pv_id":17,"pv_sdg_nbr":11,"pv_indicator":"Emissions per person","pv_vensim_name":"Energy footprint pp","pv_green":0.5,"pv_red":2.0,"pv_lowerbetter":1,"pv_ymin":0.0,"pv_ymax":15.0,"pv_subtitle":"Emissions per person (tCO2/p/y)","pv_ministry":"Energy","pv_pct":1,"pv_sdg":"Sustainable cities and communities"},{"pv_id":19,"pv_sdg_nbr":13,"pv_indicator":"Temperature rise","pv_vensim_name":"Temp surface anomaly compared to 1850 degC","pv_green":1.0,"pv_red":1.5,"pv_lowerbetter":1,"pv_ymin":0.0,"pv_ymax":3.0,"pv_subtitle":"Temperature rise (deg C above 1850)","pv_ministry":"Future","pv_pct":1,"pv_sdg":"Climate action"},{"pv_id":20,"pv_sdg_nbr":13,"pv_indicator":"Total GHG emissions","pv_vensim_name":"Total CO2 emissions","pv_green":1.0,"pv_red":5.0,"pv_lowerbetter":1,"pv_ymin":0.0,"pv_ymax":15.0,"pv_subtitle":"Total greenhouse gas emissions per year (GtCO2/yr)","pv_ministry":"Energy","pv_pct":1,"pv_sdg":"Climate action"},{"pv_id":21,"pv_sdg_nbr":14,"pv_indicator":"Ocean pH","pv_vensim_name":"pH in surface","pv_green":8.15,"pv_red":8.1,"pv_lowerbetter":0,"pv_ymin":8.0,"pv_ymax":8.2,"pv_subtitle":"Ocean surface pH","pv_ministry":"Future","pv_pct":1,"pv_sdg":"Life below water"},{"pv_id":23,"pv_sdg_nbr":16,"pv_indicator":"Public services","pv_vensim_name":"Public services pp","pv_green":15.0,"pv_red":8.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":25.0,"pv_subtitle":"Public services per person (1000 $/person-yr)","pv_ministry":"Inequality","pv_pct":1,"pv_sdg":"Peace justice and strong institutions"},{"pv_id":24,"pv_sdg_nbr":17,"pv_indicator":"Trust in institutions","pv_vensim_name":"Social trust","pv_green":1.5,"pv_red":1.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":3.0,"pv_subtitle":"Trust in institutions (1980=1)","pv_ministry":"Empowerment","pv_pct":1,"pv_sdg":"Partnership for the Goals"},{"pv_id":25,"pv_sdg_nbr":17,"pv_indicator":"Govt revenue share","pv_vensim_name":"Total government revenue as a proportion of GDP","pv_green":45.0,"pv_red":30.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":60.0,"pv_subtitle":"Total government revenue as a proportion of GDP (%)","pv_ministry":"Inequality","pv_pct":100,"pv_sdg":"Partnership for the Goals"},{"pv_id":26,"pv_sdg_nbr":0,"pv_indicator":"Population","pv_vensim_name":"Population","pv_green":1000.0,"pv_red":1500.0,"pv_lowerbetter":1,"pv_ymin":0.0,"pv_ymax":2000.0,"pv_subtitle":"Population (million people)","pv_ministry":"Future","pv_pct":1,"pv_sdg":"Total population"},{"pv_id":27,"pv_sdg_nbr":10,"pv_indicator":"Labour share of GDP","pv_vensim_name":"Labour share of GDP","pv_green":60.0,"pv_red":50.0,"pv_lowerbetter":0,"pv_ymin":40.0,"pv_ymax":70.0,"pv_subtitle":"Labour share of GDP (%)","pv_ministry":"Inequality","pv_pct":100,"pv_sdg":"Reduced inequalities"},{"pv_id":29,"pv_sdg_nbr":18,"pv_indicator":"Number of SDGs met","pv_vensim_name":"All SDG Scores","pv_green":16.0,"pv_red":14.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":17.0,"pv_subtitle":"Number of SDGs met - 17 can be met","pv_ministry":"Future","pv_pct":1,"pv_sdg":"SDG scores"},{"pv_id":30,"pv_sdg_nbr":9,"pv_indicator":"Investment share","pv_vensim_name":"Local private and govt investment share","pv_green":40.0,"pv_red":30.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":60.0,"pv_subtitle":"Private and govt investment share (% of GDP)","pv_ministry":"Poverty","pv_pct":100,"pv_sdg":"Industry innovation and infrastructure"},{"pv_id":31,"pv_sdg_nbr":11,"pv_indicator":"City area change","pv_vensim_name":"RoC Populated land","pv_green":0.0,"pv_red":1.0,"pv_lowerbetter":1,"pv_ymin":-3.0,"pv_ymax":5.0,"pv_subtitle":"Annual rate of change in city area (%)","pv_ministry":"Food","pv_pct":100,"pv_sdg":"Sustainable cities and communities"},{"pv_id":32,"pv_sdg_nbr":12,"pv_indicator":"Nitrogen use","pv_vensim_name":"Nitrogen use per ha","pv_green":10.0,"pv_red":20.0,"pv_lowerbetter":1,"pv_ymin":0.0,"pv_ymax":300.0,"pv_subtitle":"Nitrogen use (kg/ha-year)","pv_ministry":"Food","pv_pct":100,"pv_sdg":"Responsible consumption and production"},{"pv_id":33,"pv_sdg_nbr":15,"pv_indicator":"Forest area change","pv_vensim_name":"RoC in Forest land","pv_green":1.5,"pv_red":0.0,"pv_lowerbetter":0,"pv_ymin":-3.0,"pv_ymax":4.0,"pv_subtitle":"Annual change in forest area (%)","pv_ministry":"Food","pv_pct":100,"pv_sdg":"Life on land"},{"pv_id":34,"pv_sdg_nbr":9,"pv_indicator":"Donor investment share","pv_vensim_name":"LPB investment share","pv_green":30.0,"pv_red":25.0,"pv_lowerbetter":0,"pv_ymin":0.0,"pv_ymax":50.0,"pv_subtitle":"Donor and off balance-sheet investment share (% of GDP)","pv_ministry":"Inequality","pv_pct":100,"pv_sdg":"Industry innovation and infrastructure"},{"pv_id":35,"pv_sdg_nbr":0,"pv_indicator":"Planetary boundaries breached","pv_vensim_name":"Planetary risk","pv_green":0.5,"pv_red":2.0,"pv_lowerbetter":1,"pv_ymin":0.0,"pv_ymax":5.0,"pv_subtitle":"Planetary boundaries breached","pv_ministry":"Future","pv_pct":1,"pv_sdg":"Planetary boundaries"},{"pv_id":38,"pv_sdg_nbr":19,"pv_indicator":"Social trust","pv_vensim_name":"Social trust","pv_green":1.0,"pv_red":0.7,"pv_lowerbetter":0,"pv_ymin":0.2,"pv_ymax":2.0,"pv_subtitle":"Social trust (index)","pv_ministry":"Future","pv_pct":1,"pv_sdg":"Social trust"},{"pv_id":39,"pv_sdg_nbr":20,"pv_indicator":"Social tension","pv_vensim_name":"Smoothed Social tension index with trust effect","pv_green":1.0,"pv_red":1.2,"pv_lowerbetter":1,"pv_ymin":0.2,"pv_ymax":2.0,"pv_subtitle":"Smoothed Social tension index with trust effect (index)","pv_ministry":"Future","pv_pct":1,"pv_sdg":"Social tension"},{"pv_id":40,"pv_sdg_nbr":99,"pv_indicator":"Global social trust","pv_vensim_name":"Global_social_trust","pv_green":None,"pv_red":None,"pv_lowerbetter":None,"pv_ymin":None,"pv_ymax":None,"pv_subtitle":"(index)","pv_ministry":"GM","pv_pct":None,"pv_sdg":""},{"pv_id":41,"pv_sdg_nbr":99,"pv_indicator":"Global energy intensity","pv_vensim_name":"Energy_intensity_in_terms_of_GDP","pv_green":None,"pv_red":None,"pv_lowerbetter":None,"pv_ymin":None,"pv_ymax":None,"pv_subtitle":"Energy intensity in terms of primary energy and GDP (kWh/$)","pv_ministry":"GM","pv_pct":None,"pv_sdg":""},{"pv_id":42,"pv_sdg_nbr":99,"pv_indicator":"Global energy footprint","pv_vensim_name":"Global_average_Energy_footprint_pp","pv_green":None,"pv_red":None,"pv_lowerbetter":None,"pv_ymin":None,"pv_ymax":None,"pv_subtitle":"Global average energy footprint per person (toe/person)","pv_ministry":"GM","pv_pct":None,"pv_sdg":""},{"pv_id":43,"pv_sdg_nbr":99,"pv_indicator":"Perceived warming","pv_vensim_name":"Perceived_global_warming","pv_green":None,"pv_red":None,"pv_lowerbetter":None,"pv_ymin":None,"pv_ymax":None,"pv_subtitle":"Perceived global warming (degC over 1850)","pv_ministry":"GM","pv_pct":None,"pv_sdg":""},{"pv_id":44,"pv_sdg_nbr":99,"pv_indicator":"Global wellbeing","pv_vensim_name":"Global_avg_wellbeing","pv_green":None,"pv_red":None,"pv_lowerbetter":None,"pv_ymin":None,"pv_ymax":None,"pv_subtitle":"(index)","pv_ministry":"GM","pv_pct":None,"pv_sdg":""},{"pv_id":45,"pv_sdg_nbr":99,"pv_indicator":"Global inequality","pv_vensim_name":"Global_inequality","pv_green":None,"pv_red":None,"pv_lowerbetter":None,"pv_ymin":None,"pv_ymax":None,"pv_subtitle":"(index)","pv_ministry":"GM","pv_pct":None,"pv_sdg":""},{"pv_id":46,"pv_sdg_nbr":99,"pv_indicator":"Global tension","pv_vensim_name":"Global_social_tension","pv_green":None,"pv_red":None,"pv_lowerbetter":None,"pv_ymin":None,"pv_ymax":None,"pv_subtitle":"(index)","pv_ministry":"GM","pv_pct":None,"pv_sdg":""},{"pv_id":47,"pv_sdg_nbr":99,"pv_indicator":"Population below 15k","pv_vensim_name":"Pop_below_15_kpy","pv_green":None,"pv_red":None,"pv_lowerbetter":None,"pv_ymin":None,"pv_ymax":None,"pv_subtitle":"Population below 15000 $ per year (Million people)","pv_ministry":"GM","pv_pct":None,"pv_sdg":""},{"pv_id":48,"pv_sdg_nbr":99,"pv_indicator":"Global population","pv_vensim_name":"Global_Population","pv_green":None,"pv_red":None,"pv_lowerbetter":None,"pv_ymin":None,"pv_ymax":None,"pv_subtitle":"Global Population (Million people)","pv_ministry":"GM","pv_pct":None,"pv_sdg":""}]
    
    with get_db() as conn:
        # Check if already loaded
        cursor = conn.execute("SELECT COUNT(*) as count FROM plot_variables")
        if cursor.fetchone()['count'] > 0:
            return  # Already loaded
        
        # Insert plot variables
        for pv in plot_vars_json:
            conn.execute("""
                INSERT INTO plot_variables 
                (pv_id, pv_sdg_nbr, pv_indicator, pv_vensim_name, pv_green, pv_red, 
                 pv_lowerbetter, pv_ymin, pv_ymax, pv_subtitle, pv_ministry, pv_pct, pv_sdg)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (pv['pv_id'], pv['pv_sdg_nbr'], pv['pv_indicator'], pv['pv_vensim_name'],
                  pv['pv_green'], pv['pv_red'], pv['pv_lowerbetter'], pv['pv_ymin'],
                  pv['pv_ymax'], pv['pv_subtitle'], pv['pv_ministry'], pv['pv_pct'], pv['pv_sdg']))
        
        conn.commit()


def check_username_available(username: str) -> bool:
    """Check if username is available globally"""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT username FROM players WHERE username = ?",
            (username,)
        )
        return cursor.fetchone() is None


def get_game_by_gm_username(username: str) -> Optional[Dict]:
    """Get game information by GM username"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT game_id, gm_username, num_rounds, current_round, state, 
                   accept_submissions, created_at, updated_at
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


def set_ai_regions(game_id: str, region_tags: List[str]):
    """Set which regions are controlled by AI"""
    with get_db() as conn:
        # Clear existing AI regions for this game
        conn.execute("DELETE FROM ai_regions WHERE game_id = ?", (game_id,))
        
        # Insert new AI regions
        for tag in region_tags:
            conn.execute(
                "INSERT INTO ai_regions (game_id, region_tag) VALUES (?, ?)",
                (game_id, tag)
            )
        
        conn.commit()


def get_ai_regions(game_id: str) -> List[str]:
    """Get list of AI-controlled region tags for a game"""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT region_tag FROM ai_regions WHERE game_id = ?",
            (game_id,)
        )
        return [row['region_tag'] for row in cursor.fetchall()]


def get_available_regions_ministries(game_id: str) -> Dict[str, List[str]]:
    """
    Get available (unclaimed) ministries for each region (excluding AI regions)
    Returns dict: {region_tag: [ministry1, ministry2, ...]}
    """
    with get_db() as conn:
        # Get AI regions
        ai_regions = get_ai_regions(game_id)
        
        # Get all claimed positions by human players
        cursor = conn.execute(
            """
            SELECT region_tag, ministry 
            FROM players 
            WHERE game_id = ? AND is_ai = 0
            """,
            (game_id,)
        )
        claimed = {(row['region_tag'], row['ministry']) for row in cursor.fetchall()}
        
        # Build available positions (excluding AI regions)
        available = {}
        for region_tag in REGION_TAGS.keys():
            if region_tag in ai_regions:
                continue  # Skip AI regions
            
            available_ministries = [
                ministry for ministry in MINISTRIES 
                if (region_tag, ministry) not in claimed
            ]
            if available_ministries:  # Only include regions with available spots
                available[region_tag] = available_ministries
        
        return available


def create_game(gm_username: str) -> str:
    """Create a new game (always 3 rounds) and return game_id"""
    game_id = create_unique_game_id()
    
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO games (game_id, gm_username, num_rounds, current_round, state)
            VALUES (?, ?, 3, 0, 'setup')
            """,
            (game_id, gm_username)
        )
        conn.commit()
    
    return game_id


def add_player(game_id: str, username: str, region_tag: str, ministry: str, is_ai: bool = False) -> bool:
    """Add a player to the game"""
    with get_db() as conn:
        try:
            conn.execute(
                """
                INSERT INTO players (username, game_id, region_tag, ministry, is_ai)
                VALUES (?, ?, ?, ?, ?)
                """,
                (username, game_id, region_tag, ministry, is_ai)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False


def get_player_info(username: str) -> Optional[Dict]:
    """Get player information by username"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT p.player_id, p.username, p.game_id, p.region_tag, p.ministry, 
                   p.is_ai, p.has_submitted_round1, p.has_submitted_round2, 
                   p.has_submitted_round3, g.num_rounds, g.current_round, g.state
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



def get_game_by_gm_username(gm_username: str) -> Optional[Dict]:
    """Get game information by GM username (returns most recent game)"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT game_id, gm_username, num_rounds, current_round, state, 
                   accept_submissions, created_at, updated_at
            FROM games
            WHERE gm_username = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (gm_username,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def get_policies_for_ministry(ministry: str) -> List[Dict]:
    """Get all policies for a specific ministry"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT p.*, pe.explanation
            FROM policies p
            LEFT JOIN policy_explanations pe ON p.pol_tag = pe.pol_tag
            WHERE p.pol_ministry = ?
            ORDER BY p.pol_id
            """,
            (ministry,)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_plot_variables_for_ministry(ministry: str) -> List[Dict]:
    """Get all plot variables for a specific ministry"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM plot_variables
            WHERE pv_ministry = ?
            ORDER BY pv_id
            """,
            (ministry,)
        )
        return [dict(row) for row in cursor.fetchall()]


# def save_policy_decisionOLD(conn, game_id: str, round_num: int, region_tag: str, 
#                          ministry: str, pol_id: str, value: float):
#     """Save a policy decision to the database"""
#     conn.execute(
#         """
#         INSERT INTO policy_decisions (game_id, round, region_tag, ministry, pol_id, value)
#         VALUES (?, ?, ?, ?, ?, ?)
#         """,
#         (game_id, round_num, region_tag, ministry, pol_id, value)
#     )
#     # Note: NO commit here - let the caller handle it

def save_policy_decision(conn, game_id: str, round_num: int, region_tag: str, 
                         ministry: str, pol_id: int, value: float, pol_tag: str):
    """Save a policy decision to the database"""
    try:
        conn.execute(
            """
            INSERT INTO policy_decisions (game_id, round, region_tag, ministry, pol_id, value, pol_tag)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (game_id, round_num, region_tag, ministry, pol_id, value, pol_tag)
        )
    except Exception as e:
        print(f"❌ ERROR saving policy decision: {e}")
        print(f"   Data: game_id={game_id}, round={round_num}, region={region_tag}, ministry={ministry}, pol_id={pol_id}, value={value}, pol_tag={pol_tag}")
        raise

def get_policy_decisions(game_id: str, round_num: int, region_tag: str, 
                         ministry: str) -> List[Tuple[int, float]]:
    """Get policy decisions for a specific player in a round"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT pol_id, value
            FROM policy_decisions
            WHERE game_id = ? AND round = ? AND region_tag = ? AND ministry = ?
            ORDER BY pol_id
            """,
            (game_id, round_num, region_tag, ministry)
        )
        return [(row['pol_id'], row['value']) for row in cursor.fetchall()]

def generate_ai_policy_value(pol_min: float, pol_max: float) -> float:
    """
    Generate random policy value using specified algorithm
    Value will be between pol_min + range/2 and pol_max
    """
    range_val = (pol_max - pol_min) / 2
    value = pol_min + range_val + random.uniform(0, 1) * (range_val / 2)
    return round(value, 5)


# def generate_ai_policy_decisionsOLD(game_id: str, round_num: int):
#     """
#     Generate all AI policy decisions for a given round
#     """
#     with get_db() as conn:
#         # Get all AI players
#         cursor = conn.execute(
#             """
#             SELECT player_id, username, region_tag, ministry
#             FROM players
#             WHERE game_id = ? AND is_ai = 1
#             """,
#             (game_id,)
#         )
#         ai_players = cursor.fetchall()
        
#         # For each AI player, generate decisions for their ministry's policies
#         for player in REGION_ABBR:
#             if player in ai_players:
#                 pass
#             else:
#                 pass
            
#         for player in ai_players:
#             ministry = player['ministry']
#             region_tag = player['region_tag']
            
#             # Get policies for this ministry
#             policies = get_policies_for_ministry(ministry)
            
#             # Generate and save decisions
#             for policy in policies:
#                 value = generate_ai_policy_value(policy['pol_min'], policy['pol_max'])
#                 # PASS THE CONNECTION HERE
#                 save_policy_decision(
#                     conn, game_id, round_num, region_tag, ministry, 
#                     int(policy['pol_id']),  # Ensure it's an integer
#                     value, policy['pol_tag']
#                 )
        
#         conn.commit()

def generate_ai_policy_decisions(game_id: str, round_num: int):
    """
    Generate all AI policy decisions for a given round
    """
    print(f"\n🤖 === STARTING AI POLICY GENERATION ===")
    print(f"Game ID: {game_id}, Round: {round_num}")
    
    with get_db() as conn:
        # Get all AI players
        cursor = conn.execute(
            """
            SELECT player_id, username, region_tag, ministry
            FROM players
            WHERE game_id = ? AND is_ai = 1
            """,
            (game_id,)
        )
        ai_players = cursor.fetchall()
        
        print(f"Found {len(ai_players)} AI players")
        
        # For each AI player, generate decisions for their ministry's policies
        decision_count = 0
        for player in ai_players:
                ministry = player['ministry']
                region_tag = player['region_tag']
                
                print(f"\n  Processing AI player: {player['username']}")
                print(f"    Region: {region_tag}, Ministry: {ministry}")
                
                # Get policies for this ministry
                policies = get_policies_for_ministry(ministry)
                print(f"    Found {len(policies)} policies for {ministry}")
                
                # Generate and save decisions
                for policy in policies:
                    value = generate_ai_policy_value(policy['pol_min'], policy['pol_max'])
                    print(f"      Saving: pol_id={policy['pol_id']}, value={value}")
                    
                    save_policy_decision(
                        conn, game_id, round_num, region_tag, ministry, 
                        int(policy['pol_id']), value, policy['pol_tag']
                    )
                    decision_count += 1
        
        print(f"\n✅ Total decisions to save: {decision_count}")
        print(f"🔄 Committing transaction...")
        conn.commit()
        print(f"✅ Commit successful!")
        
        # Verify the data was saved
        cursor = conn.execute(
            "SELECT COUNT(*) as count FROM policy_decisions WHERE game_id = ? AND round = ?",
            (game_id, round_num)
        )
        saved_count = cursor.fetchone()['count']
        print(f"✅ Verified: {saved_count} decisions in database")
        print(f"🤖 === AI POLICY GENERATION COMPLETE ===\n")
        
        
def mark_player_submission(game_id: str, username: str, round_num: int):
    """Mark that a player has submitted their policies for a round"""
    with get_db() as conn:
        field = f"has_submitted_round{round_num}"
        conn.execute(
            f"""
            UPDATE players
            SET {field} = 1
            WHERE game_id = ? AND username = ?
            """,
            (game_id, username)
        )
        conn.commit()


def get_submission_status(game_id: str, round_num: int) -> Dict:
    """
    Get submission status for all human players in a round
    Returns: {
        'total_human': int,
        'submitted': int,
        'waiting': [(region_tag, ministry, username), ...],
        'all_submitted': bool
    }
    """
    with get_db() as conn:
        field = f"has_submitted_round{round_num}"
        
        cursor = conn.execute(
            f"""
            SELECT region_tag, ministry, username, {field} as submitted
            FROM players
            WHERE game_id = ? AND is_ai = 0
            ORDER BY region_tag, ministry
            """,
            (game_id,)
        )
        players = cursor.fetchall()
        
        total = len(players)
        submitted = sum(1 for p in players if p['submitted'])
        waiting = [(p['region_tag'], p['ministry'], p['username']) 
                   for p in players if not p['submitted']]
        
        return {
            'total_human': total,
            'submitted': submitted,
            'waiting': waiting,
            'all_submitted': (submitted == total and total > 0)
        }


def advance_round(game_id: str):
    """
    Advance game to next round
    - Increment current_round
    - Reset accept_submissions to 0
    - Generate AI decisions for new round
    """
    with get_db() as conn:
        # Get current round
        cursor = conn.execute(
            "SELECT current_round, num_rounds FROM games WHERE game_id = ?",
            (game_id,)
        )
        game = cursor.fetchone()
        
        if not game:
            return False
        
        new_round = game['current_round'] + 1
        
        if new_round > game['num_rounds']:
            # Game is complete
            conn.execute(
                """
                UPDATE games
                SET state = 'complete'
                WHERE game_id = ?
                """,
                (game_id,)
            )
        else:
            # Advance to next round
            conn.execute(
                """
                UPDATE games
                SET current_round = ?, accept_submissions = 0, 
                    state = 'playing', updated_at = CURRENT_TIMESTAMP
                WHERE game_id = ?
                """,
                (new_round, game_id)
            )
        
        conn.commit()
        
        # Generate AI decisions for new round
        if new_round <= game['num_rounds']:
            generate_ai_policy_decisions(game_id, new_round)
        
        return True


def set_accept_submissions(game_id: str, accept: bool):
    """Toggle accept_submissions flag"""
    with get_db() as conn:
        conn.execute(
            """
            UPDATE games
            SET accept_submissions = ?, updated_at = CURRENT_TIMESTAMP
            WHERE game_id = ?
            """,
            (1 if accept else 0, game_id)
        )
        conn.commit()


def get_game_info(game_id: str) -> Optional[Dict]:
    """Get complete game information"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM games WHERE game_id = ?
            """,
            (game_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_ministry_tag(ministry: str) -> str:
    """Convert ministry name to tag"""
    mapping = {
        'Poverty': 'pov',
        'Inequality': 'ineq',
        'Empowerment': 'emp',
        'Food': 'food',
        'Energy': 'ener',
        'Future': 'fut'
    }
    return mapping.get(ministry, ministry.lower()[:4])

if __name__ == "__main__":
    # Initialize database
    init_database()
    load_policies_data()
    load_plot_variables_data()
    print("Database initialized with 32 policies and 48 plot variables!")
    
    # Test game_id generation
    print("\nSample game IDs:")
    for _ in range(5):
        print(f"  {generate_game_id()}")
        