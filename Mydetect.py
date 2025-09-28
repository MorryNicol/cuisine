from sam2.build_sam import build_sam2
from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator
import time
import os
# if using Apple MPS, fall back to CPU for unsupported ops
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
import numpy as np
import torch
import matplotlib.pyplot as plt
from PIL import Image
import cv2
import shutil
import cn_clip.clip as clip
from cn_clip.clip import load_from_name
import stat

# 加载模型和预处理函数
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = load_from_name("ViT-B-16", device=device, download_root='./')
model.eval()

# 读取食材名称列表
with open('./ingredients_dictionary.txt', 'r', encoding='utf-8') as file:
    ingredients = [line.strip() for line in file.readlines()]

text = clip.tokenize(ingredients).to(device)

def Mydetect(picture_path):
    """
    输入待检测图片路径，输出检测结果

    Args:
        picture_path (string): 图片路径.

    Returns:
        list: 图片包含的菜，以列表形式返回.
    """
    
    # admit the permission
    def readonly_handler(func, path, execinfo):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    # select the device for computation
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"using device: {device}")
    print(time.ctime())

    if device.type == "cuda":
        # use bfloat16 for the entire notebook
        torch.autocast("cuda", dtype=torch.float16).__enter__()
        # turn on tfloat32 for Ampere GPUs (https://pytorch.org/docs/stable/notes/cuda.html#tensorfloat-32-tf32-on-ampere-devices)
        if torch.cuda.get_device_properties(0).major >= 8:
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
    elif device.type == "mps":
        print(
            "\nSupport for MPS devices is preliminary. SAM 2 is trained with CUDA and might "
            "give numerically different outputs and sometimes degraded performance on MPS. "
            "See e.g. https://github.com/pytorch/pytorch/issues/84936 for a discussion."
        )

    np.random.seed(3)

    image = Image.open(picture_path)
    image = np.array(image.convert("RGB"))

    sam2_checkpoint = "./checkpoints/sam2.1_hiera_tiny.pt"
    model_cfg = "configs/sam2.1/sam2.1_hiera_t.yaml"

    sam2 = build_sam2(model_cfg, sam2_checkpoint, device=device, apply_postprocessing=False)

    mask_generator = SAM2AutomaticMaskGenerator(sam2)

    masks = mask_generator.generate(image)

    from pathlib import Path
    print(time.ctime())

    output_dir = "./ingredients/"
    # 如果目录存在，则删除它
    if os.path.exists(output_dir) and os.path.isdir(output_dir):
        shutil.rmtree(output_dir, onerror=readonly_handler)
        print(f"Deleted existing directory: {output_dir}")

    # 创建新的空目录
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created new directory: {output_dir}")


    for i, mask in enumerate(masks):
        segmentation = mask['segmentation']

        # 创建二值掩码
        binary_mask = np.zeros_like(segmentation, dtype=np.uint8)
        binary_mask[segmentation] = 255

        # 寻找轮廓
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 获取最大轮廓的边界框
        if len(contours) > 0:  # 确保存在至少一个轮廓
            x, y, w, h = cv2.boundingRect(contours[0])

            # 使用边界框裁剪原始图像
            cropped_image = image[y:y + h, x:x + w]

            # 保存裁剪后的图像到临时路径
            temp_output_path = Path(output_dir) / f"object_{i}_temp.png"

            # 使用plt保存图像
            plt.figure(figsize=(20, 20))
            plt.imshow(cropped_image)
            plt.axis('off')
            plt.savefig(str(temp_output_path), bbox_inches='tight', pad_inches=0)
            plt.close()  # 关闭图形以释放内存

            final_output_path = Path(output_dir) / f"object_{i}.png"
            temp_output_path.rename(final_output_path)

    print(f"Extracted objects saved to {output_dir}")

    # 定义输入和输出目录
    input_dir = "./ingredients/"
    output_dir = "./ingredients_filtered/"

    # 如果目录存在，则删除它
    if os.path.exists(output_dir) and os.path.isdir(output_dir):
        shutil.rmtree(output_dir, onerror=readonly_handler)
        print(f"Deleted existing directory: {output_dir}")

    # 创建新的空目录
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created new directory: {output_dir}")


    # 获取并读取文件夹中的所有PNG图片
    image_files = [f for f in Path(input_dir).glob("*.png")]

    # 如果没有找到任何PNG文件，则终止程序
    if not image_files:
        print("No PNG images found in the directory.")
        return ['没有发现食材']
    else:
        # 计算每个文件的大小（以KB为单位），并将结果存储在一个列表中
        sizes_kb = [(f, f.stat().st_size / 1024) for f in image_files]

        # 按照文件大小排序
        sizes_kb.sort(key=lambda x: x[1])

        # 找到最大文件大小M
        max_size_kb = sizes_kb[-1][1] if sizes_kb else 0

        # 设置min_size和max_size为分割图像最大大小的5%和95%
        min_size_kb = max_size_kb * 0.05
        max_size_kb = max_size_kb * 1.00

        print(f"Max size of images: {max_size_kb:.2f} KB")
        print(f"Min size threshold: {min_size_kb:.2f} KB")
        print(f"Max size threshold: {max_size_kb:.2f} KB")

        # 筛选出大小在0.05M到0.95M之间的图像，并复制到新的文件夹
        filtered_images = [f for f, size in sizes_kb if min_size_kb <= size <= max_size_kb]

        for img_path in filtered_images:
            output_path = Path(output_dir) / img_path.name
            shutil.copy(img_path, output_path)
            print(f"Copied {img_path.name} with size {img_path.stat().st_size / 1024:.2f} KB to filtered directory")

        print(f"Filtered images saved to {output_dir}")
    print(time.ctime())

    torch.cuda.empty_cache()
    # # 加载模型和预处理函数
    # device = "cuda" if torch.cuda.is_available() else "cpu"
    # model, preprocess = load_from_name("ViT-B-16", device=device, download_root='./')
    # model.eval()

    # # 读取食材名称列表
    # with open('./ingredients_dictionary.txt', 'r', encoding='utf-8') as file:
    #     ingredients = [line.strip() for line in file.readlines()]

    # 定义图像文件夹路径
    image_folder = "./ingredients_filtered"

    # 获取文件夹中所有图片文件的路径，并排序以确保顺序一致
    image_paths = sorted([os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))])

    # 创建一个集合用于存储唯一类别的索引
    unique_categories_indices = set()

    # 对文本进行编码
    # text = clip.tokenize(ingredients).to(device)
    # text_features = model.encode_text(text)

    # 遍历所有图片文件（除了第一张）
    for image_path in image_paths:
        try:
            # 加载和预处理图像
            image_input = preprocess(Image.open(image_path)).unsqueeze(0).to(device)

            with torch.no_grad():
                # image_features = model.encode_image(image_input)
                # text_features = model.encode_text(text)

                # 归一化特征
                # image_features /= image_features.norm(dim=-1, keepdim=True)
                # text_features /= text_features.norm(dim=-1, keepdim=True)

                logits_per_image, _ = model.get_similarity(image_input, text)
                probs = logits_per_image.softmax(dim=-1).cpu().numpy()

                # 找出概率最大的类别索引
                max_index, max_p = max(enumerate(probs[0]), key=lambda x: x[1])
                # print(max_p)

                # 概率超过一定值才认为存在食材
                if max_p > 0.3:
                    # 添加到集合中以确保唯一性
                    unique_categories_indices.add(max_index)

        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
    print(time.ctime())

    food = [ingredients[idx] for idx in unique_categories_indices]
    return food

# print(Mydetect('./data/images/test.jpg'))
