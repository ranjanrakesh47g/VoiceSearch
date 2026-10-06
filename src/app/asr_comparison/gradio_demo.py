import os
import gradio as gr
from dotenv import load_dotenv
from src.app.asr_comparison.compare_utils import MODELS, compare


def build_demo():
    def run(filepath):
        if not filepath:
            gr.Warning("Recording is still uploading. Wait a moment and try again.")
            return tuple(gr.skip() for _ in MODELS)
        results = compare(filepath)
        return tuple(
            gr.update(value=results[name]["text"], label=f"{name} ({results[name]['latency']})")
            for name in MODELS
        )

    def ui(sources):
        audio = gr.Audio(sources=sources, type="filepath", format="wav")
        clear = gr.ClearButton()
        outputs = [gr.Textbox(label=name, lines=3) for name in MODELS]
        clear.add([audio, *outputs])
        event = audio.stop_recording if sources == "microphone" else audio.upload
        event(run, inputs=audio, outputs=outputs)

    with gr.Blocks() as demo:
        with gr.Tabs():
            with gr.Tab("Transcribe Microphone"):
                ui("microphone")
            with gr.Tab("Transcribe Audio File"):
                ui("upload")
    return demo


def main():
    load_dotenv()
    demo = build_demo()
    if os.getenv("COLAB_RELEASE_TAG"):
        demo.launch(share=True, debug=True)
    else:
        demo.launch(share=True, server_name="0.0.0.0", server_port=7681)


if __name__ == "__main__":
    main()
