import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from pathlib import Path
import os
import shutil
import uuid
import zipfile
import tempfile
import webbrowser
import platform
from datetime import datetime

class Editor:
    def __init__(self, root, project_path):
        self.root = root
        self.project_path = project_path
        
        # Set behavior pack and resource pack paths
        self.bp_path = project_path / "behavior_pack"
        self.rp_path = project_path / "resource_pack"
        
        # Load project configuration
        self.load_project_config()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="5")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create menu bar
        self.create_menu()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create left and right panels
        self.create_panels()
        
    def load_project_config(self):
        """Load project configuration"""
        config_path = self.project_path / "project.json"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    self.project_config = json.load(f)
            except:
                self.project_config = {"name": self.project_path.name}
        else:
            self.project_config = {"name": self.project_path.name}
    
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save", command=self.save_all, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export Addon", command=self.export_addon)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        
        # Behavior Pack menu
        bp_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Behavior Pack (BP)", menu=bp_menu)
        bp_menu.add_command(label="Add Item", command=lambda: self.show_config_tab("Item Configuration (BP)"))
        bp_menu.add_command(label="Add Block", command=lambda: self.show_config_tab("Block Configuration (BP)"))
        bp_menu.add_command(label="Add Entity", command=lambda: self.show_config_tab("Entity Configuration (BP)"))
        bp_menu.add_command(label="Add Recipe", command=lambda: self.show_config_tab("Recipe Configuration (BP)"))
        bp_menu.add_command(label="Add Loot Table", command=lambda: self.show_config_tab("Loot Table Configuration (BP)"))
        bp_menu.add_separator()
        bp_menu.add_command(label="Add Item Tab", command=lambda: self.show_config_tab("Item Tab Configuration (BP)"))
        bp_menu.add_separator()
        bp_menu.add_command(label="Add Structure", command=lambda: self.show_config_tab("Structure Configuration (BP)"))
        bp_menu.add_command(label="Add Biome", command=lambda: self.show_config_tab("Biome Configuration (BP)"))
        bp_menu.add_command(label="Add Dimension", command=lambda: self.show_config_tab("Dimension Configuration (BP)"))
        
        # Resource Pack menu
        rp_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Resource Pack (RP)", menu=rp_menu)
        rp_menu.add_command(label="Add Item Texture", command=lambda: self.show_config_tab("Item Texture (RP)"))
        rp_menu.add_command(label="Add Block Texture", command=lambda: self.show_config_tab("Block Texture (RP)"))
        rp_menu.add_command(label="Add Entity Texture", command=lambda: self.show_config_tab("Entity Texture (RP)"))
        rp_menu.add_command(label="Add Model", command=lambda: self.show_config_tab("Model Configuration (RP)"))
        rp_menu.add_command(label="Add Language File", command=lambda: self.show_config_tab("Language File (RP)"))
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Validate Project Structure", command=self.validate_project)
        tools_menu.add_command(label="Regenerate UUIDs", command=self.regenerate_uuids)
        tools_menu.add_separator()
        tools_menu.add_command(label="Open Behavior Pack Folder", command=lambda: self.open_folder(self.bp_path))
        tools_menu.add_command(label="Open Resource Pack Folder", command=lambda: self.open_folder(self.rp_path))
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Official Documentation", command=self.open_docs)
    
    def create_toolbar(self):
        """Create toolbar"""
        toolbar = ttk.Frame(self.main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Quick add buttons
        ttk.Button(toolbar, text="Save", command=self.save_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Item", command=lambda: self.show_config_tab("Item Configuration (BP)")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Block", command=lambda: self.show_config_tab("Block Configuration (BP)")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Entity", command=lambda: self.show_config_tab("Entity Configuration (BP)")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Recipe", command=lambda: self.show_config_tab("Recipe Configuration (BP)")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Loot Table", command=lambda: self.show_config_tab("Loot Table Configuration (BP)")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Item Tab", command=lambda: self.show_config_tab("Item Tab Configuration (BP)")).pack(side=tk.LEFT, padx=2)
        
        # Project info display
        info_frame = ttk.Frame(toolbar)
        info_frame.pack(side=tk.RIGHT, padx=5)
        
        project_label = ttk.Label(info_frame, text=f"Project: {self.project_path.name}")
        project_label.pack(side=tk.TOP, anchor=tk.E)
        
        version = self.project_config.get("version", [1, 0, 0])
        version_str = f"v{version[0]}.{version[1]}.{version[2]}"
        version_label = ttk.Label(info_frame, text=version_str, foreground="gray")
        version_label.pack(side=tk.BOTTOM, anchor=tk.E)
    
    def create_panels(self):
        """Create left and right panels"""
        # Use PanedWindow
        paned = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - File browser
        left_frame = ttk.Frame(paned, padding="5", width=250)
        paned.add(left_frame, weight=1)
        
        # Create tabs to separate BP and RP
        file_notebook = ttk.Notebook(left_frame)
        file_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Behavior Pack tab
        bp_frame = ttk.Frame(file_notebook)
        file_notebook.add(bp_frame, text="Behavior Pack (BP)")
        self.create_file_tree(bp_frame, self.bp_path, "bp")
        
        # Resource Pack tab
        rp_frame = ttk.Frame(file_notebook)
        file_notebook.add(rp_frame, text="Resource Pack (RP)")
        self.create_file_tree(rp_frame, self.rp_path, "rp")
        
        # Right panel - Edit area
        right_frame = ttk.Frame(paned, padding="5")
        paned.add(right_frame, weight=3)
        
        # Create notebook
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Welcome tab
        welcome_frame = ttk.Frame(self.notebook)
        self.notebook.add(welcome_frame, text="Welcome")
        
        welcome_text = f"""Welcome to editing project: {self.project_path.name}

Project Information:
- Behavior Pack Path: {self.bp_path}
- Resource Pack Path: {self.rp_path}
- Version: {self.project_config.get('version', [1,0,0])}
- Game Version: {self.project_config.get('min_engine_version', [1,20,0])}

Supported Features:
✅ Item Configuration
✅ Block Configuration
✅ Entity Configuration
✅ Recipe Configuration
✅ Loot Table Configuration
✅ Item Tab Configuration
⏳ Structure Configuration (In Development)
⏳ Biome Configuration (In Development)
⏳ Dimension Configuration (In Development)

Instructions:
1. Select Behavior Pack or Resource Pack files on the left
2. Double-click files to edit
3. Use menu or toolbar to add new configurations

Reference Documentation: https://learn.microsoft.com/en-us/minecraft/creator/"""
        
        welcome_label = ttk.Label(welcome_frame, text=welcome_text,
                                 font=("Segoe UI", 11),
                                 justify=tk.LEFT)
        welcome_label.pack(expand=True, padx=20, pady=20)
        
        # Store opened tabs
        self.open_tabs = {}
    
    def create_file_tree(self, parent, root_path, tree_id):
        """Create file tree"""
        # Create frame
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Create tree
        tree = ttk.Treeview(frame, show="tree", height=20)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.config(yscrollcommand=scrollbar.set)
        
        # Store tree reference
        if not hasattr(self, 'file_trees'):
            self.file_trees = {}
        self.file_trees[tree_id] = tree
        
        # Load files
        self.load_file_tree_node(tree, "", root_path, root_path.name)
        
        # Bind double-click event
        tree.bind("<Double-1>", lambda e: self.open_file_from_tree(e, tree, root_path))
    
    def load_file_tree_node(self, tree, parent, path, node_text):
        """Recursively load file tree nodes"""
        if not path.exists():
            node = tree.insert(parent, "end", text=f"{node_text} (does not exist)", open=True)
            return
        
        node = tree.insert(parent, "end", text=node_text, open=True)
        
        try:
            # Add folders first
            folders = []
            files = []
            
            for item in path.iterdir():
                if item.is_dir():
                    folders.append(item)
                else:
                    files.append(item)
            
            # Sort
            folders.sort(key=lambda x: x.name)
            files.sort(key=lambda x: x.name)
            
            # Add folders
            for folder in folders:
                self.load_file_tree_node(tree, node, folder, folder.name)
            
            # Add files
            for file in files:
                # Set different icon tags based on file type
                tags = []
                if file.suffix == '.json':
                    tags.append('json')
                elif file.suffix in ['.png', '.jpg', '.tga']:
                    tags.append('image')
                elif file.suffix == '.lang':
                    tags.append('lang')
                elif file.suffix == '.js':
                    tags.append('script')
                elif file.suffix == '.mcfunction':
                    tags.append('function')
                
                tree.insert(node, "end", text=file.name, tags=tags)
            
        except Exception as e:
            print(f"Failed to load file tree: {e}")
    
    def open_file_from_tree(self, event, tree, root_path):
        """Open file from file tree"""
        selection = tree.selection()
        if not selection:
            return
        
        item = selection[0]
        item_text = tree.item(item, "text")
        
        # Check if it's a file (has extension)
        if "." not in item_text:
            return
        
        # Get full path
        path_parts = []
        current = item
        while current:
            text = tree.item(current, "text")
            path_parts.insert(0, text)
            current = tree.parent(current)
        
        # Build file path
        # First part is the root node name, skip it
        if len(path_parts) > 1:
            file_path = root_path
            for part in path_parts[1:-1]:  # Skip root node and file name
                file_path = file_path / part
            file_path = file_path / path_parts[-1]
            
            if file_path.exists() and file_path.is_file():
                self.open_file_in_tab(file_path)
    
    def open_file_in_tab(self, file_path):
        """Open file in tab"""
        tab_name = f"{file_path.parent.name}/{file_path.name}"
        
        if tab_name in self.open_tabs:
            self.notebook.select(self.open_tabs[tab_name])
            return
        
        # Create new tab
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=tab_name)
        self.open_tabs[tab_name] = tab_frame
        self.notebook.select(tab_frame)
        
        # Display content based on file type
        if file_path.suffix == ".json":
            self.display_json_file(tab_frame, file_path)
        elif file_path.suffix == ".lang":
            self.display_text_file(tab_frame, file_path)
        elif file_path.suffix in [".png", ".jpg"]:
            self.display_image_info(tab_frame, file_path)
        else:
            self.display_text_file(tab_frame, file_path)
    
    def display_json_file(self, parent, file_path):
        """Display JSON file content"""
        # Create text box
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        text_widget = tk.Text(text_frame, wrap=tk.NONE)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbars
        scrollbar_y = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar_y.set)
        
        scrollbar_x = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=text_widget.xview)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        text_widget.config(xscrollcommand=scrollbar_x.set)
        
        # Load file content
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Format JSON
                try:
                    json_obj = json.loads(content)
                    formatted = json.dumps(json_obj, indent=2, ensure_ascii=False)
                    text_widget.insert(1.0, formatted)
                except:
                    text_widget.insert(1.0, content)
        except Exception as e:
            text_widget.insert(1.0, f"Unable to read file: {str(e)}")
        
        # Save button
        save_btn = ttk.Button(parent, text="Save Changes", 
                             command=lambda: self.save_json_file(file_path, text_widget))
        save_btn.pack(pady=5)
    
    def display_text_file(self, parent, file_path):
        """Display text file content"""
        text_widget = tk.Text(parent, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text_widget.insert(1.0, f.read())
        except:
            text_widget.insert(1.0, "Unable to read file")
    
    def display_image_info(self, parent, file_path):
        """Display image information"""
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(info_frame, text="Image File Information", font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        info_text = f"""
File Name: {file_path.name}
Path: {file_path}
Size: {file_path.stat().st_size} bytes
Type: {file_path.suffix}
        """
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(pady=10)
        
        ttk.Label(info_frame, text="Tip: Use an external image editor to edit this file").pack(pady=10)
        
        ttk.Button(info_frame, text="Open Folder", 
                  command=lambda: self.open_folder(file_path.parent)).pack(pady=5)
    
    def save_json_file(self, file_path, text_widget):
        """Save JSON file"""
        content = text_widget.get(1.0, tk.END).strip()
        try:
            # Validate JSON
            json.loads(content)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            messagebox.showinfo("Success", f"File saved: {file_path}")
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"JSON format error: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {str(e)}")
    
    def show_config_tab(self, tab_name):
        """Show configuration tab"""
        if tab_name in self.open_tabs:
            self.notebook.select(self.open_tabs[tab_name])
            return
        
        # Create new tab
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=tab_name)
        self.open_tabs[tab_name] = tab_frame
        self.notebook.select(tab_frame)
        
        # Create corresponding configuration interface based on tab name
        if tab_name == "Item Configuration (BP)":
            self.create_item_config(tab_frame)
        elif tab_name == "Block Configuration (BP)":
            self.create_block_config(tab_frame)
        elif tab_name == "Entity Configuration (BP)":
            self.create_entity_config(tab_frame)
        elif tab_name == "Recipe Configuration (BP)":
            self.create_recipe_config(tab_frame)
        elif tab_name == "Loot Table Configuration (BP)":
            self.create_loot_table_config(tab_frame)
        elif tab_name == "Item Tab Configuration (BP)":
            self.create_item_tab_config(tab_frame)
        elif tab_name == "Structure Configuration (BP)":
            self.create_placeholder_config(tab_frame, "Structure Configuration (In Development)")
        elif tab_name == "Biome Configuration (BP)":
            self.create_placeholder_config(tab_frame, "Biome Configuration (In Development)")
        elif tab_name == "Dimension Configuration (BP)":
            self.create_placeholder_config(tab_frame, "Dimension Configuration (In Development)")
        elif tab_name == "Item Texture (RP)":
            self.create_item_texture_config(tab_frame)
        elif tab_name in ["Block Texture (RP)", "Entity Texture (RP)", "Model Configuration (RP)", "Language File (RP)"]:
            self.create_placeholder_config(tab_frame, "Resource Pack configuration in development...")
        else:
            self.create_placeholder_config(tab_frame, "Configuration in development...")
    
    def create_placeholder_config(self, parent, message):
        """Create placeholder configuration interface"""
        label = ttk.Label(parent, text=message, font=("Segoe UI", 14))
        label.pack(expand=True)
    
    # ==================== Item Configuration ====================
    def create_item_config(self, parent):
        """Create item configuration interface"""
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_label = ttk.Label(scrollable_frame, text="Item Configuration (Behavior Pack)", 
                               font=("Segoe UI", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="w")
        
        # Description
        desc_label = ttk.Label(scrollable_frame, 
                              text="Define item behavior properties in the behavior pack\n"
                                   "Corresponding textures need to be configured in the resource pack",
                              justify=tk.LEFT)
        desc_label.grid(row=1, column=0, columnspan=3, pady=5, padx=10, sticky="w")
        
        # Basic information frame
        basic_frame = ttk.LabelFrame(scrollable_frame, text="Basic Information", padding="10")
        basic_frame.grid(row=2, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # Item identifier
        ttk.Label(basic_frame, text="Item Identifier:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.item_identifier = ttk.Entry(basic_frame, width=40)
        self.item_identifier.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(basic_frame, text="e.g., wiki:example_item", foreground="gray").grid(row=0, column=2, pady=5, padx=5, sticky="w")
        
        # Display name
        ttk.Label(basic_frame, text="Display Name:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.item_display_name = ttk.Entry(basic_frame, width=40)
        self.item_display_name.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        
        # Description
        ttk.Label(basic_frame, text="Item Description:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.item_description = ttk.Entry(basic_frame, width=40)
        self.item_description.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        
        # Category
        ttk.Label(basic_frame, text="Category:").grid(row=3, column=0, pady=5, padx=5, sticky="w")
        self.item_category = ttk.Combobox(basic_frame, values=["items", "equipment", "nature", "construction"], width=20)
        self.item_category.grid(row=3, column=1, pady=5, padx=5, sticky="w")
        self.item_category.set("items")
        
        # Components frame
        components_frame = ttk.LabelFrame(scrollable_frame, text="Component Configuration", padding="10")
        components_frame.grid(row=3, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # Create notebook
        component_notebook = ttk.Notebook(components_frame)
        component_notebook.grid(row=0, column=0, columnspan=3, pady=5, sticky="ew")
        
        # Basic components tab
        basic_comp_frame = ttk.Frame(component_notebook)
        component_notebook.add(basic_comp_frame, text="Basic Components")
        
        # Max stack size
        ttk.Label(basic_comp_frame, text="Max Stack Size:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.max_stack_size = ttk.Spinbox(basic_comp_frame, from_=1, to=64, width=10)
        self.max_stack_size.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        self.max_stack_size.insert(0, "64")
        
        # Hand equipped
        self.hand_equipped = tk.BooleanVar(value=True)
        ttk.Checkbutton(basic_comp_frame, text="Hand Equipped", variable=self.hand_equipped).grid(row=1, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        # Durability tab
        durability_frame = ttk.Frame(component_notebook)
        component_notebook.add(durability_frame, text="Durability")
        
        self.has_durability = tk.BooleanVar(value=False)
        ttk.Checkbutton(durability_frame, text="Enable Durability", variable=self.has_durability, 
                       command=self.toggle_durability).grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        ttk.Label(durability_frame, text="Max Durability:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.max_durability = ttk.Spinbox(durability_frame, from_=1, to=10000, width=10, state="disabled")
        self.max_durability.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        self.max_durability.insert(0, "100")
        
        # Food tab
        food_frame = ttk.Frame(component_notebook)
        component_notebook.add(food_frame, text="Food")
        
        self.is_food = tk.BooleanVar(value=False)
        ttk.Checkbutton(food_frame, text="Can be used as food", variable=self.is_food,
                       command=self.toggle_food).grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        ttk.Label(food_frame, text="Nutrition:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.nutrition = ttk.Spinbox(food_frame, from_=1, to=20, width=10, state="disabled")
        self.nutrition.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        self.nutrition.insert(0, "4")
        
        ttk.Label(food_frame, text="Saturation:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.saturation = ttk.Spinbox(food_frame, from_=0, to=20, width=10, state="disabled")
        self.saturation.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        self.saturation.insert(0, "2")
        
        # Weapon tab
        weapon_frame = ttk.Frame(component_notebook)
        component_notebook.add(weapon_frame, text="Weapon")
        
        self.is_weapon = tk.BooleanVar(value=False)
        ttk.Checkbutton(weapon_frame, text="Can be used as weapon", variable=self.is_weapon,
                       command=self.toggle_weapon).grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        ttk.Label(weapon_frame, text="Damage Value:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.damage = ttk.Spinbox(weapon_frame, from_=1, to=100, width=10, state="disabled")
        self.damage.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        self.damage.insert(0, "5")
        
        # Save path frame
        path_frame = ttk.LabelFrame(scrollable_frame, text="Save Path", padding="10")
        path_frame.grid(row=4, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        ttk.Label(path_frame, text="File Name:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.item_filename = ttk.Entry(path_frame, width=40)
        self.item_filename.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(path_frame, text=".json", foreground="gray").grid(row=0, column=2, pady=5, padx=0, sticky="w")
        
        # Button frame
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        ttk.Button(btn_frame, text="Generate JSON", command=self.generate_item_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save to Behavior Pack", command=self.save_item_to_behavior).pack(side=tk.LEFT, padx=5)
        
        # JSON preview frame
        preview_frame = ttk.LabelFrame(scrollable_frame, text="JSON Preview", padding="10")
        preview_frame.grid(row=6, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        self.item_json_preview = tk.Text(preview_frame, height=15, width=80)
        self.item_json_preview.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        preview_scrollbar = ttk.Scrollbar(self.item_json_preview, orient=tk.VERTICAL, command=self.item_json_preview.yview)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.item_json_preview.config(yscrollcommand=preview_scrollbar.set)
    
    # ==================== Block Configuration ====================
    def create_block_config(self, parent):
        """Create block configuration interface"""
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_label = ttk.Label(scrollable_frame, text="Block Configuration (Behavior Pack)", 
                               font=("Segoe UI", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="w")
        
        # Description
        desc_label = ttk.Label(scrollable_frame, 
                              text="Define custom block behaviors and properties in the behavior pack\n"
                                   "Corresponding models and textures need to be configured in the resource pack",
                              justify=tk.LEFT)
        desc_label.grid(row=1, column=0, columnspan=3, pady=5, padx=10, sticky="w")
        
        # Basic information frame
        basic_frame = ttk.LabelFrame(scrollable_frame, text="Basic Information", padding="10")
        basic_frame.grid(row=2, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # Block identifier
        ttk.Label(basic_frame, text="Block Identifier:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.block_identifier = ttk.Entry(basic_frame, width=40)
        self.block_identifier.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(basic_frame, text="e.g., wiki:example_block", foreground="gray").grid(row=0, column=2, pady=5, padx=5, sticky="w")
        
        # Display name
        ttk.Label(basic_frame, text="Display Name:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.block_display_name = ttk.Entry(basic_frame, width=40)
        self.block_display_name.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        
        # Category
        ttk.Label(basic_frame, text="Category:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.block_category = ttk.Combobox(basic_frame, values=["construction", "nature", "equipment", "items"], width=20)
        self.block_category.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        self.block_category.set("construction")
        
        # Components frame
        components_frame = ttk.LabelFrame(scrollable_frame, text="Component Configuration", padding="10")
        components_frame.grid(row=3, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # Create notebook
        component_notebook = ttk.Notebook(components_frame)
        component_notebook.grid(row=0, column=0, columnspan=3, pady=5, sticky="ew")
        
        # Basic properties tab
        basic_prop_frame = ttk.Frame(component_notebook)
        component_notebook.add(basic_prop_frame, text="Basic Properties")
        
        # Hardness
        ttk.Label(basic_prop_frame, text="Hardness:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.block_hardness = ttk.Spinbox(basic_prop_frame, from_=0, to=100, width=10)
        self.block_hardness.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        self.block_hardness.insert(0, "1.5")
        
        # Explosion resistance
        ttk.Label(basic_prop_frame, text="Explosion Resistance:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.block_resistance = ttk.Spinbox(basic_prop_frame, from_=0, to=100, width=10)
        self.block_resistance.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        self.block_resistance.insert(0, "10")
        
        # Light emission
        ttk.Label(basic_prop_frame, text="Light Emission:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.block_light_emission = ttk.Spinbox(basic_prop_frame, from_=0, to=15, width=10)
        self.block_light_emission.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        self.block_light_emission.insert(0, "0")
        
        # Transparent
        self.block_transparent = tk.BooleanVar(value=False)
        ttk.Checkbutton(basic_prop_frame, text="Transparent Block", variable=self.block_transparent).grid(row=3, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        # Flammable
        self.block_flammable = tk.BooleanVar(value=False)
        ttk.Checkbutton(basic_prop_frame, text="Flammable", variable=self.block_flammable).grid(row=4, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        # Replaceable
        self.block_replaceable = tk.BooleanVar(value=False)
        ttk.Checkbutton(basic_prop_frame, text="Replaceable", variable=self.block_replaceable).grid(row=5, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        # Loot tab
        loot_frame = ttk.Frame(component_notebook)
        component_notebook.add(loot_frame, text="Loot")
        
        ttk.Label(loot_frame, text="Loot Item:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.block_loot_item = ttk.Entry(loot_frame, width=30)
        self.block_loot_item.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        
        ttk.Label(loot_frame, text="Loot Count:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.block_loot_count = ttk.Spinbox(loot_frame, from_=1, to=64, width=10)
        self.block_loot_count.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        self.block_loot_count.insert(0, "1")
        
        # Geometry tab
        geometry_frame = ttk.Frame(component_notebook)
        component_notebook.add(geometry_frame, text="Geometry")
        
        ttk.Label(geometry_frame, text="Geometry Identifier:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.block_geometry = ttk.Entry(geometry_frame, width=30)
        self.block_geometry.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(geometry_frame, text="e.g., geometry.example_block", foreground="gray").grid(row=0, column=2, pady=5, padx=5, sticky="w")
        
        self.block_unit_cube = tk.BooleanVar(value=True)
        ttk.Checkbutton(geometry_frame, text="Use Unit Cube", variable=self.block_unit_cube).grid(row=1, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        # Material tab
        material_frame = ttk.Frame(component_notebook)
        component_notebook.add(material_frame, text="Material")
        
        ttk.Label(material_frame, text="Material Instance:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.block_material = ttk.Combobox(material_frame, values=["opaque", "alpha_test", "blend"], width=20)
        self.block_material.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        self.block_material.set("opaque")
        
        ttk.Label(material_frame, text="Texture:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.block_texture = ttk.Entry(material_frame, width=30)
        self.block_texture.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(material_frame, text="e.g., wiki:example_block", foreground="gray").grid(row=1, column=2, pady=5, padx=5, sticky="w")
        
        # Save path frame
        path_frame = ttk.LabelFrame(scrollable_frame, text="Save Path", padding="10")
        path_frame.grid(row=4, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        ttk.Label(path_frame, text="File Name:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.block_filename = ttk.Entry(path_frame, width=40)
        self.block_filename.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(path_frame, text=".json", foreground="gray").grid(row=0, column=2, pady=5, padx=0, sticky="w")
        
        # Button frame
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        ttk.Button(btn_frame, text="Generate JSON", command=self.generate_block_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save to Behavior Pack", command=self.save_block_to_behavior).pack(side=tk.LEFT, padx=5)
        
        # JSON preview frame
        preview_frame = ttk.LabelFrame(scrollable_frame, text="JSON Preview", padding="10")
        preview_frame.grid(row=6, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        self.block_json_preview = tk.Text(preview_frame, height=15, width=80)
        self.block_json_preview.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        preview_scrollbar = ttk.Scrollbar(self.block_json_preview, orient=tk.VERTICAL, command=self.block_json_preview.yview)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.block_json_preview.config(yscrollcommand=preview_scrollbar.set)
    
    # ==================== Entity Configuration ====================
    def create_entity_config(self, parent):
        """Create entity configuration interface"""
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_label = ttk.Label(scrollable_frame, text="Entity Configuration (Behavior Pack)", 
                               font=("Segoe UI", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="w")
        
        # Description
        desc_label = ttk.Label(scrollable_frame, 
                              text="Define custom entity behaviors and properties in the behavior pack\n"
                                   "Corresponding models and textures need to be configured in the resource pack",
                              justify=tk.LEFT)
        desc_label.grid(row=1, column=0, columnspan=3, pady=5, padx=10, sticky="w")
        
        # Basic information frame
        basic_frame = ttk.LabelFrame(scrollable_frame, text="Basic Information", padding="10")
        basic_frame.grid(row=2, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # Entity identifier
        ttk.Label(basic_frame, text="Entity Identifier:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.entity_identifier = ttk.Entry(basic_frame, width=40)
        self.entity_identifier.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(basic_frame, text="e.g., wiki:example_entity", foreground="gray").grid(row=0, column=2, pady=5, padx=5, sticky="w")
        
        # Display name
        ttk.Label(basic_frame, text="Display Name:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.entity_display_name = ttk.Entry(basic_frame, width=40)
        self.entity_display_name.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        
        # Entity type
        ttk.Label(basic_frame, text="Entity Type:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.entity_type = ttk.Combobox(basic_frame, values=["animal", "monster", "npc", "ambient"], width=20)
        self.entity_type.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        self.entity_type.set("animal")
        
        # Components frame
        components_frame = ttk.LabelFrame(scrollable_frame, text="Component Configuration", padding="10")
        components_frame.grid(row=3, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # Create notebook
        component_notebook = ttk.Notebook(components_frame)
        component_notebook.grid(row=0, column=0, columnspan=3, pady=5, sticky="ew")
        
        # Basic properties tab
        basic_prop_frame = ttk.Frame(component_notebook)
        component_notebook.add(basic_prop_frame, text="Basic Properties")
        
        # Health
        ttk.Label(basic_prop_frame, text="Max Health:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.entity_health = ttk.Spinbox(basic_prop_frame, from_=1, to=1000, width=10)
        self.entity_health.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        self.entity_health.insert(0, "20")
        
        # Movement speed
        ttk.Label(basic_prop_frame, text="Movement Speed:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.entity_speed = ttk.Spinbox(basic_prop_frame, from_=0.1, to=10, increment=0.1, width=10)
        self.entity_speed.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        self.entity_speed.insert(0, "0.25")
        
        # Attack damage
        ttk.Label(basic_prop_frame, text="Attack Damage:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.entity_damage = ttk.Spinbox(basic_prop_frame, from_=0, to=100, width=10)
        self.entity_damage.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        self.entity_damage.insert(0, "0")
        
        # Knockback resistance
        ttk.Label(basic_prop_frame, text="Knockback Resistance:").grid(row=3, column=0, pady=5, padx=5, sticky="w")
        self.entity_knockback_resistance = ttk.Spinbox(basic_prop_frame, from_=0, to=1, increment=0.1, width=10)
        self.entity_knockback_resistance.grid(row=3, column=1, pady=5, padx=5, sticky="w")
        self.entity_knockback_resistance.insert(0, "0")
        
        # Behavior tab
        behavior_frame = ttk.Frame(component_notebook)
        component_notebook.add(behavior_frame, text="Behavior")
        
        self.entity_friendly = tk.BooleanVar(value=True)
        ttk.Checkbutton(behavior_frame, text="Passive Mob", variable=self.entity_friendly).grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        self.entity_baby = tk.BooleanVar(value=False)
        ttk.Checkbutton(behavior_frame, text="Breedable", variable=self.entity_baby).grid(row=1, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        ttk.Label(behavior_frame, text="Behavior Template:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.entity_behavior = ttk.Combobox(behavior_frame, 
                                           values=["idle", "walk", "look", "panic", "follow_owner"], 
                                           width=20)
        self.entity_behavior.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        
        # Equipment tab
        equipment_frame = ttk.Frame(component_notebook)
        component_notebook.add(equipment_frame, text="Equipment")
        
        self.entity_equipment = tk.BooleanVar(value=False)
        ttk.Checkbutton(equipment_frame, text="Can Equip Items", variable=self.entity_equipment).grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        ttk.Label(equipment_frame, text="Equipment Table:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.entity_equipment_table = ttk.Entry(equipment_frame, width=30)
        self.entity_equipment_table.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        
        # Loot tab
        loot_frame = ttk.Frame(component_notebook)
        component_notebook.add(loot_frame, text="Loot")
        
        ttk.Label(loot_frame, text="Loot Table:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.entity_loot_table = ttk.Entry(loot_frame, width=30)
        self.entity_loot_table.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(loot_frame, text="e.g., loot_tables/entities/example.json", foreground="gray").grid(row=0, column=2, pady=5, padx=5, sticky="w")
        
        # Spawn rules tab
        spawn_frame = ttk.Frame(component_notebook)
        component_notebook.add(spawn_frame, text="Spawn Rules")
        
        self.entity_spawnable = tk.BooleanVar(value=True)
        ttk.Checkbutton(spawn_frame, text="Allow Natural Spawning", variable=self.entity_spawnable).grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        ttk.Label(spawn_frame, text="Biome:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.entity_biome = ttk.Combobox(spawn_frame, 
                                        values=["plains", "desert", "forest", "taiga", "swamp", "jungle"], 
                                        width=20)
        self.entity_biome.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        
        ttk.Label(spawn_frame, text="Spawn Weight:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.entity_spawn_weight = ttk.Spinbox(spawn_frame, from_=1, to=100, width=10)
        self.entity_spawn_weight.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        self.entity_spawn_weight.insert(0, "10")
        
        # Minimum spawn count
        ttk.Label(spawn_frame, text="Minimum Spawn:").grid(row=3, column=0, pady=5, padx=5, sticky="w")
        self.entity_spawn_min = ttk.Spinbox(spawn_frame, from_=1, to=10, width=10)
        self.entity_spawn_min.grid(row=3, column=1, pady=5, padx=5, sticky="w")
        self.entity_spawn_min.insert(0, "2")
        
        # Maximum spawn count
        ttk.Label(spawn_frame, text="Maximum Spawn:").grid(row=4, column=0, pady=5, padx=5, sticky="w")
        self.entity_spawn_max = ttk.Spinbox(spawn_frame, from_=1, to=20, width=10)
        self.entity_spawn_max.grid(row=4, column=1, pady=5, padx=5, sticky="w")
        self.entity_spawn_max.insert(0, "4")
        
        # Save path frame
        path_frame = ttk.LabelFrame(scrollable_frame, text="Save Path", padding="10")
        path_frame.grid(row=4, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        ttk.Label(path_frame, text="File Name:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.entity_filename = ttk.Entry(path_frame, width=40)
        self.entity_filename.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(path_frame, text=".json", foreground="gray").grid(row=0, column=2, pady=5, padx=0, sticky="w")
        
        # Button frame
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        ttk.Button(btn_frame, text="Generate JSON", command=self.generate_entity_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save to Behavior Pack", command=self.save_entity_to_behavior).pack(side=tk.LEFT, padx=5)
        
        # JSON preview frame
        preview_frame = ttk.LabelFrame(scrollable_frame, text="JSON Preview", padding="10")
        preview_frame.grid(row=6, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        self.entity_json_preview = tk.Text(preview_frame, height=15, width=80)
        self.entity_json_preview.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        preview_scrollbar = ttk.Scrollbar(self.entity_json_preview, orient=tk.VERTICAL, command=self.entity_json_preview.yview)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.entity_json_preview.config(yscrollcommand=preview_scrollbar.set)
    
    # ==================== Recipe Configuration ====================
    def create_recipe_config(self, parent):
        """Create recipe configuration interface"""
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_label = ttk.Label(scrollable_frame, text="Recipe Configuration (Behavior Pack)", 
                               font=("Segoe UI", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="w")
        
        # Description
        desc_label = ttk.Label(scrollable_frame, 
                              text="Define crafting recipes in the behavior pack\n"
                                   "Supports crafting table, furnace, brewing stand, etc.",
                              justify=tk.LEFT)
        desc_label.grid(row=1, column=0, columnspan=3, pady=5, padx=10, sticky="w")
        
        # Recipe type selection
        type_frame = ttk.LabelFrame(scrollable_frame, text="Recipe Type", padding="10")
        type_frame.grid(row=2, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        self.recipe_type = tk.StringVar(value="crafting_shaped")
        ttk.Radiobutton(type_frame, text="Shaped Crafting", variable=self.recipe_type, 
                       value="crafting_shaped", command=self.update_recipe_ui).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(type_frame, text="Shapeless Crafting", variable=self.recipe_type, 
                       value="crafting_shapeless", command=self.update_recipe_ui).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(type_frame, text="Furnace Recipe", variable=self.recipe_type, 
                       value="furnace", command=self.update_recipe_ui).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(type_frame, text="Brewing Recipe", variable=self.recipe_type, 
                       value="brewing", command=self.update_recipe_ui).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Recipe information frame
        info_frame = ttk.LabelFrame(scrollable_frame, text="Recipe Information", padding="10")
        info_frame.grid(row=3, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # Output item
        ttk.Label(info_frame, text="Output Item:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.recipe_output = ttk.Entry(info_frame, width=30)
        self.recipe_output.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(info_frame, text="e.g., minecraft:diamond", foreground="gray").grid(row=0, column=2, pady=5, padx=5, sticky="w")
        
        # Output count
        ttk.Label(info_frame, text="Output Count:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.recipe_output_count = ttk.Spinbox(info_frame, from_=1, to=64, width=10)
        self.recipe_output_count.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        self.recipe_output_count.insert(0, "1")
        
        # Recipe identifier
        ttk.Label(info_frame, text="Recipe Identifier:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.recipe_identifier = ttk.Entry(info_frame, width=30)
        self.recipe_identifier.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(info_frame, text="e.g., wiki:example_recipe", foreground="gray").grid(row=2, column=2, pady=5, padx=5, sticky="w")
        
        # Crafting input frame
        self.recipe_input_frame = ttk.LabelFrame(scrollable_frame, text="Crafting Input", padding="10")
        self.recipe_input_frame.grid(row=4, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # Create 3x3 crafting grid
        self.recipe_grid = []
        grid_frame = ttk.Frame(self.recipe_input_frame)
        grid_frame.pack(pady=10)
        
        for i in range(3):
            row = []
            for j in range(3):
                entry = ttk.Entry(grid_frame, width=15)
                entry.grid(row=i, column=j, padx=2, pady=2)
                row.append(entry)
            self.recipe_grid.append(row)
        
        # Pattern description
        pattern_label = ttk.Label(self.recipe_input_frame, 
                                 text="Enter item IDs (leave empty for no item)\ne.g., minecraft:stone",
                                 justify=tk.CENTER, foreground="gray")
        pattern_label.pack()
        
        # Furnace recipe specific frame
        self.furnace_frame = ttk.Frame(scrollable_frame)
        
        # Brewing recipe specific frame
        self.brewing_frame = ttk.Frame(scrollable_frame)
        
        # Save path frame
        path_frame = ttk.LabelFrame(scrollable_frame, text="Save Path", padding="10")
        path_frame.grid(row=5, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        ttk.Label(path_frame, text="File Name:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.recipe_filename = ttk.Entry(path_frame, width=40)
        self.recipe_filename.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(path_frame, text=".json", foreground="gray").grid(row=0, column=2, pady=5, padx=0, sticky="w")
        
        # Button frame
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        ttk.Button(btn_frame, text="Generate JSON", command=self.generate_recipe_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save to Behavior Pack", command=self.save_recipe_to_behavior).pack(side=tk.LEFT, padx=5)
        
        # JSON preview frame
        preview_frame = ttk.LabelFrame(scrollable_frame, text="JSON Preview", padding="10")
        preview_frame.grid(row=7, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        self.recipe_json_preview = tk.Text(preview_frame, height=15, width=80)
        self.recipe_json_preview.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        preview_scrollbar = ttk.Scrollbar(self.recipe_json_preview, orient=tk.VERTICAL, command=self.recipe_json_preview.yview)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.recipe_json_preview.config(yscrollcommand=preview_scrollbar.set)
    
    # ==================== Loot Table Configuration ====================
    def create_loot_table_config(self, parent):
        """Create loot table configuration interface"""
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_label = ttk.Label(scrollable_frame, text="Loot Table Configuration (Behavior Pack)", 
                               font=("Segoe UI", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="w")
        
        # Description
        desc_label = ttk.Label(scrollable_frame, 
                              text="Define loot drop rules for blocks, entities, or chests",
                              justify=tk.LEFT)
        desc_label.grid(row=1, column=0, columnspan=3, pady=5, padx=10, sticky="w")
        
        # Loot table type
        type_frame = ttk.LabelFrame(scrollable_frame, text="Loot Table Type", padding="10")
        type_frame.grid(row=2, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        self.loot_type = tk.StringVar(value="entity")
        ttk.Radiobutton(type_frame, text="Entity Loot", variable=self.loot_type, 
                       value="entity").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(type_frame, text="Block Loot", variable=self.loot_type, 
                       value="block").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(type_frame, text="Chest Loot", variable=self.loot_type, 
                       value="chest").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        # Loot pool frame
        pool_frame = ttk.LabelFrame(scrollable_frame, text="Loot Pool", padding="10")
        pool_frame.grid(row=3, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # Loot pool list
        self.loot_pool_listbox = tk.Listbox(pool_frame, height=5)
        self.loot_pool_listbox.pack(fill=tk.X, pady=5)
        
        # Add initial loot pool
        self.loot_pools = []
        self.loot_pool_listbox.insert(tk.END, "Main Loot Pool")
        self.loot_pools.append({"name": "Main Loot Pool", "entries": []})
        
        # Loot pool operation buttons
        pool_btn_frame = ttk.Frame(pool_frame)
        pool_btn_frame.pack(fill=tk.X)
        
        ttk.Button(pool_btn_frame, text="Add Loot Pool", command=self.add_loot_pool).pack(side=tk.LEFT, padx=2)
        ttk.Button(pool_btn_frame, text="Delete Loot Pool", command=self.delete_loot_pool).pack(side=tk.LEFT, padx=2)
        
        # Loot entry frame
        entry_frame = ttk.LabelFrame(scrollable_frame, text="Loot Entry Configuration", padding="10")
        entry_frame.grid(row=4, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # Item selection
        ttk.Label(entry_frame, text="Item:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.loot_item = ttk.Entry(entry_frame, width=30)
        self.loot_item.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        
        # Weight
        ttk.Label(entry_frame, text="Weight:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.loot_weight = ttk.Spinbox(entry_frame, from_=1, to=100, width=10)
        self.loot_weight.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        self.loot_weight.insert(0, "1")
        
        # Count range
        ttk.Label(entry_frame, text="Minimum Count:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.loot_min_count = ttk.Spinbox(entry_frame, from_=1, to=64, width=10)
        self.loot_min_count.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        self.loot_min_count.insert(0, "1")
        
        ttk.Label(entry_frame, text="Maximum Count:").grid(row=3, column=0, pady=5, padx=5, sticky="w")
        self.loot_max_count = ttk.Spinbox(entry_frame, from_=1, to=64, width=10)
        self.loot_max_count.grid(row=3, column=1, pady=5, padx=5, sticky="w")
        self.loot_max_count.insert(0, "1")
        
        # Condition
        ttk.Label(entry_frame, text="Condition:").grid(row=4, column=0, pady=5, padx=5, sticky="w")
        self.loot_condition = ttk.Combobox(entry_frame, 
                                          values=["random_chance", "killed_by_player", "on_fire"], 
                                          width=20)
        self.loot_condition.grid(row=4, column=1, pady=5, padx=5, sticky="w")
        
        # Add loot entry button
        ttk.Button(entry_frame, text="Add to Current Loot Pool", command=self.add_loot_entry).grid(row=5, column=0, columnspan=2, pady=10)
        
        # Current loot pool entries list
        current_pool_frame = ttk.LabelFrame(scrollable_frame, text="Current Loot Pool Entries", padding="10")
        current_pool_frame.grid(row=5, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        self.loot_entries_listbox = tk.Listbox(current_pool_frame, height=6)
        self.loot_entries_listbox.pack(fill=tk.X, pady=5)
        
        # Delete loot entry button
        ttk.Button(current_pool_frame, text="Delete Selected Entry", 
                  command=self.delete_loot_entry).pack(pady=5)
        
        # Save path frame
        path_frame = ttk.LabelFrame(scrollable_frame, text="Save Path", padding="10")
        path_frame.grid(row=6, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        ttk.Label(path_frame, text="File Name:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.loot_filename = ttk.Entry(path_frame, width=40)
        self.loot_filename.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(path_frame, text=".json", foreground="gray").grid(row=0, column=2, pady=5, padx=0, sticky="w")
        
        # Button frame
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=7, column=0, columnspan=3, pady=20)
        
        ttk.Button(btn_frame, text="Generate JSON", command=self.generate_loot_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save to Behavior Pack", command=self.save_loot_to_behavior).pack(side=tk.LEFT, padx=5)
        
        # JSON preview frame
        preview_frame = ttk.LabelFrame(scrollable_frame, text="JSON Preview", padding="10")
        preview_frame.grid(row=8, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        self.loot_json_preview = tk.Text(preview_frame, height=15, width=80)
        self.loot_json_preview.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        preview_scrollbar = ttk.Scrollbar(self.loot_json_preview, orient=tk.VERTICAL, command=self.loot_json_preview.yview)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.loot_json_preview.config(yscrollcommand=preview_scrollbar.set)
    
    # ==================== Item Tab Configuration ====================
    def create_item_tab_config(self, parent):
        """Create item tab configuration interface"""
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_label = ttk.Label(scrollable_frame, text="Item Tab Configuration (Behavior Pack)", 
                               font=("Segoe UI", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="w")
        
        # Description
        desc_label = ttk.Label(scrollable_frame, 
                              text="Item tabs are used to categorize items in the creative inventory\n"
                                   "Each tab can contain multiple item groups, and groups can contain multiple items",
                              justify=tk.LEFT)
        desc_label.grid(row=1, column=0, columnspan=2, pady=5, padx=10, sticky="w")
        
        # Tab list frame
        list_frame = ttk.LabelFrame(scrollable_frame, text="Tab List", padding="10")
        list_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        
        # Tab list
        self.tab_listbox = tk.Listbox(list_frame, height=6)
        self.tab_listbox.pack(fill=tk.X, pady=5)
        
        # Sample data
        sample_tabs = ["Equipment", "Tools", "Building Materials", "Food", "Redstone", "Nature"]
        for tab in sample_tabs:
            self.tab_listbox.insert(tk.END, tab)
        
        # Tab operation buttons
        tab_btn_frame = ttk.Frame(list_frame)
        tab_btn_frame.pack(fill=tk.X)
        
        ttk.Button(tab_btn_frame, text="Add Tab", command=self.add_item_tab).pack(side=tk.LEFT, padx=2)
        ttk.Button(tab_btn_frame, text="Delete Tab", command=self.delete_item_tab).pack(side=tk.LEFT, padx=2)
        
        # Current tab's group list
        group_frame = ttk.LabelFrame(scrollable_frame, text="Current Tab's Groups", padding="10")
        group_frame.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        
        # Group list
        self.group_listbox = tk.Listbox(group_frame, height=4)
        self.group_listbox.pack(fill=tk.X, pady=5)
        
        # Group operation buttons
        group_btn_frame = ttk.Frame(group_frame)
        group_btn_frame.pack(fill=tk.X)
        
        ttk.Button(group_btn_frame, text="Add Group", command=self.add_item_group).pack(side=tk.LEFT, padx=2)
        ttk.Button(group_btn_frame, text="Delete Group", command=self.delete_item_group).pack(side=tk.LEFT, padx=2)
        
        # Button frame
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Generate JSON", command=self.generate_item_tab_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save to Behavior Pack", command=self.save_item_tab_to_behavior).pack(side=tk.LEFT, padx=5)
        
        # Generated JSON preview
        preview_frame = ttk.LabelFrame(scrollable_frame, text="JSON Preview", padding="10")
        preview_frame.grid(row=5, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        
        self.tab_json_preview = tk.Text(preview_frame, height=15, width=80)
        self.tab_json_preview.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        preview_scrollbar = ttk.Scrollbar(self.tab_json_preview, orient=tk.VERTICAL, command=self.tab_json_preview.yview)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tab_json_preview.config(yscrollcommand=preview_scrollbar.set)
    
    # ==================== Item Texture Configuration ====================
    def create_item_texture_config(self, parent):
        """Create item texture configuration interface"""
        # Create frame
        main_frame = ttk.Frame(parent, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Item Texture Configuration (Resource Pack)", 
                               font=("Segoe UI", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_label = ttk.Label(main_frame, 
                              text="Configure item textures, models, and localization names in the resource pack\n"
                                   "Must correspond to item identifiers in the behavior pack",
                              justify=tk.LEFT)
        desc_label.pack(pady=(0, 20))
        
        # Create two main sections
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=10)
        
        # Left - Texture mapping
        texture_frame = ttk.LabelFrame(top_frame, text="Texture Mapping", padding="10")
        texture_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(texture_frame, text="Item Identifier:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.texture_item_id = ttk.Entry(texture_frame, width=30)
        self.texture_item_id.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        
        ttk.Label(texture_frame, text="Texture Path:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.texture_path = ttk.Entry(texture_frame, width=30)
        self.texture_path.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(texture_frame, text="e.g., textures/items/example", foreground="gray").grid(row=1, column=2, pady=5, padx=5, sticky="w")
        
        ttk.Button(texture_frame, text="Add Mapping", command=self.add_texture_mapping).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Right - Localization
        lang_frame = ttk.LabelFrame(top_frame, text="Localization", padding="10")
        lang_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(lang_frame, text="Item Identifier:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.lang_item_id = ttk.Entry(lang_frame, width=30)
        self.lang_item_id.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        
        ttk.Label(lang_frame, text="English Name:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.en_name = ttk.Entry(lang_frame, width=30)
        self.en_name.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        
        ttk.Label(lang_frame, text="Localized Name:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.zh_name = ttk.Entry(lang_frame, width=30)
        self.zh_name.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        
        ttk.Button(lang_frame, text="Add to Language File", command=self.add_to_lang).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Bottom - Texture list
        list_frame = ttk.LabelFrame(main_frame, text="Existing Texture Mappings", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create table
        columns = ("Item Identifier", "Texture Path", "Status")
        self.texture_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.texture_tree.heading(col, text=col)
            self.texture_tree.column(col, width=200)
        
        self.texture_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        tree_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.texture_tree.yview)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.texture_tree.config(yscrollcommand=tree_scrollbar.set)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Generate Texture Definition", command=self.generate_texture_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save All Changes", command=self.save_texture_changes).pack(side=tk.LEFT, padx=5)
    
    # ==================== Helper Methods ====================
    def toggle_durability(self):
        """Toggle durability component state"""
        state = "normal" if self.has_durability.get() else "disabled"
        self.max_durability.config(state=state)
    
    def toggle_food(self):
        """Toggle food component state"""
        state = "normal" if self.is_food.get() else "disabled"
        self.nutrition.config(state=state)
        self.saturation.config(state=state)
    
    def toggle_weapon(self):
        """Toggle weapon component state"""
        state = "normal" if self.is_weapon.get() else "disabled"
        self.damage.config(state=state)
    
    # ==================== Item Related Methods ====================
    def generate_item_json(self):
        """Generate item JSON configuration"""
        # Validate required fields
        identifier = self.item_identifier.get().strip()
        display_name = self.item_display_name.get().strip()
        
        if not identifier or not display_name:
            messagebox.showwarning("Warning", "Please fill in at least item identifier and display name")
            return
        
        # Build item configuration
        item_config = {
            "format_version": "1.20.0",
            "minecraft:item": {
                "description": {
                    "identifier": identifier,
                    "category": self.item_category.get() or "items"
                },
                "components": {}
            }
        }
        
        # Add display name component
        name_key = f"item.{identifier.replace(':', '.')}.name"
        item_config["minecraft:item"]["components"]["minecraft:display_name"] = {
            "value": name_key
        }
        
        # Add icon component
        icon_key = identifier.replace(':', ':')
        item_config["minecraft:item"]["components"]["minecraft:icon"] = {
            "texture": icon_key
        }
        
        # Add max stack size
        stack_size = self.max_stack_size.get()
        if stack_size:
            item_config["minecraft:item"]["components"]["minecraft:max_stack_size"] = int(stack_size)
        
        # Add hand equipped component
        if self.hand_equipped.get():
            item_config["minecraft:item"]["components"]["minecraft:hand_equipped"] = True
        
        # Add durability component
        if self.has_durability.get():
            max_dura = self.max_durability.get()
            if max_dura:
                item_config["minecraft:item"]["components"]["minecraft:durability"] = {
                    "max_durability": int(max_dura)
                }
        
        # Add food component
        if self.is_food.get():
            nutrition = self.nutrition.get()
            saturation = self.saturation.get()
            if nutrition and saturation:
                item_config["minecraft:item"]["components"]["minecraft:food"] = {
                    "nutrition": int(nutrition),
                    "saturation_modifier": float(saturation) / float(nutrition) if float(nutrition) > 0 else 0.5
                }
        
        # Add weapon component
        if self.is_weapon.get():
            damage = self.damage.get()
            if damage:
                item_config["minecraft:item"]["components"]["minecraft:damage"] = int(damage)
        
        # Convert to JSON string
        json_str = json.dumps(item_config, indent=2, ensure_ascii=False)
        
        # Display in preview
        self.item_json_preview.delete(1.0, tk.END)
        self.item_json_preview.insert(1.0, json_str)
        
        # Auto-generate filename
        if not self.item_filename.get().strip():
            name_parts = identifier.split(":")
            if len(name_parts) > 1:
                suggested_name = name_parts[1]
            else:
                suggested_name = identifier.replace(":", "_")
            
            self.item_filename.delete(0, tk.END)
            self.item_filename.insert(0, suggested_name)
    
    def save_item_to_behavior(self):
        """Save item JSON to behavior pack"""
        json_content = self.item_json_preview.get(1.0, tk.END).strip()
        if not json_content:
            messagebox.showwarning("Warning", "Please generate JSON first")
            return
        
        # Validate JSON
        try:
            json_obj = json.loads(json_content)
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"JSON format error: {str(e)}")
            return
        
        # Get filename
        filename = self.item_filename.get().strip()
        if not filename:
            messagebox.showwarning("Warning", "Please enter a filename")
            return
        
        if not filename.endswith(".json"):
            filename += ".json"
        
        # Save to behavior pack's items folder
        items_path = self.bp_path / "items"
        items_path.mkdir(exist_ok=True)
        
        file_path = items_path / filename
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_content)
            
            # Update language files
            identifier = self.item_identifier.get().strip()
            display_name = self.item_display_name.get().strip()
            
            if identifier and display_name:
                self.update_language_files(identifier, display_name)
            
            messagebox.showinfo("Success", f"Item configuration saved to behavior pack:\n{file_path}\n\n"
                                      "Tip: Don't forget to configure corresponding textures and localization names in the resource pack")
            
            # Refresh file tree
            if 'bp' in self.file_trees:
                self.file_trees['bp'].delete(*self.file_trees['bp'].get_children())
                self.load_file_tree_node(self.file_trees['bp'], "", self.bp_path, self.bp_path.name)
            
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {str(e)}")
    
    # ==================== Block Related Methods ====================
    def generate_block_json(self):
        """Generate block JSON configuration"""
        # Validate required fields
        identifier = self.block_identifier.get().strip()
        display_name = self.block_display_name.get().strip()
        
        if not identifier or not display_name:
            messagebox.showwarning("Warning", "Please fill in at least block identifier and display name")
            return
        
        # Build block configuration
        block_config = {
            "format_version": "1.20.0",
            "minecraft:block": {
                "description": {
                    "identifier": identifier,
                    "category": self.block_category.get() or "construction"
                },
                "components": {
                    "minecraft:block_light_emission": float(self.block_light_emission.get() or 0),
                    "minecraft:destroy_time": float(self.block_hardness.get() or 1.5),
                    "minecraft:explosion_resistance": float(self.block_resistance.get() or 10),
                    "minecraft:friction": 0.6,
                    "minecraft:flammable": {
                        "burn_odds": 0 if not self.block_flammable.get() else 5
                    },
                    "minecraft:map_color": "#ffffff",
                    "minecraft:material_instances": {
                        "*": {
                            "texture": self.block_texture.get() or identifier.replace(':', ':'),
                            "render_method": self.block_material.get() or "opaque"
                        }
                    }
                }
            }
        }
        
        # Add unit cube geometry
        if self.block_unit_cube.get():
            block_config["minecraft:block"]["components"]["minecraft:geometry"] = "minecraft:geometry.full_block"
        elif self.block_geometry.get().strip():
            block_config["minecraft:block"]["components"]["minecraft:geometry"] = self.block_geometry.get().strip()
        
        # Add transparent property
        if self.block_transparent.get():
            block_config["minecraft:block"]["components"]["minecraft:breathability"] = "air"
        
        # Add replaceable property
        if self.block_replaceable.get():
            block_config["minecraft:block"]["components"]["minecraft:replaceable"] = True
        
        # Add loot
        if self.block_loot_item.get().strip():
            block_config["minecraft:block"]["components"]["minecraft:loot"] = self.block_loot_item.get().strip()
        
        # Convert to JSON string
        json_str = json.dumps(block_config, indent=2, ensure_ascii=False)
        
        # Display in preview
        self.block_json_preview.delete(1.0, tk.END)
        self.block_json_preview.insert(1.0, json_str)
        
        # Auto-generate filename
        if not self.block_filename.get().strip():
            name_parts = identifier.split(":")
            if len(name_parts) > 1:
                suggested_name = name_parts[1]
            else:
                suggested_name = identifier.replace(":", "_")
            
            self.block_filename.delete(0, tk.END)
            self.block_filename.insert(0, suggested_name)
    
    def save_block_to_behavior(self):
        """Save block JSON to behavior pack"""
        json_content = self.block_json_preview.get(1.0, tk.END).strip()
        if not json_content:
            messagebox.showwarning("Warning", "Please generate JSON first")
            return
        
        # Validate JSON
        try:
            json_obj = json.loads(json_content)
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"JSON format error: {str(e)}")
            return
        
        # Get filename
        filename = self.block_filename.get().strip()
        if not filename:
            messagebox.showwarning("Warning", "Please enter a filename")
            return
        
        if not filename.endswith(".json"):
            filename += ".json"
        
        # Save to behavior pack's blocks folder
        blocks_path = self.bp_path / "blocks"
        blocks_path.mkdir(exist_ok=True)
        
        file_path = blocks_path / filename
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_content)
            
            # Update language files
            identifier = self.block_identifier.get().strip()
            display_name = self.block_display_name.get().strip()
            
            if identifier and display_name:
                name_key = f"tile.{identifier.replace(':', '.')}.name"
                self.update_language_files_custom(name_key, display_name)
            
            messagebox.showinfo("Success", f"Block configuration saved to behavior pack:\n{file_path}")
            
            # Refresh file tree
            if 'bp' in self.file_trees:
                self.file_trees['bp'].delete(*self.file_trees['bp'].get_children())
                self.load_file_tree_node(self.file_trees['bp'], "", self.bp_path, self.bp_path.name)
            
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {str(e)}")
    
    # ==================== Entity Related Methods ====================
    def generate_entity_json(self):
        """Generate entity JSON configuration"""
        # Validate required fields
        identifier = self.entity_identifier.get().strip()
        display_name = self.entity_display_name.get().strip()
        
        if not identifier or not display_name:
            messagebox.showwarning("Warning", "Please fill in at least entity identifier and display name")
            return
        
        # Build entity configuration
        entity_config = {
            "format_version": "1.20.0",
            "minecraft:entity": {
                "description": {
                    "identifier": identifier,
                    "is_spawnable": self.entity_spawnable.get(),
                    "is_summonable": True,
                    "is_experimental": False
                },
                "component_groups": {},
                "components": {
                    "minecraft:type_family": {
                        "family": [self.entity_type.get()]
                    },
                    "minecraft:health": {
                        "value": int(self.entity_health.get() or 20),
                        "max": int(self.entity_health.get() or 20)
                    },
                    "minecraft:movement": {
                        "value": float(self.entity_speed.get() or 0.25)
                    },
                    "minecraft:attack": {
                        "damage": int(self.entity_damage.get() or 0)
                    },
                    "minecraft:knockback_resistance": {
                        "value": float(self.entity_knockback_resistance.get() or 0)
                    },
                    "minecraft:nameable": {
                        "always_show": True,
                        "allow_name_tag_renaming": True
                    },
                    "minecraft:despawn": {
                        "despawn_from_distance": {
                            "min_distance": 128,
                            "max_distance": 256
                        }
                    }
                },
                "events": {}
            }
        }
        
        # Add behavior
        if self.entity_behavior.get():
            behavior_map = {
                "idle": "minecraft:behavior.look_around",
                "walk": "minecraft:behavior.random_stroll",
                "look": "minecraft:behavior.look_at_player",
                "panic": "minecraft:behavior.panic",
                "follow_owner": "minecraft:behavior.follow_owner"
            }
            
            if self.entity_behavior.get() in behavior_map:
                entity_config["minecraft:entity"]["components"][behavior_map[self.entity_behavior.get()]] = {}
        
        # Add equipment
        if self.entity_equipment.get() and self.entity_equipment_table.get().strip():
            entity_config["minecraft:entity"]["components"]["minecraft:equipment"] = {
                "table": self.entity_equipment_table.get().strip()
            }
        
        # Add loot table
        if self.entity_loot_table.get().strip():
            entity_config["minecraft:entity"]["components"]["minecraft:loot"] = {
                "table": self.entity_loot_table.get().strip()
            }
        
        # Add breedable component
        if self.entity_baby.get():
            entity_config["minecraft:entity"]["components"]["minecraft:breedable"] = {
                "require_tame": False,
                "breeds_with": [],
                "breed_items": []
            }
        
        # Convert to JSON string
        json_str = json.dumps(entity_config, indent=2, ensure_ascii=False)
        
        # Display in preview
        self.entity_json_preview.delete(1.0, tk.END)
        self.entity_json_preview.insert(1.0, json_str)
        
        # Auto-generate filename
        if not self.entity_filename.get().strip():
            name_parts = identifier.split(":")
            if len(name_parts) > 1:
                suggested_name = name_parts[1]
            else:
                suggested_name = identifier.replace(":", "_")
            
            self.entity_filename.delete(0, tk.END)
            self.entity_filename.insert(0, suggested_name)
    
    def save_entity_to_behavior(self):
        """Save entity JSON to behavior pack"""
        json_content = self.entity_json_preview.get(1.0, tk.END).strip()
        if not json_content:
            messagebox.showwarning("Warning", "Please generate JSON first")
            return
        
        # Validate JSON
        try:
            json_obj = json.loads(json_content)
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"JSON format error: {str(e)}")
            return
        
        # Get filename
        filename = self.entity_filename.get().strip()
        if not filename:
            messagebox.showwarning("Warning", "Please enter a filename")
            return
        
        if not filename.endswith(".json"):
            filename += ".json"
        
        # Save to behavior pack's entities folder
        entities_path = self.bp_path / "entities"
        entities_path.mkdir(exist_ok=True)
        
        file_path = entities_path / filename
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_content)
            
            # Update language files
            identifier = self.entity_identifier.get().strip()
            display_name = self.entity_display_name.get().strip()
            
            if identifier and display_name:
                name_key = f"entity.{identifier.replace(':', '.')}.name"
                self.update_language_files_custom(name_key, display_name)
            
            # If spawn rules exist, save spawn rules
            if self.entity_spawnable.get() and self.entity_biome.get():
                self.save_spawn_rules(identifier)
            
            messagebox.showinfo("Success", f"Entity configuration saved to behavior pack:\n{file_path}")
            
            # Refresh file tree
            if 'bp' in self.file_trees:
                self.file_trees['bp'].delete(*self.file_trees['bp'].get_children())
                self.load_file_tree_node(self.file_trees['bp'], "", self.bp_path, self.bp_path.name)
            
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {str(e)}")
    
    def save_spawn_rules(self, entity_id):
        """Save spawn rules"""
        spawn_config = {
            "format_version": "1.8.0",
            "minecraft:spawn_rules": {
                "description": {
                    "identifier": entity_id,
                    "population_control": self.entity_type.get()
                },
                "conditions": [
                    {
                        "minecraft:spawns_on_surface": {},
                        "minecraft:weight": {
                            "default": int(self.entity_spawn_weight.get() or 10)
                        },
                        "minecraft:herd": {
                            "min_size": int(self.entity_spawn_min.get() or 2),
                            "max_size": int(self.entity_spawn_max.get() or 4)
                        },
                        "minecraft:biome_filter": {
                            "test": "has_biome_tag",
                            "operator": "==",
                            "value": self.entity_biome.get()
                        }
                    }
                ]
            }
        }
        
        # Save to spawn_rules folder
        spawn_path = self.bp_path / "spawn_rules"
        spawn_path.mkdir(exist_ok=True)
        
        name_parts = entity_id.split(":")
        filename = f"{name_parts[1] if len(name_parts) > 1 else entity_id}.json"
        
        with open(spawn_path / filename, "w", encoding="utf-8") as f:
            json.dump(spawn_config, f, indent=2)
    
    # ==================== Recipe Related Methods ====================
    def update_recipe_ui(self):
        """Update recipe UI"""
        recipe_type = self.recipe_type.get()
        
        # Hide all specific frames
        if hasattr(self, 'furnace_frame'):
            self.furnace_frame.grid_remove()
        if hasattr(self, 'brewing_frame'):
            self.brewing_frame.grid_remove()
        
        if recipe_type == "furnace":
            self.show_furnace_ui()
        elif recipe_type == "brewing":
            self.show_brewing_ui()
    
    def show_furnace_ui(self):
        """Show furnace recipe UI"""
        if not hasattr(self, 'furnace_frame'):
            return
            
        self.furnace_frame.grid(row=5, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # Clear existing content
        for widget in self.furnace_frame.winfo_children():
            widget.destroy()
        
        # Furnace recipe specific controls
        ttk.Label(self.furnace_frame, text="Input Item:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.furnace_input = ttk.Entry(self.furnace_frame, width=30)
        self.furnace_input.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        
        ttk.Label(self.furnace_frame, text="Experience:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.furnace_experience = ttk.Spinbox(self.furnace_frame, from_=0, to=10, increment=0.1, width=10)
        self.furnace_experience.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        self.furnace_experience.insert(0, "0.1")
        
        ttk.Label(self.furnace_frame, text="Cooking Time:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.furnace_time = ttk.Spinbox(self.furnace_frame, from_=1, to=1000, width=10)
        self.furnace_time.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        self.furnace_time.insert(0, "200")
    
    def show_brewing_ui(self):
        """Show brewing recipe UI"""
        if not hasattr(self, 'brewing_frame'):
            return
            
        self.brewing_frame.grid(row=5, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # Clear existing content
        for widget in self.brewing_frame.winfo_children():
            widget.destroy()
        
        # Brewing recipe specific controls
        ttk.Label(self.brewing_frame, text="Input Item:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.brewing_input = ttk.Entry(self.brewing_frame, width=30)
        self.brewing_input.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        
        ttk.Label(self.brewing_frame, text="Reagent:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.brewing_reagent = ttk.Entry(self.brewing_frame, width=30)
        self.brewing_reagent.grid(row=1, column=1, pady=5, padx=5, sticky="w")
    
    def generate_recipe_json(self):
        """Generate recipe JSON configuration"""
        recipe_type = self.recipe_type.get()
        output = self.recipe_output.get().strip()
        output_count = self.recipe_output_count.get() or "1"
        
        if not output:
            messagebox.showwarning("Warning", "Please enter output item")
            return
        
        # Build recipe configuration
        if recipe_type == "crafting_shaped":
            # Shaped crafting
            pattern = []
            keys = {}
            
            # Read 3x3 grid
            for i in range(3):
                row = ""
                for j in range(3):
                    item = self.recipe_grid[i][j].get().strip()
                    if item:
                        key = chr(65 + j)  # A, B, C, ...
                        row += key
                        keys[key] = {"item": item}
                    else:
                        row += " "
                if row.strip():
                    pattern.append(row)
            
            if not pattern:
                messagebox.showwarning("Warning", "Please enter at least one item")
                return
            
            recipe_config = {
                "format_version": "1.20.0",
                "minecraft:recipe_shaped": {
                    "description": {
                        "identifier": self.recipe_identifier.get().strip() or f"wiki:recipe_{output.split(':')[-1]}"
                    },
                    "tags": ["crafting_table"],
                    "pattern": pattern,
                    "key": keys,
                    "result": {
                        "item": output,
                        "count": int(output_count)
                    }
                }
            }
            
        elif recipe_type == "crafting_shapeless":
            # Shapeless crafting
            ingredients = []
            for i in range(3):
                for j in range(3):
                    item = self.recipe_grid[i][j].get().strip()
                    if item:
                        ingredients.append({"item": item})
            
            if not ingredients:
                messagebox.showwarning("Warning", "Please enter at least one item")
                return
            
            recipe_config = {
                "format_version": "1.20.0",
                "minecraft:recipe_shapeless": {
                    "description": {
                        "identifier": self.recipe_identifier.get().strip() or f"wiki:recipe_{output.split(':')[-1]}"
                    },
                    "tags": ["crafting_table"],
                    "ingredients": ingredients,
                    "result": {
                        "item": output,
                        "count": int(output_count)
                    }
                }
            }
            
        elif recipe_type == "furnace":
            # Furnace recipe
            if not hasattr(self, 'furnace_input') or not self.furnace_input.get().strip():
                messagebox.showwarning("Warning", "Please enter input item")
                return
            
            recipe_config = {
                "format_version": "1.20.0",
                "minecraft:recipe_furnace": {
                    "description": {
                        "identifier": self.recipe_identifier.get().strip() or f"wiki:furnace_{output.split(':')[-1]}"
                    },
                    "tags": ["furnace", "blast_furnace", "smoker"],
                    "input": self.furnace_input.get().strip(),
                    "output": output,
                    "output_count": int(output_count)
                }
            }
            
        elif recipe_type == "brewing":
            # Brewing recipe
            if not hasattr(self, 'brewing_input') or not self.brewing_input.get().strip():
                messagebox.showwarning("Warning", "Please enter input item")
                return
            
            recipe_config = {
                "format_version": "1.20.0",
                "minecraft:recipe_brewing_mix": {
                    "description": {
                        "identifier": self.recipe_identifier.get().strip() or f"wiki:brewing_{output.split(':')[-1]}"
                    },
                    "tags": ["brewing_stand"],
                    "input": self.brewing_input.get().strip(),
                    "reagent": self.brewing_reagent.get().strip() if hasattr(self, 'brewing_reagent') else "",
                    "output": output
                }
            }
        else:
            messagebox.showwarning("Warning", "Please select a valid recipe type")
            return
        
        # Convert to JSON string
        json_str = json.dumps(recipe_config, indent=2, ensure_ascii=False)
        
        # Display in preview
        self.recipe_json_preview.delete(1.0, tk.END)
        self.recipe_json_preview.insert(1.0, json_str)
        
        # Auto-generate filename
        if not self.recipe_filename.get().strip():
            suggested_name = f"{output.split(':')[-1]}_{recipe_type}"
            self.recipe_filename.delete(0, tk.END)
            self.recipe_filename.insert(0, suggested_name)
    
    def save_recipe_to_behavior(self):
        """Save recipe JSON to behavior pack"""
        json_content = self.recipe_json_preview.get(1.0, tk.END).strip()
        if not json_content:
            messagebox.showwarning("Warning", "Please generate JSON first")
            return
        
        # Validate JSON
        try:
            json_obj = json.loads(json_content)
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"JSON format error: {str(e)}")
            return
        
        # Get filename
        filename = self.recipe_filename.get().strip()
        if not filename:
            messagebox.showwarning("Warning", "Please enter a filename")
            return
        
        if not filename.endswith(".json"):
            filename += ".json"
        
        # Save to behavior pack's recipes folder
        recipes_path = self.bp_path / "recipes"
        recipes_path.mkdir(exist_ok=True)
        
        file_path = recipes_path / filename
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_content)
            
            messagebox.showinfo("Success", f"Recipe configuration saved to behavior pack:\n{file_path}")
            
            # Refresh file tree
            if 'bp' in self.file_trees:
                self.file_trees['bp'].delete(*self.file_trees['bp'].get_children())
                self.load_file_tree_node(self.file_trees['bp'], "", self.bp_path, self.bp_path.name)
            
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {str(e)}")
    
    # ==================== Item Tab Related Methods ====================
    def add_item_tab(self):
        """Add item tab"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Item Tab")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Tab Name:").pack(anchor=tk.W, pady=(0, 5))
        name_entry = ttk.Entry(frame)
        name_entry.pack(fill=tk.X, pady=(0, 10))
        name_entry.focus()
        
        def add():
            name = name_entry.get().strip()
            if name:
                self.tab_listbox.insert(tk.END, name)
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Please enter tab name")
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Add", command=add).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def delete_item_tab(self):
        """Delete item tab"""
        selection = self.tab_listbox.curselection()
        if selection:
            self.tab_listbox.delete(selection[0])
    
    def add_item_group(self):
        """Add item group"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Item Group")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Group Name:").pack(anchor=tk.W, pady=(0, 5))
        name_entry = ttk.Entry(frame)
        name_entry.pack(fill=tk.X, pady=(0, 10))
        name_entry.focus()
        
        def add():
            name = name_entry.get().strip()
            if name:
                self.group_listbox.insert(tk.END, name)
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Please enter group name")
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Add", command=add).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def delete_item_group(self):
        """Delete item group"""
        selection = self.group_listbox.curselection()
        if selection:
            self.group_listbox.delete(selection[0])
    
    def generate_item_tab_json(self):
        """Generate item tab JSON configuration"""
        # Create example JSON
        item_tab_config = {
            "format_version": "1.17.0",
            "minecraft:item_group": {
                "description": {
                    "identifier": f"{self.project_path.name}:item_group",
                    "category": "items"
                },
                "components": {
                    "minecraft:icon": {
                        "texture": "textures/items/group_icon"
                    },
                    "minecraft:display_name": {
                        "value": f"{self.project_path.name} Item Group"
                    },
                    "minecraft:creative_tabs": []
                }
            }
        }
        
        # Add tab and group information
        tabs = []
        for i in range(self.tab_listbox.size()):
            tab_name = self.tab_listbox.get(i)
            tab_data = {
                "name": tab_name,
                "groups": []
            }
            
            # If this tab is selected, add its groups
            selection = self.tab_listbox.curselection()
            if selection and selection[0] == i:
                groups = []
                for j in range(self.group_listbox.size()):
                    groups.append(self.group_listbox.get(j))
                tab_data["groups"] = groups
            
            tabs.append(tab_data)
        
        if tabs:
            item_tab_config["minecraft:item_group"]["components"]["minecraft:creative_tabs"] = tabs
        
        # Convert to JSON string
        json_str = json.dumps(item_tab_config, indent=2, ensure_ascii=False)
        
        # Display in preview
        self.tab_json_preview.delete(1.0, tk.END)
        self.tab_json_preview.insert(1.0, json_str)
    
    def save_item_tab_to_behavior(self):
        """Save item tab configuration to behavior pack"""
        json_content = self.tab_json_preview.get(1.0, tk.END).strip()
        if not json_content:
            messagebox.showwarning("Warning", "Please generate JSON first")
            return
        
        # Validate JSON
        try:
            json.loads(json_content)
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"JSON format error: {str(e)}")
            return
        
        # Save to behavior pack's items folder
        items_path = self.bp_path / "items"
        items_path.mkdir(exist_ok=True)
        
        file_path = items_path / "item_tab_config.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_content)
            
            messagebox.showinfo("Success", f"Item tab configuration saved to behavior pack:\n{file_path}")
            
            # Refresh file tree
            if 'bp' in self.file_trees:
                self.file_trees['bp'].delete(*self.file_trees['bp'].get_children())
                self.load_file_tree_node(self.file_trees['bp'], "", self.bp_path, self.bp_path.name)
            
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {str(e)}")
    
    # ==================== Loot Table Related Methods ====================
    def add_loot_pool(self):
        """Add loot pool"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Loot Pool")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Loot Pool Name:").pack(anchor=tk.W, pady=(0, 5))
        name_entry = ttk.Entry(frame)
        name_entry.pack(fill=tk.X, pady=(0, 10))
        name_entry.focus()
        
        def add():
            name = name_entry.get().strip()
            if name:
                self.loot_pool_listbox.insert(tk.END, name)
                self.loot_pools.append({"name": name, "entries": []})
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Please enter loot pool name")
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Add", command=add).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def delete_loot_pool(self):
        """Delete loot pool"""
        selection = self.loot_pool_listbox.curselection()
        if selection:
            index = selection[0]
            self.loot_pool_listbox.delete(index)
            if index < len(self.loot_pools):
                del self.loot_pools[index]
    
    def add_loot_entry(self):
        """Add loot entry to current loot pool"""
        selection = self.loot_pool_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a loot pool first")
            return
        
        item = self.loot_item.get().strip()
        if not item:
            messagebox.showwarning("Warning", "Please enter item ID")
            return
        
        pool_index = selection[0]
        entry = {
            "item": item,
            "weight": int(self.loot_weight.get() or 1),
            "min_count": int(self.loot_min_count.get() or 1),
            "max_count": int(self.loot_max_count.get() or 1)
        }
        
        if self.loot_condition.get():
            entry["condition"] = self.loot_condition.get()
        
        # Add to memory
        if pool_index < len(self.loot_pools):
            self.loot_pools[pool_index]["entries"].append(entry)
        
        # Display in listbox
        display_text = f"{item} x{entry['min_count']}-{entry['max_count']} (Weight:{entry['weight']})"
        self.loot_entries_listbox.insert(tk.END, display_text)
        
        # Clear inputs
        self.loot_item.delete(0, tk.END)
        self.loot_weight.delete(0, tk.END)
        self.loot_weight.insert(0, "1")
        self.loot_min_count.delete(0, tk.END)
        self.loot_min_count.insert(0, "1")
        self.loot_max_count.delete(0, tk.END)
        self.loot_max_count.insert(0, "1")
    
    def delete_loot_entry(self):
        """Delete selected loot entry"""
        pool_selection = self.loot_pool_listbox.curselection()
        entry_selection = self.loot_entries_listbox.curselection()
        
        if pool_selection and entry_selection:
            pool_index = pool_selection[0]
            entry_index = entry_selection[0]
            
            if pool_index < len(self.loot_pools) and entry_index < len(self.loot_pools[pool_index]["entries"]):
                del self.loot_pools[pool_index]["entries"][entry_index]
                self.loot_entries_listbox.delete(entry_index)
    
    def generate_loot_json(self):
        """Generate loot table JSON configuration"""
        if not self.loot_pools:
            messagebox.showwarning("Warning", "Please add at least one loot pool")
            return
        
        # Build loot table configuration
        loot_config = {
            "pools": []
        }
        
        for pool in self.loot_pools:
            if pool["entries"]:
                pool_config = {
                    "rolls": 1,
                    "entries": []
                }
                
                for entry in pool["entries"]:
                    entry_config = {
                        "type": "item",
                        "name": entry["item"],
                        "weight": entry["weight"]
                    }
                    
                    # Add count range
                    if entry["min_count"] != entry["max_count"]:
                        entry_config["functions"] = [
                            {
                                "function": "set_count",
                                "count": {
                                    "min": entry["min_count"],
                                    "max": entry["max_count"]
                                }
                            }
                        ]
                    else:
                        entry_config["functions"] = [
                            {
                                "function": "set_count",
                                "count": entry["min_count"]
                            }
                        ]
                    
                    # Add condition
                    if entry.get("condition"):
                        entry_config["conditions"] = [
                            {
                                "condition": entry["condition"]
                            }
                        ]
                    
                    pool_config["entries"].append(entry_config)
                
                loot_config["pools"].append(pool_config)
        
        # Convert to JSON string
        json_str = json.dumps(loot_config, indent=2, ensure_ascii=False)
        
        # Display in preview
        self.loot_json_preview.delete(1.0, tk.END)
        self.loot_json_preview.insert(1.0, json_str)
        
        # Auto-generate filename
        if not self.loot_filename.get().strip():
            loot_type = self.loot_type.get()
            suggested_name = f"{loot_type}_loot_table"
            self.loot_filename.delete(0, tk.END)
            self.loot_filename.insert(0, suggested_name)
    
    def save_loot_to_behavior(self):
        """Save loot table JSON to behavior pack"""
        json_content = self.loot_json_preview.get(1.0, tk.END).strip()
        if not json_content:
            messagebox.showwarning("Warning", "Please generate JSON first")
            return
        
        # Validate JSON
        try:
            json_obj = json.loads(json_content)
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"JSON format error: {str(e)}")
            return
        
        # Get filename
        filename = self.loot_filename.get().strip()
        if not filename:
            messagebox.showwarning("Warning", "Please enter a filename")
            return
        
        if not filename.endswith(".json"):
            filename += ".json"
        
        # Select subfolder based on type
        loot_type = self.loot_type.get()
        if loot_type == "entity":
            loot_path = self.bp_path / "loot_tables" / "entities"
        elif loot_type == "block":
            loot_path = self.bp_path / "loot_tables" / "blocks"
        else:  # chest
            loot_path = self.bp_path / "loot_tables" / "chests"
        
        loot_path.mkdir(parents=True, exist_ok=True)
        
        file_path = loot_path / filename
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_content)
            
            messagebox.showinfo("Success", f"Loot table saved to behavior pack:\n{file_path}")
            
            # Refresh file tree
            if 'bp' in self.file_trees:
                self.file_trees['bp'].delete(*self.file_trees['bp'].get_children())
                self.load_file_tree_node(self.file_trees['bp'], "", self.bp_path, self.bp_path.name)
            
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {str(e)}")
    
    # ==================== Texture Related Methods ====================
    def add_texture_mapping(self):
        """Add texture mapping"""
        item_id = self.texture_item_id.get().strip()
        texture = self.texture_path.get().strip()
        
        if not item_id or not texture:
            messagebox.showwarning("Warning", "Please fill in item identifier and texture path")
            return
        
        # Add to tree view
        self.texture_tree.insert("", "end", values=(item_id, texture, "Pending Save"))
        
        # Clear input boxes
        self.texture_item_id.delete(0, tk.END)
        self.texture_path.delete(0, tk.END)
    
    def add_to_lang(self):
        """Add to language file"""
        item_id = self.lang_item_id.get().strip()
        en_name = self.en_name.get().strip()
        localized_name = self.zh_name.get().strip()
        
        if not item_id or not en_name:
            messagebox.showwarning("Warning", "Please fill in at least item identifier and English name")
            return
        
        # Build localization key
        lang_key = f"item.{item_id.replace(':', '.')}.name"
        
        try:
            # Update English language file
            en_lang_path = self.rp_path / "texts" / "en_US.lang"
            if en_lang_path.exists():
                with open(en_lang_path, "a", encoding="utf-8") as f:
                    f.write(f"\n{lang_key}={en_name}")
            
            # Update localized language file
            if localized_name:
                # Use English name as default for other languages
                # You can add support for other languages here
                pass
            
            messagebox.showinfo("Success", "Added to language file")
            
            # Clear input boxes
            self.lang_item_id.delete(0, tk.END)
            self.en_name.delete(0, tk.END)
            self.zh_name.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"Add failed: {str(e)}")
    
    def generate_texture_json(self):
        """Generate texture definition file"""
        # Get all texture mappings
        textures = {}
        for item in self.texture_tree.get_children():
            values = self.texture_tree.item(item, "values")
            if values:
                item_id = values[0]
                texture_path = values[1]
                # Use item ID as texture key
                texture_key = item_id.replace(':', ':')
                textures[texture_key] = texture_path
        
        if not textures:
            messagebox.showwarning("Warning", "No texture mappings to save")
            return
        
        # Build texture definition
        texture_config = {
            "texture_data": {}
        }
        
        for key, path in textures.items():
            texture_config["texture_data"][key] = {
                "textures": path
            }
        
        # Save file
        textures_path = self.rp_path / "textures" / "item_texture.json"
        try:
            with open(textures_path, "w", encoding="utf-8") as f:
                json.dump(texture_config, f, indent=2)
            
            messagebox.showinfo("Success", f"Texture definition saved to:\n{textures_path}")
            
            # Update status
            for item in self.texture_tree.get_children():
                self.texture_tree.item(item, values=(self.texture_tree.item(item, "values")[0],
                                                     self.texture_tree.item(item, "values")[1],
                                                     "Saved"))
            
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {str(e)}")
    
    def save_texture_changes(self):
        """Save all texture changes"""
        self.generate_texture_json()
    
    # ==================== Helper Methods ====================
    def update_language_files(self, identifier, display_name):
        """Update language files (items)"""
        lang_key = f"item.{identifier.replace(':', '.')}.name"
        self.update_language_files_custom(lang_key, display_name)
    
    def update_language_files_custom(self, lang_key, display_name):
        """Update language files (custom key)"""
        try:
            # Update English language file
            en_lang_path = self.rp_path / "texts" / "en_US.lang"
            if en_lang_path.exists():
                with open(en_lang_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                if lang_key not in content:
                    with open(en_lang_path, "a", encoding="utf-8") as f:
                        f.write(f"\n{lang_key}={display_name}")
            
            # Update Chinese language file (or other languages)
            # For English version, we might not need Chinese
            # You can add support for other languages here
            
        except Exception as e:
            print(f"Failed to update language files: {e}")
    
    def validate_project(self):
        """Validate project structure"""
        issues = []
        
        # Check necessary folders
        if not self.bp_path.exists():
            issues.append("❌ Behavior pack folder does not exist")
        else:
            # Check manifest.json
            if not (self.bp_path / "manifest.json").exists():
                issues.append("❌ Behavior pack missing manifest.json")
            
            # Check necessary subfolders
            for folder in ["items", "entities", "blocks", "recipes", "loot_tables"]:
                if not (self.bp_path / folder).exists():
                    issues.append(f"⚠️ Behavior pack missing {folder} folder")
        
        if not self.rp_path.exists():
            issues.append("❌ Resource pack folder does not exist")
        else:
            # Check manifest.json
            if not (self.rp_path / "manifest.json").exists():
                issues.append("❌ Resource pack missing manifest.json")
            
            # Check texts folder
            if not (self.rp_path / "texts").exists():
                issues.append("⚠️ Resource pack missing texts folder")
        
        if issues:
            result = "Project Validation Results:\n\n" + "\n".join(issues)
        else:
            result = "✅ Project structure is complete, no issues found"
        
        messagebox.showinfo("Project Validation", result)
    
    def regenerate_uuids(self):
        """Regenerate UUIDs"""
        if not messagebox.askyesno("Confirm", "Regenerating UUIDs will update the manifest.json file. Are you sure you want to continue?"):
            return
        
        try:
            import uuid
            
            # Generate new UUIDs
            new_bp_header = str(uuid.uuid4())
            new_bp_module = str(uuid.uuid4())
            new_rp_header = str(uuid.uuid4())
            new_rp_module = str(uuid.uuid4())
            
            # Update behavior pack manifest
            bp_manifest_path = self.bp_path / "manifest.json"
            if bp_manifest_path.exists():
                with open(bp_manifest_path, "r", encoding="utf-8") as f:
                    bp_manifest = json.load(f)
                
                bp_manifest["header"]["uuid"] = new_bp_header
                bp_manifest["modules"][0]["uuid"] = new_bp_module
                
                # Update dependency UUIDs
                if "dependencies" in bp_manifest and len(bp_manifest["dependencies"]) > 0:
                    bp_manifest["dependencies"][0]["uuid"] = new_rp_header
                
                with open(bp_manifest_path, "w", encoding="utf-8") as f:
                    json.dump(bp_manifest, f, indent=2)
            
            # Update resource pack manifest
            rp_manifest_path = self.rp_path / "manifest.json"
            if rp_manifest_path.exists():
                with open(rp_manifest_path, "r", encoding="utf-8") as f:
                    rp_manifest = json.load(f)
                
                rp_manifest["header"]["uuid"] = new_rp_header
                rp_manifest["modules"][0]["uuid"] = new_rp_module
                
                with open(rp_manifest_path, "w", encoding="utf-8") as f:
                    json.dump(rp_manifest, f, indent=2)
            
            # Update project configuration
            self.project_config["uuids"] = {
                "behavior_pack": {
                    "header": new_bp_header,
                    "module": new_bp_module
                },
                "resource_pack": {
                    "header": new_rp_header,
                    "module": new_rp_module
                }
            }
            
            config_path = self.project_path / "project.json"
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.project_config, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Success", "UUIDs have been regenerated and updated")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to regenerate UUIDs: {str(e)}")
    
    def open_folder(self, path):
        """Open folder"""
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            import subprocess
            subprocess.run(["open", path])
        else:  # Linux
            import subprocess
            subprocess.run(["xdg-open", path])
    
    def save_all(self):
        """Save all configurations"""
        # Get current selected tab
        current_tab = self.notebook.select()
        if current_tab:
            tab_text = self.notebook.tab(current_tab, "text")
            
            if tab_text == "Item Configuration (BP)":
                self.save_item_to_behavior()
            elif tab_text == "Block Configuration (BP)":
                self.save_block_to_behavior()
            elif tab_text == "Entity Configuration (BP)":
                self.save_entity_to_behavior()
            elif tab_text == "Recipe Configuration (BP)":
                self.save_recipe_to_behavior()
            elif tab_text == "Loot Table Configuration (BP)":
                self.save_loot_to_behavior()
            elif tab_text == "Item Tab Configuration (BP)":
                self.save_item_tab_to_behavior()
            elif tab_text == "Item Texture (RP)":
                self.save_texture_changes()
            else:
                # If it's a file tab, try to save
                for name, frame in self.open_tabs.items():
                    if frame == self.notebook.nametowidget(current_tab):
                        messagebox.showinfo("Tip", "Please use the file menu to save")
                        break
    
    def save_as(self):
        """Save as"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            # Get current preview content
            current_tab = self.notebook.select()
            if current_tab:
                tab_text = self.notebook.tab(current_tab, "text")
                content = None
                
                if tab_text == "Item Configuration (BP)":
                    content = self.item_json_preview.get(1.0, tk.END).strip() if hasattr(self, 'item_json_preview') else None
                elif tab_text == "Block Configuration (BP)":
                    content = self.block_json_preview.get(1.0, tk.END).strip() if hasattr(self, 'block_json_preview') else None
                elif tab_text == "Entity Configuration (BP)":
                    content = self.entity_json_preview.get(1.0, tk.END).strip() if hasattr(self, 'entity_json_preview') else None
                elif tab_text == "Recipe Configuration (BP)":
                    content = self.recipe_json_preview.get(1.0, tk.END).strip() if hasattr(self, 'recipe_json_preview') else None
                elif tab_text == "Loot Table Configuration (BP)":
                    content = self.loot_json_preview.get(1.0, tk.END).strip() if hasattr(self, 'loot_json_preview') else None
                elif tab_text == "Item Tab Configuration (BP)":
                    content = self.tab_json_preview.get(1.0, tk.END).strip() if hasattr(self, 'tab_json_preview') else None
                else:
                    messagebox.showinfo("Tip", "Current tab does not support Save As")
                    return
                
                if content:
                    try:
                        with open(filename, "w", encoding="utf-8") as f:
                            f.write(content)
                        messagebox.showinfo("Success", f"File saved to: {filename}")
                    except Exception as e:
                        messagebox.showerror("Error", f"Save failed: {str(e)}")
    
    def export_addon(self):
        """Export Addon"""
        from datetime import datetime
        
        # Select export location
        filename = filedialog.asksaveasfilename(
            defaultextension=".mcaddon",
            filetypes=[("Minecraft Addon", "*.mcaddon"), ("All files", "*.*")],
            initialfile=f"{self.project_path.name}_{datetime.now().strftime('%Y%m%d')}.mcaddon"
        )
        
        if not filename:
            return
        
        try:
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Copy behavior pack and resource pack to temporary directory
                if self.bp_path.exists():
                    shutil.copytree(self.bp_path, temp_path / "behavior_pack")
                
                if self.rp_path.exists():
                    shutil.copytree(self.rp_path, temp_path / "resource_pack")
                
                # Create ZIP file
                with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Add all files
                    for file in temp_path.rglob("*"):
                        if file.is_file():
                            arcname = file.relative_to(temp_path)
                            zipf.write(file, arcname)
            
            messagebox.showinfo("Success", f"Addon exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def open_docs(self):
        """Open official documentation"""
        webbrowser.open("https://learn.microsoft.com/en-us/minecraft/creator/")
    
    def show_about(self):
        """Show about information"""
        about_text = """Quick IDE
Version: 0.6.0
A tool for creating and editing Minecraft Bedrock Edition Addons

Developed based on official documentation:
https://learn.microsoft.com/en-us/minecraft/creator/

Project Structure:
- Behavior Pack (BP): Items, Blocks, Entities, Recipes, Loot Tables, Item Tabs, etc.
- Resource Pack (RP): Textures, Models, Language Files, Sounds, etc.

Features:
✅ Item Configuration
✅ Block Configuration
✅ Entity Configuration
✅ Recipe Configuration
✅ Loot Table Configuration
✅ Item Tab Configuration
⏳ Structure Configuration (In Development)
⏳ Biome Configuration (In Development)
⏳ Dimension Configuration (In Development)

Author: Quick Team"""
        
        messagebox.showinfo("About", about_text)


if __name__ == "__main__":
    # Test code
    root = tk.Tk()
    root.geometry("1200x700")
    root.title("Quick IDE - Test Mode")
    
    # Create temporary test project
    test_path = Path.home() / "Documents" / "Quick" / "projects" / "TestProject"
    test_path.mkdir(parents=True, exist_ok=True)
    
    # Create behavior pack and resource pack folders
    bp_path = test_path / "behavior_pack"
    rp_path = test_path / "resource_pack"
    bp_path.mkdir(exist_ok=True)
    rp_path.mkdir(exist_ok=True)
    
    # Create necessary subfolders
    (bp_path / "items").mkdir(exist_ok=True)
    (bp_path / "entities").mkdir(exist_ok=True)
    (bp_path / "blocks").mkdir(exist_ok=True)
    (bp_path / "recipes").mkdir(exist_ok=True)
    (bp_path / "loot_tables").mkdir(exist_ok=True)
    (rp_path / "textures").mkdir(exist_ok=True)
    (rp_path / "texts").mkdir(exist_ok=True)
    
    # Create basic manifest.json
    bp_manifest = {
        "format_version": 2,
        "header": {
            "name": "TestProject Behavior Pack",
            "description": "Test behavior pack",
            "uuid": "12345678-1234-1234-1234-123456789abc",
            "version": [1, 0, 0],
            "min_engine_version": [1, 20, 0]
        },
        "modules": [
            {
                "type": "data",
                "uuid": "87654321-4321-4321-4321-cba987654321",
                "version": [1, 0, 0]
            }
        ]
    }
    
    with open(bp_path / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(bp_manifest, f, indent=2)
    
    rp_manifest = {
        "format_version": 2,
        "header": {
            "name": "TestProject Resource Pack",
            "description": "Test resource pack",
            "uuid": "abcdef12-3456-7890-abcd-ef1234567890",
            "version": [1, 0, 0],
            "min_engine_version": [1, 20, 0]
        },
        "modules": [
            {
                "type": "resources",
                "uuid": "fedcba09-8765-4321-fedc-ba0987654321",
                "version": [1, 0, 0]
            }
        ]
    }
    
    with open(rp_path / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(rp_manifest, f, indent=2)
    
    # Create project configuration file
    project_config = {
        "name": "TestProject",
        "description": "Test project",
        "created": "2024-01-01 12:00:00",
        "last_modified": "2024-01-01 12:00:00",
        "type": "addon",
        "version": [1, 0, 0],
        "uuids": {
            "behavior_pack": {
                "header": "12345678-1234-1234-1234-123456789abc",
                "module": "87654321-4321-4321-4321-cba987654321"
            },
            "resource_pack": {
                "header": "abcdef12-3456-7890-abcd-ef1234567890",
                "module": "fedcba09-8765-4321-fedc-ba0987654321"
            }
        },
        "min_engine_version": [1, 20, 0]
    }
    
    with open(test_path / "project.json", "w", encoding="utf-8") as f:
        json.dump(project_config, f, indent=2, ensure_ascii=False)
    
    editor = Editor(root, test_path)
    root.mainloop()