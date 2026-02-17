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
        self.root.title("Quick IDE - Minecraft基岩版Addons编辑器")
        self.root.geometry("800x500")
        
        # 设置项目路径
        self.documents_path = Path.home() / "Documents"
        self.quick_path = self.documents_path / "Quick"
        self.projects_path = self.quick_path / "projects"
        
        # 创建必要的文件夹
        self.create_directories()
        
        # 设置样式
        self.setup_styles()
        
        # 创建界面
        self.create_widgets()
        
        # 加载项目列表
        self.load_projects()
        
    def create_directories(self):
        """创建必要的文件夹"""
        try:
            self.quick_path.mkdir(exist_ok=True)
            self.projects_path.mkdir(exist_ok=True)
        except Exception as e:
            messagebox.showerror("错误", f"无法创建文件夹: {str(e)}")
    
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.configure("Title.TLabel", font=("微软雅黑", 16, "bold"))
        style.configure("Heading.TLabel", font=("微软雅黑", 12, "bold"))
        
    def create_widgets(self):
        """创建主界面组件"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="Quick IDE", style="Title.TLabel")
        title_label.pack(pady=(0, 10))
        
        # 创建左右分栏
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧面板 - 项目列表
        left_frame = ttk.Frame(paned, padding="5")
        paned.add(left_frame, weight=1)
        
        # 项目列表标题
        projects_header = ttk.Label(left_frame, text="项目列表", style="Heading.TLabel")
        projects_header.pack(anchor=tk.W, pady=(0, 5))
        
        # 项目列表框架
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 项目列表框
        self.projects_listbox = tk.Listbox(list_frame, height=15)
        self.projects_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.projects_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.projects_listbox.config(yscrollcommand=scrollbar.set)
        
        # 绑定双击事件
        self.projects_listbox.bind("<Double-Button-1>", self.open_project)
        
        # 项目操作按钮
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="新建项目", command=self.new_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="打开项目", command=self.open_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="删除项目", command=self.delete_project).pack(side=tk.LEFT, padx=2)
        
        # 右侧面板 - 欢迎信息/项目信息
        right_frame = ttk.Frame(paned, padding="5")
        paned.add(right_frame, weight=2)
        
        # 欢迎信息
        self.welcome_label = ttk.Label(right_frame, text="欢迎使用Quick IDE\n\n选择左侧的项目开始编辑\n或创建新项目", 
                                      font=("微软雅黑", 12), justify=tk.CENTER)
        self.welcome_label.pack(expand=True)
        
        # 项目信息框架（初始隐藏）
        self.info_frame = ttk.Frame(right_frame)
        
    def load_projects(self):
        """加载项目列表"""
        self.projects_listbox.delete(0, tk.END)
        
        try:
            projects = [p for p in self.projects_path.iterdir() if p.is_dir()]
            for project in projects:
                # 检查是否是有效的项目（包含project.json）
                if (project / "project.json").exists():
                    self.projects_listbox.insert(tk.END, project.name)
        except Exception as e:
            messagebox.showerror("错误", f"无法加载项目列表: {str(e)}")
    
    def generate_uuid(self):
        """生成UUID"""
        return str(uuid.uuid4())
    
    def create_manifest(self, pack_type, pack_name, description, uuid_dict):
        """创建清单文件"""
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
        """创建完整的项目结构（BP和RP分离）"""
        try:
            # 创建行为包和资源包文件夹
            bp_path = project_path / "behavior_pack"
            rp_path = project_path / "resource_pack"
            
            bp_path.mkdir(exist_ok=True)
            rp_path.mkdir(exist_ok=True)
            
            # 生成UUID
            bp_header_uuid = self.generate_uuid()
            bp_module_uuid = self.generate_uuid()
            rp_header_uuid = self.generate_uuid()
            rp_module_uuid = self.generate_uuid()
            
            # 创建行为包的manifest.json
            bp_manifest = self.create_manifest("behavior", project_name, description, {
                "header_uuid": bp_header_uuid,
                "module_uuid": bp_module_uuid,
                "resource_uuid": rp_header_uuid
            })
            
            with open(bp_path / "manifest.json", "w", encoding="utf-8") as f:
                json.dump(bp_manifest, f, indent=2)
            
            # 创建资源包的manifest.json
            rp_manifest = self.create_manifest("resource", project_name, description, {
                "header_uuid": rp_header_uuid,
                "module_uuid": rp_module_uuid
            })
            
            with open(rp_path / "manifest.json", "w", encoding="utf-8") as f:
                json.dump(rp_manifest, f, indent=2)
            
            # 创建默认的包图标（可以是一个简单的默认图标）
            # 这里我们创建一个简单的文本文件作为占位符
            with open(bp_path / "pack_icon.txt", "w") as f:
                f.write("Place pack_icon.png here")
            
            with open(rp_path / "pack_icon.txt", "w") as f:
                f.write("Place pack_icon.png here")
            
            # 创建行为包子文件夹
            bp_subfolders = [
                "items", "entities", "blocks", "recipes", 
                "scripts", "animations", "animation_controllers",
                "functions", "loot_tables", "trading"
            ]
            
            for folder in bp_subfolders:
                (bp_path / folder).mkdir(exist_ok=True)
            
            # 创建资源包子文件夹
            rp_subfolders = [
                "textures/items", "textures/entities", "textures/blocks",
                "textures/ui", "textures/particle",
                "models/entities", "models/blocks",
                "sounds", "sounds/music", "sounds/ambient",
                "texts", "font", "particles"
            ]
            
            for folder in rp_subfolders:
                (rp_path / folder).mkdir(parents=True, exist_ok=True)
            
            # 创建语言文件
            languages_file = rp_path / "texts" / "languages.json"
            with open(languages_file, "w", encoding="utf-8") as f:
                json.dump(["en_US", "zh_CN"], f, indent=2)
            
            # 创建英文语言文件
            en_file = rp_path / "texts" / "en_US.lang"
            with open(en_file, "w", encoding="utf-8") as f:
                f.write(f"## {project_name} Resource Pack\n")
            
            # 创建中文语言文件
            zh_file = rp_path / "texts" / "zh_CN.lang"
            with open(zh_file, "w", encoding="utf-8") as f:
                f.write(f"## {project_name} 资源包\n")
            
            # 创建项目配置文件
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
            raise Exception(f"创建项目结构失败: {str(e)}")
    
    def new_project(self):
        """创建新项目"""
        dialog = tk.Toplevel(self.root)
        dialog.title("新建项目")
        dialog.geometry("500x450")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # 表单
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 项目名称
        ttk.Label(frame, text="项目名称:", font=("微软雅黑", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        name_entry = ttk.Entry(frame, width=40)
        name_entry.pack(fill=tk.X, pady=(0, 10))
        name_entry.focus()
        
        # 项目描述
        ttk.Label(frame, text="项目描述:", font=("微软雅黑", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        desc_entry = ttk.Entry(frame, width=40)
        desc_entry.pack(fill=tk.X, pady=(0, 10))
        
        # 版本设置
        version_frame = ttk.LabelFrame(frame, text="版本设置", padding="10")
        version_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(version_frame, text="项目版本:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
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
        
        # 游戏版本
        ttk.Label(version_frame, text="游戏版本:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
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
        
        # 选项
        options_frame = ttk.LabelFrame(frame, text="选项", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_scripts = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="包含脚本支持 (JavaScript)", 
                       variable=self.create_scripts).pack(anchor=tk.W)
        
        self.create_functions = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="包含函数文件夹", 
                       variable=self.create_functions).pack(anchor=tk.W)
        
        def create():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("错误", "请输入项目名称")
                return
            
            project_path = self.projects_path / name
            if project_path.exists():
                messagebox.showerror("错误", "项目已存在")
                return
            
            try:
                # 创建项目文件夹
                project_path.mkdir()
                
                # 获取版本信息
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
                
                # 创建项目结构
                self.create_project_structure(
                    project_path, 
                    name, 
                    desc_entry.get().strip()
                )
                
                # 更新项目配置文件中的版本信息
                config_path = project_path / "project.json"
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                config["version"] = version
                config["min_engine_version"] = engine_version
                
                # 如果不包含脚本，可以删除scripts文件夹
                if not self.create_scripts.get():
                    scripts_path = project_path / "behavior_pack" / "scripts"
                    if scripts_path.exists():
                        shutil.rmtree(scripts_path)
                
                # 如果不包含函数，可以删除functions文件夹
                if not self.create_functions.get():
                    functions_path = project_path / "behavior_pack" / "functions"
                    if functions_path.exists():
                        shutil.rmtree(functions_path)
                
                # 保存更新后的配置
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                dialog.destroy()
                self.load_projects()
                messagebox.showinfo("成功", f"项目 '{name}' 创建成功\n\n"
                                          "项目结构:\n"
                                          "- behavior_pack/ (行为包)\n"
                                          "- resource_pack/ (资源包)\n"
                                          "已自动生成manifest.json文件")
                
            except Exception as e:
                messagebox.showerror("错误", f"创建项目失败: {str(e)}")
                # 清理已创建的文件夹
                if project_path.exists():
                    shutil.rmtree(project_path)
        
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(btn_frame, text="创建", command=create).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def open_project(self, event=None):
        """打开项目"""
        selection = self.projects_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个项目")
            return
        
        project_name = self.projects_listbox.get(selection[0])
        project_path = self.projects_path / project_name
        
        if not project_path.exists():
            messagebox.showerror("错误", "项目文件夹不存在")
            return
        
        # 验证项目结构
        if not (project_path / "behavior_pack").exists() or not (project_path / "resource_pack").exists():
            result = messagebox.askyesno("项目结构不完整", 
                                       "该项目缺少行为包或资源包文件夹。\n"
                                       "是否要自动修复项目结构？")
            if result:
                self.fix_project_structure(project_path)
            else:
                return
        
        # 打开编辑器窗口
        editor_window = tk.Toplevel(self.root)
        editor_window.title(f"Quick IDE - {project_name}")
        editor_window.geometry("1200x700")
        
        # 创建编辑器实例
        Editor(editor_window, project_path)
        
        # 当编辑器关闭时显示主窗口
        def on_editor_close():
            editor_window.destroy()
        
        editor_window.protocol("WM_DELETE_WINDOW", on_editor_close)
    
    def fix_project_structure(self, project_path):
        """修复项目结构"""
        try:
            # 检查行为包
            bp_path = project_path / "behavior_pack"
            if not bp_path.exists():
                bp_path.mkdir()
                
                # 创建基本的manifest.json
                if not (bp_path / "manifest.json").exists():
                    # 生成UUID
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
            
            # 检查资源包
            rp_path = project_path / "resource_pack"
            if not rp_path.exists():
                rp_path.mkdir()
                
                # 创建基本的manifest.json
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
            
            messagebox.showinfo("成功", "项目结构已修复")
            
        except Exception as e:
            messagebox.showerror("错误", f"修复项目结构失败: {str(e)}")
    
    def delete_project(self):
        """删除项目"""
        selection = self.projects_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个项目")
            return
        
        project_name = self.projects_listbox.get(selection[0])
        
        if messagebox.askyesno("确认删除", f"确定要删除项目 '{project_name}' 吗？\n此操作不可恢复！"):
            project_path = self.projects_path / project_name
            try:
                shutil.rmtree(project_path)
                self.load_projects()
                messagebox.showinfo("成功", f"项目 '{project_name}' 已删除")
            except Exception as e:
                messagebox.showerror("错误", f"删除项目失败: {str(e)}")

def main():
    root = tk.Tk()
    app = QuickIDE(root)
    root.mainloop()

if __name__ == "__main__":
    main()