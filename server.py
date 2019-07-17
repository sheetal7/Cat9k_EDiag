import device_status
from flask import Flask

app = Flask(__name__)


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
    return device_status.summary_html(intf_state, switch.ioxInfo())
