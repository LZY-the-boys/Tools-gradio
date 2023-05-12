import sys
import gradio as gr
import argparse
import warnings
import time
import os
import json

def save():
    pass

def evaluate(
    inputs,
    extra,
    history,
    temperature=0.1,
    top_p=0.75,
    top_k=40,
    num_beams=4,
    max_new_tokens=128,
    min_new_tokens=1,
    repetition_penalty=2.0,
    max_memory=1024,
    do_sample=False,
    prompt_type='0',
    **kwargs,
):
    history = [] if history is None else history
    return_text = [(item['input'], item['output']) for item in history]
    show_text = ''
    if len(history) == 1:
        for i in range(10):
            show_text += str(i) + " ▌"
            yield return_text +[(inputs, show_text)], history
    elif len(history) == 2: 
        for i in range(10):
            show_text += "$" + str(i) +'$'
            yield return_text +[(inputs, show_text)], history
    elif len(history) == 3:
        for i in range(10):
            show_text += "```" + str(i) + '\nprintf("hello-world")' +'```'
            yield return_text +[(inputs, show_text)], history
    else:
        yield 'EOS'
    print('[EOS]', end='\n')
    output = show_text
    history.append({
        'input': inputs,
        'output': output,
    })           
    return_text += [(inputs, show_text)]
    yield return_text, history


with gr.Blocks() as demo:
    fn = evaluate
    title = gr.Markdown(
        "<h1 style='text-align: center; margin-bottom: 1rem'>"
        + "Chinese-Vicuna 中文小羊驼"
        + "</h1>"
    )
    description = gr.Markdown(
        "中文小羊驼由各种高质量的开源instruction数据集，结合Alpaca-lora的代码训练而来，模型基于开源的llama7B，主要贡献是对应的lora模型。由于代码训练资源要求较小，希望为llama中文lora社区做一份贡献。"
    )
    history = gr.components.State()
    with gr.Row().style(equal_height=False):
        with gr.Column(variant="panel"):
            input_component_column = gr.Column()
            with input_component_column:
                input = gr.components.Textbox(
                    lines=2, label="Input", placeholder="请输入问题."
                )
                extra = gr.components.Textbox(
                    lines=2, label="Extra", placeholder="context or persona"
                )
                temperature = gr.components.Slider(minimum=0, maximum=1, value=1.0, label="Temperature")
                topp = gr.components.Slider(minimum=0, maximum=1, value=0.9, label="Top p")
                topk = gr.components.Slider(minimum=0, maximum=100, step=1, value=60, label="Top k")
                beam_number = gr.components.Slider(minimum=1, maximum=10, step=1, value=4, label="Beams Number")
                max_new_token = gr.components.Slider(
                    minimum=1, maximum=2000, step=1, value=256, label="Max New Tokens"
                )
                min_new_token = gr.components.Slider(
                    minimum=1, maximum=100, step=1, value=5, label="Min New Tokens"
                )
                repeat_penal = gr.components.Slider(
                    minimum=0.1, maximum=10.0, step=0.1, value=2.0, label="Repetition Penalty"
                )
                max_memory = gr.components.Slider(
                    minimum=0, maximum=2048, step=1, value=256, label="Max Memory"
                )
                do_sample = gr.components.Checkbox(label="Use sample")
                # must be str, not number !
                type_of_prompt = gr.components.Dropdown(
                    ['instruct', 'chat','chat with knowledge','chat with persona'], value='chat', label="Prompt Type", info="select the specific prompt; use after clear history"
                )
                input_components = [
                    input, extra, history, temperature, topp, topk, beam_number, max_new_token, min_new_token, repeat_penal, max_memory, do_sample, type_of_prompt
                ]
                input_components_except_states = [input,extra, temperature, topp, topk, beam_number, max_new_token, min_new_token, repeat_penal, max_memory, do_sample, type_of_prompt]
            with gr.Row():
                cancel_btn = gr.Button('Cancel')
                submit_btn = gr.Button("Submit", variant="primary")
                stop_btn = gr.Button("Stop", variant="stop", visible=False)
            with gr.Row():
                reset_btn = gr.Button("Reset Parameter")
                clear_history = gr.Button("Clear History")

        with gr.Column(variant="panel"):
            chatbot = gr.Chatbot().style(height=1024)
            output_components = [ chatbot, history ]  
            with gr.Row():
                save_btn = gr.Button("Save Chat")
        
        def wrapper(*args):
            # here to support the change between the stop and submit button
            try:
                for output in fn(*args):
                    output = [o for o in output]
                    # output for output_components, the rest for [button, button]
                    yield output + [
                        gr.Button.update(visible=False),
                        gr.Button.update(visible=True),
                    ]
            finally:
                yield [{'__type__': 'generic_update'}, {'__type__': 'generic_update'}] + [ gr.Button.update(visible=True), gr.Button.update(visible=False)]

        def cancel(history, chatbot):
            if history == []:
                return (None, None)
            return history[:-1], chatbot[:-1]

        extra_output = [submit_btn, stop_btn]

        save_btn.click(
            save, 
            input_components, 
            None, 
        )

        pred = submit_btn.click(
            wrapper, 
            input_components, 
            output_components + extra_output, 
            api_name="predict",
            scroll_to_output=True,
            preprocess=True,
            postprocess=True,
            batch=False,
            max_batch_size=4,
        )
        submit_btn.click(
            lambda: (
                submit_btn.update(visible=False),
                stop_btn.update(visible=True),
            ),
            inputs=None,
            outputs=[submit_btn, stop_btn],
            queue=False,
        )
        stop_btn.click(
            lambda: (
                submit_btn.update(visible=True),
                stop_btn.update(visible=False),
            ),
            inputs=None,
            outputs=[submit_btn, stop_btn],
            cancels=[pred],
            queue=False,
        )
        cancel_btn.click(
            cancel,
            inputs=[history, chatbot],
            outputs=[history, chatbot]
        )
        reset_btn.click(
            None, 
            [],
            (
                # input_components ; don't work for history...
                input_components_except_states
                + [input_component_column]
            ),  # type: ignore
            _js=f"""() => {json.dumps([
                getattr(component, "cleared_value", None) for component in input_components_except_states ] 
                + ([gr.Column.update(visible=True)])
                + ([])
            )}
            """,
        )
        clear_history.click(lambda: (None, None), None, [history, chatbot], queue=False)

demo.queue().launch(share=0)