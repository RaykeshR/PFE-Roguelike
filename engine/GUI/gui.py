import pygame
import json
<<<<<<< HEAD
=======
import sys
import os

def resource_path(relative_path):
    """ Get the absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
>>>>>>> e1ee9e50f82e4cfb06348ea23bc5b69ec02b4e18

class Button:
    """Classe simple pour gérer un bouton graphique."""
    def __init__(self, x, y, width, height, text, font, bg_color=(200, 200, 200), text_color=(0, 0, 0), hover_color=(150, 150, 150), shadow=True, callback=None, icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.callback = callback
        self.shadow = shadow
        self.clicked = False
        self.icon = icon
        self.enabled = True

    def draw(self, screen):
        if not self.enabled:
            color = (150, 150, 150)
        else:
            mouse_pos = pygame.mouse.get_pos()
            color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.bg_color

        # Dessine l'ombre si activée
        if self.shadow:
            shadow_rect = self.rect.copy()
            shadow_rect.topleft = (self.rect.x + 4, self.rect.y + 4)
            pygame.draw.rect(screen, (100, 100, 100), shadow_rect, border_radius=6)

        # Dessine le bouton
        pygame.draw.rect(screen, color, self.rect, border_radius=6)

        # Dessine l'icône si présente
        if self.icon:
            icon_rect = self.icon.get_rect(center=(self.rect.x + 30, self.rect.centery))
            screen.blit(self.icon, icon_rect)
            text_x = self.rect.x + 60
        else:
            text_x = self.rect.centerx

        # Dessine le texte centré
        text_surf = self.font.render(self.text, True, self.text_color)
        if self.icon:
            text_rect = text_surf.get_rect(midleft=(text_x, self.rect.centery))
        else:
            text_rect = text_surf.get_rect(center=(text_x, self.rect.centery))
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
                return True
        return False
    
    def handle_event(self, event):
        if self.enabled and event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if self.callback:
                self.callback()


class Slider:
    """Widget de curseur pour ajuster des valeurs."""
    def __init__(self, x, y, width, height, min_val=0, max_val=100, initial_val=50, label="", font=None, callback=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.font = font or pygame.font.Font(None, 24)
        self.callback = callback
        self.dragging = False
        self.handle_radius = 10

    def draw(self, screen):
        # Dessine la piste
        pygame.draw.rect(screen, (150, 150, 150), self.rect, border_radius=3)
        
        # Calcule la position du curseur
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + int(ratio * self.rect.width)
        handle_y = self.rect.centery
        
        # Dessine le curseur
        pygame.draw.circle(screen, (100, 100, 255), (handle_x, handle_y), self.handle_radius)
        
        # Dessine le label et la valeur
        if self.label:
            text = f"{self.label}: {int(self.value)}"
            text_surf = self.font.render(text, True, (0, 0, 0))
            screen.blit(text_surf, (self.rect.x, self.rect.y - 25))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
            handle_x = self.rect.x + int(ratio * self.rect.width)
            handle_y = self.rect.centery
            dist = ((mouse_pos[0] - handle_x)**2 + (mouse_pos[1] - handle_y)**2)**0.5
            if dist <= self.handle_radius:
                self.dragging = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mouse_x = event.pos[0]
            ratio = (mouse_x - self.rect.x) / self.rect.width
            ratio = max(0, min(1, ratio))
            self.value = self.min_val + ratio * (self.max_val - self.min_val)
            if self.callback:
                self.callback(self.value)

    def get_value(self):
        return self.value


class Checkbox:
    """Widget de case à cocher."""
    def __init__(self, x, y, size, label="", font=None, callback=None, checked=False):
        self.rect = pygame.Rect(x, y, size, size)
        self.label = label
        self.font = font or pygame.font.Font(None, 24)
        self.callback = callback
        self.checked = checked

    def draw(self, screen):
        # Dessine la case
        pygame.draw.rect(screen, (200, 200, 200), self.rect, border_radius=3)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2, border_radius=3)
        
        # Dessine la coche si cochée
        if self.checked:
            pygame.draw.line(screen, (0, 200, 0), 
                           (self.rect.x + 5, self.rect.centery),
                           (self.rect.centerx, self.rect.bottom - 5), 3)
            pygame.draw.line(screen, (0, 200, 0),
                           (self.rect.centerx, self.rect.bottom - 5),
                           (self.rect.right - 5, self.rect.y + 5), 3)
        
        # Dessine le label
        if self.label:
            text_surf = self.font.render(self.label, True, (0, 0, 0))
            screen.blit(text_surf, (self.rect.right + 10, self.rect.y))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                if self.callback:
                    self.callback(self.checked)

    def is_checked(self):
        return self.checked


class InputBox:
    """Widget de saisie de texte."""
    def __init__(self, x, y, width, height, font=None, placeholder="", max_length=20, callback=None, password=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font or pygame.font.Font(None, 32)
        self.placeholder = placeholder
        self.text = ""
        self.active = False
        self.max_length = max_length
        self.callback = callback
        self.cursor_visible = True
        self.cursor_timer = 0
        self.password = password  # Si True, masque le texte avec des *

    def draw(self, screen):
        # Dessine la bordure
        color = (100, 100, 255) if self.active else (200, 200, 200)
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        pygame.draw.rect(screen, color, self.rect, 2, border_radius=3)
        
        # Dessine le texte ou le placeholder
        if self.text:
            # Si c'est un champ mot de passe, afficher des * au lieu du texte
            display_text = "*" * len(self.text) if self.password else self.text
            text_color = (0, 0, 0)
        else:
            display_text = self.placeholder
            text_color = (150, 150, 150)
        
        text_surf = self.font.render(display_text, True, text_color)
        screen.blit(text_surf, (self.rect.x + 5, self.rect.y + 10))
        
        # Dessine le curseur clignotant
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 5 + text_surf.get_width()
            pygame.draw.line(screen, (0, 0, 0),
                           (cursor_x, self.rect.y + 5),
                           (cursor_x, self.rect.bottom - 5), 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                if self.callback:
                    self.callback(self.text)
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.max_length:
                self.text += event.unicode

    def update(self):
        # Gère le clignotement du curseur
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def get_text(self):
        return self.text
    
    def set_text(self, text):
        self.text = text[:self.max_length]


class ProgressBar:
    """Barre de progression."""
    def __init__(self, x, y, width, height, max_value=100, current_value=100, 
                 bg_color=(200, 200, 200), fill_color=(0, 200, 0), label=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.max_value = max_value
        self.current_value = current_value
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.label = label
        self.font = pygame.font.Font(None, 20)

    def draw(self, screen):
        # Dessine le fond
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=3)
        
        # Dessine la barre de progression
        ratio = self.current_value / self.max_value
        fill_width = int(self.rect.width * ratio)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(screen, self.fill_color, fill_rect, border_radius=3)
        
        # Dessine le label
        if self.label:
            text = f"{self.label}: {int(self.current_value)}/{int(self.max_value)}"
            text_surf = self.font.render(text, True, (0, 0, 0))
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)

    def set_value(self, value):
        self.current_value = max(0, min(value, self.max_value))


class Panel:
    """Conteneur pour grouper des éléments UI."""
    def __init__(self, x, y, width, height, bg_color=(240, 240, 240), border_color=(0, 0, 0), border_width=2):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width
        self.elements = []

    def add_element(self, element):
        self.elements.append(element)

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=8)
        if self.border_width > 0:
            pygame.draw.rect(screen, self.border_color, self.rect, self.border_width, border_radius=8)
        for element in self.elements:
            element.draw(screen)

    def handle_event(self, event):
        for element in self.elements:
            element.handle_event(event)

    def update(self):
        for element in self.elements:
            if hasattr(element, 'update'):
                element.update()


class Label:
    """Widget pour afficher du texte statique."""
    def __init__(self, x, y, text, font=None, color=(0, 0, 0), align="left"):
        self.x = x
        self.y = y
        self.text = text
        self.font = font or pygame.font.Font(None, 24)
        self.color = color
        self.align = align

    def draw(self, screen):
        text_surf = self.font.render(self.text, True, self.color)
        if self.align == "center":
            rect = text_surf.get_rect(center=(self.x, self.y))
        elif self.align == "right":
            rect = text_surf.get_rect(right=self.x, top=self.y)
        else:  # left
            rect = text_surf.get_rect(left=self.x, top=self.y)
        screen.blit(text_surf, rect)

    def set_text(self, text):
        self.text = text

    def handle_event(self, event):
        pass  # Les labels ne gèrent pas d'événements


class ScrollableList:
    """Liste scrollable pour afficher des éléments."""
    def __init__(self, x, y, width, height, items=None, font=None, item_height=40):
        self.rect = pygame.Rect(x, y, width, height)
        self.items = items or []
        self.font = font or pygame.font.Font(None, 24)
        self.item_height = item_height
        self.scroll_offset = 0
        self.selected_index = None
        self.callback = None

    def draw(self, screen):
        # Fond
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        
        # Clip pour ne dessiner que dans la zone visible
        clip_rect = screen.get_clip()
        screen.set_clip(self.rect)
        
        visible_items = self.rect.height // self.item_height
        start_index = max(0, self.scroll_offset)
        
        for i in range(start_index, min(len(self.items), start_index + visible_items + 1)):
            y_pos = self.rect.y + (i - self.scroll_offset) * self.item_height
            item_rect = pygame.Rect(self.rect.x, y_pos, self.rect.width, self.item_height)
            
            # Highlight si sélectionné
            if i == self.selected_index:
                pygame.draw.rect(screen, (200, 220, 255), item_rect)
            
            # Texte de l'item
            text_surf = self.font.render(str(self.items[i]), True, (0, 0, 0))
            screen.blit(text_surf, (self.rect.x + 10, y_pos + 10))
        
        screen.set_clip(clip_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                # Scroll avec molette
                if event.button == 4:  # Scroll up
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                elif event.button == 5:  # Scroll down
                    max_scroll = max(0, len(self.items) - self.rect.height // self.item_height)
                    self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
                elif event.button == 1:  # Clic gauche
                    rel_y = event.pos[1] - self.rect.y
                    clicked_index = self.scroll_offset + (rel_y // self.item_height)
                    if 0 <= clicked_index < len(self.items):
                        self.selected_index = clicked_index
                        if self.callback:
                            self.callback(clicked_index, self.items[clicked_index])

    def set_items(self, items):
        self.items = items
        self.selected_index = None
        self.scroll_offset = 0

    def get_selected(self):
        if self.selected_index is not None and 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None


class GameGUI:
    """Classe principale pour gérer l'interface graphique du jeu."""
    def __init__(self, width=1000, height=500, title="PFE-Roguelike", bg_color=(255, 255, 255), fps=30):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(title)
<<<<<<< HEAD
=======

        # Set window icon
        icon_path = resource_path("src/gameplay.ico")
        try:
            program_Icon = pygame.image.load(icon_path)
            pygame.display.set_icon(program_Icon)
        except Exception as e:
            print(f"Error loading icon: {e}")
>>>>>>> e1ee9e50f82e4cfb06348ea23bc5b69ec02b4e18
        self.bg_color = bg_color
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.font = pygame.font.Font(None, 36)
        self.running = True
        self.state = "main"
        self.state_history = []
        self.elements = {}
        self.background_images = {}
        self.settings = {}
        self.user_data = {}  # Données utilisateur (connexion, sélection personnage, etc.)

    def add_element(self, menu_name, element):
        """Ajoute un élément UI à un menu spécifique."""
        if menu_name not in self.elements:
            self.elements[menu_name] = []
        self.elements[menu_name].append(element)

    def add_button(self, menu_name, button: Button):
        """Ajoute un bouton à un menu spécifique (compatibilité)."""
        self.add_element(menu_name, button)

    def set_background(self, menu_name, image_path):
        """Définit une image de fond pour un menu."""
        try:
            self.background_images[menu_name] = pygame.image.load(image_path)
            self.background_images[menu_name] = pygame.transform.scale(
                self.background_images[menu_name], (self.width, self.height))
        except:
            print(f"Impossible de charger l'image: {image_path}")

    def change_state(self, new_state, save_history=True):
        """Change l'état du menu avec gestion de l'historique."""
        if save_history:
            self.state_history.append(self.state)
        self.state = new_state

    def go_back(self):
        """Retourne au menu précédent."""
        if self.state_history:
            self.state = self.state_history.pop()

    def draw_elements(self):
        """Dessine tous les éléments du menu courant."""
        if self.state in self.elements:
            for element in self.elements[self.state]:
                element.draw(self.screen)

    def handle_events(self):
        """Gère les événements Pygame et retourne le bouton cliqué s'il y a."""
        clicked_button = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.go_back()
            
            if self.state in self.elements:
                for element in self.elements[self.state]:
                    element.handle_event(event)
                    if isinstance(element, Button) and element.is_clicked(event):
                        clicked_button = element.text
        return clicked_button

    def update_elements(self):
        """Met à jour tous les éléments du menu courant."""
        if self.state in self.elements:
            for element in self.elements[self.state]:
                if hasattr(element, 'update'):
                    element.update()

    def draw_text(self, text, pos, color=(0, 0, 0), font=None):
        """Dessine du texte simple sur l'écran."""
        display_font = font or self.font
        self.screen.blit(display_font.render(text, True, color), pos)

    def clear_screen(self):
        """Efface l'écran avec la couleur de fond ou une image."""
        if self.state in self.background_images:
            self.screen.blit(self.background_images[self.state], (0, 0))
        else:
            self.screen.fill(self.bg_color)

    def save_settings(self, filename="settings.json"):
        """Sauvegarde les paramètres dans un fichier JSON."""
        try:
            with open(filename, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")

    def load_settings(self, filename="settings.json"):
        """Charge les paramètres depuis un fichier JSON."""
        try:
            with open(filename, 'r') as f:
                self.settings = json.load(f)
            return True
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")
            return False

    def run_menu(self):
        """Boucle principale pour gérer le menu graphique."""
        while self.running:
            self.clear_screen()
            clicked = self.handle_events()
            self.update_elements()
            
            if clicked:
                print(f"Bouton cliqué: {clicked}")
            
            self.draw_elements()
            pygame.display.flip()
            self.clock.tick(self.fps)

    def quit(self):
        self.running = False
        pygame.quit()


# Exemple d'utilisation complet
if __name__ == "__main__":
    gui = GameGUI()

    # Callbacks
    def start_game():
        print("Démarrage du jeu...")
        gui.change_state("game")

    def open_options():
        gui.change_state("options")

    def volume_changed(value):
        gui.settings['volume'] = value

    def fullscreen_changed(checked):
        gui.settings['fullscreen'] = checked

    def name_entered(text):
        gui.settings['player_name'] = text

    # Menu principal
    gui.add_button("main", Button(400, 200, 200, 50, "Jouer", gui.font, callback=start_game))
    gui.add_button("main", Button(400, 270, 200, 50, "Options", gui.font, callback=open_options))
    gui.add_button("main", Button(400, 340, 200, 50, "Quitter", gui.font, callback=gui.quit))

    # Menu options
    panel = Panel(250, 100, 500, 350, bg_color=(230, 230, 250))
    
    volume_slider = Slider(300, 150, 400, 10, 0, 100, 50, "Volume", gui.font, callback=volume_changed)
    panel.add_element(volume_slider)
    
    fullscreen_checkbox = Checkbox(300, 220, 30, "Mode plein écran", gui.font, callback=fullscreen_changed)
    panel.add_element(fullscreen_checkbox)
    
    name_input = InputBox(300, 280, 400, 40, gui.font, placeholder="Entrez votre nom", callback=name_entered)
    panel.add_element(name_input)
    
    gui.add_element("options", panel)
    gui.add_button("options", Button(400, 400, 200, 50, "Retour", gui.font, callback=gui.go_back))

    # Menu de jeu
    health_bar = ProgressBar(50, 50, 300, 30, 100, 75, label="Vie")
    gui.add_element("game", health_bar)
    gui.add_button("game", Button(400, 400, 200, 50, "Menu Principal", gui.font, callback=lambda: gui.change_state("main", False)))

    gui.run_menu()
    gui.save_settings()
    gui.quit()