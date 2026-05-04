import random
from typing import List, Tuple

class DanbooruPromptGenerator:
    """ComfyUI Danbooru提示词生成器"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # ================= 随机种子 =================
                "seed": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 2147483647,
                    "step": 1
                }),
                
                # ==================== 开关控制区 (全部放在一起) ====================
                
                # 1. 质量词模块开关
                "enable_quality": ("BOOLEAN", {"default": True}),
                
                # 2. 人物预设开关
                "character_default": ("BOOLEAN", {"default": True}),
                
                # 3. R18标签开关
                "enable_r18": ("BOOLEAN", {"default": False}),
                
                # 4. 服饰模块开关
                "enable_clothes": ("BOOLEAN", {"default": True}),
                
                # 5. 动作模块开关
                "enable_actions": ("BOOLEAN", {"default": True}),
                
                # 6. 户外场景开关
                "enable_outdoors": ("BOOLEAN", {"default": True}),
                
                # 7. 室内场景开关
                "enable_indoors": ("BOOLEAN", {"default": False}),
                
                # 8. 天气模块开关 (整合SkyWeatherModule)
                "enable_weather": ("BOOLEAN", {"default": True}),

                # 9. Effects模块开关
                "enable_effects": ("BOOLEAN", {"default": True}),
                
                # 10.负面提示词模块
                "enable_negative": ("BOOLEAN", {"default": True}),

                # ==================== 自定义输入区 (全部放在一起) ====================
                
                # 1. 质量词自定义输入
                "custom_quality": ("STRING", {
                    "multiline": True, 
                    "default": "",
                    "placeholder": "关闭enable_quality时输入自定义质量词\n例如：masterpiece\nbest quality\nhigh resolution"
                }),
                
                # 2. 人物预设自定义输入
                "custom_character": ("STRING", {
                    "multiline": True, 
                    "default": "yousa\nred eyes\nblack hair\n(DMB_hair:1.1)",
                    "placeholder": "关闭character_default时输入自定义人物标签\n默认yousa, 1girl solo, red eyes, (DMB_hair:1.1), looking at viewer"
                }),
                
                # 3. R18标签自定义输入
                "custom_r18": ("STRING", {
                    "multiline": True, 
                    "default": "",
                    "placeholder": "关闭enable_r18时输入自定义R18标签"
                }),
                
                # 4. 服饰模块自定义输入
                "custom_clothes": ("STRING", {
                    "multiline": True, 
                    "default": "",
                    "placeholder": "关闭enable_clothes时输入自定义服饰标签"
                }),
                
                # 5. 动作模块自定义输入
                "custom_actions": ("STRING", {
                    "multiline": True, 
                    "default": "",
                    "placeholder": "关闭enable_actions时输入自定义动作标签"
                }),
                
                # 6. 户外场景自定义输入
                "custom_outdoors": ("STRING", {
                    "multiline": True, 
                    "default": "",
                    "placeholder": "关闭enable_outdoors时输入自定义户外场景"
                }),
                
                # 7. 室内场景自定义输入
                "custom_indoors": ("STRING", {
                    "multiline": True, 
                    "default": "",
                    "placeholder": "关闭enable_indoors时输入自定义室内场景"
                }),
                
                # 8. 天气模块自定义输入 (合并为一个统一的输入框)
                "custom_weather_time": ("STRING", {
                    "multiline": True, 
                    "default": "",
                    "placeholder": "关闭enable_weather时输入自定义天气/时间标签\n例如：day\nnight\nsunny\nrainy"
                }),
                # Effects模块自定义输入
                "custom_effects": ("STRING", {
                    "multiline": True, 
                    "default": "",
                    "placeholder": "关闭enable_effects时输入自定义效果标签\n例如：watercolor (medium)\ncinematic lighting\nbokeh"
                }),
                # 负面提示词模块自定义输入
                "custom_negative": ("STRING", {
                    "multiline": True, 
                    "default": "",
                    "placeholder": "关闭enable_negative时输入自定义负面提示词\n例如：low quality\nworst quality\nbad anatomy"
                }),

            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "negative_prompt")
    
    FUNCTION = "generate_prompt"
    
    CATEGORY = "Prompt Tools/Random"
    
    TITLE = "Danbooru 提示词生成器"
    
    # ==================== 内置数据池 ====================
    
    # === 质量词模块 (Danbooru规范) ===
    QUALITY_POOL = [
        # 基础质量词
        "masterpiece", "best quality", "high quality", "very high resolution",
        "4k", "8k", "hd", "detailed", "intricate details", "delicate details",
        
        # 画面描述
        "beautiful", "exquisite", "stunning", "gorgeous", "elegant", "graceful",
        "vivid colors", "vibrant colors", "colorful", "soft lighting",
        
        # 构图相关
        "perfect composition", "balanced composition", "dynamic angle",
        "cinematic", "cinematic lighting", "dramatic lighting",
        
        # 细节描述
        "sharp focus", "crisp details", "fine details", "intricate patterns",
        "textured", "highly detailed background",
        
        # 艺术风格质量词
        "professional artwork", "award winning", "trending on artstation",
        "featured on pixiv", "illustration of the day"
    ]
    
    # === 人物预设 (默认) ===
    CHARACTER_DEFAULT = ["yousa", "1girl", "solo", "red eyes", "black hair", "(DMB_hair:1.1)", "looking at viewer"]
    
    # === R18标签池  ===
    R18_POOL = [
        "huge ass","spread ass","buttjob","wakamezake","anus","anal",
        "peeing","have to pee","double anal","anal fingering","anilingus",
        "hairjob","oral","gokkun","facial","handjob","leash","lactation",
        "breast sucking","paizuri","multiple paizuri","pussy","pubic hair",
        "clitoris","fat mons","pussy juice","female ejaculation","grinding",
        "crotch rub","facesitting","cervix","cunnilingus","thigh sex",
        "footjob","masturbation","clothed masturbation","penis","testicles",
        "ejaculation","cum","public","humiliation","caught","walk-in",
        "body writing","asian","faceless male","artificial vagina","dildo",
        "sex","clothed sex","happy sex","underwater sex","cock in thighhigh",
        "doggystyle","leg lock","missionary","girl on top","cowgirl position",
        "reverse cowgirl","virgin","threesome","tribadism",
        "gangbang","femdom","condom","bandaid on pussy","cleft of venus",
        "clitoral hood","clitoris piercing","perineum","urethra","crotch seam",
        "erect clitoris","overflow","overgrown","flat ass","gaping","labia",
        "partially visible anus","partially visible vulva","pussy peek",
        "condom on penis","double handjob","fingering","guided penetration",
        "penis grab","two-handed handjob","paizuri under clothes","spanked",
        "anal fisting","enema","stomach bulge","x-ray","tentacle","gag",
        "groping","nipple torture","nipple piercing","cameltoe","insertion",
        "penetration","fisting","multiple insertions","double penetration",
        "triple penetration","double vaginal","piercing","navel piercing",
        "mound of venus","wide hips","tamakericzx","vore","transformation",
        "mind control","blood","nyotaimori","wooden horse","anal beads",
        "cock ring","double dildo","vibrator","vibrator in thighhighs",
        "vibrator under panties","slave","shibari","bondage","bdsm",
        "pillory","rope","futanari","incest","twincest","pegging",
        "ganguro","bestiality","molestation","voyeurism","exhibitionism",
        "rape","about to be raped","anal tail"
    ]
    
    # === 服饰池  ===
    CLOTHES_POOL = [
        "collarbone","wings","bat wings","butterfly wings","black wings",
        "demon wings","muscle","cape","camisole","detached sleeves","hoodie",
        "long sleeves","robe","off shoulder","bare shoulders","topless",
        "open clothes","open robe","naked cape","naked shirt","angel wings",
        "detached wings","dragon wings","fairy wings","harness","whip marks",
        "badge","arm belt","bandaged arm","bandaged hands","bangle","bead bracelet",
        "bracelet","bracer","armband","armlet","elbow gloves","fingerless gloves",
        "gloves","wrist cuffs","wristband","belly chain","bandages","barcode",
        "bow","command spell","diamond (gemstone)","heart lock (kantai collection)",
        "heart tattoo","heartbeat","mole","number tattoo","blazer","suit jacket",
        "capelet","cloak","coat","coattails","collared jacket","duffel coat",
        "hooded cape","hooded cloak","hooded coat","hooded jacket","labcoat",
        "military jacket","pant suit","tailcoat","blouse","cardigan","casual",
        "heart cutout","center frills","center opening","checkered shirt",
        "clothes between breasts","cat cutout","t-shirt","collared shirt",
        "criss-cross halter","crop top","cropped shirt","cropped vest",
        "dress shirt","faulds","front-tie top","gathers","gym shirt",
        "high-waist skirt","virgin killer sweater","open-chest sweater",
        "hooded sweater","hooded track jacket","jersey","load bearing vest",
        "lowleg","oversized shirt","sailor shirt","tank top","unbuttoned shirt",
        "vest","wet shirt","cat lingerie","dudou","bikini top","bikini top removed",
        "gloves removed","half gloves","latex gloves","layered sleeves",
        "sleeves folded up","sleeves past fingers","sleeves past wrists",
        "sleeves pushed up","hat flower","midriff","navel","hips","thigh gap",
        "tail","thighs","thick thighs","kneepits","foot","toes","apron","belt",
        "bike shorts","bloomers","legwear","lowleg panties","miniskirt",
        "no panties","panties","pink panties","pleated skirt","side-tie panties",
        "skirt","striped panties","thong","trefoil","white panties",
        "zettai ryouiki","shorts","bottomless","panty pull","pantyshot",
        "barefoot","bare legs","ankle lace-up","butt plug","diaper","leg garter",
        "bandaged leg","anklet","demon tail","dog tail","dragon tail","fox tail",
        "horse tail","bikini bottom","buruma","capri pants","chaps","checkered skirt",
        "clothes between thighs","skirt suit","short shorts","cutoffs",
        "denim shorts","denim skirt","greaves","gym shorts","bow panties",
        "buruma pull","cat ear panties","strawberry panties",
        "pantyhose under swimsuit","black garter belt","neck garter",
        "white garter straps","black garter straps","ankle garter","covering crotch",
        "pajamas","santa","school swimsuit","school uniform","see-through",
        "babydoll","bikini","bodysuit","business suit","china dress","latex",
        "letterman jacket","living clothes","loungewear","military uniform",
        "one-piece swimsuit","swimsuit","torn clothes","underwear","uniform",
        "wedding dress","gothic","lolita fashion","western","nude","torn dress",
        "wet dress","aqua dress","black dress","blue dress","brown dress",
        "green dress","dress","gym uniform","leotard","lingerie","formal",
        "lace","clothes down","short kimono","kimono","open kimono","long dress",
        "ribbed dress","ribbon-trimmed dress","short dress","side slit",
        "taut dress","see-through dress","sleeveless dress","cake dress",
        "frilled dress","fur-trimmed dress","half-dress","highleg dress",
        "high-low skirt","hobble dress","impossible dress","lace-trimmed dress",
        "latex dress","playboy bunny leotard","police uniform","reverse bunnysuit",
        "sailor","harem outfit","highleg leotard","impossible bodysuit",
        "kindergarten uniform","front zipper swimsuit","gown","halter dress",
        "hanfu","backless outfit","baseball uniform","biker clothes","bikesuit",
        "bikini skirt","bodysuit under clothes","front-print panties","g-string",
        "highleg panties","lace-trimmed panties","micro panties","panties aside",
        "panties under pantyhose","jeans","jumpsuit","leotard aside","leotard pull",
        "leotard under clothes","lowleg pants","back-print panties","bear panties",
        "chinese clothes","corset","skirt around one leg","panties around one leg",
        "swimsuit aside","crotch plate","wet panties","crotchless panties",
        "layered skirt","waist apron","pettiskirt","tutu","layered dress",
        "off-shoulder dress","bandaid on leg","mechanical legs","leg belt",
        "leg tattoo","bound legs","panty & stocking with garterbelt",
        "thighhighs over pantyhose","socks over thighhighs","panties over pantyhose",
        "serafuku"
    ]
    
    # === 动作池  ===
    ACTIONS_POOL = [
        "arm support","armpits","arms behind back","arms crossed","arms up",
        "caramelldansen","finger gun","hand on hip",
        "hands on hips","holding","middle finger","salute",
        "shushing","spread arms","thumbs up","undressing","v","waving",
        "outstretched arms","outstretched arm","outstretched hand","reaching",
        "arm up","presenting armpit","presenting panties","arms behind head",
        "kimono lift","kimono pull","skirt lift","shared food","adjusting hair",
        "adjusting legwear","adjusting panties","arm grab","arm held back",
        "armpit peek","arms at sides","beckoning",
        "belly grab","bikini pull","skirt pull",
        "carrying over shoulder","carrying under arm","paw pose","claw pose",
        "clothes lift","clothes pull","bunching hair","convenient arm",
        "convenient head","convenient leg","crossed arms","dress lift",
        "dress removed","dual wielding","palm","feeding","fingering through clothes",
        "flapping","grabbing","hair flip",
        "hair tucking","hair twirling","hand between legs","hand in hair",
        "hand in panties",
        "hand on own knee","hand on own stomach","hand to own mouth","heart hands",
        "holding arrow","holding condom","holding panties",
        "holding strap","holding syringe","holding underwear","holding whip",
        "index finger raised","lifted by self",
        "ok sign","rubbing eyes","shading eyes","sheet grab",
        "shoujo kitou-chuu","talking on phone","through clothes","tying","yawning",
        "drying hair","v over eye","tying hair",
        "mimikaki","holding eyewear","hand on ear","adjusting eyewear",
        "hand on own head","hand on own forehead","hands on own face",
        "hand on own cheek","hand on headwear","hand on own chest","hand on own shoulder","hand on own ass",
        "hands on ass","hands on own knees","hands on feet",
        "hand in pocket","hands in pockets","air quotes","bunny pose","carry me",
        "clenched hands","cupping hands","double v","fidgeting","finger counting",
        "finger frame","fist in hand","hand glasses","own hands clasped",
        "heart arms","horns pose",
        "palm-fist greeting","palm-fist tap",
        "shadow puppet","tsuki ni kawatte oshioki yo","steepled fingers","akanbe",
        "pinky out","pointing","pointing at self",
        "pointing at viewer","pointing down","pointing forward","pointing up",
        "kamina pose","saturday night fever","thumbs down","\\n/","crossed fingers",
        "fox shadow puppet","finger heart","inward v","shaka sign",
        "two-finger salute","\\m/","middle w","\\||/",
        "open hand","ohikaenasutte","spread fingers","straight-arm salute",
        "vulcan salute","clenched hand","fig sign","power fist","raised fist",
        "stroking own chin",
        "hat tip","v over mouth","w","air guitar","curtsey",
        "heart tail","kuji-in","shrugging","toe-point",
        "victory pose","orchid fingers","holding flower","smelling flower",
        "dress tug","open dress","dress pull","all fours","arched back",
        "bent over","crossed legs","fetal position","fighting stance",
        "hugging own legs","indian style","kneeling","leaning forward","leg lift",
        "legs up","lying","on stomach","princess carry","seiza","sitting",
        "spread legs","squatting","wariza","yokozuwari",
        "zombie pose","humpbacked","head back","bowing","leaning",
        "leaning back","leaning to the side","on back","on side","reclining",
        "the pose","head tilt",
        "head down","one knee","butterfly sitting","figure four sitting",
        "lotus position","upright straddle",
        "standing","legs apart","standing on one leg","balancing","crawling",
        "jumping","running","walking","wallwalking","prostration","chest stand",
        "cowering","crucifixion","faceplant","battoujutsu stance","full scorpion",
        "stretching","superhero landing","handstand","headstand","yoga",
        "scorpion pose","slouching","twisted torso","crossed ankles","folded",
        "leg up","knees to chest","legs over head","outstretched leg","split",
        "standing split","watson cross",
        "hand on own neck",
    ]
    
    # === 户外场景池 ===
    OUTDOORS_POOL = [
        "airfield","alley","amusement park","aqueduct","bamboo forest","beach",
        "bridge","canyon","carousel","cave","city","cliff","canal","crosswalk",
        "dam","desert","dirt road","dock","drydock","ferris wheel","field",
        "floating city","floating island","forest","flower field","fountain",
        "garden","geyser","graveyard","harbor","hill","highway","island",
        "jetty","jungle","lake","market","market stall","meadow","mountain",
        "nature","oasis","ocean","ocean bottom","park","parking lot","paper lantern",
        "path","phone booth","pier","plain","playground","pond","poolside",
        "railroad crossing","railroad tracks","rice paddy","river","road",
        "roller coaster","runway","running track","rural","savannah","shore",
        "sidewalk","soccer field","stone walkway","stream","street","trench",
        "town","tunnel","village","volcano","water","waterfall","waterpark",
        "wasteland","well","wetland","wooden bridge","rope bridge","zoo",
        "airport","control tower","hangar","apartment","aquarium","arcade",
        "bar","izakaya","tavern","barn","space elevator","military base",
        "mosque","museum","art gallery","nightclub","observatory","onsen",
        "pagoda","planetarium","prison","school","skating rink","shack",
        "shrine","shop","bakery","bookstore","convenience store","skyscrapers",
        "neon lights","cityscape","fences","building"
    ]
    
    # === 室内场景池  ===
    INDOORS_POOL = [
        "bathroom","bathtub","toilet stall","shower","bedroom","hotel room",
        "messy room","otaku room","cafeteria","changing room","classroom",
        "clubroom","conservatory","courtroom","dining room","dressing room",
        "dungeon","prison cell","fitting room","gym","locker room",
        "gym storeroom","infirmary","kitchen","laboratory","library",
        "living room","office","cubicle","stage","staff room","storage room",
        "armory","closet","workshop"
    ]
    
    # ==================== 天气模块 - 合并为统一随机池 (重构) ====================
    # 原6个子模块合并为一个，去除重复项（cloudy只保留一次）
    WEATHER_TIME_POOL = [
        # === 时间 (Time) ===
        "day", "night", "dusk", "twilight", "morning", "afternoon", "evening",
        
        # === 天体 (Celestial) ===
        "sun", "moon", "full moon", "blue moon", "stars", "shooting star",
        
        # === 天空状态 (Sky State) - 去除了重复的 cloudy ===
        "sky", "night sky", "beautiful detailed sky", 
        "sunburst background", "skyline", "starry sky",
        
        # === 天气条件 (Weather Condition) - 修复了 sunny 的空格问题，去除了重复的 cloudy ===
        "raining", "snowing", "sunny", "foggy",
        
        # === 季节 (Seasons) ===
        "in spring", "in summer", "in autumn", "in winter",
        
        # === 特殊效果 (Special) ===
        "moonlight", "sunset"
    ]
    # ==================== 特效模块 ====================
    EFFECTS_POOL = [
    # === 艺术风格/媒介 ===
    "abstract", "acrylic paint (medium)", "airbrush (medium)", "alphonse mucha", 
    "amigurumi (medium)", "art deco", "art nouveau", "ballpoint pen (medium)", 
    "book cover (medium)", "brush (medium)", "brushpen (medium)", 
    "calligraphy brush (medium)", "calligraphy pen (medium)", "canvas (medium)", 
    "chalk (medium)", "charcoal (medium)", "clay (medium)", "color ink (medium)", 
    "color trace", "colored pencil (medium)", "cosplay", "coupy pencil (medium)", 
    "crayon (medium)", "cursor (medium)", "cyberpunk", "dakimakura (medium)", 
    "disc (medium)", "faux figurine", "faux traditional media", 
    "fine art parody", "flame painter", "flat color", "fourth wall", 
    "fudepen (medium)", "g-pen (medium)", "google sketchup (medium)", 
    "gouache (medium)", "graffiti (medium)", "graphite (medium)", 
    "illustrator (medium)", "impressionism", "ink (medium)", "leaf (medium)", 
    "lego (medium)", "ligne claire", "marker (medium)", "millipen (medium)", 
    "minimalism", "mousepad (medium)", "nib pen (medium)", "nihonga", 
    "oil painting (medium)", "painting (medium)", "pastel (medium)", 
    "pastel color", "pen (medium)", "photorealistic", "porcelain (medium)", 
    "print (medium)", "realistic", "retro artstyle", "style parody", "sumi-e", 
    "surreal", "swapnote (medium)", "tempera (medium)", "theatre (medium)", 
    "traditional media", "ukiyo-e", "washi tape (medium)", 
    "watercolor (medium)", "watercolor pencil (medium)", "whiteboard (medium)",
    
    # === 视觉效果/镜头效果 ===
    "chromatic aberration", "lens flare", "motion blur", "sparkle", 
    "cinematic lighting", "glowing light", "god rays", "ray tracing", 
    "reflection light", "overexposure", "backlighting", "blending", 
    "bloom", "bokeh", "caustics", "chiaroscuro", "diffraction spikes", 
    "depth of field", "dithering", "drop shadow", "emphasis lines", 
    "film grain", "foreshortening", "halftone", "image fill", 
    "motion lines", "multiple monochrome", "optical illusion", "anaglyph", 
    "stereogram", "scanlines", "silhouette", "speed lines", "vignetting", 
    "first-person view", "pov",  
    "between fingers", "between legs", "between thighs", 
    "blurry foreground", "breast conscious", "breast awe", "close-up", 
    "cowboy shot", "dutch angle", "fisheye",
    "vanishing point", "wide shot", "from above", "from behind", 
    "from below", "from outside", "from side", "atmospheric perspective", 
    "panorama", "perspective", "rotated", "sideways","dark theme",
    "green theme","orange theme","blue theme","purple theme","pink theme",
    "cyan theme",
    ]

    # ==================== 负面提示词池 ====================
    NEGATIVE_POOL = [
    # === 基础质量负面词 ===
    "low quality", "worst quality", "bad quality", "poor quality",
    "jpeg artifacts", "signature", "watermark", "text", "error",
    
    # === 人物/身体负面词 ===
    "bad anatomy", "bad hands", "missing fingers", "extra limbs",
    "mutated hands", "poorly drawn hands", "poorly drawn face",
    "mutation", "deformed", "disfigured", "ugly", "blurry",
    
    # === 画面/构图负面词 ===
    "out of frame", "cropped", "worst quality", "lowres",
    "bad proportions", "clumsy", "morning light", "flat color",
    
    # === 其他常见负面词 ===
    "duplicate", "morning", "brave", "monochrome", "gradient",
    "hand drawn", "3d", "anime", "cartoon", "illustration"
    ]
    
    def parse_text_list(self, text: str) -> List[str]:
        """解析多行文本为列表"""
        if not text.strip():
            return []
        items = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned = []
        for item in items:
            item = item.strip('"\'').strip(',')
            if item:
                cleaned.append(item)
        return cleaned
    
    def smart_select(self, pool: List[str], min_count: int, max_count: int, rng: random.Random) -> List[str]:
        """根据池子大小智能选择数量"""
        pool_size = len(pool)
        
        if pool_size <= 5:
            # 小池子：选1-2个
            count = rng.randint(1, min(2, pool_size))
        elif pool_size <= 20:
            # 中等池子：选min-max个
            count = rng.randint(min_count, min(max_count, pool_size))
        else:
            # 大池子：根据大小动态选择
            if pool_size > 100:
                count = rng.randint(3, 6)
            elif pool_size > 50:
                count = rng.randint(2, 5)
            else:
                count = rng.randint(min_count, max_count)
        
        return rng.sample(pool, min(count, pool_size))
    
    def generate_prompt(self, 
                    seed: int,
                    # === 开关参数 ===
                    enable_quality: bool,
                    character_default: bool,
                    enable_r18: bool,
                    enable_clothes: bool,
                    enable_actions: bool,
                    enable_outdoors: bool,
                    enable_indoors: bool,
                    enable_weather: bool,
                    enable_effects: bool,
                    enable_negative: bool,

                    # === 自定义输入参数 ===
                    custom_quality: str,
                    custom_character: str,
                    custom_r18: str,
                    custom_clothes: str,
                    custom_actions: str,
                    custom_outdoors: str,
                    custom_indoors: str,
                    custom_weather_time: str,
                    custom_effects: str,
                    custom_negative: str) -> Tuple[str, str]:

        
        rng = random.Random(seed)
        prompt_parts = []
        negative_prompt_parts = []
        
        # ==================== 1. 质量词模块 (新增) ====================
        if enable_quality:
            selected = self.smart_select(self.QUALITY_POOL, 2, 4, rng)
            prompt_parts.extend(selected)
        else:
            custom_list = self.parse_text_list(custom_quality)
            if custom_list:
                count = min(rng.randint(2, 4), len(custom_list))
                prompt_parts.extend(rng.sample(custom_list, count))
        
        # ==================== 2. 人物预设模块 ====================
        if character_default:
            character_tags = self.CHARACTER_DEFAULT.copy()
        else:
            character_tags = self.parse_text_list(custom_character)
        prompt_parts.extend(character_tags)
        
        # ==================== 3. R18标签模块 ====================
        if enable_r18:
            selected = self.smart_select(self.R18_POOL, 2, 4, rng)
            prompt_parts.extend(selected)
        else:
            custom_list = self.parse_text_list(custom_r18)
            if custom_list:
                count = min(rng.randint(2, 4), len(custom_list))
                prompt_parts.extend(rng.sample(custom_list, count))
        
        # ==================== 4. 服饰模块 ====================
        if enable_clothes:
            selected = self.smart_select(self.CLOTHES_POOL, 3, 5, rng)
            prompt_parts.extend(selected)
        else:
            custom_list = self.parse_text_list(custom_clothes)
            if custom_list:
                count = min(rng.randint(3, 5), len(custom_list))
                prompt_parts.extend(rng.sample(custom_list, count))
        
        # ==================== 5. 动作模块 ====================
        if enable_actions:
            selected = self.smart_select(self.ACTIONS_POOL, 2, 4, rng)
            prompt_parts.extend(selected)
        else:
            custom_list = self.parse_text_list(custom_actions)
            if custom_list:
                count = min(rng.randint(2, 4), len(custom_list))
                prompt_parts.extend(rng.sample(custom_list, count))
        
        # ==================== 6. 户外场景模块 ====================
        if enable_outdoors:
            selected = self.smart_select(self.OUTDOORS_POOL, 1, 2, rng)
            prompt_parts.extend(selected)
        else:
            custom_list = self.parse_text_list(custom_outdoors)
            if custom_list:
                count = min(rng.randint(1, 2), len(custom_list))
                prompt_parts.extend(rng.sample(custom_list, count))
        
        # ==================== 7. 室内场景模块 ====================
        if enable_indoors:
            selected = self.smart_select(self.INDOORS_POOL, 1, 2, rng)
            prompt_parts.extend(selected)
        else:
            custom_list = self.parse_text_list(custom_indoors)
            if custom_list:
                count = min(rng.randint(1, 2), len(custom_list))
                prompt_parts.extend(rng.sample(custom_list, count))
        # ==================== 8. 天气模块 (重构 - 统一随机池) ====================
        if enable_weather:
            # 从统一的 WEATHER_TIME_POOL 中随机选择 3-5 个标签
            selected = self.smart_select(self.WEATHER_TIME_POOL, 3, 5, rng)
            prompt_parts.extend(selected)
        else:
            # 使用自定义输入
            custom_list = self.parse_text_list(custom_weather_time)
            if custom_list:
                count = min(rng.randint(3, 5), len(custom_list))
                prompt_parts.extend(rng.sample(custom_list, count))

        # ==================== Effects模块处理逻辑 ====================
        if enable_effects:
            # 从132个标签中随机选择4-6个（大池子）
            selected = self.smart_select(self.EFFECTS_POOL, 4, 6, rng)
            prompt_parts.extend(selected)
        else:
            # 使用自定义输入
            custom_list = self.parse_text_list(custom_effects)
            if custom_list:
                count = min(rng.randint(4, 6), len(custom_list))
                prompt_parts.extend(rng.sample(custom_list, count))

        # ==================== 负面提示词模块处理逻辑 ====================
        if enable_negative:
            selected = self.smart_select(self.NEGATIVE_POOL, 4, 6, rng)
            negative_prompt_parts.extend(selected)
        else:
            custom_list = self.parse_text_list(custom_negative)
            if custom_list:
                count = min(rng.randint(4, 6), len(custom_list))
                negative_prompt_parts.extend(rng.sample(custom_list, count))

        
        # ==================== 组合最终提示词 ====================
        final_prompt = ", ".join(prompt_parts)
        final_negative_prompt = ", ".join(negative_prompt_parts)
        
        return (final_prompt, final_negative_prompt,)


# ComfyUI 注册信息
NODE_CLASS_MAPPINGS = {
    "DanbooruPromptGenerator": DanbooruPromptGenerator,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DanbooruPromptGenerator": "🎨 Danbooru Prompt Generator",
}
