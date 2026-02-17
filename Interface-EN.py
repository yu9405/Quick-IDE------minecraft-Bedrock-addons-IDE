import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
from pathlib import Path
import shutil
import uuid
from datetime import datetime
from Editor import Editor

class QuickIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Quick IDE - Minecraft Bedrock Edition Addons Editor")
        self.root.geometry("800x500")
        
        # Set project paths
        self.documents_path = Path.home() / "Documents"
        self.quick_path = self.documents_path / "Quick"
        self.projects_path = self.quick_path / "projects"
        
        # Create necessary folders
        self.create_directories()
        
        # Set up styles
        self.setup_styles()
        
        # Create interface
        self.create_widgets()
        
        # Load project list
        self.load_projects()
        
    def create_directories(self):
        """Create necessary folders"""
        try:
            self.quick_path.mkdir(exist_ok=True)
            self.projects_path.mkdir(exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Unable to create folders: {str(e)}")
    
    def setup_styles(self):
        """Set up interface styles"""
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Heading.TLabel", font=("Segoe UI", 12, "bold"))
        
    def create_widgets(self):
        """Create main interface widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Quick IDE", style="Title.TLabel")
        title_label.pack(pady=(0, 10))
        
        # Create left and right panels
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Project list
        left_frame = ttk.Frame(paned, padding="5")
        paned.add(left_frame, weight=1)
        
        # Project list header
        projects_header = ttk.Label(left_frame, text="Projects", style="Heading.TLabel")
        projects_header.pack(anchor=tk.W, pady=(0, 5))
        
        # Project list frame
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Project list box
        self.projects_listbox = tk.Listbox(list_frame, height=15)
        self.projects_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.projects_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.projects_listbox.config(yscrollcommand=scrollbar.set)
        
        # Bind double-click event
        self.projects_listbox.bind("<Double-Button-1>", self.open_project)
        
        # Project operation buttons
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="New Project", command=self.new_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Open Project", command=self.open_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete Project", command=self.delete_project).pack(side=tk.LEFT, padx=2)
        
        # Right panel - Welcome information/Project information
        right_frame = ttk.Frame(paned, padding="5")
        paned.add(right_frame, weight=2)
        
        # Welcome message
        self.welcome_label = ttk.Label(right_frame, text="Welcome to Quick IDE\n\nSelect a project from the list to start editing\nor create a new project", 
                                      font=("Segoe UI", 12), justify=tk.CENTER)
        self.welcome_label.pack(expand=True)
        
        # Project information frame (initially hidden)
        self.info_frame = ttk.Frame(right_frame)
        
    def load_projects(self):
        """Load project list"""
        self.projects_listbox.delete(0, tk.END)
        
        try:
            projects = [p for p in self.projects_path.iterdir() if p.is_dir()]
            for project in projects:
                # Check if it's a valid project (contains project.json)
                if (project / "project.json").exists():
                    self.projects_listbox.insert(tk.END, project.name)
        except Exception as e:
            messagebox.showerror("Error", f"Unable to load project list: {str(e)}")
    
    def generate_uuid(self):
        """Generate UUID"""
        return str(uuid.uuid4())
    
    def create_manifest(self, pack_type, pack_name, description, uuid_dict):
        """Create manifest file"""
        if pack_type == "behavior":
            manifest = {
                "format_version": 2,
                "header": {
                    "name": f"{pack_name} Behavior Pack",
                    "description": description,
                    "uuid": uuid_dict["header_uuid"],
                    "version": [1, 0, 0],
                    "min_engine_version": [1, 20, 0]
                },
                "modules": [
                    {
                        "type": "data",
                        "uuid": uuid_dict["module_uuid"],
                        "version": [1, 0, 0]
                    }
                ],
                "dependencies": [
                    {
                        "uuid": uuid_dict["resource_uuid"],
                        "version": [1, 0, 0]
                    }
                ]
            }
        else:  # resource pack
            manifest = {
                "format_version": 2,
                "header": {
                    "name": f"{pack_name} Resource Pack",
                    "description": description,
                    "uuid": uuid_dict["header_uuid"],
                    "version": [1, 0, 0],
                    "min_engine_version": [1, 20, 0]
                },
                "modules": [
                    {
                        "type": "resources",
                        "uuid": uuid_dict["module_uuid"],
                        "version": [1, 0, 0]
                    }
                ]
            }
        
        return manifest
    
    def create_project_structure(self, project_path, project_name, description):
        """Create complete project structure (BP and RP separate)"""
        try:
            # Create behavior pack and resource pack folders
            bp_path = project_path / "behavior_pack"
            rp_path = project_path / "resource_pack"
            
            bp_path.mkdir(exist_ok=True)
            rp_path.mkdir(exist_ok=True)
            
            # Generate UUIDs
            bp_header_uuid = self.generate_uuid()
            bp_module_uuid = self.generate_uuid()
            rp_header_uuid = self.generate_uuid()
            rp_module_uuid = self.generate_uuid()
            
            # Create behavior pack manifest.json
            bp_manifest = self.create_manifest("behavior", project_name, description, {
                "header_uuid": bp_header_uuid,
                "module_uuid": bp_module_uuid,
                "resource_uuid": rp_header_uuid
            })
            
            with open(bp_path / "manifest.json", "w", encoding="utf-8") as f:
                json.dump(bp_manifest, f, indent=2)
            
            # Create resource pack manifest.json
            rp_manifest = self.create_manifest("resource", project_name, description, {
                "header_uuid": rp_header_uuid,
                "module_uuid": rp_module_uuid
            })
            
            with open(rp_path / "manifest.json", "w", encoding="utf-8") as f:
                json.dump(rp_manifest, f, indent=2)
            
            # Create default pack icons (can be placeholder files)
            with open(bp_path / "pack_icon.txt", "w") as f:
                f.write("Place pack_icon.png here")
            
            with open(rp_path / "pack_icon.txt", "w") as f:
                f.write("Place pack_icon.png here")
            
            # Create behavior pack subfolders
            bp_subfolders = [
                "items", "entities", "blocks", "recipes", 
                "scripts", "animations", "animation_controllers",
                "functions", "loot_tables", "trading"
            ]
            
            for folder in bp_subfolders:
                (bp_path / folder).mkdir(exist_ok=True)
            
            # Create resource pack subfolders
            rp_subfolders = [
                "textures/items", "textures/entities", "textures/blocks",
                "textures/ui", "textures/particle",
                "models/entities", "models/blocks",
                "sounds", "sounds/music", "sounds/ambient",
                "texts", "font", "particles"
            ]
            
            for folder in rp_subfolders:
                (rp_path / folder).mkdir(parents=True, exist_ok=True)
            
            # Create language files
            languages_file = rp_path / "texts" / "languages.json"
            with open(languages_file, "w", encoding="utf-8") as f:
                json.dump(["en_US"], f, indent=2)  # Only English for English version
            
            # Create English language file
            en_file = rp_path / "texts" / "en_US.lang"
            with open(en_file, "w", encoding="utf-8") as f:
                f.write(f"## {project_name} Resource Pack\n")
            
            # Create project configuration file
            project_config = {
                "name": project_name,
                "description": description,
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": "addon",
                "version": [1, 0, 0],
                "uuids": {
                    "behavior_pack": {
                        "header": bp_header_uuid,
                        "module": bp_module_uuid
                    },
                    "resource_pack": {
                        "header": rp_header_uuid,
                        "module": rp_module_uuid
                    }
                },
                "min_engine_version": [1, 20, 0]
            }
            
            with open(project_path / "project.json", "w", encoding="utf-8") as f:
                json.dump(project_config, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to create project structure: {str(e)}")
    
    def new_project(self):
        """Create new project"""
        dialog = tk.Toplevel(self.root)
        dialog.title("New Project")
        dialog.geometry("500x450")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Form
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Project name
        ttk.Label(frame, text="Project Name:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        name_entry = ttk.Entry(frame, width=40)
        name_entry.pack(fill=tk.X, pady=(0, 10))
        name_entry.focus()
        
        # Project description
        ttk.Label(frame, text="Project Description:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        desc_entry = ttk.Entry(frame, width=40)
        desc_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Version settings
        version_frame = ttk.LabelFrame(frame, text="Version Settings", padding="10")
        version_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(version_frame, text="Project Version:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        version_major = ttk.Spinbox(version_frame, from_=0, to=9, width=5)
        version_major.grid(row=0, column=1, padx=2, pady=5)
        version_major.insert(0, "1")
        
        ttk.Label(version_frame, text=".").grid(row=0, column=2, padx=0, pady=5)
        version_minor = ttk.Spinbox(version_frame, from_=0, to=9, width=5)
        version_minor.grid(row=0, column=3, padx=2, pady=5)
        version_minor.insert(0, "0")
        
        ttk.Label(version_frame, text=".").grid(row=0, column=4, padx=0, pady=5)
        version_patch = ttk.Spinbox(version_frame, from_=0, to=9, width=5)
        version_patch.grid(row=0, column=5, padx=2, pady=5)
        version_patch.insert(0, "0")
        
        # Game version
        ttk.Label(version_frame, text="Game Version:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        engine_major = ttk.Spinbox(version_frame, from_=1, to=2, width=5)
        engine_major.grid(row=1, column=1, padx=2, pady=5)
        engine_major.insert(0, "1")
        
        ttk.Label(version_frame, text=".").grid(row=1, column=2, padx=0, pady=5)
        engine_minor = ttk.Spinbox(version_frame, from_=0, to=99, width=5)
        engine_minor.grid(row=1, column=3, padx=2, pady=5)
        engine_minor.insert(0, "20")
        
        ttk.Label(version_frame, text=".").grid(row=1, column=4, padx=0, pady=5)
        engine_patch = ttk.Spinbox(version_frame, from_=0, to=99, width=5)
        engine_patch.grid(row=1, column=5, padx=2, pady=5)
        engine_patch.insert(0, "0")
        
        # Options
        options_frame = ttk.LabelFrame(frame, text="Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_scripts = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Include Script Support (JavaScript)", 
                       variable=self.create_scripts).pack(anchor=tk.W)
        
        self.create_functions = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Include Functions Folder", 
                       variable=self.create_functions).pack(anchor=tk.W)
        
        def create():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Please enter a project name")
                return
            
            project_path = self.projects_path / name
            if project_path.exists():
                messagebox.showerror("Error", "Project already exists")
                return
            
            try:
                # Create project folder
                project_path.mkdir()
                
                # Get version information
                version = [
                    int(version_major.get()),
                    int(version_minor.get()),
                    int(version_patch.get())
                ]
                
                engine_version = [
                    int(engine_major.get()),
                    int(engine_minor.get()),
                    int(engine_patch.get())
                ]
                
                # Create project structure
                self.create_project_structure(
                    project_path, 
                    name, 
                    desc_entry.get().strip()
                )
                
                # Update project configuration file with version information
                config_path = project_path / "project.json"
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                config["version"] = version
                config["min_engine_version"] = engine_version
                
                # If not including scripts, delete scripts folder
                if not self.create_scripts.get():
                    scripts_path = project_path / "behavior_pack" / "scripts"
                    if scripts_path.exists():
                        shutil.rmtree(scripts_path)
                
                # If not including functions, delete functions folder
                if not self.create_functions.get():
                    functions_path = project_path / "behavior_pack" / "functions"
                    if functions_path.exists():
                        shutil.rmtree(functions_path)
                
                # Save updated configuration
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                dialog.destroy()
                self.load_projects()
                messagebox.showinfo("Success", f"Project '{name}' created successfully\n\n"
                                          "Project Structure:\n"
                                          "- behavior_pack/ (Behavior Pack)\n"
                                          "- resource_pack/ (Resource Pack)\n"
                                          "manifest.json files have been automatically generated")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create project: {str(e)}")
                # Clean up created folder
                if project_path.exists():
                    shutil.rmtree(project_path)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(btn_frame, text="Create", command=create).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def open_project(self, event=None):
        """Open project"""
        selection = self.projects_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a project first")
            return
        
        project_name = self.projects_listbox.get(selection[0])
        project_path = self.projects_path / project_name
        
        if not project_path.exists():
            messagebox.showerror("Error", "Project folder does not exist")
            return
        
        # Validate project structure
        if not (project_path / "behavior_pack").exists() or not (project_path / "resource_pack").exists():
            result = messagebox.askyesno("Incomplete Project Structure", 
                                       "This project is missing behavior pack or resource pack folders.\n"
                                       "Would you like to automatically fix the project structure?")
            if result:
                self.fix_project_structure(project_path)
            else:
                return
        
        # Open editor window
        editor_window = tk.Toplevel(self.root)
        editor_window.title(f"Quick IDE - {project_name}")
        editor_window.geometry("1200x700")
        
        # Create editor instance
        Editor(editor_window, project_path)
        
        # Show main window when editor closes
        def on_editor_close():
            editor_window.destroy()
        
        editor_window.protocol("WM_DELETE_WINDOW", on_editor_close)
    
    def fix_project_structure(self, project_path):
        """Fix project structure"""
        try:
            # Check behavior pack
            bp_path = project_path / "behavior_pack"
            if not bp_path.exists():
                bp_path.mkdir()
                
                # Create basic manifest.json
                if not (bp_path / "manifest.json").exists():
                    # Generate UUIDs
                    bp_header_uuid = self.generate_uuid()
                    bp_module_uuid = self.generate_uuid()
                    
                    manifest = {
                        "format_version": 2,
                        "header": {
                            "name": f"{project_path.name} Behavior Pack",
                            "description": "Auto-generated behavior pack",
                            "uuid": bp_header_uuid,
                            "version": [1, 0, 0],
                            "min_engine_version": [1, 20, 0]
                        },
                        "modules": [
                            {
                                "type": "data",
                                "uuid": bp_module_uuid,
                                "version": [1, 0, 0]
                            }
                        ]
                    }
                    
                    with open(bp_path / "manifest.json", "w", encoding="utf-8") as f:
                        json.dump(manifest, f, indent=2)
            
            # Check resource pack
            rp_path = project_path / "resource_pack"
            if not rp_path.exists():
                rp_path.mkdir()
                
                # Create basic manifest.json
                if not (rp_path / "manifest.json").exists():
                    rp_header_uuid = self.generate_uuid()
                    rp_module_uuid = self.generate_uuid()
                    
                    manifest = {
                        "format_version": 2,
                        "header": {
                            "name": f"{project_path.name} Resource Pack",
                            "description": "Auto-generated resource pack",
                            "uuid": rp_header_uuid,
                            "version": [1, 0, 0],
                            "min_engine_version": [1, 20, 0]
                        },
                        "modules": [
                            {
                                "type": "resources",
                                "uuid": rp_module_uuid,
                                "version": [1, 0, 0]
                            }
                        ]
                    }
                    
                    with open(rp_path / "manifest.json", "w", encoding="utf-8") as f:
                        json.dump(manifest, f, indent=2)
            
            messagebox.showinfo("Success", "Project structure has been fixed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fix project structure: {str(e)}")
    
    def delete_project(self):
        """Delete project"""
        selection = self.projects_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a project first")
            return
        
        project_name = self.projects_listbox.get(selection[0])
        
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete project '{project_name}'?\nThis action cannot be undone!"):
            project_path = self.projects_path / project_name
            try:
                shutil.rmtree(project_path)
                self.load_projects()
                messagebox.showinfo("Success", f"Project '{project_name}' has been deleted")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete project: {str(e)}")

def main():
    root = tk.Tk()
    app = QuickIDE(root)
    root.mainloop()

if __name__ == "__main__":
    main()