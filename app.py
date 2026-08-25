"""Interactive myopia lesson, deployed as a native Gradio application."""

from __future__ import annotations

import os

import gradio as gr


# These fixed values represent one myopic eye.  At about 25 cm, its image
# point reaches the retina; farther objects focus in front of the retina.
MYOPIC_EYE_POWER_D = 51.6
RETINA_DISTANCE_MM = 21.0
NEAR_LIMIT_M = 0.10
FAR_LIMIT_M = 20.0


def focus_distance_mm(object_distance_m: float, eye_power_d: float) -> float:
    """Thin-lens image distance: 1/v = P - 1/u, returned in millimetres."""
    return 1000.0 / (eye_power_d - 1.0 / object_distance_m)


def metric(label: str, value: str) -> str:
    return f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>'


def ray_diagram(object_distance_m: float, eye_power_d: float, axial_length_mm: float) -> str:
    focal_mm = focus_distance_mm(object_distance_m, eye_power_d)
    lens_x, zero_y, scale = 640, 360, 20
    retina_x = lens_x + axial_length_mm * scale
    focus_x = lens_x + focal_mm * scale
    centre_x = (lens_x + retina_x) / 2
    eye_radius_x = (retina_x - lens_x) / 2 + 50
    # The physical distances are compressed for the screen.  Near
    # objects sit visibly closer to the eye; distant objects move left.
    object_x = 460 - ((object_distance_m - NEAR_LIMIT_M) / (FAR_LIMIT_M - NEAR_LIMIT_M)) * 330
    colours = ["#ff9200", "#40c6b7", "#0879dd", "#dce3f2", "#7950f2"]
    heights = [-112, -50, 0, 50, 112]

    ray_lines = []
    for height, colour in zip(heights, colours):
        lens_y = zero_y + height
        end_x = max(retina_x + 38, focus_x + 34)
        end_y = zero_y - (height / focal_mm / scale) * (end_x - focus_x)
        ray_lines.extend(
            [
                f'<line class="pre" stroke="{colour}" x1="{object_x}" y1="250" x2="{lens_x}" y2="{lens_y}"/>',
                f'<line class="post" stroke="{colour}" x1="{lens_x}" y1="{lens_y}" x2="{focus_x}" y2="{zero_y}"/>',
                f'<line class="after" stroke="{colour}" x1="{focus_x}" y1="{zero_y}" x2="{end_x}" y2="{end_y}"/>',
            ]
        )

    return f"""
    <div class="diagram">
      <svg viewBox="0 0 1320 630" role="img" aria-label="Ray diagram of a myopic eye">
        <line class="grid" x1="80" x2="1280" y1="120" y2="120"/><line class="grid" x1="80" x2="1280" y1="240" y2="240"/>
        <line class="grid" x1="80" x2="1280" y1="360" y2="360"/><line class="grid" x1="80" x2="1280" y1="480" y2="480"/><line class="grid" x1="80" x2="1280" y1="570" y2="570"/>
        <text class="axis-text" x="82" y="610">Distance through the eye (mm)</text>
        <text class="axis-text" x="15" y="365">0</text><text class="axis-text" x="15" y="245">5</text><text class="axis-text" x="10" y="125">10</text>
        <ellipse class="eye" cx="{centre_x}" cy="360" rx="{eye_radius_x}" ry="235"/>
        <line class="retina" x1="{retina_x}" x2="{retina_x}" y1="210" y2="510"/>
        <line class="lens" x1="640" x2="640" y1="240" y2="480"/>
        <line class="object" x1="{object_x}" x2="{object_x}" y1="360" y2="250"/>
        <text class="label" x="{object_x - 25}" y="230">Object</text><text class="label" x="606" y="211">Eye lens</text>
        <text class="label" x="{retina_x - 25}" y="182">Retina</text><text class="small-label" x="{focus_x - 28}" y="544">Focus</text>
        {''.join(ray_lines)}
        <line class="focus-mark" x1="{focus_x - 8}" y1="{zero_y - 8}" x2="{focus_x + 8}" y2="{zero_y + 8}"/>
        <line class="focus-mark" x1="{focus_x - 8}" y1="{zero_y + 8}" x2="{focus_x + 8}" y2="{zero_y - 8}"/>
      </svg>
    </div>
    """


def perceived_vision(offset_mm: float) -> str:
    """A qualitative retinal-image preview based on defocus from the retina."""
    blur_px = min(9.0, max(0.0, abs(offset_mm) * 3.8))
    if abs(offset_mm) <= 0.30:
        state = "CLEAR"
        explanation = "The rays meet on the retina, so this nearby object can be seen clearly."
        extra_class = "clear"
    elif offset_mm < 0:
        state = "BLURRY"
        explanation = "The rays meet before the retina and have spread out again by the time they reach it."
        extra_class = "blurry"
    else:
        state = "BLURRY"
        explanation = "The rays would meet behind the retina, so the retinal image is not sharp."
        extra_class = "blurry"
    return f'''
    <section class="vision-panel {extra_class}">
      <div><div class="vision-label">Perceived vision</div><div class="vision-state">{state}</div><p>{explanation}</p></div>
      <div class="vision-target" style="filter:blur({blur_px:.1f}px)">E</div>
    </section>'''


def update(object_distance: float):
    focal_mm = focus_distance_mm(object_distance, MYOPIC_EYE_POWER_D)
    offset = focal_mm - RETINA_DISTANCE_MM
    if offset < -0.15:
        banner = '<div class="notice">Focus forms IN FRONT of the retina. The retina is beyond the natural focal point, so the image on the retina is blurred.</div>'
    elif abs(offset) <= 0.15:
        banner = '<div class="notice good">Focus reaches the retina. The rays meet on the retinal surface, producing the clearest image in this model.</div>'
    else:
        banner = '<div class="notice">Focus falls BEHIND the retina. The eye is under-powered for this retinal position, so the image is not sharply focused.</div>'
    return (
        metric("Object distance", f"{object_distance:.1f} m"),
        metric("Focal point", f"{focal_mm:.1f} mm"),
        metric("Fixed retina position", f"{RETINA_DISTANCE_MM:.1f} mm"),
        banner,
        ray_diagram(object_distance, MYOPIC_EYE_POWER_D, RETINA_DISTANCE_MM),
        perceived_vision(offset),
    )


CSS = """
html, body { width:100%; max-width:100%; overflow-x:hidden; }
body, .gradio-container { background:#0d1016 !important; color:#f7f8fb !important; font-family:Arial,Helvetica,sans-serif !important; }
.gradio-container { width:100% !important; max-width:none !important; padding:0 !important; overflow-x:hidden !important; }
footer { display:none !important; }
.shell { width:100% !important; max-width:100% !important; min-height:900px; align-items:stretch !important; gap:0 !important; }
.sidebar { background:#262731; border-right:1px solid #353842; padding:52px 25px !important; min-width:260px !important; }
.sidebar h2 { margin:0 0 34px; font-size:23px; }
.sidebar .block { margin-bottom:28px !important; }
.sidebar label, .sidebar .wrap { color:#f6f7fb !important; font-weight:700 !important; }
.sidebar input[type=range] { accent-color:#ff575f; }
.sidebar .gr-button { background:#343844 !important; border-color:#4a5060 !important; color:#dfe7f3 !important; }
.content { min-width:0 !important; padding:70px clamp(28px,6vw,100px) 50px !important; overflow:hidden; }
.title h1 { font-size:clamp(32px,3.3vw,53px); letter-spacing:-2px; margin:0 0 17px; font-weight:800; }
.subtitle { color:#a9afbb; font-size:17px; margin:0 0 32px; }
.metric-row { gap:20px !important; margin-bottom:30px; }
.metric { min-height:94px; }.metric-label { font-size:16px; font-weight:700; margin-bottom:13px; }.metric-value { font-size:40px; letter-spacing:-1.5px; }
.notice { padding:24px 20px; border-radius:10px; background:#17314b; color:#3598ff; font-size:17px; line-height:1.4; font-weight:700; margin-bottom:17px; }
.notice.good { background:#153b34; color:#63e6be; }
.diagram { width:100%; min-width:0; aspect-ratio:1320 / 630; max-height:635px; overflow:hidden; }.diagram svg { display:block; width:100%; min-width:0; height:100%; overflow:visible; }
.grid { stroke:#303540; stroke-width:1; }.axis-text { fill:#aeb7c5; font-size:14px; }.label { fill:#fbfcff; font-size:15px; font-weight:700; }.small-label { fill:#ffc5cb; font-size:14px; }
.eye { fill:none; stroke:#79bfff; stroke-width:2.4; }.retina { stroke:#0877d8; stroke-width:7; }.lens { stroke:#ffa9ae; stroke-width:5; }.object { stroke:#ff424d; stroke-width:7; }
.pre { fill:none; stroke-width:2.6; stroke-dasharray:4 5; }.post { fill:none; stroke-width:3.8; }.after { fill:none; stroke-width:2.2; stroke-dasharray:8 8; opacity:.9; }.focus-mark { stroke:#f1f4fa; stroke-width:5; }
.caption { color:#939baa; font-size:14px; margin:-7px 0 30px; }.students { font-size:29px; margin:0 0 20px; }
.vision-panel { display:flex; justify-content:space-between; align-items:center; gap:18px; background:#151922; border:1px solid #2a2f3b; border-radius:12px; margin:4px 0 28px; padding:18px 22px; }.vision-label { color:#c9d0dc; font-size:15px; font-weight:700; }.vision-state { font-size:28px; font-weight:800; letter-spacing:.04em; color:#ff8b92; margin:4px 0; }.vision-panel.clear .vision-state { color:#63e6be; }.vision-panel p { margin:0; max-width:660px; color:#b5bdca; line-height:1.45; }.vision-target { width:96px; height:96px; display:grid; place-items:center; border-radius:9px; background:#f2f5f9; color:#0f1520; font-size:76px; font-family:Arial,sans-serif; font-weight:800; transition:filter .16s ease; }
.cards { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }.card { background:#151922; border:1px solid #2a2f3b; border-radius:12px; padding:19px; min-height:136px; }.card h3 { font-size:17px; margin:0 0 9px; }.card p { color:#c2c8d2; margin:0; line-height:1.52; }
@media(max-width:850px) { .shell { display:flex !important; flex-direction:column !important; flex-wrap:nowrap !important; }.sidebar { min-width:0 !important; width:100% !important; max-width:100% !important; flex:0 0 auto !important; padding:28px 22px !important; }.content { width:100% !important; max-width:100% !important; min-width:0 !important; padding:35px 18px !important; }.metric-row { flex-direction:column !important; }.cards { grid-template-columns:1fr; }.vision-panel { align-items:flex-start; }.vision-target { width:76px; height:76px; font-size:58px; flex:0 0 auto; }.diagram { width:100%; height:auto; max-height:none; aspect-ratio:1320 / 630; border-radius:10px; background:#0d1016; }.diagram .label { font-size:28px; }.diagram .small-label { font-size:26px; }.diagram .axis-text { font-size:22px; } }
"""


initial = update(0.25)

with gr.Blocks(css=CSS, title="Myopia Interactive", theme=gr.themes.Base()) as demo:
    with gr.Row(elem_classes="shell"):
        with gr.Column(scale=1, min_width=260, elem_classes="sidebar"):
            gr.HTML("<h2>Controls</h2>")
            object_distance = gr.Slider(NEAR_LIMIT_M, FAR_LIMIT_M, value=0.25, step=0.05, label="Object distance (m)")
            gr.HTML('<p class="side-note">This eye is fixed as myopic. Move only the object: nearby objects become clearer; distant ones blur.</p><p class="side-note"><b>Fixed eye power:</b> 51.6 D<br><b>Fixed retina distance:</b> 21.0 mm</p>')
            reset = gr.Button("Reset object to clear distance")

        with gr.Column(scale=5, elem_classes="content"):
            gr.HTML('<div class="title"><h1>👁️ Myopia: Why distant objects look blurred</h1><p class="subtitle">Interactive Class 10 Physics visualization — ray focusing in a myopic eye</p></div>')
            with gr.Row(elem_classes="metric-row"):
                distance_metric = gr.HTML(initial[0])
                focus_metric = gr.HTML(initial[1])
                retina_metric = gr.HTML(initial[2])
            banner = gr.HTML(initial[3])
            diagram = gr.HTML(initial[4])
            vision = gr.HTML(initial[5])
            gr.HTML('<p class="caption">The myopic eye stays fixed. Only object distance changes the incoming rays and the refracted image position.</p>')
            gr.HTML('<h2 class="students">What should students notice?</h2><section class="cards"><div class="card"><h3>1. A distant object</h3><p>Light from a far-away object reaches the eye almost parallel. The eye lens bends these rays inward.</p></div><div class="card"><h3>2. In a myopic eye</h3><p>If the eye is too powerful or the eyeball is too long, the rays meet before reaching the retina.</p></div><div class="card"><h3>3. Why the image blurs</h3><p>After crossing at the focus, rays spread out again. The retina receives a spread-out image.</p></div></section>')

    outputs = [distance_metric, focus_metric, retina_metric, banner, diagram, vision]
    object_distance.input(update, inputs=object_distance, outputs=outputs, queue=False, show_progress="hidden")
    reset.click(
        lambda: 0.25,
        outputs=object_distance,
        queue=False,
    ).then(update, inputs=object_distance, outputs=outputs, queue=False, show_progress="hidden")


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", "7860")),
    )
