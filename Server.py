from flask import Flask, render_template, request, send_from_directory
from waitress import serve
import os
import subprocess
import sys
import json
import logging


osSystem = 'windows'# 'linux'




if osSystem == 'windows':
    folder=r'C:\Users\Public.DESKTOP-J6Q3U28\Desktop\lstm1_final'
    # folder= r'.'
else:
    folder='/home/n/Desktop/lstm1_final'
    # folder = '.'

app = Flask(__name__)
port_input   = 5000
num_threads = 5
logging.basicConfig(level=logging.DEBUG) 
logger = logging.getLogger(__name__)  

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    predictions = []  
    if request.method == 'POST':
        phase = request.form.get('phase')  
        buldingname = request.form.get('buldingname') 
        logger.debug(f"Received phase: {phase}, buldingname: {buldingname}") 
        message, predictions = run_phase(phase, buldingname)
    return render_template('index.html', message=message, predictions=predictions)             

def run_phase(phase, buldingname):
    os.environ['PHASE'] = phase 
    os.environ['buldingname'] = buldingname  
    logger.debug(f"Environment variables set: PHASE={phase}, buldingname={buldingname}")  

    try:
        if osSystem == 'windows' :
            script_path=f'{folder}\\run.py'
        else :
            script_path=f'{folder}/run.py'

        logger.debug(f"Running script at path: {script_path}") 
        subprocess.run([sys.executable, script_path], check=True)

        if osSystem == 'windows' :
            jsonresults=f'{folder}\Results\{buldingname}\{buldingname}.json'
        else :
            jsonresults=f'{folder}/Results/{buldingname}/{buldingname}.json'        
        
        with open(jsonresults, 'r') as f:
            predictions = json.load(f)
        return f"Phase {phase} with meter {buldingname} executed successfully.", predictions  

    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred: {e}")  
        return f"Error occurred: {str(e)}", []



if __name__ == '__main__':
    # app.run(debug=True)
    serve(app, host='127.0.0.1', port=port_input, threads=num_threads)

