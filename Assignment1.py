#!/usr/bin/env python
# coding: utf-8

# 1. Gender Response Rate
# 2. Age Group Response Rate
# 3. Recent Purchase Response Rate
# 4. Usage Response Rate
# 5. Deployment
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import pandas as pd
import warnings
warnings.filterwarnings("ignore")


# -------------------------------------------------
# Read Data
# -------------------------------------------------
df = pd.read_csv("skin clinic campaign.csv")

# -------------------------------------------------
# Bin Purchases into Groups
# -------------------------------------------------
df["binned_purchases"] = pd.cut(\
    df["Unique_Products_Purchased"],\
    bins=[0, 5, 8, float("inf")],\
    labels=["1-4", "5-8", "8+"]\
    )
# -------------------------------------------------
# Response rate table function
# -------------------------------------------------
def get_response_rate(df, item):
    table = pd.crosstab(df[item], df["Response_to_Campaign"])
    table["Response Rate (%)"] = (table["Yes"] / table.sum(axis=1) * 100).round(1)
    return(table.reset_index())

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():

    return """
    <!DOCTYPE html>
    <html>

    <head>
        <title>Campaign Analysis</title>

        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
            }

            select, button {
                padding: 8px;
                font-size: 16px;
            }

            button {
                cursor: pointer;
            }
        </style>
    </head>

    <body>

        <h1>Campaign Analysis</h1>

        <form action="/campaign-analysis" method="post">

            <label for="grouping">
                Analyse response rate by:
            </label>

            <select name="grouping" id="grouping">

                <option value="gender">
                    Gender
                </option>

                <option value="age">
                    Age Group
                </option>

                <option value="buy">
                    Purchase in Last Quarter
                </option>
                
                <option value="usage">
                    Product Usage
                </option>

            </select>

            <br><br>

            <button type="submit">
                Run Analysis
            </button>

        </form>

    </body>

    </html>
    """

@app.post("/campaign-analysis", response_class=HTMLResponse)
def campaign_analysis(grouping: str = Form(...)):

    # Determine which variable to analyse

    if grouping == "gender":

        group_column = "Gender"
        title = "Response Rate by Gender"

    elif grouping == "age":
        
        group_column = "AgeGroup"
        title = "Response Rate by Age Group"

    elif grouping == "buy":

        group_column = "Purchase_Last_Quarter"
        title = "Response Rate by Purchase in Last Quarter"
        
    elif grouping == "usage":

        group_column = "binned_purchases"
        title = "Response Rate by Product Usage"

    else:

        return HTMLResponse(
            content="Invalid grouping selected.",
            status_code=400
        )


    # Calculate response rate
    table = get_response_rate(
        df,
        group_column
    )


    # Convert dataframe to HTML
    html_table = f"""
    <table class="data-table">

        <thead>
            <tr>
                <th colspan="4">Campaign Response Analysis</th>
            </tr>

            <tr>
                <th>{group_column}</th>
                <th>No</th>
                <th>Yes</th>
                <th>Response Rate (%)</th>
            </tr>
        </thead>

        <tbody>
    """

    for _, row in table.iterrows():
        html_table += f"""
            <tr>
                <td>{row[group_column]}</td>
                <td>{row["No"]}</td>
                <td>{row["Yes"]}</td>
                <td>{row["Response Rate (%)"]}</td>
            </tr>
        """

    html_table += """
        </tbody>
    </table>
    """

    return f"""
    <!DOCTYPE html>
    <html>

    <head>

        <title>Campaign Analysis</title>

        <style>

            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
            }}

            table {{
                border-collapse: collapse;
                width: 600px;
                margin-top: 20px;
            }}

            th, td {{
                border: 1px solid #ddd;
                padding: 10px;
                text-align: center;
            }}

            th {{
                background-color: #f2f2f2;
            }}

            tr:nth-child(even) {{
                background-color: #fafafa;
            }}

            a {{
                display: inline-block;
                margin-top: 20px;
            }}

        </style>

    </head>

    <body>

        <h1>{title}</h1>

        {html_table}

        <a href="/">
            Back to Analysis Selection
        </a>

    </body>

    </html>
    """
