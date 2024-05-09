import random

from loguru import logger

from utils.env import env
from utils.jsondata import json_for_t2i
from utils.utils import (
    file_namel2pathl,
    file_path2list,
    format_str,
    generate_image,
    read_json,
    read_txt,
    save_image,
    sleep_for_cool,
)


def random_artists(
    prompt,
    random_weight,
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
        artist = artists[random.choice(list(artists.keys()))]
        if artist_pref:
            artist = f"artist:{artist}"

        if random_weight:
            num = random.randint(min_weights, max_weights)
            if lower_weight and higher_weight:
                symbol = random.choice([["[", "]"], ["{", "}"]])
                artist = symbol[0] * num + artist + symbol[1] * num
            elif lower_weight:
                if random.random() < medium:
                    artist = "[" * num + artist + "]"
            elif higher_weight:
                if random.random() < medium:
                    artist = "{" * num + artist + "}"
            else:
                pass

            chose_artists += f"{artist},"

    if year_2023:
        chose_artists += "year 2023"

    return f"{format_str(chose_artists)}, {format_str(prompt)}", format_str(
        chose_artists
    )


def generate_img(
    path,
    random_from_path,
    prompt,
    negative,
    scale,
    steps,
    resolution,
    sampler,
    noise_schedule,
    sm,
    sm_dyn,
    seed,
    random_weight,
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
    prompt, artists = random_artists(
        prompt,
        random_weight,
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

    if sampler == "随机":
        sampler = random.choice(
            [
                "k_euler",
                "k_euler_ancestral",
                "k_dpmpp_2s_ancestral",
                "k_dpmpp_2m",
                "k_dpmpp_sde",
                "ddim_v3",
            ]
        )
    json_for_t2i["parameters"]["sampler"] = sampler

    json_for_t2i["parameters"]["steps"] = steps

    if sm == "随机":
        sm = random.choice([True, False])
    if sm:
        if sm_dyn == "随机":
            sm_dyn = random.choice([True, False])
    else:
        sm_dyn = False
    json_for_t2i["parameters"]["sm"] = sm
    json_for_t2i["parameters"]["sm_dyn"] = sm_dyn

    if noise_schedule == "随机":
        noise_schedule = random.choice(
            ["native", "karras", "exponential", "polyexponential"]
        )
    json_for_t2i["parameters"]["noise_schedule"] = noise_schedule

    if seed == "-1":
        seed = random.randint(1000000000, 9999999999)
    else:
        seed = int(seed)
    json_for_t2i["parameters"]["seed"] = seed

    json_for_t2i["parameters"]["negative_prompt"] = negative

    logger.debug(json_for_t2i)

    saved_path = save_image(generate_image(json_for_t2i), "t2i", seed, "None", "None")

    sleep_for_cool(env.t2i_cool_time - 6, env.t2i_cool_time + 6)

    return saved_path, artists
