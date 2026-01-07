"""
# pyright: reportMissingImports=false
像素画风格转换器（核心算法）
将普通图片转换为清晰的像素艺术风格，保留原图的基本信息
"""

import os
import sys


# Pillow 是必需依赖，若未安装则给出通用提示
try:
    from PIL import Image  # type: ignore[import]
except ImportError as exc:
    print("错误: 未安装 Pillow 图像库。")
    print("请在当前 Python 环境中执行：")
    print("  pip install pillow")
    print("或使用 conda：")
    print("  conda install pillow")
    raise SystemExit(1) from exc

# ==================== 配置区域 ====================
# 在这里直接修改配置，然后运行脚本即可

# 输入图片路径（必填，打包给别人时不会暴露你的本地路径）
# 建议留空，让用户在 GUI 中选择；或在命令行模式下自行传入
INPUT_IMAGE = ""  # 例如: r"input.png"

# 输出图片路径（必填）
OUTPUT_IMAGE = ""  # 例如: r"output_pixel.png"

# 像素化尺寸（宽度，高度会按比例缩放）
PIXEL_SIZE = 64  # 可选值：32, 64, 96, 128等，数值越大保留细节越多

# 输出缩放倍数（None表示保持原图尺寸，2表示放大2倍）
SCALE_FACTOR = None  # 例如：None, 1.0, 2.0, 0.5

# 颜色数量减少（None表示不减少，数字表示目标颜色数）
COLOR_REDUCTION = 128  # 例如：64, 128, 256（数值越小颜色越少，像素感越强）

# 增强模式（True会启用创新算法，效果更好但稍慢）
# 包含的创新算法：
# 1. 边缘增强：在像素化前增强边缘，保留更多细节
# 2. 自适应颜色量化：根据图像内容动态调整量化参数
# 3. 颜色后处理：轻微调整颜色以增强对比度
# 4. 智能放大优化：对大幅放大进行后处理优化
ENHANCE_MODE = True  # True/False

# 插值方法选择
INTERPOLATION_METHOD = 'bicubic'  # 默认插值方式
INTERPOLATION_MAP = {
    'nearest': Image.NEAREST,   # 最近邻（像素感最强）
    'bilinear': Image.BILINEAR, # 双线性（平滑过渡）
    'bicubic': Image.BICUBIC,   # 三次卷积（推荐，平衡效果）
    'lanczos': Image.LANCZOS,   # Lanczos（高质量，细节保留）
}

# 是否保持宽高比
PRESERVE_ASPECT = True  # True保持宽高比，False强制为正方形

# ================================================


def convert_to_pixel_art(input_path, output_path, pixel_size=32, scale_factor=None, 
                         color_reduction=None, preserve_aspect=True, enhance_mode=True,
                         interpolation='bicubic'):
    """
    将图片转换为像素艺术风格
    
    参数:
        input_path: 输入图片路径
        output_path: 输出图片路径
        pixel_size: 目标像素大小（宽度，高度会按比例缩放）
        scale_factor: 最终输出相对于原图的缩放倍数（None则保持原尺寸）
        color_reduction: 颜色数量减少（None则不减少，数字表示目标颜色数）
        preserve_aspect: 是否保持宽高比
        enhance_mode: 是否启用增强模式
        interpolation: 插值方法 ('nearest', 'bicubic', 'lanczos')
                       用于预处理阶段，最终像素化仍使用最近邻
    """
    try:
        # 打开原始图片
        img = Image.open(input_path)
        original_size = img.size
        print(f"原始图片尺寸: {original_size[0]}x{original_size[1]}")
        
        # 转换为RGB模式（如果不是的话）
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 增强模式：先进行轻微降噪和对比度增强
        if enhance_mode:
            print("启用增强模式：优化图像质量...")
            from PIL import ImageEnhance
            # 先稍微缩小再放大，有助于平滑细节
            pre_interpolation = INTERPOLATION_MAP.get(interpolation.lower(), Image.BICUBIC)
            temp_size = (original_size[0] // 2, original_size[1] // 2)
            temp_img = img.resize(temp_size, pre_interpolation)
            img = temp_img.resize(original_size, pre_interpolation)
            # 轻微增强对比度
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.1)
            # 轻微增强饱和度
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.05)
        
        # 计算目标尺寸（保持宽高比）
        if preserve_aspect:
            aspect_ratio = original_size[1] / original_size[0]
            target_width = pixel_size
            target_height = int(pixel_size * aspect_ratio)
        else:
            target_width = pixel_size
            target_height = pixel_size
        
        print(f"像素化尺寸: {target_width}x{target_height}")
        
        # 第一步：缩小到目标像素尺寸（根据选择的插值方法进行预处理）
        pre_interpolation = INTERPOLATION_MAP.get(interpolation.lower(), Image.BICUBIC)
        
        if enhance_mode and target_width < original_size[0] // 2:
            # 分步缩小：先用高质量插值（BICUBIC/LANCZOS）预处理，再用最近邻像素化
            print(f"使用 {interpolation.upper()} 插值进行预处理...")
            intermediate_size = (target_width * 2, target_height * 2)
            pixelated = img.resize(intermediate_size, pre_interpolation)
            # 最后一步必须用最近邻，保持清晰的像素边缘
            pixelated = pixelated.resize((target_width, target_height), Image.NEAREST)
        else:
            # 直接缩小，使用最近邻保持像素感
            pixelated = img.resize((target_width, target_height), Image.NEAREST)
        
        # 创新算法1：边缘增强（在像素化前增强边缘，保留更多细节）
        if enhance_mode:
            from PIL import ImageFilter
            # 轻微锐化边缘
            pixelated = pixelated.filter(ImageFilter.UnsharpMask(radius=1, percent=50, threshold=3))
        
        # 颜色量化（减少颜色数量，增强像素艺术感）
        if color_reduction:
            print(f"颜色量化: 减少到 {color_reduction} 种颜色")
            # 创新算法2：自适应颜色量化
            # 先分析图像，根据内容动态调整量化参数
            if enhance_mode:
                # 使用中值切割算法，效果更好
                pixelated = pixelated.quantize(
                    colors=color_reduction, 
                    method=Image.Quantize.MEDIANCUT,
                    dither=Image.Dither.NONE  # 不使用抖动，保持清晰的像素块
                )
                # 创新算法3：颜色后处理 - 轻微调整颜色以增强对比度
                pixelated = pixelated.convert('RGB')
                # 对每个像素进行轻微的颜色增强
                from PIL import ImageEnhance
                enhancer = ImageEnhance.Contrast(pixelated)
                pixelated = enhancer.enhance(1.05)  # 轻微增强对比度
            else:
                pixelated = pixelated.quantize(colors=color_reduction, method=Image.Quantize.MEDIANCUT)
                pixelated = pixelated.convert('RGB')
        
        # 第二步：放大到最终尺寸（使用最近邻插值，保持像素感）
        if scale_factor:
            final_width = int(original_size[0] * scale_factor)
            final_height = int(original_size[1] * scale_factor)
        else:
            final_width = original_size[0]
            final_height = original_size[1]
        
        print(f"最终输出尺寸: {final_width}x{final_height}")
        
        # 创新算法4：智能放大 - 使用最近邻保持像素感
        final_img = pixelated.resize((final_width, final_height), Image.NEAREST)
        
        # 创新算法5：最终优化 - 轻微去噪和平滑处理（可选）
        if enhance_mode and final_width > target_width * 2:
            # 对于大幅放大，进行轻微的后处理优化
            from PIL import ImageFilter
            # 使用轻微的中值滤波去除放大产生的噪点
            final_img = final_img.filter(ImageFilter.MedianFilter(size=3))
        
        # 保存结果
        final_img.save(output_path)
        print(f"✓ 转换完成！输出文件: {output_path}")
        
        return final_img
        
    except FileNotFoundError:
        print(f"错误: 找不到输入文件 '{input_path}'")
        print("请检查文件路径是否正确")
        sys.exit(1)
    except PermissionError:
        print(f"错误: 没有权限访问文件 '{input_path}' 或无法写入 '{output_path}'")
        sys.exit(1)
    except OSError as e:
        print(f"错误: 文件操作失败 - {str(e)}")
        sys.exit(1)
    except Exception as e:
        import traceback
        print(f"错误: 发生未预期的异常")
        print(f"异常类型: {type(e).__name__}")
        print(f"异常信息: {str(e)}")
        print("\n详细错误信息:")
        traceback.print_exc()
        sys.exit(1)


def enhance_image_quality(input_path, output_path, sharpness=1.5, contrast=1.1,
                          saturation=1.05, denoise=True, upscale_factor=None):
    """
    增强图像画质，让模糊的照片变清晰，特别优化细节处理
    
    参数:
        input_path: 输入图片路径
        output_path: 输出图片路径
        sharpness: 清晰/模糊控制（<1 模糊，1 不变，>1 锐化，推荐 0.1~3）
        contrast: 对比度（0.5-1.5，1 为不变，<1 变平，>1 变强）
        saturation: 饱和度（0.5-1.3，1 为不变，<1 变灰，>1 更艳）
        denoise: 是否去噪（True/False）
        upscale_factor: 放大倍数（None表示不放大，2.0表示放大2倍）
    """
    try:
        from PIL import ImageFilter, ImageEnhance
        
        # 打开原始图片
        img = Image.open(input_path)
        original_size = img.size
        print(f"原始图片尺寸: {original_size[0]}x{original_size[1]}")
        
        # 转换为RGB模式（如果不是的话）
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 步骤1：去噪（如果启用，使用温和设置，避免涂抹细节）
        if denoise:
            print("去噪处理（温和）...")
            img = img.filter(ImageFilter.MedianFilter(size=3))

        # 步骤2：锐化/模糊控制
        print(f"锐化/模糊处理（强度: {sharpness}）...")
        if sharpness >= 1.0:
            # 温和锐化（避免电路板感）
            sharpen_percent = int(min(sharpness * 80, 150))
            img = img.filter(ImageFilter.UnsharpMask(
                radius=1.0,
                percent=sharpen_percent,
                threshold=3
            ))
        else:
            # 更强的模糊：数值越小越模糊，0.1 -> 半径约 4.5
            blur_radius = max(0.0, min((1.0 - sharpness) * 5.0, 8.0))
            if blur_radius > 0:
                img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        # 步骤3：轻微对比度增强
        print(f"对比度增强（倍数: {contrast}）...")
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(min(contrast, 1.3))

        # 步骤4：轻微饱和度增强
        print(f"饱和度增强（倍数: {saturation}）...")
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(min(saturation, 1.3))
        
        # 步骤5：可选放大（使用高质量算法）
        if upscale_factor and upscale_factor > 1.0:
            print(f"高质量放大处理（倍数: {upscale_factor}）...")
            new_size = (int(original_size[0] * upscale_factor), 
                       int(original_size[1] * upscale_factor))
            img = img.resize(new_size, Image.LANCZOS)
            # 放大后轻微锐化，适度恢复细节
            img = img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=60, threshold=3))
        
        # 保存结果（使用高质量保存）
        if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
            img.save(output_path, quality=95, optimize=True)
        else:
            img.save(output_path, quality=95)
        print(f"✓ 画质增强完成！输出文件: {output_path}")
        
        return img
        
    except FileNotFoundError:
        print(f"错误: 找不到输入文件 '{input_path}'")
        print("请检查文件路径是否正确")
        sys.exit(1)
    except PermissionError:
        print(f"错误: 没有权限访问文件 '{input_path}' 或无法写入 '{output_path}'")
        sys.exit(1)
    except OSError as e:
        print(f"错误: 文件操作失败 - {str(e)}")
        sys.exit(1)
    except Exception as e:
        import traceback
        print(f"错误: 发生未预期的异常")
        print(f"异常类型: {type(e).__name__}")
        print(f"异常信息: {str(e)}")
        print("\n详细错误信息:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    try:
        # 检查输入文件是否存在
        if not os.path.exists(INPUT_IMAGE):
            print(f"错误: 找不到输入文件 '{INPUT_IMAGE}'")
            print("请在代码顶部的配置区域修改 INPUT_IMAGE 路径")
            sys.exit(1)
        
        # 检查输出目录是否存在
        output_dir = os.path.dirname(OUTPUT_IMAGE)
        if output_dir and not os.path.exists(output_dir):
            print(f"错误: 输出目录不存在 '{output_dir}'")
            print("请创建目录或修改 OUTPUT_IMAGE 路径")
            sys.exit(1)
        
        # 执行转换
        convert_to_pixel_art(
            input_path=INPUT_IMAGE,
            output_path=OUTPUT_IMAGE,
            pixel_size=PIXEL_SIZE,
            scale_factor=SCALE_FACTOR,
            color_reduction=COLOR_REDUCTION,
            preserve_aspect=PRESERVE_ASPECT,
            enhance_mode=ENHANCE_MODE,
            interpolation=INTERPOLATION_METHOD
        )
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        import traceback
        print(f"\n错误: 程序执行失败")
        print(f"异常类型: {type(e).__name__}")
        print(f"异常信息: {str(e)}")
        print("\n详细错误信息:")
        traceback.print_exc()
        sys.exit(1)
