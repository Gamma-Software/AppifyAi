# 🤖 ChatbotX

Welcome to ChatbotX, an innovative project that brings together the power of natural language processing and dynamic web application generation. ChatbotX is your personal assistant that can transform your instructions into fully functional and interactive web applications with just a conversation.

<details>
  <summary>Click me for more</summary>
## Unleash the Power of Conversational Programming

With ChatbotX, you don't need to be a coding expert to create stunning web applications. Simply engage in a conversation with our intelligent chatbot, express your vision, and watch as the magic happens. Our cutting-edge natural language processing engine comprehends your instructions with remarkable accuracy, ensuring a seamless user experience.

## Dynamic Code Generation, Instant Web Applications

ChatbotX's intelligent core generates high-quality Python code snippets on the fly, tailored to your exact specifications. Through the fusion of your creativity and our advanced algorithms, you'll witness the birth of captivating visualizations, intuitive interfaces, and dynamic functionality. No need to fiddle with complex frameworks or wrestle with tedious coding – ChatbotX handles it all for you.

## Streamlit: The Gateway to Web App Excellence

We have chosen Streamlit, the beloved Python library, as the foundation for our web applications. With Streamlit's simplicity and elegance, your creations come to life effortlessly. Seamlessly integrated with ChatbotX, Streamlit ensures that your applications are not only visually stunning but also highly interactive, providing an immersive experience for your users.

## Let Your Imagination Soar

ChatbotX is the ultimate tool for unleashing your creativity. Whether you want to build captivating data visualizations, develop intuitive dashboards, or create innovative machine learning applications, ChatbotX is your steadfast companion. It adapts to your needs, guides you through the process, and transforms your ideas into reality.

## Join the ChatbotX Revolution

Become a part of the ChatbotX revolution and redefine the way web applications are built. Collaborate with fellow developers, share your creations, and inspire others. Your contributions make a difference, shaping the future of intelligent conversational programming.
</details>

## Demo

TODO

## Features

- Natural Language Processing (NLP): The chatbot utilizes NLP techniques to understand and interpret user instructions.
- Conversation Flow: The chatbot follows a well-defined conversational flow to interact with users and gather instructions.
- Code Generation: The chatbot dynamically generates Python code snippets based on user instructions.
- Streamlit Integration: The generated code is incorporated into a Streamlit application, providing an interactive web interface.
- Code Explanation: The chatbot provides detailed explanations of the generated code to help users understand its functionality.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```shell
pip install -r requirements.txt
```

That's it ! You are ready to go !

### Usage

1. Add you own OpenAI API key, by renaming the file `.streamlit/secrets_template.toml` to `.streamlit/secrets.toml` and add your own API key in the following line:
```toml
openai_api_key = "your key here"
````

2. Then run the following command to start the app:

```shell
streamlit run generative_app/🏠ChatbotX.py
```

3. Interact with the bot to generate the Streamlit App of your dreams !

## Usage Examples

Here are some example instructions you can provide to the chatbot:

    "Create a bar chart showing the sales data for the last quarter given earlier."
    "Generate a scatter plot with the temperature and humidity data given earlier."
    "Add a sidebar to the application with a dropdown menu for selecting options ("update", "save", "reset")."

The chatbot will interpret these instructions, generate the corresponding Python code, and create a Streamlit application accordingly in the page 🤖GeneratedApp.

## Roadmap

- [x] Add a chatbot
- [x] Add a sandbox page for the bot to play with
- [x] Add commands to /undo, /reset, /save
- [ ] Embed in vector stores the up to dat documentation of Streamlit https://github.com/streamlit/docs/tree/main/content
- [ ] Add a voice assistant (text to speech and speech to text)
- [ ] Add a page to show the documentation of the app


## Built With

* [OpenAI LLM](https://openai.com) - Creating safe AGI that benefits all of humanity
* [Langchain](https://github.com/hwchase17/langchain) - 🦜️🔗 LangChain ⚡ Building applications with LLMs through composability ⚡

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/Gamma-Software/GenerativeApp/tags).

## Authors

* **Valentin Rudloff** - *Initial work* - [GenerativeApp](https://github.com/Gamma-Software/GenerativeApp)

See also the list of [contributors](https://github.com/Gamma-Software/CustomerCareAI/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

The inital idea came after frustruation of not being able to correctly communicate with an robot assistant by phone. ChatGPT's power combined to Langchain with the toolset the thinking capabilities was the solution to this problem.