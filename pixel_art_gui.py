"""
像素画风格转换器 - 图形界面版本
提供友好的用户界面，方便进行像素画转换、画质增强和 AI 超分
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from PIL import Image


# 项目根目录
BASE_DIR = Path(__file__).resolve().parent

# Real-ESRGAN 可执行文件相对路径（你已解压到项目目录下）
# 这里使用包含 models 文件夹的版本目录
REALESRGAN_EXE = BASE_DIR / "realesrgan-ncnn-vulkan-20220424-windows" / "realesrgan-ncnn-vulkan.exe"


# 导入转换函数
try:
    from pixel_art_converter import convert_to_pixel_art, enhance_image_quality
except ImportError:
    messagebox.showerror("错误", "无法导入 pixel_art_converter 模块")
    sys.exit(1)


class PixelArtConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("图像处理工具")
        self.root.geometry("600x750")
        self.root.resizable(False, False)
        
        # 像素画转换变量
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.pixel_size = tk.IntVar(value=64)
        self.color_reduction = tk.IntVar(value=128)
        self.scale_factor = tk.StringVar(value="")
        self.enhance_mode = tk.BooleanVar(value=True)
        self.interpolation = tk.StringVar(value="bicubic")
        self.preserve_aspect = tk.BooleanVar(value=True)
        
        # 画质增强变量
        self.enhance_input_path = tk.StringVar()
        self.enhance_output_path = tk.StringVar()
        self.sharpness = tk.DoubleVar(value=1.5)
        self.contrast = tk.DoubleVar(value=1.1)
        self.saturation = tk.DoubleVar(value=1.05)
        self.denoise = tk.BooleanVar(value=True)
        self.upscale_factor = tk.StringVar(value="")

        # AI 超分变量（Real-ESRGAN）
        self.sr_input_path = tk.StringVar()
        self.sr_output_path = tk.StringVar()
        self.sr_scale = tk.StringVar(value="2")  # 放大倍数，默认 2 倍
        
        self.create_widgets()
        
    def create_widgets(self):
        # 标题
        title_label = tk.Label(
            self.root, 
            text="图像处理工具",
            font=("Microsoft YaHei", 16, "bold"),
            pady=10
        )
        title_label.pack()
        
        # 创建标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 像素画转换标签页
        self.pixel_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pixel_frame, text="像素画转换")
        self.create_pixel_art_tab()
        
        # 画质增强标签页
        self.enhance_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.enhance_frame, text="画质增强")
        self.create_enhance_tab()

        # AI 超分标签页（Real-ESRGAN）
        self.sr_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sr_frame, text="AI 超分 (Real-ESRGAN)")
        self.create_super_res_tab()
        
        # 状态栏
        self.status_label = tk.Label(
            self.root,
            text="准备就绪",
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Microsoft YaHei", 9)
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_pixel_art_tab(self):
        # 输入文件选择
        input_frame = tk.Frame(self.pixel_frame, pady=10)
        input_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(input_frame, text="输入图片:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W)
        input_path_frame = tk.Frame(input_frame)
        input_path_frame.pack(fill=tk.X, pady=5)
        
        self.input_entry = tk.Entry(input_path_frame, textvariable=self.input_path, width=50)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(
            input_path_frame, 
            text="浏览...", 
            command=self.select_input_file,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # 输出文件选择
        output_frame = tk.Frame(self.pixel_frame, pady=10)
        output_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(output_frame, text="输出图片:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W)
        output_path_frame = tk.Frame(output_frame)
        output_path_frame.pack(fill=tk.X, pady=5)
        
        self.output_entry = tk.Entry(output_path_frame, textvariable=self.output_path, width=50)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(
            output_path_frame, 
            text="浏览...", 
            command=self.select_output_file,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # 参数设置区域
        params_frame = tk.LabelFrame(
            self.pixel_frame, 
            text="转换参数", 
            font=("Microsoft YaHei", 10, "bold"),
            pady=10,
            padx=20
        )
        params_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 像素大小
        pixel_frame = tk.Frame(params_frame)
        pixel_frame.pack(fill=tk.X, pady=5)
        tk.Label(pixel_frame, text="像素大小:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        pixel_scale = tk.Scale(
            pixel_frame,
            from_=16,
            to=256,
            orient=tk.HORIZONTAL,
            variable=self.pixel_size,
            length=300
        )
        pixel_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.pixel_label = tk.Label(pixel_frame, text="64", width=5)
        self.pixel_label.pack(side=tk.LEFT, padx=5)
        pixel_scale.config(command=lambda v: self.pixel_label.config(text=str(int(v))))
        
        # 颜色数量
        color_frame = tk.Frame(params_frame)
        color_frame.pack(fill=tk.X, pady=5)
        tk.Label(color_frame, text="颜色数量:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        color_scale = tk.Scale(
            color_frame,
            from_=16,
            to=256,
            orient=tk.HORIZONTAL,
            variable=self.color_reduction,
            length=300
        )
        color_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.color_label = tk.Label(color_frame, text="128", width=5)
        self.color_label.pack(side=tk.LEFT, padx=5)
        color_scale.config(command=lambda v: self.color_label.config(text=str(int(v))))
        
        # 缩放倍数
        scale_frame = tk.Frame(params_frame)
        scale_frame.pack(fill=tk.X, pady=5)
        tk.Label(scale_frame, text="输出缩放:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        scale_entry = tk.Entry(scale_frame, textvariable=self.scale_factor, width=10)
        scale_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(scale_frame, text="(留空=保持原尺寸, 例如: 2.0=放大2倍)", 
                font=("Microsoft YaHei", 8), fg="gray").pack(side=tk.LEFT, padx=5)
        
        # 插值方法
        interp_frame = tk.Frame(params_frame)
        interp_frame.pack(fill=tk.X, pady=5)
        tk.Label(interp_frame, text="插值方法:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        # 插值方法映射：中文显示 -> 英文值
        self.interpolation_map = {
            "最近邻（最快，像素感最强）": "nearest",
            "双线性（平滑过渡）": "bilinear",
            "三次卷积（推荐，平衡效果）": "bicubic",
            "Lanczos（高质量，细节保留）": "lanczos"
        }
        self.interpolation_display = tk.StringVar(value="三次卷积（推荐，平衡效果）")
        interp_combo = ttk.Combobox(
            interp_frame,
            textvariable=self.interpolation_display,
            values=list(self.interpolation_map.keys()),
            state="readonly",
            width=30
        )
        interp_combo.pack(side=tk.LEFT, padx=5)
        
        # 增强模式
        enhance_frame = tk.Frame(params_frame)
        enhance_frame.pack(fill=tk.X, pady=5)
        tk.Label(enhance_frame, text="增强模式:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        tk.Checkbutton(
            enhance_frame,
            variable=self.enhance_mode,
            text="启用（推荐，效果更好）"
        ).pack(side=tk.LEFT, padx=5)
        
        # 保持宽高比
        aspect_frame = tk.Frame(params_frame)
        aspect_frame.pack(fill=tk.X, pady=5)
        tk.Label(aspect_frame, text="保持宽高比:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        tk.Checkbutton(
            aspect_frame,
            variable=self.preserve_aspect,
            text="是"
        ).pack(side=tk.LEFT, padx=5)
        
        # 转换按钮
        button_frame = tk.Frame(self.pixel_frame, pady=20)
        button_frame.pack()
        
        self.convert_button = tk.Button(
            button_frame,
            text="开始转换",
            command=self.convert_image,
            font=("Microsoft YaHei", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            width=20,
            height=2,
            cursor="hand2"
        )
        self.convert_button.pack()
    
    def create_enhance_tab(self):
        # 输入文件选择
        input_frame = tk.Frame(self.enhance_frame, pady=10)
        input_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(input_frame, text="输入图片:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W)
        input_path_frame = tk.Frame(input_frame)
        input_path_frame.pack(fill=tk.X, pady=5)
        
        self.enhance_input_entry = tk.Entry(input_path_frame, textvariable=self.enhance_input_path, width=50)
        self.enhance_input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(
            input_path_frame, 
            text="浏览...", 
            command=self.select_enhance_input_file,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # 输出文件选择
        output_frame = tk.Frame(self.enhance_frame, pady=10)
        output_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(output_frame, text="输出图片:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W)
        output_path_frame = tk.Frame(output_frame)
        output_path_frame.pack(fill=tk.X, pady=5)
        
        self.enhance_output_entry = tk.Entry(output_path_frame, textvariable=self.enhance_output_path, width=50)
        self.enhance_output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(
            output_path_frame, 
            text="浏览...", 
            command=self.select_enhance_output_file,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # 参数设置区域
        params_frame = tk.LabelFrame(
            self.enhance_frame, 
            text="增强参数", 
            font=("Microsoft YaHei", 10, "bold"),
            pady=10,
            padx=20
        )
        params_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 锐化强度
        sharp_frame = tk.Frame(params_frame)
        sharp_frame.pack(fill=tk.X, pady=5)
        tk.Label(sharp_frame, text="锐化/模糊:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        sharp_scale = tk.Scale(
            sharp_frame,
            from_=0.1,
            to=3.0,
            resolution=0.05,
            orient=tk.HORIZONTAL,
            variable=self.sharpness,
            length=300
        )
        sharp_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.sharp_label = tk.Label(sharp_frame, text="1.5", width=6)
        self.sharp_label.pack(side=tk.LEFT, padx=5)
        sharp_scale.config(command=lambda v: self.sharp_label.config(text=f"{float(v):.2f}"))
        
        # 对比度
        contrast_frame = tk.Frame(params_frame)
        contrast_frame.pack(fill=tk.X, pady=5)
        tk.Label(contrast_frame, text="对比度:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        contrast_scale = tk.Scale(
            contrast_frame,
            from_=0.5,
            to=1.5,
            resolution=0.05,
            orient=tk.HORIZONTAL,
            variable=self.contrast,
            length=300
        )
        contrast_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.contrast_label = tk.Label(contrast_frame, text="1.1", width=5)
        self.contrast_label.pack(side=tk.LEFT, padx=5)
        contrast_scale.config(command=lambda v: self.contrast_label.config(text=f"{float(v):.2f}"))
        
        # 饱和度
        sat_frame = tk.Frame(params_frame)
        sat_frame.pack(fill=tk.X, pady=5)
        tk.Label(sat_frame, text="饱和度:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        sat_scale = tk.Scale(
            sat_frame,
            from_=0.5,
            to=1.3,
            resolution=0.05,
            orient=tk.HORIZONTAL,
            variable=self.saturation,
            length=300
        )
        sat_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.sat_label = tk.Label(sat_frame, text="1.05", width=5)
        self.sat_label.pack(side=tk.LEFT, padx=5)
        sat_scale.config(command=lambda v: self.sat_label.config(text=f"{float(v):.2f}"))
        
        # 放大倍数
        upscale_frame = tk.Frame(params_frame)
        upscale_frame.pack(fill=tk.X, pady=5)
        tk.Label(upscale_frame, text="放大倍数:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        upscale_entry = tk.Entry(upscale_frame, textvariable=self.upscale_factor, width=10)
        upscale_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(upscale_frame, text="(留空=不放大, 例如: 2.0=放大2倍)", 
                font=("Microsoft YaHei", 8), fg="gray").pack(side=tk.LEFT, padx=5)
        
        # 去噪选项
        denoise_frame = tk.Frame(params_frame)
        denoise_frame.pack(fill=tk.X, pady=5)
        tk.Label(denoise_frame, text="去噪处理:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        tk.Checkbutton(
            denoise_frame,
            variable=self.denoise,
            text="启用（推荐，减少噪点）"
        ).pack(side=tk.LEFT, padx=5)
        
        # 增强按钮
        button_frame = tk.Frame(self.enhance_frame, pady=20)
        button_frame.pack()
        
        self.enhance_button = tk.Button(
            button_frame,
            text="开始增强",
            command=self.enhance_image,
            font=("Microsoft YaHei", 12, "bold"),
            bg="#2196F3",
            fg="white",
            width=20,
            height=2,
            cursor="hand2"
        )
        self.enhance_button.pack()

    def create_super_res_tab(self):
        """AI 超分（Real-ESRGAN）标签页"""
        # 输入文件选择
        input_frame = tk.Frame(self.sr_frame, pady=10)
        input_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(input_frame, text="输入图片:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W)
        input_path_frame = tk.Frame(input_frame)
        input_path_frame.pack(fill=tk.X, pady=5)
        
        self.sr_input_entry = tk.Entry(input_path_frame, textvariable=self.sr_input_path, width=50)
        self.sr_input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(
            input_path_frame,
            text="浏览...",
            command=self.select_sr_input_file,
            width=10
        ).pack(side=tk.LEFT, padx=5)

        # 输出文件选择
        output_frame = tk.Frame(self.sr_frame, pady=10)
        output_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(output_frame, text="输出图片:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W)
        output_path_frame = tk.Frame(output_frame)
        output_path_frame.pack(fill=tk.X, pady=5)
        
        self.sr_output_entry = tk.Entry(output_path_frame, textvariable=self.sr_output_path, width=50)
        self.sr_output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(
            output_path_frame,
            text="浏览...",
            command=self.select_sr_output_file,
            width=10
        ).pack(side=tk.LEFT, padx=5)

        # 参数区域
        params_frame = tk.LabelFrame(
            self.sr_frame,
            text="超分参数",
            font=("Microsoft YaHei", 10, "bold"),
            pady=10,
            padx=20
        )
        params_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 放大倍数
        scale_frame = tk.Frame(params_frame)
        scale_frame.pack(fill=tk.X, pady=5)
        tk.Label(scale_frame, text="放大倍数:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        tk.Entry(scale_frame, textvariable=self.sr_scale, width=10).pack(side=tk.LEFT, padx=5)
        tk.Label(
            scale_frame,
            text="(建议 2 或 3；越大越耗时)",
            font=("Microsoft YaHei", 8),
            fg="gray"
        ).pack(side=tk.LEFT, padx=5)

        # 路径提示
        info_frame = tk.Frame(params_frame)
        info_frame.pack(fill=tk.X, pady=5)
        tk.Label(
            info_frame,
            text=f"Real-ESRGAN 路径: {REALESRGAN_EXE.name}",
            font=("Microsoft YaHei", 8),
            fg="gray"
        ).pack(anchor=tk.W)

        # 超分按钮
        button_frame = tk.Frame(self.sr_frame, pady=20)
        button_frame.pack()
        
        self.sr_button = tk.Button(
            button_frame,
            text="开始 AI 超分",
            command=self.run_super_res,
            font=("Microsoft YaHei", 12, "bold"),
            bg="#9C27B0",
            fg="white",
            width=20,
            height=2,
            cursor="hand2"
        )
        self.sr_button.pack()
        
    def select_input_file(self):
        filename = filedialog.askopenfilename(
            title="选择输入图片",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("所有文件", "*.*")
            ]
        )
        if filename:
            self.input_path.set(filename)
            # 自动设置输出路径
            if not self.output_path.get():
                input_path = Path(filename)
                output_path = input_path.parent / f"{input_path.stem}_pixel{input_path.suffix}"
                self.output_path.set(str(output_path))
    
    def select_output_file(self):
        filename = filedialog.asksaveasfilename(
            title="选择输出图片",
            defaultextension=".png",
            filetypes=[
                ("PNG文件", "*.png"),
                ("JPEG文件", "*.jpg"),
                ("所有文件", "*.*")
            ]
        )
        if filename:
            self.output_path.set(filename)

    def select_sr_input_file(self):
        filename = filedialog.askopenfilename(
            title="选择输入图片",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("所有文件", "*.*")
            ]
        )
        if filename:
            self.sr_input_path.set(filename)
            if not self.sr_output_path.get():
                input_path = Path(filename)
                output_path = input_path.parent / f"{input_path.stem}_SRx{self.sr_scale.get() or '2'}{input_path.suffix}"
                self.sr_output_path.set(str(output_path))

    def select_sr_output_file(self):
        filename = filedialog.asksaveasfilename(
            title="选择输出图片",
            defaultextension=".png",
            filetypes=[
                ("PNG文件", "*.png"),
                ("JPEG文件", "*.jpg"),
                ("所有文件", "*.*")
            ]
        )
        if filename:
            self.sr_output_path.set(filename)
    
    def select_enhance_input_file(self):
        filename = filedialog.askopenfilename(
            title="选择输入图片",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("所有文件", "*.*")
            ]
        )
        if filename:
            self.enhance_input_path.set(filename)
            # 自动设置输出路径
            if not self.enhance_output_path.get():
                input_path = Path(filename)
                output_path = input_path.parent / f"{input_path.stem}_enhanced{input_path.suffix}"
                self.enhance_output_path.set(str(output_path))
    
    def select_enhance_output_file(self):
        filename = filedialog.asksaveasfilename(
            title="选择输出图片",
            defaultextension=".png",
            filetypes=[
                ("PNG文件", "*.png"),
                ("JPEG文件", "*.jpg"),
                ("所有文件", "*.*")
            ]
        )
        if filename:
            self.enhance_output_path.set(filename)
    
    def convert_image(self):
        # 验证输入
        if not self.input_path.get():
            messagebox.showerror("错误", "请选择输入图片！")
            return
        
        if not os.path.exists(self.input_path.get()):
            messagebox.showerror("错误", "输入文件不存在！")
            return
        
        if not self.output_path.get():
            messagebox.showerror("错误", "请选择输出路径！")
            return
        
        # 获取参数
        try:
            pixel_size = self.pixel_size.get()
            color_reduction = self.color_reduction.get()
            scale_factor = None
            if self.scale_factor.get().strip():
                scale_factor = float(self.scale_factor.get())
        except ValueError:
            messagebox.showerror("错误", "缩放倍数必须是数字！")
            return
        
        # 禁用按钮，显示处理中
        self.convert_button.config(state=tk.DISABLED, text="转换中...")
        self.status_label.config(text="正在转换，请稍候...")
        self.root.update()
        
        try:
            # 获取插值方法的英文值
            interpolation_value = self.interpolation_map.get(
                self.interpolation_display.get(), 
                "bicubic"
            )
            
            # 执行转换
            convert_to_pixel_art(
                input_path=self.input_path.get(),
                output_path=self.output_path.get(),
                pixel_size=pixel_size,
                scale_factor=scale_factor,
                color_reduction=color_reduction,
                preserve_aspect=self.preserve_aspect.get(),
                enhance_mode=self.enhance_mode.get(),
                interpolation=interpolation_value
            )
            
            messagebox.showinfo("成功", f"转换完成！\n输出文件：{self.output_path.get()}")
            self.status_label.config(text="转换完成！")
            
        except Exception as e:
            messagebox.showerror("错误", f"转换失败：\n{str(e)}")
            self.status_label.config(text="转换失败")
        finally:
            # 恢复按钮
            self.convert_button.config(state=tk.NORMAL, text="开始转换")

    def run_super_res(self):
        """调用 Real-ESRGAN 进行 AI 超分（放到子线程中，避免界面假死）"""
        # 检查 exe 是否存在
        if not REALESRGAN_EXE.exists():
            messagebox.showerror(
                "错误",
                f"未找到 Real-ESRGAN 可执行文件：\n{REALESRGAN_EXE}\n\n"
                "请确认已解压到项目目录，或修改代码中的 REALESRGAN_EXE 路径。"
            )
            return

        # 验证输入
        if not self.sr_input_path.get():
            messagebox.showerror("错误", "请选择输入图片！")
            return
        if not os.path.exists(self.sr_input_path.get()):
            messagebox.showerror("错误", "输入文件不存在！")
            return
        if not self.sr_output_path.get():
            messagebox.showerror("错误", "请选择输出路径！")
            return

        # 目标放大倍数
        try:
            target_scale = float(self.sr_scale.get())
            if target_scale < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("错误", "放大倍数必须是大于等于 1 的数字！")
            return

        # 自动选择可用模型，并匹配模型尺度
        models_dir = REALESRGAN_EXE.parent / "models"
        model_defs = [
            ("realesr-animevideov3", 2),
            ("realesrgan-x4plus-anime", 4),
            ("realesrgan-x4plus", 4),
        ]
        chosen_name, chosen_scale = None, None
        for name, mscale in model_defs:
            if (models_dir / f"{name}.param").exists():
                chosen_name, chosen_scale = name, mscale
                break
        if chosen_name is None:
            messagebox.showerror("错误", f"未在 models 目录找到可用模型，请检查 {models_dir}")
            return

        # 运行尺度为模型本身的倍数；若与目标不同，事后再缩放
        run_scale = chosen_scale
        post_ratio = target_scale / run_scale if run_scale != target_scale else 1.0

        # 组装命令（GPU 0 / 输出 png / tile 自动）
        cmd = [
            str(REALESRGAN_EXE),
            "-i", self.sr_input_path.get(),
            "-o", self.sr_output_path.get(),
            "-s", str(run_scale),
            "-n", chosen_name,
            "-g", "0",
            "-f", "png",
            "-t", "0",
        ]

        # 禁用按钮，显示状态
        self.sr_button.config(state=tk.DISABLED, text="超分处理中...")
        self.status_label.config(text="正在进行 AI 超分，请稍候...")
        self.root.update()

        import threading

        def worker():
            try:
                # 在 Real-ESRGAN 可执行文件所在目录下运行，保证能正确找到 models 文件夹
                result = subprocess.run(
                    cmd,
                    cwd=str(REALESRGAN_EXE.parent),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="ignore"
                )

                def on_finish():
                    if result.returncode != 0:
                        message = result.stderr or result.stdout or "未知错误"
                        messagebox.showerror(
                            "错误",
                            f"AI 超分执行失败。\n\n命令：\n{' '.join(cmd)}\n\n错误信息：\n{message}"
                        )
                        self.status_label.config(text="AI 超分失败")
                        self.sr_button.config(state=tk.NORMAL, text="开始 AI 超分")
                        return

                    # 如模型尺度与目标尺度不同，事后再缩放到目标尺寸
                    if post_ratio != 1.0:
                        try:
                            img = Image.open(self.sr_output_path.get())
                            new_w = int(img.width * post_ratio)
                            new_h = int(img.height * post_ratio)
                            if new_w > 0 and new_h > 0:
                                img = img.resize((new_w, new_h), Image.LANCZOS)
                                img.save(self.sr_output_path.get())
                        except Exception as e:
                            messagebox.showwarning("提示", f"超分成功，但后处理缩放失败：{e}")

                    messagebox.showinfo("成功", f"AI 超分完成！\n输出文件：{self.sr_output_path.get()}")
                    self.status_label.config(text="AI 超分完成！")
                    self.sr_button.config(state=tk.NORMAL, text="开始 AI 超分")

                # 回到主线程更新 UI
                self.root.after(0, on_finish)

            except Exception as e:
                def on_error():
                    messagebox.showerror("错误", f"AI 超分执行异常：\n{str(e)}")
                    self.status_label.config(text="AI 超分失败")
                    self.sr_button.config(state=tk.NORMAL, text="开始 AI 超分")

                self.root.after(0, on_error)

        threading.Thread(target=worker, daemon=True).start()
    
    def enhance_image(self):
        # 验证输入
        if not self.enhance_input_path.get():
            messagebox.showerror("错误", "请选择输入图片！")
            return
        
        if not os.path.exists(self.enhance_input_path.get()):
            messagebox.showerror("错误", "输入文件不存在！")
            return
        
        if not self.enhance_output_path.get():
            messagebox.showerror("错误", "请选择输出路径！")
            return
        
        # 获取参数
        try:
            sharpness = self.sharpness.get()
            contrast = self.contrast.get()
            saturation = self.saturation.get()
            upscale_factor = None
            if self.upscale_factor.get().strip():
                upscale_factor = float(self.upscale_factor.get())
        except ValueError:
            messagebox.showerror("错误", "放大倍数必须是数字！")
            return
        
        # 禁用按钮，显示处理中
        self.enhance_button.config(state=tk.DISABLED, text="处理中...")
        self.status_label.config(text="正在增强画质，请稍候...")
        self.root.update()
        
        try:
            # 执行增强
            enhance_image_quality(
                input_path=self.enhance_input_path.get(),
                output_path=self.enhance_output_path.get(),
                sharpness=sharpness,
                contrast=contrast,
                saturation=saturation,
                denoise=self.denoise.get(),
                upscale_factor=upscale_factor,
            )
            
            messagebox.showinfo("成功", f"画质增强完成！\n输出文件：{self.enhance_output_path.get()}")
            self.status_label.config(text="画质增强完成！")
            
        except Exception as e:
            messagebox.showerror("错误", f"增强失败：\n{str(e)}")
            self.status_label.config(text="增强失败")
        finally:
            # 恢复按钮
            self.enhance_button.config(state=tk.NORMAL, text="开始增强")


def main():
    root = tk.Tk()
    app = PixelArtConverterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
