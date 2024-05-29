# ML-Backtest-Application
## Usage
1) Make sure you have Docker desktop running on your machine, download [here](https://www.docker.com/products/docker-desktop/).
2) Type the following command to clone the repo <pre>git clone https://github.com/MaxwellMendenhall/ML-Backtest-App.git</pre>
3) Type the following command to switch current working dir <pre>cd ml-backtest-app</pre> 
4) Build & run the multi-container application <pre>docker-compose up --build</pre>
5) Visit http://localhost:3000 on your machine to see the application up and running.

## What is this?
This is a pre-built application for the [ml-backtest](https://pypi.org/project/ml-backtest/) Python library. It provides a no-code solution for training and obtaining models for trading strategies.

## Customizable
Have your own strategy you want to use? Just create it and add it to the backend, you can find the 
documentation [here](https://github.com/MaxwellMendenhall/ml_backtest). 
