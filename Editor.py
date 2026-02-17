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
        
        # 设置行为包和资源包路径
        self.bp_path = project_path / "behavior_pack"
        self.rp_path = project_path / "resource_pack"
        
        # 加载项目配置
        self.load_project_config()
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="5")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建左右分栏
        self.create_panels()
        
    def load_project_config(self):
        """加载项目配置"""
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
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="保存", command=self.save_all, accelerator="Ctrl+S")
        file_menu.add_command(label="另存为", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="导出Addon", command=self.export_addon)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.destroy)
        
        # 行为包菜单
        bp_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="行为包 (BP)", menu=bp_menu)
        bp_menu.add_command(label="添加物品", command=lambda: self.show_config_tab("物品配置 (BP)"))
        bp_menu.add_command(label="添加方块", command=lambda: self.show_config_tab("方块配置 (BP)"))
        bp_menu.add_command(label="添加实体", command=lambda: self.show_config_tab("实体配置 (BP)"))
        bp_menu.add_command(label="添加配方", command=lambda: self.show_config_tab("配方配置 (BP)"))
        bp_menu.add_command(label="添加掉落表", command=lambda: self.show_config_tab("掉落表配置 (BP)"))
        bp_menu.add_separator()
        bp_menu.add_command(label="添加物品分页", command=lambda: self.show_config_tab("物品分页配置 (BP)"))
        bp_menu.add_separator()
        bp_menu.add_command(label="添加结构", command=lambda: self.show_config_tab("结构配置 (BP)"))
        bp_menu.add_command(label="添加生物群系", command=lambda: self.show_config_tab("生物群系配置 (BP)"))
        bp_menu.add_command(label="添加维度", command=lambda: self.show_config_tab("维度配置 (BP)"))
        
        # 资源包菜单
        rp_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="资源包 (RP)", menu=rp_menu)
        rp_menu.add_command(label="添加物品纹理", command=lambda: self.show_config_tab("物品纹理 (RP)"))
        rp_menu.add_command(label="添加方块纹理", command=lambda: self.show_config_tab("方块纹理 (RP)"))
        rp_menu.add_command(label="添加实体纹理", command=lambda: self.show_config_tab("实体纹理 (RP)"))
        rp_menu.add_command(label="添加模型", command=lambda: self.show_config_tab("模型配置 (RP)"))
        rp_menu.add_command(label="添加语言文件", command=lambda: self.show_config_tab("语言文件 (RP)"))
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="验证项目结构", command=self.validate_project)
        tools_menu.add_command(label="重新生成UUID", command=self.regenerate_uuids)
        tools_menu.add_separator()
        tools_menu.add_command(label="打开行为包文件夹", command=lambda: self.open_folder(self.bp_path))
        tools_menu.add_command(label="打开资源包文件夹", command=lambda: self.open_folder(self.rp_path))
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
        help_menu.add_command(label="官方文档", command=self.open_docs)
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = ttk.Frame(self.main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # 快速添加按钮
        ttk.Button(toolbar, text="保存", command=self.save_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="物品", command=lambda: self.show_config_tab("物品配置 (BP)")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="方块", command=lambda: self.show_config_tab("方块配置 (BP)")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="实体", command=lambda: self.show_config_tab("实体配置 (BP)")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="配方", command=lambda: self.show_config_tab("配方配置 (BP)")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="掉落表", command=lambda: self.show_config_tab("掉落表配置 (BP)")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="物品分页", command=lambda: self.show_config_tab("物品分页配置 (BP)")).pack(side=tk.LEFT, padx=2)
        
        # 项目信息显示
        info_frame = ttk.Frame(toolbar)
        info_frame.pack(side=tk.RIGHT, padx=5)
        
        project_label = ttk.Label(info_frame, text=f"项目: {self.project_path.name}")
        project_label.pack(side=tk.TOP, anchor=tk.E)
        
        version = self.project_config.get("version", [1, 0, 0])
        version_str = f"v{version[0]}.{version[1]}.{version[2]}"
        version_label = ttk.Label(info_frame, text=version_str, foreground="gray")
        version_label.pack(side=tk.BOTTOM, anchor=tk.E)
    
    def create_panels(self):
        """创建左右分栏"""
        # 使用PanedWindow
        paned = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧面板 - 文件浏览器
        left_frame = ttk.Frame(paned, padding="5", width=250)
        paned.add(left_frame, weight=1)
        
        # 创建标签页来区分BP和RP
        file_notebook = ttk.Notebook(left_frame)
        file_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 行为包标签页
        bp_frame = ttk.Frame(file_notebook)
        file_notebook.add(bp_frame, text="行为包 (BP)")
        self.create_file_tree(bp_frame, self.bp_path, "bp")
        
        # 资源包标签页
        rp_frame = ttk.Frame(file_notebook)
        file_notebook.add(rp_frame, text="资源包 (RP)")
        self.create_file_tree(rp_frame, self.rp_path, "rp")
        
        # 右侧面板 - 编辑区域
        right_frame = ttk.Frame(paned, padding="5")
        paned.add(right_frame, weight=3)
        
        # 创建选项卡
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 欢迎选项卡
        welcome_frame = ttk.Frame(self.notebook)
        self.notebook.add(welcome_frame, text="欢迎")
        
        welcome_text = f"""欢迎编辑项目: {self.project_path.name}

项目信息:
- 行为包路径: {self.bp_path}
- 资源包路径: {self.rp_path}
- 版本: {self.project_config.get('version', [1,0,0])}
- 游戏版本: {self.project_config.get('min_engine_version', [1,20,0])}

支持的功能:
✅ 物品配置
✅ 方块配置
✅ 实体配置
✅ 配方配置
✅ 掉落表配置
✅ 物品分页配置
⏳ 结构配置 (开发中)
⏳ 生物群系配置 (开发中)
⏳ 维度配置 (开发中)

使用说明:
1. 在左侧选择行为包或资源包文件
2. 双击文件进行编辑
3. 使用菜单或工具栏添加新配置

参考文档: https://learn.microsoft.com/zh-cn/minecraft/creator/"""
        
        welcome_label = ttk.Label(welcome_frame, text=welcome_text,
                                 font=("微软雅黑", 11),
                                 justify=tk.LEFT)
        welcome_label.pack(expand=True, padx=20, pady=20)
        
        # 存储打开的选项卡
        self.open_tabs = {}
    
    def create_file_tree(self, parent, root_path, tree_id):
        """创建文件树"""
        # 创建框架
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建树
        tree = ttk.Treeview(frame, show="tree", height=20)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.config(yscrollcommand=scrollbar.set)
        
        # 存储树引用
        if not hasattr(self, 'file_trees'):
            self.file_trees = {}
        self.file_trees[tree_id] = tree
        
        # 加载文件
        self.load_file_tree_node(tree, "", root_path, root_path.name)
        
        # 绑定双击事件
        tree.bind("<Double-1>", lambda e: self.open_file_from_tree(e, tree, root_path))
    
    def load_file_tree_node(self, tree, parent, path, node_text):
        """递归加载文件树节点"""
        if not path.exists():
            node = tree.insert(parent, "end", text=f"{node_text} (不存在)", open=True)
            return
        
        node = tree.insert(parent, "end", text=node_text, open=True)
        
        try:
            # 先添加文件夹
            folders = []
            files = []
            
            for item in path.iterdir():
                if item.is_dir():
                    folders.append(item)
                else:
                    files.append(item)
            
            # 排序
            folders.sort(key=lambda x: x.name)
            files.sort(key=lambda x: x.name)
            
            # 添加文件夹
            for folder in folders:
                self.load_file_tree_node(tree, node, folder, folder.name)
            
            # 添加文件
            for file in files:
                # 根据文件类型设置不同的图标标记
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
            print(f"加载文件树失败: {e}")
    
    def open_file_from_tree(self, event, tree, root_path):
        """从文件树打开文件"""
        selection = tree.selection()
        if not selection:
            return
        
        item = selection[0]
        item_text = tree.item(item, "text")
        
        # 检查是否为文件（有扩展名）
        if "." not in item_text:
            return
        
        # 获取完整路径
        path_parts = []
        current = item
        while current:
            text = tree.item(current, "text")
            path_parts.insert(0, text)
            current = tree.parent(current)
        
        # 构建文件路径
        # 第一个部分是根节点名称，需要跳过
        if len(path_parts) > 1:
            file_path = root_path
            for part in path_parts[1:-1]:  # 跳过根节点和文件名
                file_path = file_path / part
            file_path = file_path / path_parts[-1]
            
            if file_path.exists() and file_path.is_file():
                self.open_file_in_tab(file_path)
    
    def open_file_in_tab(self, file_path):
        """在选项卡中打开文件"""
        tab_name = f"{file_path.parent.name}/{file_path.name}"
        
        if tab_name in self.open_tabs:
            self.notebook.select(self.open_tabs[tab_name])
            return
        
        # 创建新选项卡
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=tab_name)
        self.open_tabs[tab_name] = tab_frame
        self.notebook.select(tab_frame)
        
        # 根据文件类型显示内容
        if file_path.suffix == ".json":
            self.display_json_file(tab_frame, file_path)
        elif file_path.suffix == ".lang":
            self.display_text_file(tab_frame, file_path)
        elif file_path.suffix in [".png", ".jpg"]:
            self.display_image_info(tab_frame, file_path)
        else:
            self.display_text_file(tab_frame, file_path)
    
    def display_json_file(self, parent, file_path):
        """显示JSON文件内容"""
        # 创建文本框
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        text_widget = tk.Text(text_frame, wrap=tk.NONE)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar_y = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar_y.set)
        
        scrollbar_x = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=text_widget.xview)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        text_widget.config(xscrollcommand=scrollbar_x.set)
        
        # 加载文件内容
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                # 格式化JSON
                try:
                    json_obj = json.loads(content)
                    formatted = json.dumps(json_obj, indent=2, ensure_ascii=False)
                    text_widget.insert(1.0, formatted)
                except:
                    text_widget.insert(1.0, content)
        except Exception as e:
            text_widget.insert(1.0, f"无法读取文件: {str(e)}")
        
        # 保存按钮
        save_btn = ttk.Button(parent, text="保存修改", 
                             command=lambda: self.save_json_file(file_path, text_widget))
        save_btn.pack(pady=5)
    
    def display_text_file(self, parent, file_path):
        """显示文本文件内容"""
        text_widget = tk.Text(parent, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text_widget.insert(1.0, f.read())
        except:
            text_widget.insert(1.0, "无法读取文件")
    
    def display_image_info(self, parent, file_path):
        """显示图片信息"""
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(info_frame, text="图片文件信息", font=("微软雅黑", 12, "bold")).pack(pady=10)
        
        info_text = f"""
文件名: {file_path.name}
路径: {file_path}
大小: {file_path.stat().st_size} 字节
类型: {file_path.suffix}
        """
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(pady=10)
        
        ttk.Label(info_frame, text="提示: 请使用外部图像编辑器编辑此文件").pack(pady=10)
        
        ttk.Button(info_frame, text="打开文件夹", 
                  command=lambda: self.open_folder(file_path.parent)).pack(pady=5)
    
    def save_json_file(self, file_path, text_widget):
        """保存JSON文件"""
        content = text_widget.get(1.0, tk.END).strip()
        try:
            # 验证JSON
            json.loads(content)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            messagebox.showinfo("成功", f"文件已保存: {file_path}")
        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"JSON格式错误: {str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def show_config_tab(self, tab_name):
        """显示配置选项卡"""
        if tab_name in self.open_tabs:
            self.notebook.select(self.open_tabs[tab_name])
            return
        
        # 创建新选项卡
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=tab_name)
        self.open_tabs[tab_name] = tab_frame
        self.notebook.select(tab_frame)
        
        # 根据选项卡名称创建对应的配置界面
        if tab_name == "物品配置 (BP)":
            self.create_item_config(tab_frame)
        elif tab_name == "方块配置 (BP)":
            self.create_block_config(tab_frame)
        elif tab_name == "实体配置 (BP)":
            self.create_entity_config(tab_frame)
        elif tab_name == "配方配置 (BP)":
            self.create_recipe_config(tab_frame)
        elif tab_name == "掉落表配置 (BP)":
            self.create_loot_table_config(tab_frame)
        elif tab_name == "物品分页配置 (BP)":
            self.create_item_tab_config(tab_frame)
        elif tab_name == "结构配置 (BP)":
            self.create_placeholder_config(tab_frame, "结构配置 (开发中)")
        elif tab_name == "生物群系配置 (BP)":
            self.create_placeholder_config(tab_frame, "生物群系配置 (开发中)")
        elif tab_name == "维度配置 (BP)":
            self.create_placeholder_config(tab_frame, "维度配置 (开发中)")
        elif tab_name == "物品纹理 (RP)":
            self.create_item_texture_config(tab_frame)
        elif tab_name in ["方块纹理 (RP)", "实体纹理 (RP)", "模型配置 (RP)", "语言文件 (RP)"]:
            self.create_placeholder_config(tab_frame, "资源包配置开发中...")
        else:
            self.create_placeholder_config(tab_frame, "配置开发中...")
    
    def create_placeholder_config(self, parent, message):
        """创建占位配置界面"""
        label = ttk.Label(parent, text=message, font=("微软雅黑", 14))
        label.pack(expand=True)
    
    # ==================== 物品配置 ====================
    def create_item_config(self, parent):
        """创建物品配置界面"""
        # 创建滚动框架
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
        
        # 标题
        title_label = ttk.Label(scrollable_frame, text="物品配置 (行为包)", 
                               font=("微软雅黑", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="w")
        
        # 说明
        desc_label = ttk.Label(scrollable_frame, 
                              text="在行为包中定义物品的行为属性\n"
                                   "对应的纹理需要在资源包中配置",
                              justify=tk.LEFT)
        desc_label.grid(row=1, column=0, columnspan=3, pady=5, padx=10, sticky="w")
        
        # 基本信息框架
        basic_frame = ttk.LabelFrame(scrollable_frame, text="基本信息", padding="10")
        basic_frame.grid(row=2, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # 物品标识符
        ttk.Label(basic_frame, text="物品标识符:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.item_identifier = ttk.Entry(basic_frame, width=40)
        self.item_identifier.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(basic_frame, text="例如: wiki:example_item", foreground="gray").grid(row=0, column=2, pady=5, padx=5, sticky="w")
        
        # 显示名称
        ttk.Label(basic_frame, text="显示名称:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.item_display_name = ttk.Entry(basic_frame, width=40)
        self.item_display_name.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        
        # 描述
        ttk.Label(basic_frame, text="物品描述:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.item_description = ttk.Entry(basic_frame, width=40)
        self.item_description.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        
        # 类别
        ttk.Label(basic_frame, text="类别:").grid(row=3, column=0, pady=5, padx=5, sticky="w")
        self.item_category = ttk.Combobox(basic_frame, values=["items", "equipment", "nature", "construction"], width=20)
        self.item_category.grid(row=3, column=1, pady=5, padx=5, sticky="w")
        self.item_category.set("items")
        
        # 组件框架
        components_frame = ttk.LabelFrame(scrollable_frame, text="组件配置", padding="10")
        components_frame.grid(row=3, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # 创建标签页
        component_notebook = ttk.Notebook(components_frame)
        component_notebook.grid(row=0, column=0, columnspan=3, pady=5, sticky="ew")
        
        # 基础组件标签页
        basic_comp_frame = ttk.Frame(component_notebook)
        component_notebook.add(basic_comp_frame, text="基础组件")
        
        # 最大堆叠数量
        ttk.Label(basic_comp_frame, text="最大堆叠数量:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.max_stack_size = ttk.Spinbox(basic_comp_frame, from_=1, to=64, width=10)
        self.max_stack_size.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        self.max_stack_size.insert(0, "64")
        
        # 是否可手持
        self.hand_equipped = tk.BooleanVar(value=True)
        ttk.Checkbutton(basic_comp_frame, text="可手持", variable=self.hand_equipped).grid(row=1, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        # 耐久度标签页
        durability_frame = ttk.Frame(component_notebook)
        component_notebook.add(durability_frame, text="耐久度")
        
        self.has_durability = tk.BooleanVar(value=False)
        ttk.Checkbutton(durability_frame, text="启用耐久度", variable=self.has_durability, 
                       command=self.toggle_durability).grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        ttk.Label(durability_frame, text="最大耐久度:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.max_durability = ttk.Spinbox(durability_frame, from_=1, to=10000, width=10, state="disabled")
        self.max_durability.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        self.max_durability.insert(0, "100")
        
        # 食物标签页
        food_frame = ttk.Frame(component_notebook)
        component_notebook.add(food_frame, text="食物")
        
        self.is_food = tk.BooleanVar(value=False)
        ttk.Checkbutton(food_frame, text="可作为食物", variable=self.is_food,
                       command=self.toggle_food).grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        ttk.Label(food_frame, text="营养值:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.nutrition = ttk.Spinbox(food_frame, from_=1, to=20, width=10, state="disabled")
        self.nutrition.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        self.nutrition.insert(0, "4")
        
        ttk.Label(food_frame, text="饱和度:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.saturation = ttk.Spinbox(food_frame, from_=0, to=20, width=10, state="disabled")
        self.saturation.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        self.saturation.insert(0, "2")
        
        # 武器标签页
        weapon_frame = ttk.Frame(component_notebook)
        component_notebook.add(weapon_frame, text="武器")
        
        self.is_weapon = tk.BooleanVar(value=False)
        ttk.Checkbutton(weapon_frame, text="可作为武器", variable=self.is_weapon,
                       command=self.toggle_weapon).grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        ttk.Label(weapon_frame, text="伤害值:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.damage = ttk.Spinbox(weapon_frame, from_=1, to=100, width=10, state="disabled")
        self.damage.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        self.damage.insert(0, "5")
        
        # 保存路径框架
        path_frame = ttk.LabelFrame(scrollable_frame, text="保存路径", padding="10")
        path_frame.grid(row=4, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        ttk.Label(path_frame, text="文件名:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.item_filename = ttk.Entry(path_frame, width=40)
        self.item_filename.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(path_frame, text=".json", foreground="gray").grid(row=0, column=2, pady=5, padx=0, sticky="w")
        
        # 按钮框架
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        ttk.Button(btn_frame, text="生成JSON", command=self.generate_item_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="保存到行为包", command=self.save_item_to_behavior).pack(side=tk.LEFT, padx=5)
        
        # JSON预览框架
        preview_frame = ttk.LabelFrame(scrollable_frame, text="JSON预览", padding="10")
        preview_frame.grid(row=6, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        self.item_json_preview = tk.Text(preview_frame, height=15, width=80)
        self.item_json_preview.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        preview_scrollbar = ttk.Scrollbar(self.item_json_preview, orient=tk.VERTICAL, command=self.item_json_preview.yview)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.item_json_preview.config(yscrollcommand=preview_scrollbar.set)
    
    # ==================== 方块配置 ====================
    def create_block_config(self, parent):
        """创建方块配置界面"""
        # 创建滚动框架
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
        
        # 标题
        title_label = ttk.Label(scrollable_frame, text="方块配置 (行为包)", 
                               font=("微软雅黑", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="w")
        
        # 说明
        desc_label = ttk.Label(scrollable_frame, 
                              text="在行为包中定义自定义方块的行为和属性\n"
                                   "对应的模型和纹理需要在资源包中配置",
                              justify=tk.LEFT)
        desc_label.grid(row=1, column=0, columnspan=3, pady=5, padx=10, sticky="w")
        
        # 基本信息框架
        basic_frame = ttk.LabelFrame(scrollable_frame, text="基本信息", padding="10")
        basic_frame.grid(row=2, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # 方块标识符
        ttk.Label(basic_frame, text="方块标识符:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.block_identifier = ttk.Entry(basic_frame, width=40)
        self.block_identifier.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(basic_frame, text="例如: wiki:example_block", foreground="gray").grid(row=0, column=2, pady=5, padx=5, sticky="w")
        
        # 显示名称
        ttk.Label(basic_frame, text="显示名称:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.block_display_name = ttk.Entry(basic_frame, width=40)
        self.block_display_name.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        
        # 类别
        ttk.Label(basic_frame, text="类别:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.block_category = ttk.Combobox(basic_frame, values=["construction", "nature", "equipment", "items"], width=20)
        self.block_category.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        self.block_category.set("construction")
        
        # 组件框架
        components_frame = ttk.LabelFrame(scrollable_frame, text="组件配置", padding="10")
        components_frame.grid(row=3, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # 创建标签页
        component_notebook = ttk.Notebook(components_frame)
        component_notebook.grid(row=0, column=0, columnspan=3, pady=5, sticky="ew")
        
        # 基础属性标签页
        basic_prop_frame = ttk.Frame(component_notebook)
        component_notebook.add(basic_prop_frame, text="基础属性")
        
        # 硬度
        ttk.Label(basic_prop_frame, text="硬度:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.block_hardness = ttk.Spinbox(basic_prop_frame, from_=0, to=100, width=10)
        self.block_hardness.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        self.block_hardness.insert(0, "1.5")
        
        # 爆炸抗性
        ttk.Label(basic_prop_frame, text="爆炸抗性:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.block_resistance = ttk.Spinbox(basic_prop_frame, from_=0, to=100, width=10)
        self.block_resistance.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        self.block_resistance.insert(0, "10")
        
        # 发光等级
        ttk.Label(basic_prop_frame, text="发光等级:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.block_light_emission = ttk.Spinbox(basic_prop_frame, from_=0, to=15, width=10)
        self.block_light_emission.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        self.block_light_emission.insert(0, "0")
        
        # 透光
        self.block_transparent = tk.BooleanVar(value=False)
        ttk.Checkbutton(basic_prop_frame, text="透明方块", variable=self.block_transparent).grid(row=3, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        # 可燃
        self.block_flammable = tk.BooleanVar(value=False)
        ttk.Checkbutton(basic_prop_frame, text="可燃", variable=self.block_flammable).grid(row=4, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        # 可替代
        self.block_replaceable = tk.BooleanVar(value=False)
        ttk.Checkbutton(basic_prop_frame, text="可被替代", variable=self.block_replaceable).grid(row=5, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        # 破坏掉落标签页
        loot_frame = ttk.Frame(component_notebook)
        component_notebook.add(loot_frame, text="破坏掉落")
        
        ttk.Label(loot_frame, text="掉落物品:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.block_loot_item = ttk.Entry(loot_frame, width=30)
        self.block_loot_item.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        
        ttk.Label(loot_frame, text="掉落数量:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.block_loot_count = ttk.Spinbox(loot_frame, from_=1, to=64, width=10)
        self.block_loot_count.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        self.block_loot_count.insert(0, "1")
        
        # 几何体标签页
        geometry_frame = ttk.Frame(component_notebook)
        component_notebook.add(geometry_frame, text="几何体")
        
        ttk.Label(geometry_frame, text="几何体标识符:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.block_geometry = ttk.Entry(geometry_frame, width=30)
        self.block_geometry.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(geometry_frame, text="例如: geometry.example_block", foreground="gray").grid(row=0, column=2, pady=5, padx=5, sticky="w")
        
        self.block_unit_cube = tk.BooleanVar(value=True)
        ttk.Checkbutton(geometry_frame, text="使用单位立方体", variable=self.block_unit_cube).grid(row=1, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        # 材质标签页
        material_frame = ttk.Frame(component_notebook)
        component_notebook.add(material_frame, text="材质")
        
        ttk.Label(material_frame, text="材质实例:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.block_material = ttk.Combobox(material_frame, values=["opaque", "alpha_test", "blend"], width=20)
        self.block_material.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        self.block_material.set("opaque")
        
        ttk.Label(material_frame, text="纹理:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.block_texture = ttk.Entry(material_frame, width=30)
        self.block_texture.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(material_frame, text="例如: wiki:example_block", foreground="gray").grid(row=1, column=2, pady=5, padx=5, sticky="w")
        
        # 保存路径框架
        path_frame = ttk.LabelFrame(scrollable_frame, text="保存路径", padding="10")
        path_frame.grid(row=4, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        ttk.Label(path_frame, text="文件名:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.block_filename = ttk.Entry(path_frame, width=40)
        self.block_filename.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(path_frame, text=".json", foreground="gray").grid(row=0, column=2, pady=5, padx=0, sticky="w")
        
        # 按钮框架
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        ttk.Button(btn_frame, text="生成JSON", command=self.generate_block_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="保存到行为包", command=self.save_block_to_behavior).pack(side=tk.LEFT, padx=5)
        
        # JSON预览框架
        preview_frame = ttk.LabelFrame(scrollable_frame, text="JSON预览", padding="10")
        preview_frame.grid(row=6, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        self.block_json_preview = tk.Text(preview_frame, height=15, width=80)
        self.block_json_preview.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        preview_scrollbar = ttk.Scrollbar(self.block_json_preview, orient=tk.VERTICAL, command=self.block_json_preview.yview)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.block_json_preview.config(yscrollcommand=preview_scrollbar.set)
    
    # ==================== 实体配置 ====================
    def create_entity_config(self, parent):
        """创建实体配置界面"""
        # 创建滚动框架
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
        
        # 标题
        title_label = ttk.Label(scrollable_frame, text="实体配置 (行为包)", 
                               font=("微软雅黑", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="w")
        
        # 说明
        desc_label = ttk.Label(scrollable_frame, 
                              text="在行为包中定义自定义实体的行为和属性\n"
                                   "对应的模型和纹理需要在资源包中配置",
                              justify=tk.LEFT)
        desc_label.grid(row=1, column=0, columnspan=3, pady=5, padx=10, sticky="w")
        
        # 基本信息框架
        basic_frame = ttk.LabelFrame(scrollable_frame, text="基本信息", padding="10")
        basic_frame.grid(row=2, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # 实体标识符
        ttk.Label(basic_frame, text="实体标识符:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.entity_identifier = ttk.Entry(basic_frame, width=40)
        self.entity_identifier.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(basic_frame, text="例如: wiki:example_entity", foreground="gray").grid(row=0, column=2, pady=5, padx=5, sticky="w")
        
        # 显示名称
        ttk.Label(basic_frame, text="显示名称:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.entity_display_name = ttk.Entry(basic_frame, width=40)
        self.entity_display_name.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        
        # 实体类型
        ttk.Label(basic_frame, text="实体类型:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.entity_type = ttk.Combobox(basic_frame, values=["animal", "monster", "npc", "ambient"], width=20)
        self.entity_type.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        self.entity_type.set("animal")
        
        # 组件框架
        components_frame = ttk.LabelFrame(scrollable_frame, text="组件配置", padding="10")
        components_frame.grid(row=3, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # 创建标签页
        component_notebook = ttk.Notebook(components_frame)
        component_notebook.grid(row=0, column=0, columnspan=3, pady=5, sticky="ew")
        
        # 基础属性标签页
        basic_prop_frame = ttk.Frame(component_notebook)
        component_notebook.add(basic_prop_frame, text="基础属性")
        
        # 生命值
        ttk.Label(basic_prop_frame, text="最大生命值:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.entity_health = ttk.Spinbox(basic_prop_frame, from_=1, to=1000, width=10)
        self.entity_health.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        self.entity_health.insert(0, "20")
        
        # 移动速度
        ttk.Label(basic_prop_frame, text="移动速度:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.entity_speed = ttk.Spinbox(basic_prop_frame, from_=0.1, to=10, increment=0.1, width=10)
        self.entity_speed.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        self.entity_speed.insert(0, "0.25")
        
        # 攻击伤害
        ttk.Label(basic_prop_frame, text="攻击伤害:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.entity_damage = ttk.Spinbox(basic_prop_frame, from_=0, to=100, width=10)
        self.entity_damage.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        self.entity_damage.insert(0, "0")
        
        # 击退抗性
        ttk.Label(basic_prop_frame, text="击退抗性:").grid(row=3, column=0, pady=5, padx=5, sticky="w")
        self.entity_knockback_resistance = ttk.Spinbox(basic_prop_frame, from_=0, to=1, increment=0.1, width=10)
        self.entity_knockback_resistance.grid(row=3, column=1, pady=5, padx=5, sticky="w")
        self.entity_knockback_resistance.insert(0, "0")
        
        # 行为标签页
        behavior_frame = ttk.Frame(component_notebook)
        component_notebook.add(behavior_frame, text="行为")
        
        self.entity_friendly = tk.BooleanVar(value=True)
        ttk.Checkbutton(behavior_frame, text="被动生物", variable=self.entity_friendly).grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        self.entity_baby = tk.BooleanVar(value=False)
        ttk.Checkbutton(behavior_frame, text="可繁殖", variable=self.entity_baby).grid(row=1, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        ttk.Label(behavior_frame, text="行为模板:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.entity_behavior = ttk.Combobox(behavior_frame, 
                                           values=["idle", "walk", "look", "panic", "follow_owner"], 
                                           width=20)
        self.entity_behavior.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        
        # 装备标签页
        equipment_frame = ttk.Frame(component_notebook)
        component_notebook.add(equipment_frame, text="装备")
        
        self.entity_equipment = tk.BooleanVar(value=False)
        ttk.Checkbutton(equipment_frame, text="可装备物品", variable=self.entity_equipment).grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        ttk.Label(equipment_frame, text="装备表:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.entity_equipment_table = ttk.Entry(equipment_frame, width=30)
        self.entity_equipment_table.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        
        # 掉落物标签页
        loot_frame = ttk.Frame(component_notebook)
        component_notebook.add(loot_frame, text="掉落物")
        
        ttk.Label(loot_frame, text="掉落表:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.entity_loot_table = ttk.Entry(loot_frame, width=30)
        self.entity_loot_table.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(loot_frame, text="例如: loot_tables/entities/example.json", foreground="gray").grid(row=0, column=2, pady=5, padx=5, sticky="w")
        
        # 生成规则标签页
        spawn_frame = ttk.Frame(component_notebook)
        component_notebook.add(spawn_frame, text="生成规则")
        
        self.entity_spawnable = tk.BooleanVar(value=True)
        ttk.Checkbutton(spawn_frame, text="允许自然生成", variable=self.entity_spawnable).grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        ttk.Label(spawn_frame, text="生物群系:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.entity_biome = ttk.Combobox(spawn_frame, 
                                        values=["plains", "desert", "forest", "taiga", "swamp", "jungle"], 
                                        width=20)
        self.entity_biome.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        
        ttk.Label(spawn_frame, text="生成权重:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.entity_spawn_weight = ttk.Spinbox(spawn_frame, from_=1, to=100, width=10)
        self.entity_spawn_weight.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        self.entity_spawn_weight.insert(0, "10")
        
        # 最小生成数量
        ttk.Label(spawn_frame, text="最小生成:").grid(row=3, column=0, pady=5, padx=5, sticky="w")
        self.entity_spawn_min = ttk.Spinbox(spawn_frame, from_=1, to=10, width=10)
        self.entity_spawn_min.grid(row=3, column=1, pady=5, padx=5, sticky="w")
        self.entity_spawn_min.insert(0, "2")
        
        # 最大生成数量
        ttk.Label(spawn_frame, text="最大生成:").grid(row=4, column=0, pady=5, padx=5, sticky="w")
        self.entity_spawn_max = ttk.Spinbox(spawn_frame, from_=1, to=20, width=10)
        self.entity_spawn_max.grid(row=4, column=1, pady=5, padx=5, sticky="w")
        self.entity_spawn_max.insert(0, "4")
        
        # 保存路径框架
        path_frame = ttk.LabelFrame(scrollable_frame, text="保存路径", padding="10")
        path_frame.grid(row=4, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        ttk.Label(path_frame, text="文件名:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.entity_filename = ttk.Entry(path_frame, width=40)
        self.entity_filename.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(path_frame, text=".json", foreground="gray").grid(row=0, column=2, pady=5, padx=0, sticky="w")
        
        # 按钮框架
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        ttk.Button(btn_frame, text="生成JSON", command=self.generate_entity_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="保存到行为包", command=self.save_entity_to_behavior).pack(side=tk.LEFT, padx=5)
        
        # JSON预览框架
        preview_frame = ttk.LabelFrame(scrollable_frame, text="JSON预览", padding="10")
        preview_frame.grid(row=6, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        self.entity_json_preview = tk.Text(preview_frame, height=15, width=80)
        self.entity_json_preview.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        preview_scrollbar = ttk.Scrollbar(self.entity_json_preview, orient=tk.VERTICAL, command=self.entity_json_preview.yview)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.entity_json_preview.config(yscrollcommand=preview_scrollbar.set)
    
    # ==================== 配方配置 ====================
    def create_recipe_config(self, parent):
        """创建配方配置界面"""
        # 创建滚动框架
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
        
        # 标题
        title_label = ttk.Label(scrollable_frame, text="配方配置 (行为包)", 
                               font=("微软雅黑", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="w")
        
        # 说明
        desc_label = ttk.Label(scrollable_frame, 
                              text="在行为包中定义合成配方\n"
                                   "支持工作台、熔炉、酿造台等配方类型",
                              justify=tk.LEFT)
        desc_label.grid(row=1, column=0, columnspan=3, pady=5, padx=10, sticky="w")
        
        # 配方类型选择
        type_frame = ttk.LabelFrame(scrollable_frame, text="配方类型", padding="10")
        type_frame.grid(row=2, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        self.recipe_type = tk.StringVar(value="crafting_shaped")
        ttk.Radiobutton(type_frame, text="有序合成", variable=self.recipe_type, 
                       value="crafting_shaped", command=self.update_recipe_ui).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(type_frame, text="无序合成", variable=self.recipe_type, 
                       value="crafting_shapeless", command=self.update_recipe_ui).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(type_frame, text="熔炉配方", variable=self.recipe_type, 
                       value="furnace", command=self.update_recipe_ui).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(type_frame, text="酿造配方", variable=self.recipe_type, 
                       value="brewing", command=self.update_recipe_ui).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # 配方信息框架
        info_frame = ttk.LabelFrame(scrollable_frame, text="配方信息", padding="10")
        info_frame.grid(row=3, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # 输出物品
        ttk.Label(info_frame, text="输出物品:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.recipe_output = ttk.Entry(info_frame, width=30)
        self.recipe_output.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(info_frame, text="例如: minecraft:diamond", foreground="gray").grid(row=0, column=2, pady=5, padx=5, sticky="w")
        
        # 输出数量
        ttk.Label(info_frame, text="输出数量:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.recipe_output_count = ttk.Spinbox(info_frame, from_=1, to=64, width=10)
        self.recipe_output_count.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        self.recipe_output_count.insert(0, "1")
        
        # 配方标识符
        ttk.Label(info_frame, text="配方标识符:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.recipe_identifier = ttk.Entry(info_frame, width=30)
        self.recipe_identifier.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(info_frame, text="例如: wiki:example_recipe", foreground="gray").grid(row=2, column=2, pady=5, padx=5, sticky="w")
        
        # 合成输入框架
        self.recipe_input_frame = ttk.LabelFrame(scrollable_frame, text="合成输入", padding="10")
        self.recipe_input_frame.grid(row=4, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # 创建3x3合成网格
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
        
        # 图案说明
        pattern_label = ttk.Label(self.recipe_input_frame, 
                                 text="输入物品ID (空表示无物品)\n例如: minecraft:stone",
                                 justify=tk.CENTER, foreground="gray")
        pattern_label.pack()
        
        # 熔炉配方特定框架
        self.furnace_frame = ttk.Frame(scrollable_frame)
        
        # 酿造配方特定框架
        self.brewing_frame = ttk.Frame(scrollable_frame)
        
        # 保存路径框架
        path_frame = ttk.LabelFrame(scrollable_frame, text="保存路径", padding="10")
        path_frame.grid(row=5, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        ttk.Label(path_frame, text="文件名:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.recipe_filename = ttk.Entry(path_frame, width=40)
        self.recipe_filename.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(path_frame, text=".json", foreground="gray").grid(row=0, column=2, pady=5, padx=0, sticky="w")
        
        # 按钮框架
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        ttk.Button(btn_frame, text="生成JSON", command=self.generate_recipe_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="保存到行为包", command=self.save_recipe_to_behavior).pack(side=tk.LEFT, padx=5)
        
        # JSON预览框架
        preview_frame = ttk.LabelFrame(scrollable_frame, text="JSON预览", padding="10")
        preview_frame.grid(row=7, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        self.recipe_json_preview = tk.Text(preview_frame, height=15, width=80)
        self.recipe_json_preview.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        preview_scrollbar = ttk.Scrollbar(self.recipe_json_preview, orient=tk.VERTICAL, command=self.recipe_json_preview.yview)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.recipe_json_preview.config(yscrollcommand=preview_scrollbar.set)
    
    # ==================== 掉落表配置 ====================
    def create_loot_table_config(self, parent):
        """创建掉落表配置界面"""
        # 创建滚动框架
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
        
        # 标题
        title_label = ttk.Label(scrollable_frame, text="掉落表配置 (行为包)", 
                               font=("微软雅黑", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="w")
        
        # 说明
        desc_label = ttk.Label(scrollable_frame, 
                              text="定义方块、实体或宝箱的掉落物品规则",
                              justify=tk.LEFT)
        desc_label.grid(row=1, column=0, columnspan=3, pady=5, padx=10, sticky="w")
        
        # 掉落表类型
        type_frame = ttk.LabelFrame(scrollable_frame, text="掉落表类型", padding="10")
        type_frame.grid(row=2, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        self.loot_type = tk.StringVar(value="entity")
        ttk.Radiobutton(type_frame, text="实体掉落", variable=self.loot_type, 
                       value="entity").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(type_frame, text="方块掉落", variable=self.loot_type, 
                       value="block").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(type_frame, text="宝箱战利品", variable=self.loot_type, 
                       value="chest").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        # 掉落池框架
        pool_frame = ttk.LabelFrame(scrollable_frame, text="掉落池", padding="10")
        pool_frame.grid(row=3, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # 掉落池列表
        self.loot_pool_listbox = tk.Listbox(pool_frame, height=5)
        self.loot_pool_listbox.pack(fill=tk.X, pady=5)
        
        # 添加初始掉落池
        self.loot_pools = []
        self.loot_pool_listbox.insert(tk.END, "主掉落池")
        self.loot_pools.append({"name": "主掉落池", "entries": []})
        
        # 掉落池操作按钮
        pool_btn_frame = ttk.Frame(pool_frame)
        pool_btn_frame.pack(fill=tk.X)
        
        ttk.Button(pool_btn_frame, text="添加掉落池", command=self.add_loot_pool).pack(side=tk.LEFT, padx=2)
        ttk.Button(pool_btn_frame, text="删除掉落池", command=self.delete_loot_pool).pack(side=tk.LEFT, padx=2)
        
        # 掉落项框架
        entry_frame = ttk.LabelFrame(scrollable_frame, text="掉落项配置", padding="10")
        entry_frame.grid(row=4, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # 物品选择
        ttk.Label(entry_frame, text="物品:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.loot_item = ttk.Entry(entry_frame, width=30)
        self.loot_item.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        
        # 权重
        ttk.Label(entry_frame, text="权重:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.loot_weight = ttk.Spinbox(entry_frame, from_=1, to=100, width=10)
        self.loot_weight.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        self.loot_weight.insert(0, "1")
        
        # 数量范围
        ttk.Label(entry_frame, text="最小数量:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.loot_min_count = ttk.Spinbox(entry_frame, from_=1, to=64, width=10)
        self.loot_min_count.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        self.loot_min_count.insert(0, "1")
        
        ttk.Label(entry_frame, text="最大数量:").grid(row=3, column=0, pady=5, padx=5, sticky="w")
        self.loot_max_count = ttk.Spinbox(entry_frame, from_=1, to=64, width=10)
        self.loot_max_count.grid(row=3, column=1, pady=5, padx=5, sticky="w")
        self.loot_max_count.insert(0, "1")
        
        # 条件
        ttk.Label(entry_frame, text="条件:").grid(row=4, column=0, pady=5, padx=5, sticky="w")
        self.loot_condition = ttk.Combobox(entry_frame, 
                                          values=["random_chance", "killed_by_player", "on_fire"], 
                                          width=20)
        self.loot_condition.grid(row=4, column=1, pady=5, padx=5, sticky="w")
        
        # 添加掉落项按钮
        ttk.Button(entry_frame, text="添加到当前掉落池", command=self.add_loot_entry).grid(row=5, column=0, columnspan=2, pady=10)
        
        # 当前掉落池的掉落项列表
        current_pool_frame = ttk.LabelFrame(scrollable_frame, text="当前掉落池的掉落项", padding="10")
        current_pool_frame.grid(row=5, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        self.loot_entries_listbox = tk.Listbox(current_pool_frame, height=6)
        self.loot_entries_listbox.pack(fill=tk.X, pady=5)
        
        # 删除掉落项按钮
        ttk.Button(current_pool_frame, text="删除选中掉落项", 
                  command=self.delete_loot_entry).pack(pady=5)
        
        # 保存路径框架
        path_frame = ttk.LabelFrame(scrollable_frame, text="保存路径", padding="10")
        path_frame.grid(row=6, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        ttk.Label(path_frame, text="文件名:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.loot_filename = ttk.Entry(path_frame, width=40)
        self.loot_filename.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(path_frame, text=".json", foreground="gray").grid(row=0, column=2, pady=5, padx=0, sticky="w")
        
        # 按钮框架
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=7, column=0, columnspan=3, pady=20)
        
        ttk.Button(btn_frame, text="生成JSON", command=self.generate_loot_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="保存到行为包", command=self.save_loot_to_behavior).pack(side=tk.LEFT, padx=5)
        
        # JSON预览框架
        preview_frame = ttk.LabelFrame(scrollable_frame, text="JSON预览", padding="10")
        preview_frame.grid(row=8, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        self.loot_json_preview = tk.Text(preview_frame, height=15, width=80)
        self.loot_json_preview.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        preview_scrollbar = ttk.Scrollbar(self.loot_json_preview, orient=tk.VERTICAL, command=self.loot_json_preview.yview)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.loot_json_preview.config(yscrollcommand=preview_scrollbar.set)
    
    # ==================== 物品分页配置 ====================
    def create_item_tab_config(self, parent):
        """创建物品分页配置界面"""
        # 创建滚动框架
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
        
        # 标题
        title_label = ttk.Label(scrollable_frame, text="物品分页配置 (行为包)", 
                               font=("微软雅黑", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="w")
        
        # 说明
        desc_label = ttk.Label(scrollable_frame, 
                              text="物品分页用于在创造模式物品栏中分类显示物品\n"
                                   "每个分页可以包含多个物品组，组内可以包含多个物品",
                              justify=tk.LEFT)
        desc_label.grid(row=1, column=0, columnspan=2, pady=5, padx=10, sticky="w")
        
        # 分页列表框架
        list_frame = ttk.LabelFrame(scrollable_frame, text="分页列表", padding="10")
        list_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        
        # 分页列表
        self.tab_listbox = tk.Listbox(list_frame, height=6)
        self.tab_listbox.pack(fill=tk.X, pady=5)
        
        # 示例数据
        sample_tabs = ["装备", "工具", "建筑材料", "食物", "红石", "自然"]
        for tab in sample_tabs:
            self.tab_listbox.insert(tk.END, tab)
        
        # 分页操作按钮
        tab_btn_frame = ttk.Frame(list_frame)
        tab_btn_frame.pack(fill=tk.X)
        
        ttk.Button(tab_btn_frame, text="添加分页", command=self.add_item_tab).pack(side=tk.LEFT, padx=2)
        ttk.Button(tab_btn_frame, text="删除分页", command=self.delete_item_tab).pack(side=tk.LEFT, padx=2)
        
        # 当前分页的组列表
        group_frame = ttk.LabelFrame(scrollable_frame, text="当前分页的组", padding="10")
        group_frame.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        
        # 组列表
        self.group_listbox = tk.Listbox(group_frame, height=4)
        self.group_listbox.pack(fill=tk.X, pady=5)
        
        # 组操作按钮
        group_btn_frame = ttk.Frame(group_frame)
        group_btn_frame.pack(fill=tk.X)
        
        ttk.Button(group_btn_frame, text="添加组", command=self.add_item_group).pack(side=tk.LEFT, padx=2)
        ttk.Button(group_btn_frame, text="删除组", command=self.delete_item_group).pack(side=tk.LEFT, padx=2)
        
        # 按钮框架
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="生成JSON", command=self.generate_item_tab_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="保存到行为包", command=self.save_item_tab_to_behavior).pack(side=tk.LEFT, padx=5)
        
        # 生成的JSON预览
        preview_frame = ttk.LabelFrame(scrollable_frame, text="JSON预览", padding="10")
        preview_frame.grid(row=5, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        
        self.tab_json_preview = tk.Text(preview_frame, height=15, width=80)
        self.tab_json_preview.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        preview_scrollbar = ttk.Scrollbar(self.tab_json_preview, orient=tk.VERTICAL, command=self.tab_json_preview.yview)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tab_json_preview.config(yscrollcommand=preview_scrollbar.set)
    
    # ==================== 物品纹理配置 ====================
    def create_item_texture_config(self, parent):
        """创建物品纹理配置界面"""
        # 创建框架
        main_frame = ttk.Frame(parent, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="物品纹理配置 (资源包)", 
                               font=("微软雅黑", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 说明
        desc_label = ttk.Label(main_frame, 
                              text="在资源包中配置物品的纹理、模型和本地化名称\n"
                                   "需要与行为包中的物品标识符对应",
                              justify=tk.LEFT)
        desc_label.pack(pady=(0, 20))
        
        # 创建两个主要部分
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=10)
        
        # 左侧 - 纹理映射
        texture_frame = ttk.LabelFrame(top_frame, text="纹理映射", padding="10")
        texture_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(texture_frame, text="物品标识符:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.texture_item_id = ttk.Entry(texture_frame, width=30)
        self.texture_item_id.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        
        ttk.Label(texture_frame, text="纹理路径:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.texture_path = ttk.Entry(texture_frame, width=30)
        self.texture_path.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        ttk.Label(texture_frame, text="例如: textures/items/example", foreground="gray").grid(row=1, column=2, pady=5, padx=5, sticky="w")
        
        ttk.Button(texture_frame, text="添加映射", command=self.add_texture_mapping).grid(row=2, column=0, columnspan=2, pady=10)
        
        # 右侧 - 本地化
        lang_frame = ttk.LabelFrame(top_frame, text="本地化名称", padding="10")
        lang_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(lang_frame, text="物品标识符:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.lang_item_id = ttk.Entry(lang_frame, width=30)
        self.lang_item_id.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        
        ttk.Label(lang_frame, text="英文名称:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.en_name = ttk.Entry(lang_frame, width=30)
        self.en_name.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        
        ttk.Label(lang_frame, text="中文名称:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.zh_name = ttk.Entry(lang_frame, width=30)
        self.zh_name.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        
        ttk.Button(lang_frame, text="添加到语言文件", command=self.add_to_lang).grid(row=3, column=0, columnspan=2, pady=10)
        
        # 底部 - 纹理列表
        list_frame = ttk.LabelFrame(main_frame, text="现有纹理映射", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建表格
        columns = ("物品标识符", "纹理路径", "状态")
        self.texture_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.texture_tree.heading(col, text=col)
            self.texture_tree.column(col, width=200)
        
        self.texture_tree.pack(fill=tk.BOTH, expand=True)
        
        # 滚动条
        tree_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.texture_tree.yview)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.texture_tree.config(yscrollcommand=tree_scrollbar.set)
        
        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="生成纹理定义文件", command=self.generate_texture_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="保存所有更改", command=self.save_texture_changes).pack(side=tk.LEFT, padx=5)
    
    # ==================== 辅助方法 ====================
    def toggle_durability(self):
        """切换耐久度组件状态"""
        state = "normal" if self.has_durability.get() else "disabled"
        self.max_durability.config(state=state)
    
    def toggle_food(self):
        """切换食物组件状态"""
        state = "normal" if self.is_food.get() else "disabled"
        self.nutrition.config(state=state)
        self.saturation.config(state=state)
    
    def toggle_weapon(self):
        """切换武器组件状态"""
        state = "normal" if self.is_weapon.get() else "disabled"
        self.damage.config(state=state)
    
    # ==================== 物品相关方法 ====================
    def generate_item_json(self):
        """生成物品JSON配置"""
        # 验证必填字段
        identifier = self.item_identifier.get().strip()
        display_name = self.item_display_name.get().strip()
        
        if not identifier or not display_name:
            messagebox.showwarning("警告", "请至少填写物品标识符和显示名称")
            return
        
        # 构建物品配置
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
        
        # 添加显示名称组件
        name_key = f"item.{identifier.replace(':', '.')}.name"
        item_config["minecraft:item"]["components"]["minecraft:display_name"] = {
            "value": name_key
        }
        
        # 添加图标组件
        icon_key = identifier.replace(':', ':')
        item_config["minecraft:item"]["components"]["minecraft:icon"] = {
            "texture": icon_key
        }
        
        # 添加最大堆叠数量
        stack_size = self.max_stack_size.get()
        if stack_size:
            item_config["minecraft:item"]["components"]["minecraft:max_stack_size"] = int(stack_size)
        
        # 添加手持组件
        if self.hand_equipped.get():
            item_config["minecraft:item"]["components"]["minecraft:hand_equipped"] = True
        
        # 添加耐久度组件
        if self.has_durability.get():
            max_dura = self.max_durability.get()
            if max_dura:
                item_config["minecraft:item"]["components"]["minecraft:durability"] = {
                    "max_durability": int(max_dura)
                }
        
        # 添加食物组件
        if self.is_food.get():
            nutrition = self.nutrition.get()
            saturation = self.saturation.get()
            if nutrition and saturation:
                item_config["minecraft:item"]["components"]["minecraft:food"] = {
                    "nutrition": int(nutrition),
                    "saturation_modifier": float(saturation) / float(nutrition) if float(nutrition) > 0 else 0.5
                }
        
        # 添加武器组件
        if self.is_weapon.get():
            damage = self.damage.get()
            if damage:
                item_config["minecraft:item"]["components"]["minecraft:damage"] = int(damage)
        
        # 转换为JSON字符串
        json_str = json.dumps(item_config, indent=2, ensure_ascii=False)
        
        # 显示在预览框中
        self.item_json_preview.delete(1.0, tk.END)
        self.item_json_preview.insert(1.0, json_str)
        
        # 自动生成文件名
        if not self.item_filename.get().strip():
            name_parts = identifier.split(":")
            if len(name_parts) > 1:
                suggested_name = name_parts[1]
            else:
                suggested_name = identifier.replace(":", "_")
            
            self.item_filename.delete(0, tk.END)
            self.item_filename.insert(0, suggested_name)
    
    def save_item_to_behavior(self):
        """保存物品JSON到行为包"""
        json_content = self.item_json_preview.get(1.0, tk.END).strip()
        if not json_content:
            messagebox.showwarning("警告", "请先生成JSON")
            return
        
        # 验证JSON
        try:
            json_obj = json.loads(json_content)
        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"JSON格式错误: {str(e)}")
            return
        
        # 获取文件名
        filename = self.item_filename.get().strip()
        if not filename:
            messagebox.showwarning("警告", "请输入文件名")
            return
        
        if not filename.endswith(".json"):
            filename += ".json"
        
        # 保存到行为包的items文件夹
        items_path = self.bp_path / "items"
        items_path.mkdir(exist_ok=True)
        
        file_path = items_path / filename
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_content)
            
            # 同时更新语言文件
            identifier = self.item_identifier.get().strip()
            display_name = self.item_display_name.get().strip()
            
            if identifier and display_name:
                self.update_language_files(identifier, display_name)
            
            messagebox.showinfo("成功", f"物品配置已保存到行为包:\n{file_path}\n\n"
                                      "提示: 别忘了在资源包中配置对应的纹理和本地化名称")
            
            # 刷新文件树
            if 'bp' in self.file_trees:
                self.file_trees['bp'].delete(*self.file_trees['bp'].get_children())
                self.load_file_tree_node(self.file_trees['bp'], "", self.bp_path, self.bp_path.name)
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    # ==================== 方块相关方法 ====================
    def generate_block_json(self):
        """生成方块JSON配置"""
        # 验证必填字段
        identifier = self.block_identifier.get().strip()
        display_name = self.block_display_name.get().strip()
        
        if not identifier or not display_name:
            messagebox.showwarning("警告", "请至少填写方块标识符和显示名称")
            return
        
        # 构建方块配置
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
        
        # 添加单位立方体几何体
        if self.block_unit_cube.get():
            block_config["minecraft:block"]["components"]["minecraft:geometry"] = "minecraft:geometry.full_block"
        elif self.block_geometry.get().strip():
            block_config["minecraft:block"]["components"]["minecraft:geometry"] = self.block_geometry.get().strip()
        
        # 添加透光属性
        if self.block_transparent.get():
            block_config["minecraft:block"]["components"]["minecraft:breathability"] = "air"
        
        # 添加可替代属性
        if self.block_replaceable.get():
            block_config["minecraft:block"]["components"]["minecraft:replaceable"] = True
        
        # 添加掉落物
        if self.block_loot_item.get().strip():
            block_config["minecraft:block"]["components"]["minecraft:loot"] = self.block_loot_item.get().strip()
        
        # 转换为JSON字符串
        json_str = json.dumps(block_config, indent=2, ensure_ascii=False)
        
        # 显示在预览框中
        self.block_json_preview.delete(1.0, tk.END)
        self.block_json_preview.insert(1.0, json_str)
        
        # 自动生成文件名
        if not self.block_filename.get().strip():
            name_parts = identifier.split(":")
            if len(name_parts) > 1:
                suggested_name = name_parts[1]
            else:
                suggested_name = identifier.replace(":", "_")
            
            self.block_filename.delete(0, tk.END)
            self.block_filename.insert(0, suggested_name)
    
    def save_block_to_behavior(self):
        """保存方块JSON到行为包"""
        json_content = self.block_json_preview.get(1.0, tk.END).strip()
        if not json_content:
            messagebox.showwarning("警告", "请先生成JSON")
            return
        
        # 验证JSON
        try:
            json_obj = json.loads(json_content)
        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"JSON格式错误: {str(e)}")
            return
        
        # 获取文件名
        filename = self.block_filename.get().strip()
        if not filename:
            messagebox.showwarning("警告", "请输入文件名")
            return
        
        if not filename.endswith(".json"):
            filename += ".json"
        
        # 保存到行为包的blocks文件夹
        blocks_path = self.bp_path / "blocks"
        blocks_path.mkdir(exist_ok=True)
        
        file_path = blocks_path / filename
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_content)
            
            # 更新语言文件
            identifier = self.block_identifier.get().strip()
            display_name = self.block_display_name.get().strip()
            
            if identifier and display_name:
                name_key = f"tile.{identifier.replace(':', '.')}.name"
                self.update_language_files_custom(name_key, display_name)
            
            messagebox.showinfo("成功", f"方块配置已保存到行为包:\n{file_path}")
            
            # 刷新文件树
            if 'bp' in self.file_trees:
                self.file_trees['bp'].delete(*self.file_trees['bp'].get_children())
                self.load_file_tree_node(self.file_trees['bp'], "", self.bp_path, self.bp_path.name)
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    # ==================== 实体相关方法 ====================
    def generate_entity_json(self):
        """生成实体JSON配置"""
        # 验证必填字段
        identifier = self.entity_identifier.get().strip()
        display_name = self.entity_display_name.get().strip()
        
        if not identifier or not display_name:
            messagebox.showwarning("警告", "请至少填写实体标识符和显示名称")
            return
        
        # 构建实体配置
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
        
        # 添加行为
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
        
        # 添加装备
        if self.entity_equipment.get() and self.entity_equipment_table.get().strip():
            entity_config["minecraft:entity"]["components"]["minecraft:equipment"] = {
                "table": self.entity_equipment_table.get().strip()
            }
        
        # 添加掉落表
        if self.entity_loot_table.get().strip():
            entity_config["minecraft:entity"]["components"]["minecraft:loot"] = {
                "table": self.entity_loot_table.get().strip()
            }
        
        # 添加繁殖组件
        if self.entity_baby.get():
            entity_config["minecraft:entity"]["components"]["minecraft:breedable"] = {
                "require_tame": False,
                "breeds_with": [],
                "breed_items": []
            }
        
        # 转换为JSON字符串
        json_str = json.dumps(entity_config, indent=2, ensure_ascii=False)
        
        # 显示在预览框中
        self.entity_json_preview.delete(1.0, tk.END)
        self.entity_json_preview.insert(1.0, json_str)
        
        # 自动生成文件名
        if not self.entity_filename.get().strip():
            name_parts = identifier.split(":")
            if len(name_parts) > 1:
                suggested_name = name_parts[1]
            else:
                suggested_name = identifier.replace(":", "_")
            
            self.entity_filename.delete(0, tk.END)
            self.entity_filename.insert(0, suggested_name)
    
    def save_entity_to_behavior(self):
        """保存实体JSON到行为包"""
        json_content = self.entity_json_preview.get(1.0, tk.END).strip()
        if not json_content:
            messagebox.showwarning("警告", "请先生成JSON")
            return
        
        # 验证JSON
        try:
            json_obj = json.loads(json_content)
        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"JSON格式错误: {str(e)}")
            return
        
        # 获取文件名
        filename = self.entity_filename.get().strip()
        if not filename:
            messagebox.showwarning("警告", "请输入文件名")
            return
        
        if not filename.endswith(".json"):
            filename += ".json"
        
        # 保存到行为包的entities文件夹
        entities_path = self.bp_path / "entities"
        entities_path.mkdir(exist_ok=True)
        
        file_path = entities_path / filename
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_content)
            
            # 更新语言文件
            identifier = self.entity_identifier.get().strip()
            display_name = self.entity_display_name.get().strip()
            
            if identifier and display_name:
                name_key = f"entity.{identifier.replace(':', '.')}.name"
                self.update_language_files_custom(name_key, display_name)
            
            # 如果有生成规则，保存生成规则
            if self.entity_spawnable.get() and self.entity_biome.get():
                self.save_spawn_rules(identifier)
            
            messagebox.showinfo("成功", f"实体配置已保存到行为包:\n{file_path}")
            
            # 刷新文件树
            if 'bp' in self.file_trees:
                self.file_trees['bp'].delete(*self.file_trees['bp'].get_children())
                self.load_file_tree_node(self.file_trees['bp'], "", self.bp_path, self.bp_path.name)
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def save_spawn_rules(self, entity_id):
        """保存生成规则"""
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
        
        # 保存到spawn_rules文件夹
        spawn_path = self.bp_path / "spawn_rules"
        spawn_path.mkdir(exist_ok=True)
        
        name_parts = entity_id.split(":")
        filename = f"{name_parts[1] if len(name_parts) > 1 else entity_id}.json"
        
        with open(spawn_path / filename, "w", encoding="utf-8") as f:
            json.dump(spawn_config, f, indent=2)
    
    # ==================== 配方相关方法 ====================
    def update_recipe_ui(self):
        """更新配方UI"""
        recipe_type = self.recipe_type.get()
        
        # 隐藏所有特定框架
        if hasattr(self, 'furnace_frame'):
            self.furnace_frame.grid_remove()
        if hasattr(self, 'brewing_frame'):
            self.brewing_frame.grid_remove()
        
        if recipe_type == "furnace":
            self.show_furnace_ui()
        elif recipe_type == "brewing":
            self.show_brewing_ui()
    
    def show_furnace_ui(self):
        """显示熔炉配方UI"""
        if not hasattr(self, 'furnace_frame'):
            return
            
        self.furnace_frame.grid(row=5, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # 清空现有内容
        for widget in self.furnace_frame.winfo_children():
            widget.destroy()
        
        # 熔炉配方特定控件
        ttk.Label(self.furnace_frame, text="输入物品:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.furnace_input = ttk.Entry(self.furnace_frame, width=30)
        self.furnace_input.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        
        ttk.Label(self.furnace_frame, text="经验值:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.furnace_experience = ttk.Spinbox(self.furnace_frame, from_=0, to=10, increment=0.1, width=10)
        self.furnace_experience.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        self.furnace_experience.insert(0, "0.1")
        
        ttk.Label(self.furnace_frame, text="烧炼时间:").grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.furnace_time = ttk.Spinbox(self.furnace_frame, from_=1, to=1000, width=10)
        self.furnace_time.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        self.furnace_time.insert(0, "200")
    
    def show_brewing_ui(self):
        """显示酿造配方UI"""
        if not hasattr(self, 'brewing_frame'):
            return
            
        self.brewing_frame.grid(row=5, column=0, columnspan=3, pady=10, padx=10, sticky="ew")
        
        # 清空现有内容
        for widget in self.brewing_frame.winfo_children():
            widget.destroy()
        
        # 酿造配方特定控件
        ttk.Label(self.brewing_frame, text="输入物品:").grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.brewing_input = ttk.Entry(self.brewing_frame, width=30)
        self.brewing_input.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        
        ttk.Label(self.brewing_frame, text="试剂:").grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.brewing_reagent = ttk.Entry(self.brewing_frame, width=30)
        self.brewing_reagent.grid(row=1, column=1, pady=5, padx=5, sticky="w")
    
    def generate_recipe_json(self):
        """生成配方JSON配置"""
        recipe_type = self.recipe_type.get()
        output = self.recipe_output.get().strip()
        output_count = self.recipe_output_count.get() or "1"
        
        if not output:
            messagebox.showwarning("警告", "请输入输出物品")
            return
        
        # 构建配方配置
        if recipe_type == "crafting_shaped":
            # 有序合成
            pattern = []
            keys = {}
            
            # 读取3x3网格
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
                messagebox.showwarning("警告", "请至少填入一个物品")
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
            # 无序合成
            ingredients = []
            for i in range(3):
                for j in range(3):
                    item = self.recipe_grid[i][j].get().strip()
                    if item:
                        ingredients.append({"item": item})
            
            if not ingredients:
                messagebox.showwarning("警告", "请至少填入一个物品")
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
            # 熔炉配方
            if not hasattr(self, 'furnace_input') or not self.furnace_input.get().strip():
                messagebox.showwarning("警告", "请输入输入物品")
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
            # 酿造配方
            if not hasattr(self, 'brewing_input') or not self.brewing_input.get().strip():
                messagebox.showwarning("警告", "请输入输入物品")
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
            messagebox.showwarning("警告", "请选择有效的配方类型")
            return
        
        # 转换为JSON字符串
        json_str = json.dumps(recipe_config, indent=2, ensure_ascii=False)
        
        # 显示在预览框中
        self.recipe_json_preview.delete(1.0, tk.END)
        self.recipe_json_preview.insert(1.0, json_str)
        
        # 自动生成文件名
        if not self.recipe_filename.get().strip():
            suggested_name = f"{output.split(':')[-1]}_{recipe_type}"
            self.recipe_filename.delete(0, tk.END)
            self.recipe_filename.insert(0, suggested_name)
    
    def save_recipe_to_behavior(self):
        """保存配方JSON到行为包"""
        json_content = self.recipe_json_preview.get(1.0, tk.END).strip()
        if not json_content:
            messagebox.showwarning("警告", "请先生成JSON")
            return
        
        # 验证JSON
        try:
            json_obj = json.loads(json_content)
        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"JSON格式错误: {str(e)}")
            return
        
        # 获取文件名
        filename = self.recipe_filename.get().strip()
        if not filename:
            messagebox.showwarning("警告", "请输入文件名")
            return
        
        if not filename.endswith(".json"):
            filename += ".json"
        
        # 保存到行为包的recipes文件夹
        recipes_path = self.bp_path / "recipes"
        recipes_path.mkdir(exist_ok=True)
        
        file_path = recipes_path / filename
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_content)
            
            messagebox.showinfo("成功", f"配方配置已保存到行为包:\n{file_path}")
            
            # 刷新文件树
            if 'bp' in self.file_trees:
                self.file_trees['bp'].delete(*self.file_trees['bp'].get_children())
                self.load_file_tree_node(self.file_trees['bp'], "", self.bp_path, self.bp_path.name)
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    # ==================== 物品分页相关方法 ====================
    def add_item_tab(self):
        """添加物品分页"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加物品分页")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="分页名称:").pack(anchor=tk.W, pady=(0, 5))
        name_entry = ttk.Entry(frame)
        name_entry.pack(fill=tk.X, pady=(0, 10))
        name_entry.focus()
        
        def add():
            name = name_entry.get().strip()
            if name:
                self.tab_listbox.insert(tk.END, name)
                dialog.destroy()
            else:
                messagebox.showerror("错误", "请输入分页名称")
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="添加", command=add).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def delete_item_tab(self):
        """删除物品分页"""
        selection = self.tab_listbox.curselection()
        if selection:
            self.tab_listbox.delete(selection[0])
    
    def add_item_group(self):
        """添加物品组"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加物品组")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="组名称:").pack(anchor=tk.W, pady=(0, 5))
        name_entry = ttk.Entry(frame)
        name_entry.pack(fill=tk.X, pady=(0, 10))
        name_entry.focus()
        
        def add():
            name = name_entry.get().strip()
            if name:
                self.group_listbox.insert(tk.END, name)
                dialog.destroy()
            else:
                messagebox.showerror("错误", "请输入组名称")
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="添加", command=add).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def delete_item_group(self):
        """删除物品组"""
        selection = self.group_listbox.curselection()
        if selection:
            self.group_listbox.delete(selection[0])
    
    def generate_item_tab_json(self):
        """生成物品分页的JSON配置"""
        # 创建示例JSON
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
                        "value": f"{self.project_path.name}物品组"
                    },
                    "minecraft:creative_tabs": []
                }
            }
        }
        
        # 添加分页和组信息
        tabs = []
        for i in range(self.tab_listbox.size()):
            tab_name = self.tab_listbox.get(i)
            tab_data = {
                "name": tab_name,
                "groups": []
            }
            
            # 如果当前选中了这个分页，添加其组
            selection = self.tab_listbox.curselection()
            if selection and selection[0] == i:
                groups = []
                for j in range(self.group_listbox.size()):
                    groups.append(self.group_listbox.get(j))
                tab_data["groups"] = groups
            
            tabs.append(tab_data)
        
        if tabs:
            item_tab_config["minecraft:item_group"]["components"]["minecraft:creative_tabs"] = tabs
        
        # 转换为JSON字符串
        json_str = json.dumps(item_tab_config, indent=2, ensure_ascii=False)
        
        # 显示在预览框中
        self.tab_json_preview.delete(1.0, tk.END)
        self.tab_json_preview.insert(1.0, json_str)
    
    def save_item_tab_to_behavior(self):
        """保存物品分页配置到行为包"""
        json_content = self.tab_json_preview.get(1.0, tk.END).strip()
        if not json_content:
            messagebox.showwarning("警告", "请先生成JSON")
            return
        
        # 验证JSON
        try:
            json.loads(json_content)
        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"JSON格式错误: {str(e)}")
            return
        
        # 保存到行为包的items文件夹
        items_path = self.bp_path / "items"
        items_path.mkdir(exist_ok=True)
        
        file_path = items_path / "item_tab_config.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_content)
            
            messagebox.showinfo("成功", f"物品分页配置已保存到行为包:\n{file_path}")
            
            # 刷新文件树
            if 'bp' in self.file_trees:
                self.file_trees['bp'].delete(*self.file_trees['bp'].get_children())
                self.load_file_tree_node(self.file_trees['bp'], "", self.bp_path, self.bp_path.name)
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    # ==================== 掉落表相关方法 ====================
    def add_loot_pool(self):
        """添加掉落池"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加掉落池")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="掉落池名称:").pack(anchor=tk.W, pady=(0, 5))
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
                messagebox.showerror("错误", "请输入掉落池名称")
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="添加", command=add).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def delete_loot_pool(self):
        """删除掉落池"""
        selection = self.loot_pool_listbox.curselection()
        if selection:
            index = selection[0]
            self.loot_pool_listbox.delete(index)
            if index < len(self.loot_pools):
                del self.loot_pools[index]
    
    def add_loot_entry(self):
        """添加掉落项到当前掉落池"""
        selection = self.loot_pool_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个掉落池")
            return
        
        item = self.loot_item.get().strip()
        if not item:
            messagebox.showwarning("警告", "请输入物品ID")
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
        
        # 添加到内存
        if pool_index < len(self.loot_pools):
            self.loot_pools[pool_index]["entries"].append(entry)
        
        # 显示在列表框中
        display_text = f"{item} x{entry['min_count']}-{entry['max_count']} (权重:{entry['weight']})"
        self.loot_entries_listbox.insert(tk.END, display_text)
        
        # 清空输入
        self.loot_item.delete(0, tk.END)
        self.loot_weight.delete(0, tk.END)
        self.loot_weight.insert(0, "1")
        self.loot_min_count.delete(0, tk.END)
        self.loot_min_count.insert(0, "1")
        self.loot_max_count.delete(0, tk.END)
        self.loot_max_count.insert(0, "1")
    
    def delete_loot_entry(self):
        """删除选中的掉落项"""
        pool_selection = self.loot_pool_listbox.curselection()
        entry_selection = self.loot_entries_listbox.curselection()
        
        if pool_selection and entry_selection:
            pool_index = pool_selection[0]
            entry_index = entry_selection[0]
            
            if pool_index < len(self.loot_pools) and entry_index < len(self.loot_pools[pool_index]["entries"]):
                del self.loot_pools[pool_index]["entries"][entry_index]
                self.loot_entries_listbox.delete(entry_index)
    
    def generate_loot_json(self):
        """生成掉落表JSON配置"""
        if not self.loot_pools:
            messagebox.showwarning("警告", "请至少添加一个掉落池")
            return
        
        # 构建掉落表配置
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
                    
                    # 添加数量范围
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
                    
                    # 添加条件
                    if entry.get("condition"):
                        entry_config["conditions"] = [
                            {
                                "condition": entry["condition"]
                            }
                        ]
                    
                    pool_config["entries"].append(entry_config)
                
                loot_config["pools"].append(pool_config)
        
        # 转换为JSON字符串
        json_str = json.dumps(loot_config, indent=2, ensure_ascii=False)
        
        # 显示在预览框中
        self.loot_json_preview.delete(1.0, tk.END)
        self.loot_json_preview.insert(1.0, json_str)
        
        # 自动生成文件名
        if not self.loot_filename.get().strip():
            loot_type = self.loot_type.get()
            suggested_name = f"{loot_type}_loot_table"
            self.loot_filename.delete(0, tk.END)
            self.loot_filename.insert(0, suggested_name)
    
    def save_loot_to_behavior(self):
        """保存掉落表JSON到行为包"""
        json_content = self.loot_json_preview.get(1.0, tk.END).strip()
        if not json_content:
            messagebox.showwarning("警告", "请先生成JSON")
            return
        
        # 验证JSON
        try:
            json_obj = json.loads(json_content)
        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"JSON格式错误: {str(e)}")
            return
        
        # 获取文件名
        filename = self.loot_filename.get().strip()
        if not filename:
            messagebox.showwarning("警告", "请输入文件名")
            return
        
        if not filename.endswith(".json"):
            filename += ".json"
        
        # 根据类型选择子文件夹
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
            
            messagebox.showinfo("成功", f"掉落表已保存到行为包:\n{file_path}")
            
            # 刷新文件树
            if 'bp' in self.file_trees:
                self.file_trees['bp'].delete(*self.file_trees['bp'].get_children())
                self.load_file_tree_node(self.file_trees['bp'], "", self.bp_path, self.bp_path.name)
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    # ==================== 纹理相关方法 ====================
    def add_texture_mapping(self):
        """添加纹理映射"""
        item_id = self.texture_item_id.get().strip()
        texture = self.texture_path.get().strip()
        
        if not item_id or not texture:
            messagebox.showwarning("警告", "请填写物品标识符和纹理路径")
            return
        
        # 添加到树形视图
        self.texture_tree.insert("", "end", values=(item_id, texture, "待保存"))
        
        # 清空输入框
        self.texture_item_id.delete(0, tk.END)
        self.texture_path.delete(0, tk.END)
    
    def add_to_lang(self):
        """添加到语言文件"""
        item_id = self.lang_item_id.get().strip()
        en_name = self.en_name.get().strip()
        zh_name = self.zh_name.get().strip()
        
        if not item_id or not en_name:
            messagebox.showwarning("警告", "请至少填写物品标识符和英文名称")
            return
        
        # 构建本地化键
        lang_key = f"item.{item_id.replace(':', '.')}.name"
        
        try:
            # 更新英文语言文件
            en_lang_path = self.rp_path / "texts" / "en_US.lang"
            if en_lang_path.exists():
                with open(en_lang_path, "a", encoding="utf-8") as f:
                    f.write(f"\n{lang_key}={en_name}")
            
            # 更新中文语言文件
            if zh_name:
                zh_lang_path = self.rp_path / "texts" / "zh_CN.lang"
                if zh_lang_path.exists():
                    with open(zh_lang_path, "a", encoding="utf-8") as f:
                        f.write(f"\n{lang_key}={zh_name}")
            
            messagebox.showinfo("成功", "已添加到语言文件")
            
            # 清空输入框
            self.lang_item_id.delete(0, tk.END)
            self.en_name.delete(0, tk.END)
            self.zh_name.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("错误", f"添加失败: {str(e)}")
    
    def generate_texture_json(self):
        """生成纹理定义文件"""
        # 获取所有纹理映射
        textures = {}
        for item in self.texture_tree.get_children():
            values = self.texture_tree.item(item, "values")
            if values:
                item_id = values[0]
                texture_path = values[1]
                # 使用物品ID作为纹理键
                texture_key = item_id.replace(':', ':')
                textures[texture_key] = texture_path
        
        if not textures:
            messagebox.showwarning("警告", "没有纹理映射需要保存")
            return
        
        # 构建纹理定义
        texture_config = {
            "texture_data": {}
        }
        
        for key, path in textures.items():
            texture_config["texture_data"][key] = {
                "textures": path
            }
        
        # 保存文件
        textures_path = self.rp_path / "textures" / "item_texture.json"
        try:
            with open(textures_path, "w", encoding="utf-8") as f:
                json.dump(texture_config, f, indent=2)
            
            messagebox.showinfo("成功", f"纹理定义已保存到:\n{textures_path}")
            
            # 更新状态
            for item in self.texture_tree.get_children():
                self.texture_tree.item(item, values=(self.texture_tree.item(item, "values")[0],
                                                     self.texture_tree.item(item, "values")[1],
                                                     "已保存"))
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def save_texture_changes(self):
        """保存所有纹理更改"""
        self.generate_texture_json()
    
    # ==================== 辅助方法 ====================
    def update_language_files(self, identifier, display_name):
        """更新语言文件（物品）"""
        lang_key = f"item.{identifier.replace(':', '.')}.name"
        self.update_language_files_custom(lang_key, display_name)
    
    def update_language_files_custom(self, lang_key, display_name):
        """更新语言文件（自定义键）"""
        try:
            # 更新英文语言文件
            en_lang_path = self.rp_path / "texts" / "en_US.lang"
            if en_lang_path.exists():
                with open(en_lang_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                if lang_key not in content:
                    with open(en_lang_path, "a", encoding="utf-8") as f:
                        f.write(f"\n{lang_key}={display_name}")
            
            # 更新中文语言文件
            zh_lang_path = self.rp_path / "texts" / "zh_CN.lang"
            if zh_lang_path.exists():
                with open(zh_lang_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                if lang_key not in content:
                    with open(zh_lang_path, "a", encoding="utf-8") as f:
                        f.write(f"\n{lang_key}={display_name}")
                        
        except Exception as e:
            print(f"更新语言文件失败: {e}")
    
    def validate_project(self):
        """验证项目结构"""
        issues = []
        
        # 检查必要文件夹
        if not self.bp_path.exists():
            issues.append("❌ 行为包文件夹不存在")
        else:
            # 检查manifest.json
            if not (self.bp_path / "manifest.json").exists():
                issues.append("❌ 行为包缺少manifest.json")
            
            # 检查必要子文件夹
            for folder in ["items", "entities", "blocks", "recipes", "loot_tables"]:
                if not (self.bp_path / folder).exists():
                    issues.append(f"⚠️ 行为包缺少 {folder} 文件夹")
        
        if not self.rp_path.exists():
            issues.append("❌ 资源包文件夹不存在")
        else:
            # 检查manifest.json
            if not (self.rp_path / "manifest.json").exists():
                issues.append("❌ 资源包缺少manifest.json")
            
            # 检查texts文件夹
            if not (self.rp_path / "texts").exists():
                issues.append("⚠️ 资源包缺少 texts 文件夹")
        
        if issues:
            result = "项目检查结果:\n\n" + "\n".join(issues)
        else:
            result = "✅ 项目结构完整，没有发现问题"
        
        messagebox.showinfo("项目验证", result)
    
    def regenerate_uuids(self):
        """重新生成UUID"""
        if not messagebox.askyesno("确认", "重新生成UUID会更新manifest.json文件，确定要继续吗？"):
            return
        
        try:
            import uuid
            
            # 生成新UUID
            new_bp_header = str(uuid.uuid4())
            new_bp_module = str(uuid.uuid4())
            new_rp_header = str(uuid.uuid4())
            new_rp_module = str(uuid.uuid4())
            
            # 更新行为包manifest
            bp_manifest_path = self.bp_path / "manifest.json"
            if bp_manifest_path.exists():
                with open(bp_manifest_path, "r", encoding="utf-8") as f:
                    bp_manifest = json.load(f)
                
                bp_manifest["header"]["uuid"] = new_bp_header
                bp_manifest["modules"][0]["uuid"] = new_bp_module
                
                # 更新依赖中的资源包UUID
                if "dependencies" in bp_manifest and len(bp_manifest["dependencies"]) > 0:
                    bp_manifest["dependencies"][0]["uuid"] = new_rp_header
                
                with open(bp_manifest_path, "w", encoding="utf-8") as f:
                    json.dump(bp_manifest, f, indent=2)
            
            # 更新资源包manifest
            rp_manifest_path = self.rp_path / "manifest.json"
            if rp_manifest_path.exists():
                with open(rp_manifest_path, "r", encoding="utf-8") as f:
                    rp_manifest = json.load(f)
                
                rp_manifest["header"]["uuid"] = new_rp_header
                rp_manifest["modules"][0]["uuid"] = new_rp_module
                
                with open(rp_manifest_path, "w", encoding="utf-8") as f:
                    json.dump(rp_manifest, f, indent=2)
            
            # 更新项目配置
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
            
            messagebox.showinfo("成功", "UUID已重新生成并更新")
            
        except Exception as e:
            messagebox.showerror("错误", f"重新生成UUID失败: {str(e)}")
    
    def open_folder(self, path):
        """打开文件夹"""
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            import subprocess
            subprocess.run(["open", path])
        else:  # Linux
            import subprocess
            subprocess.run(["xdg-open", path])
    
    def save_all(self):
        """保存所有配置"""
        # 获取当前选中的选项卡
        current_tab = self.notebook.select()
        if current_tab:
            tab_text = self.notebook.tab(current_tab, "text")
            
            if tab_text == "物品配置 (BP)":
                self.save_item_to_behavior()
            elif tab_text == "方块配置 (BP)":
                self.save_block_to_behavior()
            elif tab_text == "实体配置 (BP)":
                self.save_entity_to_behavior()
            elif tab_text == "配方配置 (BP)":
                self.save_recipe_to_behavior()
            elif tab_text == "掉落表配置 (BP)":
                self.save_loot_to_behavior()
            elif tab_text == "物品分页配置 (BP)":
                self.save_item_tab_to_behavior()
            elif tab_text == "物品纹理 (RP)":
                self.save_texture_changes()
            else:
                # 如果是文件选项卡，尝试保存
                for name, frame in self.open_tabs.items():
                    if frame == self.notebook.nametowidget(current_tab):
                        messagebox.showinfo("提示", "请使用文件菜单保存")
                        break
    
    def save_as(self):
        """另存为"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            # 获取当前预览内容
            current_tab = self.notebook.select()
            if current_tab:
                tab_text = self.notebook.tab(current_tab, "text")
                content = None
                
                if tab_text == "物品配置 (BP)":
                    content = self.item_json_preview.get(1.0, tk.END).strip() if hasattr(self, 'item_json_preview') else None
                elif tab_text == "方块配置 (BP)":
                    content = self.block_json_preview.get(1.0, tk.END).strip() if hasattr(self, 'block_json_preview') else None
                elif tab_text == "实体配置 (BP)":
                    content = self.entity_json_preview.get(1.0, tk.END).strip() if hasattr(self, 'entity_json_preview') else None
                elif tab_text == "配方配置 (BP)":
                    content = self.recipe_json_preview.get(1.0, tk.END).strip() if hasattr(self, 'recipe_json_preview') else None
                elif tab_text == "掉落表配置 (BP)":
                    content = self.loot_json_preview.get(1.0, tk.END).strip() if hasattr(self, 'loot_json_preview') else None
                elif tab_text == "物品分页配置 (BP)":
                    content = self.tab_json_preview.get(1.0, tk.END).strip() if hasattr(self, 'tab_json_preview') else None
                else:
                    messagebox.showinfo("提示", "当前选项卡不支持另存为")
                    return
                
                if content:
                    try:
                        with open(filename, "w", encoding="utf-8") as f:
                            f.write(content)
                        messagebox.showinfo("成功", f"文件已保存到: {filename}")
                    except Exception as e:
                        messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def export_addon(self):
        """导出Addon"""
        from datetime import datetime
        
        # 选择导出位置
        filename = filedialog.asksaveasfilename(
            defaultextension=".mcaddon",
            filetypes=[("Minecraft Addon", "*.mcaddon"), ("All files", "*.*")],
            initialfile=f"{self.project_path.name}_{datetime.now().strftime('%Y%m%d')}.mcaddon"
        )
        
        if not filename:
            return
        
        try:
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # 复制行为包和资源包到临时目录
                if self.bp_path.exists():
                    shutil.copytree(self.bp_path, temp_path / "behavior_pack")
                
                if self.rp_path.exists():
                    shutil.copytree(self.rp_path, temp_path / "resource_pack")
                
                # 创建ZIP文件
                with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # 添加所有文件
                    for file in temp_path.rglob("*"):
                        if file.is_file():
                            arcname = file.relative_to(temp_path)
                            zipf.write(file, arcname)
            
            messagebox.showinfo("成功", f"Addon已导出到:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def open_docs(self):
        """打开官方文档"""
        webbrowser.open("https://learn.microsoft.com/zh-cn/minecraft/creator/")
    
    def show_about(self):
        """显示关于信息"""
        about_text = """Quick IDE
版本: 0.6.0
用于创建和编辑Minecraft基岩版Addons

基于官方文档开发:
https://learn.microsoft.com/zh-cn/minecraft/creator/

项目结构:
- 行为包 (BP): 物品、方块、实体、配方、掉落表、物品分页等
- 资源包 (RP): 纹理、模型、语言文件、音效等

功能:
✅ 物品配置
✅ 方块配置
✅ 实体配置
✅ 配方配置
✅ 掉落表配置
✅ 物品分页配置
⏳ 结构配置 (开发中)
⏳ 生物群系配置 (开发中)
⏳ 维度配置 (开发中)

作者: Quick Team"""
        
        messagebox.showinfo("关于", about_text)


if __name__ == "__main__":
    # 测试代码
    root = tk.Tk()
    root.geometry("1200x700")
    root.title("Quick IDE - 测试模式")
    
    # 创建临时测试项目
    test_path = Path.home() / "Documents" / "Quick" / "projects" / "TestProject"
    test_path.mkdir(parents=True, exist_ok=True)
    
    # 创建行为包和资源包文件夹
    bp_path = test_path / "behavior_pack"
    rp_path = test_path / "resource_pack"
    bp_path.mkdir(exist_ok=True)
    rp_path.mkdir(exist_ok=True)
    
    # 创建必要的子文件夹
    (bp_path / "items").mkdir(exist_ok=True)
    (bp_path / "entities").mkdir(exist_ok=True)
    (bp_path / "blocks").mkdir(exist_ok=True)
    (bp_path / "recipes").mkdir(exist_ok=True)
    (bp_path / "loot_tables").mkdir(exist_ok=True)
    (rp_path / "textures").mkdir(exist_ok=True)
    (rp_path / "texts").mkdir(exist_ok=True)
    
    # 创建基本的manifest.json
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
    
    # 创建项目配置文件
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