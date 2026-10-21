import os
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock
import random
import pygame

# --- НАСТРОЙКИ ---
Window.clearcolor = (0.04, 0.04, 0.04, 1) # Тёмный фон
STORIES_DIR = "stories"
SOUND_FILE = "hum.wav"

# Цвета для Kivy
GREEN = (0, 1, 0, 1)
CYAN = (0, 0.8, 0.53, 1)
WHITE = (1, 1, 1, 1)
GRAY = (0.5, 0.5, 0.5, 1)

class CryptArchiveApp(App):
    def build(self):
        self.title = "CryptArchive // Mobile"
        self.images = []
        
        main_layout = BoxLayout(orientation='horizontal')
        
        # --- ЛЕВАЯ ПАНЕЛЬ (СПИСОК) ---
        sidebar = BoxLayout(orientation='vertical', size_hint_x=0.35, padding=dp(10), spacing=dp(5))
        sidebar.add_widget(Label(text=">>> LIST", color=GRAY, font_size='14sp', size_hint_y=None, height=dp(30)))
        
        scroll = ScrollView(size_hint=(1, 1))
        list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        self.stories = self.load_stories()
        for story in self.stories:
            btn = Button(text=story["title"], color=GREEN, background_color=(0,0,0,0), 
                         size_hint_y=None, height=dp(40), halign='left', valign='middle')
            btn.bind(on_release=lambda instance, s=story: self.open_story(s))
            list_layout.add_widget(btn)
            
        scroll.add_widget(list_layout)
        sidebar.add_widget(scroll)
        
        # --- ПРАВАЯ ПАНЕЛЬ (ТЕКСТ) ---
        right_panel = BoxLayout(orientation='vertical', size_hint_x=0.65, padding=dp(10))
        self.text_scroll = ScrollView(size_hint=(1, 1))
        self.text_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        self.text_layout.bind(minimum_height=self.text_layout.setter('height'))
        
        self.text_scroll.add_widget(self.text_layout)
        right_panel.add_widget(self.text_scroll)
        
        main_layout.add_widget(sidebar)
        main_layout.add_widget(right_panel)
        
        Clock.schedule_once(lambda dt: self.init_sound(), 1)
        return main_layout

    def load_stories(self):
        stories = []
        if not os.path.exists(STORIES_DIR):
            os.makedirs(STORIES_DIR)
            return stories
            
        for folder in os.listdir(STORIES_DIR):
            folder_path = os.path.join(STORIES_DIR, folder)
            if os.path.isdir(folder_path):
                for file in os.listdir(folder_path):
                    if file.endswith(".md"):
                        md_file = os.path.join(folder_path, file)
                        title = folder
                        try:
                            with open(md_file, "r", encoding="utf-8-sig") as f:
                                first_line = f.readline().replace("\r", "").strip()
                                if first_line.startswith("#") or first_line.startswith("\\#"):
                                    title = first_line.replace("\\", "").replace("#", "").strip()
                        except:
                            pass
                        stories.append({"path": md_file, "title": title})
                        break
        stories.sort(key=lambda x: x["title"])
        return stories

    def open_story(self, story):
        self.text_layout.clear_widgets()
        self.images.clear()
        
        try:
            with open(story["path"], "r", encoding="utf-8-sig") as f:
                content = f.read()

            lines = content.split("\n")
            for line in lines:
                clean_line = line.replace("\r", "").replace("\\", "").strip()
                if not clean_line:
                    continue
                
                if clean_line.startswith("### ") or clean_line.startswith("## "):
                    text = clean_line.replace("###", "").replace("##", "").strip()
                    lbl = Label(text=text, color=CYAN, font_size='16sp', bold=True, 
                                size_hint_y=None, text_size=(self.root.width, None), halign='left')
                    lbl.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
                    self.text_layout.add_widget(lbl)
                
                elif clean_line.startswith("# "):
                    text = clean_line.replace("#", "").strip()
                    lbl = Label(text=text, color=CYAN, font_size='20sp', bold=True, 
                                size_hint_y=None, text_size=(self.root.width, None), halign='left')
                    lbl.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
                    self.text_layout.add_widget(lbl)
                
                elif clean_line.startswith("![") and "](" in clean_line:
                    match = re.search(r'!\[.*?\]\((.*?)\)', clean_line)
                    if match:
                        img_name = match.group(1)
                        img_path = os.path.join(os.path.dirname(story["path"]), img_name)
                        if os.path.exists(img_path):
                            img = Image(source=img_path, size_hint_y=None, height=dp(250), allow_stretch=True)
                            self.text_layout.add_widget(img)
                        else:
                            self.text_layout.add_widget(Label(text="[Image not found]", color=(1,0,0,1)))
                
                elif clean_line == "---":
                    self.text_layout.add_widget(Label(text="—"*30, color=GRAY, size_hint_y=None))
                
                else:
                    parts = re.split(r'(\*\*.*?\*\*)', clean_line)
                    for part in parts:
                        if part.startswith("**") and part.endswith("**"):
                            text = part[2:-2]
                            lbl = Label(text=text, color=WHITE, font_size='14sp', bold=True,
                                        size_hint_y=None, text_size=(self.root.width, None), halign='left')
                        else:
                            if not part: continue
                            lbl = Label(text=part, color=GREEN, font_size='14sp',
                                        size_hint_y=None, text_size=(self.root.width, None), halign='left')
                        
                        lbl.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
                        self.text_layout.add_widget(lbl)
                        
        except Exception as e:
            self.text_layout.add_widget(Label(text=f"ERROR: {e}", color=(1,0,0,1)))

    def init_sound(self):
        try:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(0.1)
            self.play_hum()
        except Exception as e:
            print("Sound error:", e)

    def play_hum(self, *args):
        try:
            if os.path.exists(SOUND_FILE):
                pygame.mixer.music.load(SOUND_FILE)
                pygame.mixer.music.play()
                Clock.schedule_once(self.stop_hum, 2)
        except:
            pass

    def stop_hum(self, *args):
        try:
            pygame.mixer.music.stop()
        except:
            pass
        delay = random.randint(5, 15)
        Clock.schedule_once(self.play_hum, delay)

if __name__ == "__main__":
    app = CryptArchiveApp()
    app.run()