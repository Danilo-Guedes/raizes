# Daily Sales Automation and Business Intelligence Ra!zes Restaurant

## Table of Contents

- [Introduction](#introduction)
- [1) Daily Sales in my whatsapp with one click](#daily-sales-in-my-whatsapp-with-one-click)
  - [Overview](#overview)
  - [How it Works](#how-it-works)
  - [Technologies Used](#technologies-used)
  - [Screenshots](#screenshots)
- [2) Custom PowerBI](#custom-powerbi)
  - [Overview](#overview-1)
  - [How it Works](#how-it-works-1)
  - [Technologies Used](#technologies-used-1)
  - [Screenshots](#screenshots)

## Introduction

This repository houses two powerful projects: "Daily Sales Whatsapp Report," a daily Python routine orchestrating seamless interactions with a restaurant ERP and disseminating insights via WhatsApp, and "Custom PowerBI," a dynamic data app utilizing Python, Streamlit, and Altair to extract, visualize, and communicate key metrics from the same ERP. Streamline the restaurant management with automated processes, dinamic charts and insightful reporting.

## Daily Sales in my whatsapp with one click

### Overview

This automations is a daily routine powered by Python, leveraging technologies like Requests, Playwright, and Pandas. It seamlessly interacts with a restaurant ERP, retrieves sales data, generates insightful considerations, and effortlessly shares the top 7 products' performance on a WhatsApp group.

### How it Works

Explain the steps of the automation process:

1. Call a restaurant ERP API.
2. Authenticate using OAuth 2.0. and refresh the token if is needed
3. GET data from a sales endpoint.
4. Parses the JSON and analyzes and summarize the content.
5. Create a considerations/resume text with a table of the top 7 products with the best sales earnings.
6. Open a browser in your web WhatsApp already in a group.
7. Send the message to the group.

### Technologies Used

- Python 3
- Requests
- Pandas
- Playwright
- Pyperclip
- Locale
- Tabulate
- tqdm

**Fun Fact:** These automations run every single day for more than 2 years.

#### Screenshots

![Daily Sales Screenshot1](/automations/daily_sales_report/screenshots/initial-terminal.png)
![Daily Sales Screenshot2](/automations/daily_sales_report/screenshots/final-terminal.png)
![Daily Sales Screenshot3](/automations/daily_sales_report/screenshots/main.png)
![Daily Sales Screenshot4](/automations/daily_sales_report/screenshots/folders.png)
![Daily Sales Screenshot5](/automations/daily_sales_report/screenshots/whatsapp.png)

## Custom PowerBI

### Overview

Report is a dynamic data app crafted with Python, Pandas, Streamlit, and Altair. Extracting insights from a restaurant ERP, it offers a user-friendly interface to upload CSV files, clean and wrangle data, and present visually appealing and informative charts. The reports, printed in PDF, are tailored for effective communication with stakeholders.

### How it Works

Explain the steps of the reporting process:

1. Run a web server with a menu separated by topics.
2. Upload CSV files extracted from the restaurant ERP.
3. Read, clean, and wrangle the data with Pandas.
4. Display beautiful and helpful charts with customized colors using Streamlit and Altair.
5. Print the reports in PDF to send to restaurant stakeholders.

### Technologies Used

- Python 3
- Pandas
- Streamlit
- Altair

## Screenshots


![Custom PowerBI Screenshot1](/report/screenshots/1.png)
![Custom PowerBI Screenshot2](/report/screenshots/2.png)
![Custom PowerBI Screenshot3](/report/screenshots/3.png)
![Custom PowerBI Screenshot4](/report/screenshots/4.png)
![Custom PowerBI Screenshot5](/report/screenshots/5.png)
![Custom PowerBI Screenshot6](/report/screenshots/6.png)
![Custom PowerBI Screenshot7](/report/screenshots/7.png)
![Custom PowerBI Screenshot8](/report/screenshots/8.png)
