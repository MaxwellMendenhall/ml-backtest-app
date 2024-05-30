##########################################################################
#############      DO NOT      CHANGE     CODE     HERE      #############
##########################################################################

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS # type: ignore
import pandas as pd # type: ignore
from werkzeug.utils import secure_filename
import io
import json
import traceback
import numpy as np # type: ignore
from ml_backtest import Backtest, MachineLearning # type: ignore
from ml_backtest.machine_learning import CandleStickDataProcessing # type: ignore
import os

# Import the changeable configuration
import config

app = Flask(__name__)
CORS(app)

# Directory to save model files
MODEL_DIR = 'models'
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)
    
def get_analysis_data(df):
    df['cumulative_pnl'] = df['pnl'].cumsum()
    analysis_chart_data = []
    for entry_time, value in zip(df['entry time'], df['cumulative_pnl']):
        unix_time = convert_to_unix_conditional(entry_time)
        integer_value = int(round(value))
        analysis_chart_data.append({"time": unix_time, "value": integer_value})
    return analysis_chart_data

def get_candle_stick_data(df):
    candle_stick_data = []
    for date, open, close, high, low in zip(df['date'], df['open'], df['close'], df['high'], df['low']):
        unix_time = convert_to_unix_conditional(date)
        candle_stick_data.append({"time": unix_time, "open": open, "close": close, "high": high, "low": low})
    return candle_stick_data

def get_trade_times(df):
    trade_time_data = []
    for exit_time, entry_time, entry_price, exit_price in zip(df['exit time'], df['entry time'], df['entry price'], df['exit price']):
        unix_exit_time = convert_to_unix_conditional(exit_time)
        unix_entry_time = convert_to_unix_conditional(entry_time)
        trade_time_data.append({"exit": unix_exit_time, "entry": unix_entry_time, "entryPrice": entry_price, "exitPrice": exit_price})
    return trade_time_data

def convert_to_unix_conditional(time):
    date_formats = ["%m/%d/%Y %I:%M:%S %p", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S"]

    for date_format in date_formats:
        try:
            converted_time = pd.to_datetime(time, format=date_format)
            return int(converted_time.timestamp())
        except (ValueError, TypeError):
            continue

    if isinstance(time, (int, np.integer)):
        return time
    else:
        raise ValueError(f"Time '{time}' does not match any provided date formats and is not in Unix format.")

def convert_numpy_types(data):
    if isinstance(data, dict):
        return {k: convert_numpy_types(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_types(v) for v in data]
    elif isinstance(data, np.integer):
        return int(data)
    elif isinstance(data, np.floating):
        return float(data)
    elif isinstance(data, np.ndarray):
        return data.tolist()
    else:
        return data

@app.route('/get-selection-strats', methods=['GET'])
def get_selection_strats():
    return jsonify(config.get_selection_strats())

@app.route('/get-selection-models', methods=['GET'])
def get_selection_models():
    return jsonify(config.get_selection_models())

@app.route('/get-column-names', methods=['GET'])
def get_column_names():
    return jsonify(config.get_column_names())

@app.route('/submit-form', methods=['POST'])
def handle_form_submission():
    file = request.files.get('file')
    try:
        rows_number = int(request.form.get('rowsNumber'))
    except ValueError:
        rows_number = 10
    strategy_type = request.form.get('strategyType')
    ml_type = request.form.get('mlType')
    columns_value = request.form.get('columns')
    filename = request.form.get('filename')

    try:
        true_columns = json.loads(columns_value)
        if not isinstance(true_columns, list):
            raise ValueError("Columns should be a list.")
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error parsing columns: {e}")
        return jsonify({"error": f"Error parsing columns: {e}"}), 400
    
    strategy_class = config.strategy_mappings.get(strategy_type)
    strategy_instance = strategy_class()    
    ml_class = config.ml_mappings.get(ml_type)

    if file and secure_filename(file.filename).endswith('.csv'):
        try:
            file_content = file.stream.read().decode('utf-8')
            df = pd.read_csv(io.StringIO(file_content))
            
            norm_df1 = df.copy()
            candleStickData1 = get_candle_stick_data(df=norm_df1)
            
            backtest = Backtest(df, strategy_instance)
            json_result1 = backtest.get_results().to_json(orient='index')
            json_result1_dict = json.loads(json_result1)
            
            norm_df = backtest.get_trades().copy()
            analysis_chart_data1 = get_analysis_data(norm_df)
            trade_times_data1 = get_trade_times(norm_df)
            
            ml = MachineLearning(ml_class=ml_class,
                                df=df,
                                results=backtest.get_trades(),
                                rows=rows_number,
                                columns=true_columns)
            ml.run(dp_pattern=CandleStickDataProcessing.calculate_inverted_hammer_features)
            model, columns, rows = ml.get_util()
            data = ml.get_data()

            ml_backtest = Backtest(data, strategy_instance, model=model, columns=columns, rows=rows, cs_pattern=True)
            json_result2 = ml_backtest.get_results().to_json(orient='index')
            json_result2_dict = json.loads(json_result2)
            
            candleStickData2 = get_candle_stick_data(df=data.copy())
            ml_df = ml_backtest.get_trades()
            analysis_chart_data2 = get_analysis_data(ml_df)
            trade_times_data2 = get_trade_times(ml_df)
            
            trade_results1 = backtest.get_trades().to_dict(orient='records')
            trade_results2 = ml_backtest.get_trades().to_dict(orient='records')

            trade_results1 = convert_numpy_types(trade_results1)
            trade_results2 = convert_numpy_types(trade_results2)
            
            model_filename = os.path.join(MODEL_DIR, filename)
            ml.dump_model(filename=model_filename)
            
        except Exception as e:
            print(f"Error reading the CSV file: {e}")
    else:
        print("No file uploaded or the file is not a CSV.")
        
    sample_data = {
        "candleStickData1": candleStickData1,
        "candleStickData2": candleStickData2,
        "analysisChartData1": analysis_chart_data1,
        "analysisChartData2": analysis_chart_data2,
        "tradeData1": trade_times_data1,
        "tradeData2": trade_times_data2,
        "tradeResults1": json_result1_dict,
        "tradeResults2": json_result2_dict,
    }

    sample_data = convert_numpy_types(sample_data)

    return jsonify(sample_data), 200

@app.route('/download', methods=['POST'])
def download_model():
    filename = request.form.get('filename')
    if filename:
        file_path = os.path.join(MODEL_DIR, f"{filename}.joblib")
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({"error": "File not found"}), 404
    else:
        return jsonify({"error": "Filename not provided"}), 400

    
if __name__ == '__main__':
    app.run(debug=True)

##########################################################################
##########################################################################
##########################################################################