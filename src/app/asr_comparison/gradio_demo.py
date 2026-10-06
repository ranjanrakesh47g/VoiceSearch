import os
import gradio as gr
from dotenv import load_dotenv
from src.app.asr_comparison.compare_utils import MODELS, compare, log_comparison


def skip_run():
    return tuple(gr.skip() for _ in range(len(MODELS) * 2 + 1))


def log_unchecked(audio_path, results):
    for item in results.values():
        item["is_best"] = False
    log_comparison(audio_path, results)
    return {"audio": audio_path, "transcriptions": results}


def show_transcriptions(results):
    return tuple(gr.update(value=results[name]["text"], label=f"{name} ({results[name]['latency']})") for name in MODELS)


def clear_checks():
    return tuple(gr.update(value=False) for _ in MODELS)


def reset_labels():
    return tuple(gr.update(label=name) for name in MODELS)


def selected_models(checks):
    return {name for name, checked in zip(MODELS, checks) if checked}


def selection_changed(state, chosen):
    return any(item["is_best"] != (name in chosen) for name, item in state["transcriptions"].items())


def apply_selection(state, chosen):
    for name, item in state["transcriptions"].items():
        item["is_best"] = name in chosen
    log_comparison(state["audio"], state["transcriptions"])
    return state


def model_row(name):
    with gr.Row():
        output = gr.Textbox(label=name, lines=3, scale=4)
        check = gr.Checkbox(label="Is best transcription?", elem_classes="best-check")
    return output, check


def build_demo():
    def run(filepath):
        if not filepath:
            gr.Warning("Recording is still uploading. Wait a moment and try again.")
            return skip_run()
        results, audio_path = compare(filepath, log=False)
        return (*show_transcriptions(results), log_unchecked(audio_path, results), *clear_checks())

    def save_feedback(filepath, state, *checks):
        chosen = selected_models(checks)
        if filepath and state and selection_changed(state, chosen):
            return apply_selection(state, chosen)
        if not filepath and any(checks):
            gr.Warning("Transcribe audio first.")
        return gr.skip()

    def ui(sources):
        audio = gr.Audio(sources=sources, type="filepath", format="wav")
        clear = gr.ClearButton()
        outputs, checks = [], []
        for name in MODELS:
            output, check = model_row(name)
            outputs.append(output)
            checks.append(check)
        state = gr.State(None)
        clear.add([audio, *outputs, *checks])
        clear.click(reset_labels, outputs=outputs)
        event = audio.stop_recording if sources == "microphone" else audio.upload
        event(run, inputs=audio, outputs=[*outputs, state, *checks])
        for check in checks:
            check.change(save_feedback, inputs=[audio, state, *checks], outputs=state)

    with gr.Blocks(css=".best-check label{display:flex;flex-direction:column-reverse;align-items:flex-start}") as demo:
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
