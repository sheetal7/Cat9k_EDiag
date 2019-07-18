import device_status
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)

switch = device_status.getDefaultSwitchInfo()
switch.connect()

@app.route('/device_status.json')
def index_json():
	intf_state = device_status.get_intf_state()
	return device_status.summary(intf_state, switch.ioxInfo(), switch.resInfo(), switch.appListInfo())


@app.route('/')
@app.route('/device_status.html')
def index():
    intf_state = device_status.get_intf_state()
    return device_status.summary_html(intf_state, switch)

@app.route('/runAppInt')
def runAppInt():
	return switch.appInter()

@app.route('/runIox')
def runIox():
	return switch.iox()
