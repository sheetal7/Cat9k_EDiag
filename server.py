import device_status
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)


@app.route('/device_status.json')
def index_json():
	switch = device_status.getDefaultSwitchInfo()
	switch.connect()
	intf_state = device_status.get_intf_state()
	return device_status.summary(intf_state, switch.ioxInfo(), switch.resInfo(), switch.appListInfo())


@app.route('/')
@app.route('/device_status.html')
def index():
    intf_state = device_status.get_intf_state()
    return device_status.summary_html(intf_state, switch.ioxInfo())

@app.route('/runAppInt')
def runAppInt():
	switch = device_status.getDefaultSwitchInfo()
	switch.appInter()

@app.route('/runIox')
def runIox():
	switch = device_status.getDefaultSwitchInfo()
	switch.iox()