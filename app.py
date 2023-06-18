import json
from flask import Flask, render_template, request, session
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    xlsx_file = request.files['file']
    column_number = int(request.form['column'])-1

    if xlsx_file:
        df = pd.read_excel(xlsx_file)
        if column_number < 0 or column_number >= df.shape[1]:
            return "Invalid column number."
        selected_column = df.iloc[:, column_number]

        averages = []

        for i in range(0, len(selected_column) - 1, 2):
            avg = (selected_column[i] + selected_column[i + 1]) / 2
            averages.append(avg)

        avg_dia = np.array(averages)

        averages_flattened = avg_dia.flatten()

        j = 1
        average_values = []
        for value in averages_flattened:
            average_values.append(f"{value:.4f}")  # Remove the braces and format the value
            j = j + 1

        session['avg_dia'] = avg_dia.tolist()
        total_grains = len(avg_dia)

        return render_template('result.html', selected_column=selected_column.tolist(), averages=average_values, avg_dia=avg_dia,total_grains=total_grains)
        
    
    return "No file uploaded."

@app.route('/chart', methods=['POST'])
def chart():
    avg_dia = np.array(session['avg_dia'])
    range_value = int(request.form['range'])
    total_grains = len(avg_dia)

    max_value = np.max(avg_dia)
    rounded_value = math.ceil(max_value / 10) * 10

    lower_bound = 0
    upper_bound = rounded_value

    x = []

    while lower_bound < upper_bound:
        range_label = f"{lower_bound}-{lower_bound+range_value}"
        x.append(range_label)
        lower_bound += range_value

    x_new = x

    num_ranges = upper_bound // range_value

    count_array = [0] * num_ranges

    for value in avg_dia:
        lower_bound = int(value) // range_value * range_value
        upper_bound_range = min(lower_bound + range_value, upper_bound)

        range_index = lower_bound // range_value
        count_array[range_index] += 1

    y_new = np.array(count_array)
    y = y_new / total_grains

    return render_template('chart.html', x=x_new, y_new=y_new.tolist(), normalized_y=y.tolist(), range_value=range_value, max_value=max_value, total_grains=total_grains)

@app.route('/print', methods=["POST"])
def print_results():
    avg_dia = np.array(session['avg_dia'])
    range_value = int(request.form['range'])
    total_grains = len(avg_dia)

    max_value = np.max(avg_dia)
    rounded_value = math.ceil(max_value / 10) * 10

    lower_bound = 0
    upper_bound = rounded_value

    x = []

    while lower_bound < upper_bound:
        range_label = f"{lower_bound}-{lower_bound+range_value}"
        x.append(range_label)
        lower_bound += range_value

    x_new = x

    num_ranges = upper_bound // range_value

    count_array = [0] * num_ranges

    for value in avg_dia:
        lower_bound = int(value) // range_value * range_value
        upper_bound_range = min(lower_bound + range_value, upper_bound)

        range_index = lower_bound // range_value
        count_array[range_index] += 1

    y_new = np.array(count_array)
    y = y_new / total_grains

    return render_template('print.html', x=x_new, y_new=y_new.tolist(), normalized_y=y.tolist(), range_value=range_value, max_value=max_value, total_grains=total_grains)


if __name__ == '__main__':
    app.run(debug=True)
