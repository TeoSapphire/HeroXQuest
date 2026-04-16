# HeroXQuest App game
# ---------------------- MEMO ---------------------- #
# 1. Class Definitions
# 2. JSON files 
# 3. Every game function
# 4. Pygame
# 5. Assets, UI, Variables
# 6. UI elements position
# 7. Main (Event, Loop game, credits)
# ----------------------------------------------------#

import json, random, pygame, os, sys

# - - - - - - - - - - CLASS DEFINITIONS - - - - - - - - - - #

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Character class : all party members objects
class Character:
    def __init__(self, name, char_class, level, max_hp, hp, atk, df, skill):
        self.name = name              # Character name
        self.char_class = char_class  # Character class (Hero, Wizard, Monster)
        self.level = level            # Current level
        self.max_hp = max_hp          # Maximum HP
        self.hp = hp                  # Current HP
        self.atk = atk                # Attack power
        self.df = df                  # Defense power
        self.skill = skill            # Special skill

# Monster class : represents enemy and final boss stage
class Monster:
    def __init__(self, name, level, max_hp, hp, atk, df, skill, sprite, pos):
        self.name = name              # Monster name
        self.level = level            # Monster level
        self.max_hp = max_hp          # Maximum HP
        self.hp = hp                  # Current HP
        self.atk = atk                # Attack power
        self.df = df                  # Defense power
        self.skill = skill            # Special skill
        self.sprite = sprite          # Monster sprite image
        self.rect = sprite.get_rect(topleft=pos)  # Position rectangle for collision detection

# QuestionData class : about the questions of battle system
class QuestionData:
    def __init__(self, prompt, choices, answer, typ3):
        self.prompt = prompt          # Question text
        self.choices = choices        # List of answer choices (A, B, C)
        self.correct = answer         # Index of correct answer
        self.typ3 = typ3              # Question type

# - - - - - - - - - - FILE JSON LOADING - - - - - - - - - - #

# JSON Party_member
def load_PartyJSON():
    with open("data/classParty.json", "r", encoding="utf-8") as json_file:
        data_party = json.load(json_file)
    return data_party

# JSON Monster and stages
def load_MonstersJSON():
    with open("data/monsters.json", "r", encoding="utf-8") as json_file:
        data_MO = json.load(json_file)
    return data_MO

# JSON Questions and answers
def load_QuestionJSON():
    with open("data/questions.json", "r", encoding="utf-8") as json_file:
        data_Q = json.load(json_file)
    return data_Q   

# - - - - - - - - - - GAME FUNCTIONS - - - - - - - - - - #

# Select the main character from the user_choice
def character_selection(user_choice, data_party):
    main_data = data_party[user_choice][0]  # Get first character of chosen class
    
    return Character(main_data["name"], main_data["char_class"], main_data["level"], 
                    main_data["max_hp"], main_data["hp"], main_data["atk"], 
                    main_data["df"], main_data["skill"])

# Create a party member group with main character (user_choice)
def create_party(main_character, data_party):
    party = [main_character]  # Start with main character
    
    # Add other characters to fill party to 3 members
    for role, members in data_party.items():
        for m in members:
            if m["name"] != main_character.name and len(party) < 3:
                allcharacter = Character(
                    m["name"],
                    m["char_class"],
                    m["level"],
                    m["max_hp"],
                    m["hp"],
                    m["atk"],
                    m["df"],
                    m["skill"]
                )
                party.append(allcharacter)
    
    return party

# Function to generate random questions from JSON file (Question)
def generate_question(question_data):
    q = random.choice(question_data["questions"])  # Pick random question
    mapping = {"A": 0, "B": 1, "C": 2}  # Map letter answers to indices
    index_q = mapping.get(q["answer"], 0)
    return QuestionData(q["prompt"], q["choices"], index_q, q["type"])

# Player Turn function
def player_turn(party, monsters, attack_target, correct_answer):
    # If answer was wrong, skip attack
    if not correct_answer:
        return monsters
    
    # if attack target is valid
    if attack_target >= len(monsters):
        attack_target = 0
    
    target_mo = monsters[attack_target]  # Primary target
    
    # Each party member attacks
    for i, member in enumerate(party):
        if not monsters:
            break
        
        # First member attacks selected target, others attack random
        current_target = target_mo if i == 0 else random.choice(monsters)
        
        # Calculate damage (attack - defense, minimum 0)
        dmg = max(0, member.atk - current_target.df)
        current_target.hp = max(0, current_target.hp - dmg)
    
    # Return only monsters that are still alive
    return [m for m in monsters if m.hp > 0]

# Enemy turn function
def enemy_turn(monsters, party):
    # Each monster attacks a random party member
    for m in monsters: 
        if not party:
            break
        
        target_party = random.choice(party)  # Random target
        dmg = max(0, m.atk - target_party.df)  # Calculate damage
        target_party.hp = max(0, target_party.hp - dmg)
    
    # Return only party members that are still alive
    return [member for member in party if member.hp > 0]

# Function to create stage and monsters
def stage_creation(stagedata, forest_mo1, forest_mo2, cave_mo1, cave_mo2, cave_mo3, Boss_mo):
    monsters = []
    total = len(stagedata["monsters"])
    start_x = 400 - (total - 1) * 70  # Center monsters on screen
    
    # Create each monster with appropriate sprite
    for i, m in enumerate(stagedata["monsters"]):
        if stagedata["stage"] == "FOREST":
            sprite = forest_mo1 if i % 2 else forest_mo2  # Alternate sprites
        elif stagedata["stage"] == "CAVE":
            if i == 0:
                sprite = cave_mo1 
            elif i == 1:
                sprite = cave_mo2
            else:
                sprite = cave_mo3
        else:  # CASTLE stage
            sprite = Boss_mo
        
        pos = (start_x + i * 140, 100)  # Position with spacing
        mo = Monster(m["name"], m["level"], m["max_hp"], m["hp"], 
                    m["atk"], m["df"], m["skill"], sprite, pos)
        monsters.append(mo)
    
    return monsters

# HP bar
def hp_bar(surface, screenX, screenY, hp, hp_max, width=120, height=12):
    ratio = max(0, min(1.0, hp/hp_max))  # Calculate HP percentage (0-1)
    
    # Draw background (dark gray)
    pygame.draw.rect(surface, (60, 60, 60), (screenX, screenY, width, height))
    # Draw HP bar (green)
    pygame.draw.rect(surface, (0, 200, 0), (screenX, screenY, int(width * ratio), height))
    # Draw border (white)
    pygame.draw.rect(surface, (255, 255, 255), (screenX, screenY, width, height), 1)

# Wrap text to fit within a maximum width
def wrap_text(text, font, max_width):
    """Wrap text to fit within max_width"""
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

# - - - - - - - - - - PYGAME - - - - - - - - -#

pygame.init()

# Set game icon and window title
game_icon = pygame.image.load(resource_path("assets/icon/HeroXQuest_Icon.png"))
pygame.display.set_icon(game_icon)
pygame.display.set_caption("HeroXQuest")

# Create game window
game_screen = pygame.display.set_mode((800, 400))
clock = pygame.time.Clock()

# - - - - - - - - - - LOAD ASSETS - - - - - - - - - - #

# Background images
Start_BG = pygame.image.load(resource_path("assets/UI/Title.png"))
BG_1 = pygame.image.load(resource_path("assets/bg/Forest_bg.png"))
BG_2 = pygame.image.load(resource_path("assets/bg/Cave_bg.png"))
BG_3 = pygame.image.load(resource_path("assets/bg/Castle_bg.png"))
WIN_BG = pygame.image.load(resource_path("assets/UI/Victory.png"))
GAMEOVER_BG = pygame.image.load(resource_path("assets/UI/GameOver.png"))

# Fonts
game_font = pygame.font.SysFont("msgothic", 16)
question_font = pygame.font.SysFont("msgothic", 14)  # Smaller font for questions

# UI elements
hero_icon = pygame.image.load(resource_path("assets/UI/Box_Party/icon_hero.png"))
wizard_icon = pygame.image.load(resource_path("assets/UI/Box_Party/icon_wizard.png"))
monster_icon = pygame.image.load(resource_path("assets/UI/Box_Party/icon_monster.png"))
box_question = pygame.image.load(resource_path("assets/UI/Question/Box_questions.png"))
attack_button = pygame.image.load(resource_path("assets/UI/Attack.png"))
menu_choices_party = pygame.image.load(resource_path("assets/UI/Menu_Choices_Characters.png"))
select_choices_party_button = pygame.image.load(resource_path("assets/UI/Select_Characters.png"))

# Character sprites
hero_pg = pygame.image.load(resource_path("assets/sprites/HERO.png"))
wizard_pg = pygame.image.load(resource_path("assets/sprites/WIZARD.png"))
monster_pg = pygame.image.load(resource_path("assets/sprites/MONSTER.png"))

# Monster sprites
forest_mo1 = pygame.image.load(resource_path("assets/sprites/Forest_Monster/PoisonBug1.png"))
forest_mo2 = pygame.image.load(resource_path("assets/sprites/Forest_Monster/PoisonBug2.png"))
cave_mo1 = pygame.image.load(resource_path("assets/sprites/Cave_Monster/IceGolem1.png"))
cave_mo2 = pygame.image.load(resource_path("assets/sprites/Cave_Monster/IceGolem2.png"))
cave_mo3 = pygame.image.load(resource_path("assets/sprites/Cave_Monster/IceDragon.png"))
Boss_mo = pygame.image.load(resource_path("assets/sprites/Castle_Boss/LordSkeleton.png"))

# - - - - - - - - - - GAME VARIABLES - - - - - - - - - - #

# Game state management
running = True
game_state = "TITLE"  # Current screen: TITLE, MENU_SELECT_CHAR, CONFIRM_CHAR, INTRO, LOADING, BATTLE, WIN, GAME_OVER
battle_phase = None   # Battle phase: SELECT_ENEMY, ANSWER_QUESTION, PLAYER_ATTACK, ENEMY_ATTACK, CHECK_END

# Battle variables
answer_rects = []        # Rectangles for answer choices (the user can click to answer)
current_question = None  # Current question being asked
select_enemy = None      # Index of selected enemy to attack
correct_answer = False   # Whether the answer was correct

# Party and monster lists
party = []
monsters = []

# User selection
user_choice = None  # User's character choice: HERO, WIZARD, or MONSTER

# Stage management
stage_battle = None  # Current stage name
stage_data = None    # Current stage data
index_stage = 0      # Current stage index
stages = ["FOREST", "CAVE", "CASTLE"]  # List of all stages

# Timing
state_time = pygame.time.get_ticks()  # Timer for screen transitions

# - - - - - - - - - -  UI ELEMENT POSITIONS - - - - - - - - - - #

# Rules button
rules_rect = pygame.Rect(640, 350, 150, 40)
back_author = pygame.Rect(640, 350, 150, 40)

#Credit button
credit_rect = pygame.Rect(640, 350, 150, 40)

# Character selection layout (3 columns)
screenX, screenY = game_screen.get_size()
col = screenX // 3
columns = [
    pygame.Rect(0, 0, col, screenY),        # Left column (Wizard)
    pygame.Rect(col, 0, col, screenY),      # Middle column (Hero)
    pygame.Rect(col*2, 0, col, screenY)     # Right column (Monster)
]

# Position character sprites in columns
wizard_rect = wizard_pg.get_rect(center=columns[0].center)
hero_rect = hero_pg.get_rect(center=columns[1].center)
monster_rect = monster_pg.get_rect(center=columns[2].center)

# Position selection buttons
button_y = int(screenY * 0.80)
wizard_button = select_choices_party_button.get_rect(midtop=(columns[0].centerx, button_y))
hero_button = select_choices_party_button.get_rect(midtop=(columns[1].centerx, button_y))
monster_button = select_choices_party_button.get_rect(midtop=(columns[2].centerx, button_y))

# Confirmation buttons (Yes/No)
yes_button = pygame.Rect(250, 260, 120, 40)
no_button = pygame.Rect(430, 260, 120, 40)

# - - - - - - - - - - MAIN GAME LOOP - - - - - - - - - - #

while running:
    # - - - - - - - - - EVENT HANDLING - - - - - - - - - - #
    for event in pygame.event.get():
        mouse_pos = pygame.mouse.get_pos()
        
        # Quit game
        if event.type == pygame.QUIT:
            running = False
        
        # - - - - - - - - - KEYBOARD EVENTS - - - - - - - - - #
        if event.type == pygame.KEYDOWN:
            # TITLE screen - press ENTER to start the game and go to the next phase
            if game_state == "TITLE":
                if event.key == pygame.K_RETURN:
                    game_state = "MENU_SELECT_CHAR"
            
            # RULES screen - press any key to return
            elif game_state == "RULES":
                game_state = "TITLE"
            
            # CREDIT screen - press any key to return to WIN screen
            elif game_state == "CREDIT":
                game_state = "WIN"

            # WIN/GAME_OVER screens - press ENTER to return to title
            elif game_state == "WIN" or game_state == "GAME_OVER":
                if event.key == pygame.K_RETURN:
                    # Reset all game variables
                    index_stage = 0
                    party = []
                    monsters = []
                    user_choice = None
                    game_state = "TITLE"
        
        # - - - - - - - - - MOUSE CLICK EVENTS - - - - - - - - - #
        if event.type == pygame.MOUSEBUTTONDOWN:
            # TITLE screen - click rules button
            if game_state == "TITLE":
                if rules_rect.collidepoint(event.pos):
                    game_state = "RULES"
            
            # RULES screen - click anywhere to return
            elif game_state == "RULES":
                game_state = "TITLE"

            # WIN screen - click credit button
            elif game_state == "WIN":
                if credit_rect.collidepoint(event.pos):
                    game_state = "CREDIT"
            # CREDIT screen - click anywhere to return to win title
            elif game_state == "CREDIT":
                game_state == "WIN"
            
            # MENU_SELECT_CHAR - menu where the user can choice the main character of the adventure
            elif game_state == "MENU_SELECT_CHAR":
                if wizard_button.collidepoint(event.pos):
                    user_choice = "WIZARD"
                    game_state = "CONFIRM_CHAR"
                elif hero_button.collidepoint(event.pos):
                    user_choice = "HERO"
                    game_state = "CONFIRM_CHAR"
                elif monster_button.collidepoint(event.pos):
                    user_choice = "MONSTER"
                    game_state = "CONFIRM_CHAR"
            
            # CONFIRM_CHAR - confirm or cancel selection
            elif game_state == "CONFIRM_CHAR":
                if yes_button.collidepoint(event.pos):
                    # Create party and start game
                    data_party = load_PartyJSON()
                    main_char = character_selection(user_choice, data_party)
                    party = create_party(main_char, data_party)
                    game_state = "INTRO"
                    state_time = pygame.time.get_ticks()
                elif no_button.collidepoint(event.pos):
                    # Return to character selection
                    game_state = "MENU_SELECT_CHAR"
            
            # BATTLE screen
            elif game_state == "BATTLE":
                # SELECT_ENEMY phase - click on enemy to attack
                if battle_phase == "SELECT_ENEMY":
                    for i, m in enumerate(monsters):
                        if m.rect.collidepoint(event.pos):
                            select_enemy = i
                            # Load and display question
                            question = load_QuestionJSON()
                            current_question = generate_question(question)
                            battle_phase = "ANSWER_QUESTION"
                            break
                
                # ANSWER_QUESTION phase - click on answer choice
                elif battle_phase == "ANSWER_QUESTION":
                    for i, rect in enumerate(answer_rects):
                        if rect.collidepoint(event.pos):
                            # Check if answer is correct
                            correct_answer = (i == current_question.correct)
                            
                            # Show visual feedback
                            color = (0, 255, 0) if correct_answer else (255, 0, 0)
                            pygame.draw.rect(game_screen, color, rect, 4)
                            pygame.display.flip()
                            
                            # Show HIT/MISS text
                            feedback_text = "HIT!" if correct_answer else "MISSED!"
                            surf = game_font.render(feedback_text, True, color)
                            game_screen.blit(surf, (400 - surf.get_width()//2, 200))
                            pygame.display.flip()
                            
                            # Wait 1 second before continuing
                            pygame.time.delay(1000)
                            battle_phase = "PLAYER_ATTACK"
                            break

    # - - - - - - - - - RENDERING - - - - - - - - - #
    
    game_screen.fill((0, 0, 0))  # Clear screen with black
    
    # - - - - - - - - - - TITLE SCREEN - - - - - - - - - - #
    if game_state == "TITLE":
        game_screen.blit(Start_BG, (0, 0))
        # Draw rules button
        pygame.draw.rect(game_screen, (100, 100, 100), rules_rect)
        txt_rules = game_font.render("RULES", True, (255, 255, 255))
        game_screen.blit(txt_rules, (rules_rect.x + 50, rules_rect.y + 12))

        # Size for background author
        back_author.x = 800 - rules_rect.x - back_author.width 
        back_author.y = rules_rect.y 

        pygame.draw.rect(game_screen, (100, 100, 100), back_author)
        author_game = game_font.render("KABIKABI", True, (255, 255, 255))
        game_screen.blit(author_game, (back_author.x + 40, back_author.y + 12))
    
    # - - - - - - - - - - RULES SCREEN - - - - - - - - - - #
    elif game_state == "RULES":
        game_screen.fill((0, 0, 0))
        rules = [
            "1. メインキャラクターを選択してください：勇者、魔法使い、モンスター。",
            "2. バトルパーティは3人です(メインキャラクター＋他の2人）。",
            "3. バトルステージは全部で3つあり、各ステージにモンスターが登場します。最終ステージにはボスがいます",
            "4. 戦闘システムはRPG形式です。敵にダメージを与えるには、問題に正しく答える必要があります。",
            "5. 間違えると攻撃は失敗します！",
            "6. 問題の内容は日本語の漢字と語彙に関するものです。",
            "7. メインキャラクターが倒されるとゲームオーバーです！",
            "",
            "タイトルに戻るには、いずれかのボタンを押してください!"
        ]
        for i, line in enumerate(rules):
            r = question_font.render(line, True, (255, 255, 255))
            game_screen.blit(r, (50, 50 + i * 30))
    
    # - - - - - - - - - - CHARACTER SELECTION SCREEN - - - - - - - - - - #
    elif game_state == "MENU_SELECT_CHAR":
        game_screen.blit(menu_choices_party, (0, 0))
        
        # Highlight selected character
        if user_choice == "WIZARD":
            pygame.draw.rect(game_screen, (255, 255, 0), wizard_rect, 3)
        elif user_choice == "HERO":
            pygame.draw.rect(game_screen, (255, 255, 0), hero_rect, 3)
        elif user_choice == "MONSTER": 
            pygame.draw.rect(game_screen, (255, 255, 0), monster_rect, 3)
        
        # Draw character sprites and buttons
        game_screen.blit(wizard_pg, wizard_rect)
        game_screen.blit(hero_pg, hero_rect)
        game_screen.blit(monster_pg, monster_rect)
        game_screen.blit(select_choices_party_button, wizard_button)
        game_screen.blit(select_choices_party_button, hero_button)
        game_screen.blit(select_choices_party_button, monster_button)
    
    # - - - - - - - - - - CONFIRMATION SCREEN - - - - - - - - - - #
    elif game_state == "CONFIRM_CHAR":
        game_screen.fill((0, 0, 0))
        
        # Centered confirmation message
        message = game_font.render("このキャラクターで決定しますか？?", True, (255, 255, 255))
        text_rect = message.get_rect(center=(400, 180))
        game_screen.blit(message, text_rect)
        
        # Yes/No buttons
        pygame.draw.rect(game_screen, (0, 200, 0), yes_button)
        pygame.draw.rect(game_screen, (200, 0, 0), no_button)
        
        yes_text = game_font.render("YES", True, (0, 0, 0))
        no_text = game_font.render("NO", True, (0, 0, 0))
        
        game_screen.blit(yes_text, (yes_button.x + 35, yes_button.y + 10))
        game_screen.blit(no_text, (no_button.x + 45, no_button.y + 10))
    
    # - - - - - - - - - - INTRO SCREEN - - - - - - - - - - #
    elif game_state == "INTRO":
        game_screen.fill((0, 0, 0))
        message2 = game_font.render("あなたの冒険はこれから始まりますよ!", True, (255, 255, 255))
        text_rect = message2.get_rect(center=(400, 200))
        game_screen.blit(message2, text_rect)
        
        # Auto-transition after 2 seconds
        if pygame.time.get_ticks() - state_time > 2000:
            game_state = "LOADING"
            state_time = pygame.time.get_ticks()
    
    # - - - - - - - - - - LOADING SCREEN - - - - - - - - - - #
    elif game_state == "LOADING":
        game_screen.fill((0, 0, 0))
        loading_text = game_font.render("Loading...", True, (255, 255, 255))
        text_rect = loading_text.get_rect(center=(400, 200))
        game_screen.blit(loading_text, text_rect)
        
        # Load stage data after 1.5 seconds
        if pygame.time.get_ticks() - state_time > 1500:
            stage_battle = stages[index_stage]
            all_stages_data = load_MonstersJSON()["stages"]
            
            # Find current stage data
            stage_data = None
            for s in all_stages_data:
                if s["stage"] == stage_battle:
                    stage_data = s
                    break
            
            # Create monsters and start battle
            if stage_data:
                monsters = stage_creation(stage_data, forest_mo1, forest_mo2, cave_mo1, cave_mo2, cave_mo3, Boss_mo)
                battle_phase = "SELECT_ENEMY"
                game_state = "BATTLE"
    
    # - - - - - - - - - - BATTLE SCREEN - - - - - - - - - - #
    elif game_state == "BATTLE":
        # Draw appropriate background based on stage
        if stage_battle == "FOREST":
            game_screen.blit(BG_1, (0, 0))
        elif stage_battle == "CAVE":
            game_screen.blit(BG_2, (0, 0))
        else:  # CASTLE
            game_screen.blit(BG_3, (0, 0))
        
        # Draw monsters and their HP bars
        for m in monsters:
            game_screen.blit(m.sprite, m.rect)
            hp_bar(game_screen, m.rect.x, m.rect.y - 15, m.hp, m.max_hp, width=60)
        
        # Draw party UI panel at bottom
        pygame.draw.rect(game_screen, (20, 20, 20), (0, 300, 800, 100))
        pygame.draw.line(game_screen, (255, 255, 255), (0, 300), (800, 300), 2)
        
        # Draw each party member's info box
        for i, member in enumerate(party):
            pX = 30 + i * 260  # Horizontal position
            pY = 310           # Vertical position
            
            # Draw info box background
            pygame.draw.rect(game_screen, (50, 50, 50), (pX, pY, 230, 80), border_radius=5)
            pygame.draw.rect(game_screen, (200, 200, 200), (pX, pY, 230, 80), 2, border_radius=5)
            
            # Select appropriate icon based on character class (box party)
            member_name_lower = member.name.lower()
            char_class_lower = member.char_class.lower()
            
            # I tried this fix because there was a bug of character icons...
            if "hero" in member_name_lower or "hero" in char_class_lower or "knight" in char_class_lower:
                current_icon = hero_icon
            elif "wizard" in member_name_lower or "wizard" in char_class_lower or "mage" in char_class_lower or "wiz" in char_class_lower:
                current_icon = wizard_icon
            elif "monster" in member_name_lower or "monster" in char_class_lower or "orc" in char_class_lower:
                current_icon = monster_icon
            else:
                # Default fallback based on user's initial choice
                if i == 0 and user_choice == "HERO":
                    current_icon = hero_icon
                elif i == 0 and user_choice == "WIZARD":
                    current_icon = wizard_icon
                elif i == 0 and user_choice == "MONSTER":
                    current_icon = monster_icon
                else:
                    current_icon = monster_icon
            
            # Draw icon, name, and HP bar
            game_screen.blit(current_icon, (pX + 10, pY + 15))
            name_text = game_font.render(member.name, True, (255, 255, 255))
            game_screen.blit(name_text, (pX + 80, pY + 10))
            hp_bar(game_screen, pX + 80, pY + 35, member.hp, member.max_hp, width=130)
            hp_val = game_font.render(f"{member.hp}/{member.max_hp}", True, (200, 200, 200))
            game_screen.blit(hp_val, (pX + 80, pY + 55))
        
        # - - - - - - - - - - ANSWER_QUESTION PHASE - - - - - - - - - - #
        if battle_phase == "ANSWER_QUESTION":
            # Draw question box
            box_scaled = pygame.transform.scale(box_question, (600, 220))
            game_screen.blit(box_scaled, (100, 40))
            answer_rects = []
            
            # White background for question text
            pygame.draw.rect(game_screen, (255, 255, 255), (115, 55, 570, 35))
            
            # Wrap and display question text
            wrapped_lines = wrap_text(current_question.prompt, question_font, 560)
            y_offset = 60
            for line in wrapped_lines:
                q_text = question_font.render(line, True, (0, 0, 0))
                game_screen.blit(q_text, (120, y_offset))
                y_offset += 18
            
            # Position answer choices below question
            choice_start_y = max(100, y_offset + 10)
            
            # Draw answer choice buttons
            for i, choice in enumerate(current_question.choices):
                r = pygame.Rect(115, choice_start_y + i * 45, 570, 35)
                pygame.draw.rect(game_screen, (240, 240, 240), r)
                pygame.draw.rect(game_screen, (100, 100, 100), r, 2)
                
                txt = question_font.render(choice, True, (0, 0, 0))
                game_screen.blit(txt, (125, choice_start_y + 10 + i * 45))
                answer_rects.append(r)
        
        # - - - - - - - - - - PLAYER_ATTACK PHASE - - - - - - - - - - #
        elif battle_phase == "PLAYER_ATTACK":
            monsters = player_turn(party, monsters, select_enemy, correct_answer)
            battle_phase = "ENEMY_ATTACK"
        
        # - - - - - - - - - - ENEMY_ATTACK PHASE - - - - - - - - - - #
        elif battle_phase == "ENEMY_ATTACK":
            party = enemy_turn(monsters, party)
            battle_phase = "CHECK_END"
        
        # - - - - - - - - - - CHECK_END PHASE - - - - - - - - - - #
        elif battle_phase == "CHECK_END":
            # Check if main character is dead
            if not party or party[0].hp <= 0:
                game_state = "GAME_OVER"
            # Check if all monsters are defeated
            elif not monsters:
                index_stage += 1
                # Check if all stages completed
                if index_stage >= len(stages):
                    game_state = "WIN"
                else:
                    # Move to next stage
                    stage_battle = stages[index_stage] 
                    game_state = "LOADING"
                    state_time = pygame.time.get_ticks()
            else:
                # Continue battle - select next enemy
                battle_phase = "SELECT_ENEMY"
    
    # - - - - - - - - - - WIN SCREEN - - - - - - - - - - #
    elif game_state == "WIN":
        game_screen.blit(WIN_BG, (0, 0))
        message = game_font.render("タイトル戻るには、ENTERを押してください！", True, (255, 255, 255))
        text_rect = message.get_rect(center=(400, 350))
        game_screen.blit(message, text_rect)
        # Draw credit button
        pygame.draw.rect(game_screen, (100, 100, 100), credit_rect)
        txt_credit = game_font.render("CREDIT", True, (255, 255, 255))
        game_screen.blit(txt_credit, (credit_rect.x + 50, credit_rect.y + 15))
    
    #Credit of game contents
    elif game_state == "CREDIT":
        game_screen.fill((0, 0, 0))
        credit1 = game_font.render("HeroXQUestをプレイしていただき、ありがとうございました！", True, (255, 255, 255))
        credit2 = game_font.render("ゲーム制作・デザイン：KabiKabiDev", True, (255, 255, 255))
        credit3 = game_font.render("SNS：@KabiKabiDev", True, (255, 255, 255))
        credit4 = game_font.render("", True, (255, 255, 255))
        credit5 = game_font.render("タイトルに戻るには、いずれかのボタンを押してください!", True, (255, 255, 255))
        game_screen.blit(credit1, (150, 120))
        game_screen.blit(credit2, (250, 160))
        game_screen.blit(credit3, (320, 200))
        game_screen.blit(credit4, (200, 240))
        game_screen.blit(credit5, (200, 240))
    
    # - - - - - - - - - - GAME OVER SCREEN - - - - - - - - - - #
    elif game_state == "GAME_OVER":
        game_screen.blit(GAMEOVER_BG, (0, 0))
        message = game_font.render("タイトル戻るには、ENTERを押してください！", True, (255, 255, 255))
        text_rect = message.get_rect(center=(400, 350))
        game_screen.blit(message, text_rect)
    
    # Update display
    pygame.display.flip()
    
    # Maintain 60 FPS
    clock.tick(60)

# - - - - - - - - - - CLEANUP - - - - - - - - - - #
pygame.quit()