# GUI/pygame.py
import pygame

class Button:
    """Classe simple pour gérer un bouton graphique."""
    def __init__(self, x, y, width, height, text, font, bg_color=(200, 200, 200), text_color=(0, 0, 0), hover_color=(150, 150, 150), shadow=True, callback=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.callback = callback
        self.shadow = shadow
        self.clicked = False

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.bg_color

        # Dessine l'ombre si activée
        if self.shadow:
            shadow_rect = self.rect.copy()
            shadow_rect.topleft = (self.rect.x + 4, self.rect.y + 4)
            pygame.draw.rect(screen, (100, 100, 100), shadow_rect, border_radius=6)

        # Dessine le bouton
        pygame.draw.rect(screen, color, self.rect, border_radius=6)

        # Dessine le texte centré
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
                return True
        return False
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if self.callback:
                self.callback()


class GameGUI:
    """Classe principale pour gérer l'interface graphique du jeu."""
    def __init__(self, width=1000, height=500, title="PFE-Roguelike", bg_color=(255, 255, 255), fps=30):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(title)
        self.bg_color = bg_color
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.font = pygame.font.Font(None, 36)
        self.running = True
        self.state = "main"
        self.buttons = {}  # Dictionnaire pour stocker les boutons par menu

    def add_button(self, menu_name, button: Button):
        """Ajoute un bouton à un menu spécifique."""
        if menu_name not in self.buttons:
            self.buttons[menu_name] = []
        self.buttons[menu_name].append(button)

    def draw_buttons(self):
        """Dessine tous les boutons du menu courant."""
        if self.state in self.buttons:
            for btn in self.buttons[self.state]:
                btn.draw(self.screen)

    def handle_events(self):
        """Gère les événements Pygame et retourne le bouton cliqué s'il y a."""
        clicked_button = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if self.state in self.buttons:
                for btn in self.buttons[self.state]:
                    btn.handle_event(event) 
                    if btn.is_clicked(event):
                        clicked_button = btn.text
        return clicked_button

    def draw_text(self, text, pos, color=(0, 0, 0)):
        """Dessine du texte simple sur l'écran."""
        self.screen.blit(self.font.render(text, True, color), pos)

    def clear_screen(self):
        """Efface l'écran avec la couleur de fond."""
        self.screen.fill(self.bg_color)

    def run_menu(self):
        """Boucle principale pour gérer le menu graphique."""
        while self.running:
            self.clear_screen()
            clicked = self.handle_events()
            if clicked:
                print(f"Bouton cliqué: {clicked}")
                # Exemple simple : changer de menu
                if clicked == "Options":
                    self.state = "options"
                elif clicked == "Retour":
                    self.state = "main"
            self.draw_buttons()
            pygame.display.flip()
            self.clock.tick(self.fps)

    def quit(self):
        pygame.quit()


# Exemple d'utilisation
if __name__ == "__main__":
    gui = GameGUI()

    # Menu principal
    gui.add_button("main", Button(400, 200, 200, 50, "Jouer", gui.font))
    gui.add_button("main", Button(400, 300, 200, 50, "Options", gui.font))

    # Menu options
    gui.add_button("options", Button(400, 400, 200, 50, "Retour", gui.font))

    gui.run_menu()
    gui.quit()
