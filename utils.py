import random

from utils.env import env

if "nai-diffusion-4" not in env.model:
    from utils.jsondata import json_for_t2i
else:
    from utils.jsondata import json_for_t2i_v4 as json_for_t2i
from utils.prepare import logger
from utils.utils import (
    NOISE_SCHEDULE,
    SAMPLER,
    file_namel2pathl,
    file_path2list,
    format_str,
    generate_image,
    generate_random_str,
    read_json,
    read_txt,
    save_image,
    sleep_for_cool,
)


def random_artists(
    prompt,
    position,
    random_weight,
    year_2022,
    year_2023,
    artist_pref,
    lower_weight,
    higher_weight,
    max_artists,
    max_weights,
    min_artists,
    min_weights,
):
    medium = 0.5
    artists: dict = read_json("./plugins/t2i/sanp_plugin_random_artists/artists.json")
    chose_artists = ""
    for _ in range(random.randint(min_artists, max_artists)):
        while (artist := artists[random.choice(list(artists.keys()))]) in chose_artists:
            pass
        if artist_pref:
            artist = f"artist:{artist}"

        if random_weight:
            num = random.randint(min_weights, max_weights)
            if lower_weight and higher_weight:
                symbol = random.choice([["[", "]"], ["{", "}"]])
                artist = symbol[0] * num + artist + symbol[1] * num
            elif lower_weight:
                if random.random() < medium:
                    artist = "[" * num + artist + "]" * num
            elif higher_weight:
                if random.random() < medium:
                    artist = "{" * num + artist + "}" * num
            else:
                pass

            chose_artists += f"{artist},"

    if year_2022:
        chose_artists += random.choice(["year 2022,", ""])

    if "year 2022" in chose_artists:
        pass
    else:
        if year_2023:
            chose_artists += random.choice(["year 2023,", ""])

    if position == "最后面":
        return (
            f"{format_str(str(prompt))}, {format_str(str(chose_artists))}",
            format_str(str(chose_artists)),
        )
    elif position == "最前面":
        return (
            f"{format_str(str(chose_artists))}, {format_str(str(prompt))}",
            format_str(str(chose_artists)),
        )


def generate_img(
    path,
    random_from_path,
    prompt,
    negative,
    position,
    scale,
    rescale,
    steps,
    resolution,
    sampler,
    noise_schedule,
    sm,
    sm_dyn,
    variety,
    decrisp,
    seed,
    random_weight,
    year_2022,
    year_2023,
    artist_pref,
    lower_weight,
    higher_weight,
    max_artists,
    max_weights,
    min_artists,
    min_weights,
):
    if random_from_path:
        prompt_list = file_namel2pathl(file_path2list(path), path)
        prompt = random.choice(prompt_list)
        if str(prompt).endswith(".txt"):
            prompt = read_txt(prompt)
        else:
            prompt = ""
    prompt, artists = random_artists(
        prompt,
        position,
        random_weight,
        year_2022,
        year_2023,
        artist_pref,
        lower_weight,
        higher_weight,
        max_artists,
        max_weights,
        min_artists,
        min_weights,
    )
    json_for_t2i["input"] = prompt

    if resolution == "随机":
        resolution = random.choice(["832x1216", "1216x832", "1024x1024"])
    json_for_t2i["parameters"]["width"] = int(resolution.split("x")[0])
    json_for_t2i["parameters"]["height"] = int(resolution.split("x")[1])

    json_for_t2i["parameters"]["scale"] = scale
    json_for_t2i["parameters"]["cfg_rescale"] = rescale

    if sampler == "随机":
        sampler = random.choice(SAMPLER)
    json_for_t2i["parameters"]["sampler"] = sampler

    json_for_t2i["parameters"]["steps"] = steps

    if "nai-diffusion-4" not in env.model:
        if sm == "随机":
            sm = random.choice([True, False]) if sampler != "ddim_v3" else False
        if sm and sampler != "ddim_v3":
            if sm_dyn == "随机":
                sm_dyn = random.choice([True, False])
        else:
            sm_dyn = False
        json_for_t2i["parameters"]["sm"] = sm
        json_for_t2i["parameters"]["sm_dyn"] = sm_dyn

    if variety == "随机":
        variety = random.choice([None, 19])
    elif variety is True:
        variety = 19
    else:
        variety = None
    json_for_t2i["parameters"]["skip_cfg_above_sigma"] = variety

    if decrisp == "随机":
        decrisp = random.choice([True, False])
    json_for_t2i["parameters"]["dynamic_thresholding"] = decrisp

    if noise_schedule == "随机":
        noise_schedule = random.choice(NOISE_SCHEDULE)
    if sampler != "ddim_v3":
        json_for_t2i["parameters"]["noise_schedule"] = noise_schedule

    if seed == "-1":
        seed_ = random.randint(1000000000, 9999999999)
    else:
        seed_ = int(seed)
    json_for_t2i["parameters"]["seed"] = seed_

    json_for_t2i["parameters"]["negative_prompt"] = negative

    if "nai-diffusion-4" in env.model:
        json_for_t2i["parameters"]["use_coords"] = False
        json_for_t2i["parameters"]["v4_prompt"]["caption"]["base_caption"] = prompt
        json_for_t2i["parameters"]["v4_prompt"]["use_coords"] = False
        json_for_t2i["parameters"]["v4_negative_prompt"]["caption"][
            "base_caption"
        ] = negative

    logger.debug(json_for_t2i)

    saved_path = save_image(
        generate_image(json_for_t2i),
        "t2i",
        seed_ if seed == "-1" else generate_random_str(10),
        "None",
        "None",
    )

    sleep_for_cool(env.t2i_cool_time - 3, env.t2i_cool_time + 3)

    return saved_path, artists


def gen_script(*args):
    sm = '"随机"' if args[10] == "随机" else args[10]
    sm_dyn = '"随机"' if args[11] == "随机" else args[11]
    variety = '"随机"' if args[12] == "随机" else args[12]
    decrisp = '"随机"' if args[13] == "随机" else args[13]

    with open("stand_alone_scripts.py", "w", encoding="utf-8") as script:
        script.write(
            f"""from plugins.t2i.sanp_plugin_random_artists.utils import generate_img
from utils.env import env
from utils.prepare import logger

times = 0
_times = 0

while times + 1 <= env.times_for_scripts:
    if env.times_for_scripts == 0:
        _times += 1
    else:
        times += 1
    info = "正在生成第 " + str(_times if env.times_for_scripts == 0 else times) + " 张图片..."
    logger.info(info)
    generate_img(
        "{args[0]}",
        {args[1]},
        \"\"\"{args[2]}\"\"\",
        \"\"\"{args[3]}\"\"\",
        "{args[4]}",
        {args[5]},
        {args[6]},
        "{args[7]}",
        "{args[8]}",
        "{args[9]}",
        {sm},
        {sm_dyn},
        {variety},
        {decrisp},
        "{args[14]}",
        {args[15]},
        {args[16]},
        {args[17]},
        {args[18]},
        {args[19]},
        {args[20]},
        {args[21]},
        {args[22]},
        {args[23]},
        {args[24]},
    )
"""
        )
        logger.success("生成成功, 运行 run_stand_alone_scripts.bat 即可独立执行该操作")
