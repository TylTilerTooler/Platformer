import pygame
import sys

class Menu:
    def __init__(self, screen, settings):
        self.screen = screen
        self.settings = settings
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.clock = pygame.time.Clock()
        
        # Using generic fonts (None) or specific ones if preferred
        self.title_font = pygame.font.SysFont(None, 100)
        self.option_font = pygame.font.SysFont(None, 60)
        
        self.options = ["Start Game", "Quit"]
        self.selected_index = 0
        
        # State management
        self.in_settings = False
        
        # Pre-calculate rectangles for each option to use as button hitboxes
        self.option_rects = []
        for i, option in enumerate(self.options):
            # Create a temporary surface to calculate the correct centered rectangle
            surf = self.option_font.render(option, True, (255, 255, 255))
            rect = surf.get_rect(center=(self.width // 2, 350 + i * 80))
            self.option_rects.append(rect)
            
        # Settings icon (Top Right)
        self.settings_rect = pygame.Rect(self.width - 80, 20, 60, 60)
        
        # Settings Page UI elements
        self.shadow_toggle_rect = pygame.Rect(self.width // 2 - 210, 150, 420, 60)
        self.daycycle_toggle_rect = pygame.Rect(self.width // 2 - 210, 225, 420, 60)
        self.weather_toggle_rect = pygame.Rect(self.width // 2 - 210, 300, 420, 60)
        self.clouds_toggle_rect = pygame.Rect(self.width // 2 - 210, 375, 420, 60)
        self.back_button_rect = pygame.Rect(self.width // 2 - 100, 480, 200, 60)

    def draw(self):
        self.screen.fill((0, 0, 0)) # BLACK
        
        if self.in_settings:
            self.draw_settings()
        else:
            self.draw_main()

    def draw_main(self):
        # Draw Settings Icon (Placeholder gear)
        pygame.draw.rect(self.screen, (255, 255, 255), self.settings_rect, 3, border_radius=10)
        s_text = self.option_font.render("S", True, (255, 255, 255))
        self.screen.blit(s_text, s_text.get_rect(center=self.settings_rect.center))
        
        title_surf = self.title_font.render("PLATFORMER", True, (255, 255, 255)) # WHITE
        title_rect = title_surf.get_rect(center=(self.width // 2, 150))
        self.screen.blit(title_surf, title_rect)
        
        for i, option in enumerate(self.options):
            color = (0, 255, 0) if i == self.selected_index else (255, 255, 255) # GREEN if selected
            option_surf = self.option_font.render(option, True, color)
            self.screen.blit(option_surf, self.option_rects[i])

    def draw_settings(self):
        # Title
        title_surf = self.title_font.render("SETTINGS", True, (255, 255, 255))
        self.screen.blit(title_surf, title_surf.get_rect(center=(self.width // 2, 70)))

        # Toggles status
        shadow_status = "ON" if self.settings["shadows"] else "OFF"
        shadow_color = (0, 255, 0) if self.settings["shadows"] else (255, 0, 0)
        daycycle_status = "ON" if self.settings["daylight_cycle"] else "OFF"
        daycycle_color = (0, 255, 0) if self.settings["daylight_cycle"] else (255, 0, 0)
        weather_status = "ON" if self.settings["weather"] else "OFF"
        weather_color = (0, 255, 0) if self.settings["weather"] else (255, 0, 0)
        clouds_status = "ON" if self.settings["clouds"] else "OFF"
        clouds_color = (0, 255, 0) if self.settings["clouds"] else (255, 0, 0)
        
        # Shadow Button
        shadow_text = self.option_font.render(f"Shadows: {shadow_status}", True, shadow_color)
        self.screen.blit(shadow_text, shadow_text.get_rect(center=self.shadow_toggle_rect.center))
        pygame.draw.rect(self.screen, shadow_color, self.shadow_toggle_rect, 2, border_radius=10)
        
        # Daycycle Button
        daycycle_text = self.option_font.render(f"Daylight Cycle: {daycycle_status}", True, daycycle_color)
        self.screen.blit(daycycle_text, daycycle_text.get_rect(center=self.daycycle_toggle_rect.center))
        pygame.draw.rect(self.screen, daycycle_color, self.daycycle_toggle_rect, 2, border_radius=10)

        # Weather Button
        weather_text = self.option_font.render(f"Weather: {weather_status}", True, weather_color)
        self.screen.blit(weather_text, weather_text.get_rect(center=self.weather_toggle_rect.center))
        pygame.draw.rect(self.screen, weather_color, self.weather_toggle_rect, 2, border_radius=10)

        # Clouds Button
        clouds_text = self.option_font.render(f"Clouds: {clouds_status}", True, clouds_color)
        self.screen.blit(clouds_text, clouds_text.get_rect(center=self.clouds_toggle_rect.center))
        pygame.draw.rect(self.screen, clouds_color, self.clouds_toggle_rect, 2, border_radius=10)

        # Back Button
        back_text = self.option_font.render("Back", True, (255, 255, 255))
        self.screen.blit(back_text, back_text.get_rect(center=self.back_button_rect.center))
        pygame.draw.rect(self.screen, (255, 255, 255), self.back_button_rect, 2, border_radius=10)

    def run(self):
        while True:
            self.clock.tick(60) # Limit CPU usage
            self.draw()
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Handle Mouse Movement (Hover)
                if event.type == pygame.MOUSEMOTION:
                    if not self.in_settings:
                        self.selected_index = -1
                        for i, rect in enumerate(self.option_rects):
                            if rect.collidepoint(event.pos):
                                self.selected_index = i

                # Handle Mouse Clicks
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left click
                        if self.in_settings:
                            # Check Shadow Toggle
                            if self.shadow_toggle_rect.collidepoint(event.pos):
                                self.settings["shadows"] = not self.settings["shadows"]
                            # Check Daylight Cycle Toggle
                            elif self.daycycle_toggle_rect.collidepoint(event.pos):
                                self.settings["daylight_cycle"] = not self.settings["daylight_cycle"]
                            elif self.weather_toggle_rect.collidepoint(event.pos):
                                self.settings["weather"] = not self.settings["weather"]
                            elif self.clouds_toggle_rect.collidepoint(event.pos):
                                self.settings["clouds"] = not self.settings["clouds"]
                            # Check Back Button
                            elif self.back_button_rect.collidepoint(event.pos):
                                self.in_settings = False
                        else:
                            # Check Settings Icon
                            if self.settings_rect.collidepoint(event.pos):
                                self.in_settings = True
                            
                            # Check Menu Options
                            for i, rect in enumerate(self.option_rects):
                                if rect.collidepoint(event.pos):
                                    if i == 0: # Start Game
                                        return
                                    elif i == 1: # Quit
                                        pygame.quit()
                                        sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.in_settings:
                            self.in_settings = False
                    elif event.key == pygame.K_UP and not self.in_settings:
                        self.selected_index = (self.selected_index - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN and not self.in_settings:
                        self.selected_index = (self.selected_index + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN and not self.in_settings:
                        if self.selected_index == 0: # Start Game
                            return
                        elif self.selected_index == 1: # Quit
                            pygame.quit()
                            sys.exit()
