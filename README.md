# Categorise your Halifax Credit Card Transactions into Spend Groups
![Python 3.8](https://img.shields.io/badge/python_3.8-green)
![ChatGPT API](https://img.shields.io/badge/ChatGPT_API-black)
![Halifax](https://img.shields.io/badge/Halifax_Bank-blue)

I love how online banks like Monzo categorise your payments into Spend Groups (e.g. Eating out). Unfortunately, I bank with Halifax. What's even worse, Halifax credit card bank statements are all in pdf format. This makes personal spend analysis a nightmare. I suffered this pain and wrote this code, so that you don't have to!

## Description
This repository contains a python script which transforms this unstructured pdf data into a structured csv format, and asks ChatGPT to categorise your payments into 11 Spend Groups (following the Monzo model):
```
categories = ["Savings","Rent","Eating out","Transport","Groceries","Shopping","Holidays","Entertainment","Personal Care","General","Charity"]
```

For those fellow Halifax customers who want to understand their credit spending behaviour, but are limited by Halifax's archaic system, I hope you will use this code for yourselves to take ownership of your financial data. This code does the following:

1. Converts multiple PDF Statements into a single Pandas DataFrame 
2. Uses the ChatGPT API to categorise transactions into spend groups for analysis
3. Outputs the categorised transaction data as a CSV

## Pre-requisites
* A terminal where you can run a python script e.g. Jupyter Notebook / Visual Studio Code. If you don't have this on your computer, [download Anaconda](https://www.anaconda.com/download)
* You have an [OpenAI account](https://chat.openai.com/auth/login) (if opened in the last 3 months you can run API queries free of charge, otherwise you'll need to provide payment information to OpenAI - with the default set-up I've gone for, this will cost <1p per run)
* Dependencies: requirements can be found in the requirements.txt file, and can be loaded via pip.

## Getting started
### clone the repo
Clone the repository. To learn about what this means, and how to use Git, see the [Git guide](https://nhsdigital.github.io/rap-community-of-practice/training_resources/git/using-git-collaboratively/).

```
git clone https://github.com/harry843/halifax-credit-statement-categorisation.git
```

### install dependencies
Make a [virtual environment](https://nhsdigital.github.io/rap-community-of-practice/training_resources/python/virtual-environments/venv/) and install the dependencies:
```
pip install -r requirements.txt
```

### create your OpenAI personal access token
[Check out this guide](https://medium.com/geekculture/a-simple-guide-to-chatgpt-api-with-python-c147985ae28)

### make a .env file to store this token
Create a new file called openai.env in the same directory as the credit_statement_payment_categorisation.py file (if you followed the steps above, this will be the folder called halifax-credit-statement-categorisation). The .env file extension may not be recognised by default depending on your operating system, so if you get asked what application to open it with, choose Notepad.

Inside the file, replace the dummy access token text after the equals sign with the OpenAI access token you created above:
```
OPENAI_ACCESS_TOKEN=dummyaccesstoken
```
Now save the file.

### run the script
Once you have run the script, you will be prompted to enter the folder path where you have saved your pdf Halifax credit card statements. In file explorer, navigate to this directory and copy the full path (e.g. C:\Users\YourName\Documents\Finances\Statements)

Paste this path into the input text box on screen and press Enter.

Now the script will work its magic - nice job for getting this far!

## Contact

This repo is currently maintained by [@harry843](https://github.com/harry843) - raise an issue or a pull request if you have any suggestions, or just contact me on my [LinkedIn](https://www.linkedin.com/in/harry-kelleher/)

