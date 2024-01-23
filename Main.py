from openai import OpenAI
import re

import streamlit as st


def produce_response():
    response = client.chat.completions.create(
        model="gpt-4", messages=st.session_state.messages
    )

    return response.choices[0].message.content.replace("\n", "")


def check_response(response: str):
    feedback = None
    score = None
    question = None

    m = re.search(r"<feedback>(.*)</feedback>", response)
    if m:
        feedback = m.group(1)
    m = re.search(r"<score>(.*)</score>", response)
    if m:
        score = m.group(1)
    m = re.search(r"<question>(.*)</question>", response)
    if m:
        question = m.group(1)

    if feedback is not None and score is not None:
        return True

    return False


st.title("Thothica Test Taker App")

client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a smart assistant."},
        {
            "role": "user",
            "content": """Hello Professor Weber,

I am a teacher currently instructing my students on the first two chapters of your book, "The Protestant Ethic and the Spirit of Capitalism." I would like to request your assistance in evaluating my students' understanding of the material.

From this point onward, you will be engaging with my students by posing questions to them, and they will provide you with their responses. I kindly ask you to provide feedback regarding the accuracy of their answers and to rate them on a scale of ten. Additionally, please provide compelling reasons for your ratings, considering factors such as accuracy, writing style, and grammar.

Kindly enclose your feedback within the following XML tags:

<feedback>
</feedback>

and score within these XML tags:

<score>
x/10
</score>

Where x is the specific score.

Also the next question as :

<question>
</question>

Please note that this portion of our correspondence will not be shared with my students.

Thank you for your cooperation. Now You are going to talk to my student, start giving questions. This is an exam, an individual exam. You will ask 5 questions in total and ask one by one. Do not address me now, only give feedback when the student answers.

The test begins, welcome the student and start.""",
        },
    ]

if len(st.session_state.messages) == 2:
    response = client.chat.completions.create(
        model="gpt-4-1106-preview", messages=st.session_state.messages
    )
    if "<question>" in response.choices[0].message.content.split():
        response = (
            response.choices[0].message.content.split("<question>")[0]
            + " \n\n ## Question "
            + response.choices[0]
            .message.content.split("<question>")[1]
            .split("</question>")[0]
        )
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.session_state.messages.append(
            {"role": "assistant", "content": response.choices[0].message.content}
        )

for n, message in enumerate(st.session_state.messages[2:]):
    if message["role"] == "assistant":
        if n == 0:
            st.markdown(message["content"])
        else:
            with st.chat_message(message["role"]):
                feedback = None
                score = None
                question = None

                m = re.search(r"<feedback>(.*)</feedback>", message["content"])
                if m:
                    feedback = m.group(1)
                m = re.search(r"<score>(.*)</score>", message["content"])
                if m:
                    score = m.group(1)
                m = re.search(r"<question>(.*)</question>", message["content"])
                if m:
                    question = m.group(1)

                if feedback is not None and score is not None:
                    st.markdown("# Score - \n\n " + score)
                    st.markdown("## Feedback - \n\n " + feedback)
                    if question:
                        st.markdown("## Next Question - \n\n " + question)
    else:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

prompt = st.chat_input()
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        response = client.chat.completions.create(
            model="gpt-4", messages=st.session_state.messages
        )

        full_response = response.choices[0].message.content.replace("\n", "")

        i = 0

        while not check_response(full_response) and i < 3:
            full_response = produce_response()
            i += 1

        feedback = None
        score = None
        question = None

        m = re.search(r"<feedback>(.*)</feedback>", full_response)
        if m:
            feedback = m.group(1)
        m = re.search(r"<score>(.*)</score>", full_response)
        if m:
            score = m.group(1)
        m = re.search(r"<question>(.*)</question>", full_response)
        if m:
            question = m.group(1)

        if feedback is not None and score is not None:
            st.markdown("# Score - \n\n " + score)
            st.markdown("## Feedback - \n\n " + feedback)
            if question:
                st.markdown("## Next Question - \n\n " + question)
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response
                }
            )
        else:
            st.write(full_response)
            st.write("gpt failed")