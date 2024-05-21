import gradio as gr

from plugins.t2i.sanp_plugin_random_artists.utils import gen_script, generate_img
from utils.utils import open_folder, return_random


def plugin():
    with gr.Tab("画风生成"):
        gr.Markdown(
            "> 单画师文件在 ./plugins/t2i/sanp_plugin_random_artists/artists.json"
        )
        with gr.Row():
            with gr.Column(scale=4):
                prompt = gr.Textbox("", label="固定提示词", lines=3)
                negative = gr.Textbox(
                    "nsfw, lowres, {bad}, error, fewer, extra, missing, worst quality, jpeg artifacts, bad quality, watermark, unfinished, displeasing, chromatic aberration, signature, extra digits, artistic error, username, scan, [abstract],",
                    label="负面提示词",
                    lines=2,
                )
            with gr.Column(scale=1):
                folder = gr.Textbox("./output/i2i", visible=False)
                stand_alone = gr.Button("生成独立脚本")
                open_folder_ = gr.Button("打开保存目录")
                open_folder_.click(open_folder, inputs=folder)
                generate = gr.Button("开始生成")
                stop = gr.Button("停止生成")
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    path = gr.Textbox("./files/prompt", label="提示词文件路径", scale=7)
                    random_from_path = gr.Checkbox(
                        True, label="从路径抽取提示词", scale=2
                    )
                with gr.Row():
                    scale = gr.Slider(0, 10, 5, step=0.1, label="提示词相关性")
                    steps = gr.Slider(0, 50, 28, step=1, label="采样步数")
                resolution = gr.Dropdown(
                    ["随机", "832x1216", "1216x832", "1024x1024"],
                    value="随机",
                    label="分辨率",
                )
                with gr.Row():
                    sampler = gr.Dropdown(
                        [
                            "随机",
                            "k_euler",
                            "k_euler_ancestral",
                            "k_dpmpp_2s_ancestral",
                            "k_dpmpp_2m",
                            "k_dpmpp_sde",
                            "ddim_v3",
                        ],
                        value="k_euler",
                        label="采样器",
                    )
                    noise_schedule = gr.Dropdown(
                        ["随机", "native", "karras", "exponential", "polyexponential"],
                        value="native",
                        label="噪声计划表",
                    )
                with gr.Row():
                    sm = gr.Dropdown(["随机", True, False], value=False, label="sm")
                    sm_dyn = gr.Dropdown(
                        ["随机", True, False], value=False, label="sm_dyn"
                    )
                with gr.Row():
                    seed = gr.Textbox("-1", label="随机种子", scale=7)
                    random_button = gr.Button(value="♻️", size="sm", scale=1)
                    random_button.click(return_random, inputs=None, outputs=seed)
                with gr.Row():
                    random_weight = gr.Checkbox(True, label="随机权重")
                    year_2023 = gr.Checkbox(True, label="year 2023")
                    artist_pref = gr.Checkbox(True, label="artist: 前缀")
                with gr.Row():
                    lower_weight = gr.Checkbox(True, label="使用 []")
                    higher_weight = gr.Checkbox(True, label="使用 {}")
                with gr.Row():
                    max_artists = gr.Slider(
                        1, 20, 12, step=1, label="最大抽取的画师数量"
                    )
                    max_weights = gr.Slider(1, 10, 3, step=1, label="最大添加权重次数")
                with gr.Row():
                    min_artists = gr.Slider(
                        1, 20, 3, step=1, label="最小抽取的画师数量"
                    )
                    min_weights = gr.Slider(1, 10, 0, step=1, label="最小添加权重次数")
            with gr.Column():
                otp_artists = gr.Textbox(label="本次随机的画风")
                image = gr.Image()
        cancle = image.change(
            generate_img,
            inputs=[
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
            ],
            outputs=[image, otp_artists],
            show_progress=False,
        )
        generate.click(
            generate_img,
            inputs=[
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
            ],
            outputs=[image, otp_artists],
        )
        stand_alone.click(
            gen_script,
            inputs=[
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
            ],
            outputs=None,
        )
        stop.click(None, None, None, cancels=[cancle])
