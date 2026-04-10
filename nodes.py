# ComfyUI-DanbooruPromptNode/nodes.py - V14.8 (yousa预设增强 + 权重支持 + 多行文本框)

import random

class DanbooruPromptGenerator:
    """ComfyUI 自定义节点：danbooru提示词生成器"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                # ================= 角色配置 =================
                "character_preset": (["yousa", "general"],),
                
                # ================= 模块开关（布尔值）=================
                "enable_quality": ("BOOLEAN", {"default": True}),
                "enable_outfit": ("BOOLEAN", {"default": True}),
                "enable_nsfw": ("BOOLEAN", {"default": True}),
                "enable_action": ("BOOLEAN", {"default": True}),
                "enable_environment": ("BOOLEAN", {"default": True}),
                
                # ================= 随机种子 =================
                "seed": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 2147483647,
                    "step": 1
                }),
            },
            "optional": {
                # ================= 【V14.7新增】各模块自定义内容输入（STRING）=================
                # 【V14.8更新】multiline: True - 改为多行文本框
                "custom_quality": ("STRING", {"default": "", "multiline": True}),
                "custom_outfit": ("STRING", {"default": "", "multiline": True}),
                "custom_nsfw": ("STRING", {"default": "", "multiline": True}),
                "custom_action": ("STRING", {"default": "", "multiline": True}),
                "custom_environment": ("STRING", {"default": "", "multiline": True}),
                
                # ================= 可选输入：clip模型（用于直接输出CONDITIONING）=================
                "clip": ("CLIP",),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "CONDITIONING", "CONDITIONING")
    RETURN_NAMES = ("positive_prompt", "negative_prompt", "positive_conditioning", "negative_conditioning")
    
    FUNCTION = "generate_prompts"
    
    CATEGORY = "Danbooru/Prompt Generation"
    TITLE = "🎨 Danbooru Prompt Generator V14.8 (YouSa Enhanced)"

    def generate_prompts(self, character_preset, enable_quality, enable_outfit, 
                         enable_nsfw, enable_action, enable_environment, seed,
                         custom_quality="", custom_outfit="", custom_nsfw="", 
                         custom_action="", custom_environment="", clip=None):
        """生成提示词的核心函数"""
        
        # 设置随机种子
        random.seed(seed)
        
        # ================= 标签库（内置）=================
        tag_quality = [
            "masterpiece", "best quality", "highres", "8k uhd", 
            "anime style", "cel shading", "vibrant colors", "clean lines"
        ]
        
        tag_character = [
            "long hair", "twintails", "short hair", "bob cut",
            "silver hair", "black hair", "pink hair", "blue hair",
            "green eyes", "golden eyes", "heterochromia",
            "smile", "blush", "neutral expression", "serious face",
            "crying", "tears", "happy tears", "sad tears"
        ]
        
        tag_outfit = [
            "t-shirt", "tank top", "crop top", "camisole", 
            "blouse", "shirt", "sweater", "vest", "hoodie",
            "skirt", "layered skirt", "pleated skirt", "mini skirt", 
            "shorts", "pants", "jeans", "leggings",
            "dress", "frilly dress", "evening gown", "wedding dress", 
            "school uniform", "office lady suit", "nurse outfit", 
            "maid outfit", "magical girl costume", "gym wear", 
            "swimsuit", "bikini", "lingerie", "nightgown"
        ]
        
        tag_nsfw = [
            "bikini", "swimsuit", "lingerie", "panties", "bra", 
            "nipples", "sweat on skin", 
            "cleavage", "bare shoulders", "upper body nude",
            "pussy", "between the thighs", "legs spread", "pubic hair", "navel"
        ]
        
        tag_action = [
            "standing", "sitting", "kneeling", "lying down", "crouching",
            "crossed legs", "spread legs", "on all fours",
            "upper body", "chest up", "looking at viewer", "profile view",
            "hands on hips", "arms crossed", "finger heart", "peace sign"
        ]
        
        tag_time = [
            "morning", "daylight", "afternoon", 
            "golden hour", "sunset", "dusk", 
            "night view", "midnight"
        ]
        
        tag_weather = [
            "clear sky", "cloudy", "sunny day", 
            "rainy day", "raining", "snowing", "snow field", 
            "foggy", "misty atmosphere"
        ]
        
        tag_location = [
            # 自然景观
            "cherry blossoms", "sakura petals", 
            "beach", "ocean waves", "mountain landscape", 
            "forest", "fantasy forest", "garden", "park",
            # 城市建筑
            "city street", "urban view", "skyscrapers", 
            "rooftop", "balcony", "modern building", 
            "cyberpunk city", "neon lights", "alleyway",
            # 室内空间
            "classroom interior", "cozy cafe", "library", "bedroom room", 
            "living room", "kitchen scene", "laboratory", "onsen bath",
            "shop store", "restaurant interior", "hospital ward"
        ]
        
        tag_negative = [
            "lowres, low quality, worst quality", "text, watermark", 
            "bad anatomy, bad hands, missing fingers, extra limbs",
            "3d render style, realistic texture, flat coloring error"
        ]
        
        # ================= 生成逻辑 ==================
        positive_parts = []
        
        # A. 质量层 (Quality) - 【V14.7支持自定义】
        if enable_quality:
            quality_part = ", ".join(random.sample(tag_quality, min(3, len(tag_quality))))
            if quality_part: positive_parts.append(quality_part)
        elif custom_quality.strip():
            # 开关关闭但有自定义输入 → 使用自定义内容（支持多行）
            positive_parts.extend(self._parse_multiline_tags(custom_quality))
        
        # B. 角色核心层 (Character) - 【V14.8 yousa预设增强】
        if character_preset == "yousa":
            # 【V14.8更新】yousa固定标签（带权重）
            fixed_tags = [
                "yousa", 
                "1girl", 
                "solo", 
                "(DMb_hair:1.1)",  
                "black hair",  
                "red eyes"    
            ]
            positive_parts.extend(fixed_tags)
            
            # 【V14.8更新】过滤冲突标签（排除 black hair, red eyes）
            filtered_character = [t for t in tag_character if t not in 
                                  ["long hair", "short hair", "twintails", "bob cut",
                                   "silver hair", "black hair", "pink hair", "blue hair",
                                   "green eyes", "golden eyes", "heterochromia"]]  # 新增排除眼部标签
        else:
            fixed_tags = []
            filtered_character = tag_character
        
        char_part = ", ".join(random.sample(filtered_character, min(2, len(filtered_character)))) 
        if char_part: positive_parts.append(char_part)
        
        # C. 服饰 (Outfit) - 【V14.7支持自定义】
        if enable_outfit:
            outfit_part = ", ".join(random.sample(tag_outfit, min(2, len(tag_outfit))))
            if outfit_part: positive_parts.append(outfit_part)
        elif custom_outfit.strip():
            # 开关关闭但有自定义输入 → 使用自定义内容（支持多行）
            positive_parts.extend(self._parse_multiline_tags(custom_outfit))
        
        # D. NSFW - 【V14.7支持自定义】
        if enable_nsfw:
            nsfw_count = 5
            nsfw_part = ", ".join(random.sample(tag_nsfw, min(nsfw_count, len(tag_nsfw))))
            if nsfw_part: positive_parts.append(nsfw_part)
        elif custom_nsfw.strip():
            # 开关关闭但有自定义输入 → 使用自定义内容（支持多行）
            positive_parts.extend(self._parse_multiline_tags(custom_nsfw))
        
        # E. 动作 (Action) - 【V14.7支持自定义】
        if enable_action:
            action_part = ", ".join(random.sample(tag_action, min(3, len(tag_action))))
            if action_part: positive_parts.append(action_part)
        elif custom_action.strip():
            # 开关关闭但有自定义输入 → 使用自定义内容（支持多行）
            positive_parts.extend(self._parse_multiline_tags(custom_action))
        
        # F. 环境 (Environment) - 【V14.7支持自定义】
        if enable_environment:
            time_tag = random.choice(tag_time) if tag_time else ""
            weather_tag = random.choice(tag_weather) if tag_weather else ""
            location_part = ", ".join(random.sample(tag_location, min(2, len(tag_location))))
            
            for tag in [time_tag, weather_tag, location_part]:
                if tag: positive_parts.append(tag)
        elif custom_environment.strip():
            # 开关关闭但有自定义输入 → 使用自定义内容（支持多行）
            positive_parts.extend(self._parse_multiline_tags(custom_environment))
        
        # G. 组合最终提示词
        positive_prompt = ", ".join(positive_parts)
        negative_sample = random.sample(tag_negative, min(3, len(tag_negative)))
        negative_prompt = ", ".join(negative_sample)
        
        # ================= 【V14.6】生成CONDITIONING输出 ==================
        positive_conditioning = None
        negative_conditioning = None
        
        if clip is not None:
            # 使用clip.encode_token_to_conditioning方法编码提示词
            tokens_positive = clip.tokenize(positive_prompt)
            tokens_negative = clip.tokenize(negative_prompt)
            
            positive_conditioning, _ = clip.encode_from_tokens(tokens_positive, return_pooled=True)
            negative_conditioning, _ = clip.encode_from_tokens(tokens_negative, return_pooled=True)
        
        return (positive_prompt, negative_prompt, positive_conditioning, negative_conditioning)
    
    def _parse_multiline_tags(self, tag_string):
        """解析多行文本标签（支持换行和逗号分隔）"""
        # 替换换行为逗号，然后按逗号分割
        normalized = tag_string.replace("\n", ",").replace("\r", ",")
        tags = [t.strip() for t in normalized.split(",") if t.strip()]
        return tags


# ================= 节点注册 =================

NODE_CLASS_MAPPINGS = {
    "DanbooruPromptGenerator": DanbooruPromptGenerator,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DanbooruPromptGenerator": "🎨 Danbooru Prompt Generator",
}
