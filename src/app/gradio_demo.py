import gradio as gr

from src.app.pipeline import VoiceSearchPipeline


def build_demo(pipeline=None):
    pipeline = pipeline or VoiceSearchPipeline()

    def run_voice_search(filepath):
        if not filepath:
            gr.Warning("Recording is still uploading. Wait a moment and try again.")
            return tuple(gr.skip() for _ in range(5))
        voice_search = pipeline.run(filepath)

        def component(value, name, latency):
            return gr.update(value=value, label=name if not latency else f"{name} ({latency})")

        return (
            component(voice_search.user_query_text, "Transcription", voice_search.latency_transcription),
            component(voice_search.intent, "Intent", voice_search.latency_intent_detection),
            component(voice_search.searchable_query, "Searchable query", voice_search.latency_query_extraction),
            component(voice_search.search_results, "Search results", voice_search.latency_search),
            voice_search.latency_overall,
        )

    def voice_search_ui(sources):
        audio = gr.Audio(sources=sources, type="filepath", format="wav")
        clear = gr.ClearButton()
        outputs = [
            gr.Textbox(label="Transcription", lines=3),
            gr.Textbox(label="Intent"),
            gr.Textbox(label="Searchable query"),
            gr.JSON(label="Search results"),
            gr.Textbox(label="Overall latency"),
        ]
        clear.add([audio, *outputs])
        if sources == "microphone":
            audio.stop_recording(run_voice_search, inputs=audio, outputs=outputs)
        else:
            audio.upload(run_voice_search, inputs=audio, outputs=outputs)

    with gr.Blocks() as demo:
        with gr.Tabs():
            with gr.Tab("Transcribe Microphone"):
                voice_search_ui("microphone")
            with gr.Tab("Transcribe Audio File"):
                voice_search_ui("upload")

    return demo
