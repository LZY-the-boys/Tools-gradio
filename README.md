# Tools-gradio

custom widget using gradio


- Chinese-Vicuna Chatbot used in [Chinese-Vicuna](https://github.com/Facico/Chinese-Vicuna)
- a compare dialogue viewer | 对话标注工具界面
    - NOTE: only read from file, don't generate dynamically because don't have enough momery to run all the models :(, the API way you can see [here]((https://github.com/sunner/ChatALL) | 动态运行所有模型显然不现实，这里提供的是一个通过提前准备好文件，读取加载打分比较的方式。当然另一种方式是调API比较，[在这里有实现](https://github.com/sunner/ChatALL)
    - It has two mode: 1) compare all models ; 2) compare all others with one main model | 有两种模式：一种是所有模型比较， 一种是只跟一个主模型比较好坏