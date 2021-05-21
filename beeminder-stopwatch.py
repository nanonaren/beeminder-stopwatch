import PySimpleGUI as sg
import time
import json
import os.path


CONFIG_PATH = "~/.beeminder_stopwatch.json"

config_file = os.path.expanduser(CONFIG_PATH)

try:
    with open(config_file) as f:
        config = json.load(f)
except OSError:
    config = {}


def submit_time(goal, value):
    import requests
    datapoints_url = 'https://www.beeminder.com/api/v1/users/%s/goals/%s/datapoints.json' % (config.get('username', ''), goal)
    try:
        resp = requests.post(datapoints_url, json={
            'auth_token': config.get('auth_token', ''),
            'value': value})
        if 'status' in resp.json() and resp.json()['status'] == 'created':
            return True
        else:
            print(resp.json())
    except Exception as e:
        print(e)
    return False


settings = [
    [sg.Text('Settings')],
    [sg.Text('Config file at %s' % config_file)],
    [sg.Text('Username'), sg.In(config.get('username', ''), key='username')],
    [sg.Text('Auth token'), sg.In(config.get('auth_token', ''), key='auth_token')],
    [sg.Button('Save')]
]

layout = [
    [sg.Text('00:00:00', size=(50,1), key='watch')],
    [sg.In(size=(20,1), key='goal'),
     sg.Button('Start'), sg.Button('Stop'), sg.Button('Setup')],
    [sg.pin(sg.Column(settings, key='-SETTINGS-', visible=False))]
]

window = sg.Window('Beeminder Stopwatch', layout, keep_on_top=True)
start_time = None
setting_visibility = False

while True:
    event, values = window.read(timeout=1000)
    if event == sg.WIN_CLOSED:
        break
    elif event == 'Start':
        start_time = int(time.time())
    elif event == 'Stop':
        start_time = None
        val = window['watch'].get()
        window['watch'].update('SENDING %s to goal "%s"...' % (val, values['goal']))
        window.Refresh()
        if not submit_time(values['goal'], val):
            window['watch'].update('FAILED to sumbit %s to goal "%s".' % (val, values['goal']))
        else:
            window['watch'].update('ADDED %s to goal "%s".' % (val, values['goal']))
        
    elif event == 'Setup':
        setting_visibility = not setting_visibility
        window['-SETTINGS-'].update(visible=setting_visibility)
    elif event == 'Save':
        config['username'] = values['username']
        config['auth_token'] = values['auth_token']
        with open(config_file, 'w') as f:
            json.dump(config, f)

    # update timer
    if start_time is not None:
        dur = int(time.time()) - start_time
        window['watch'].update('%02d:%02d:%02d' % (dur / 3600,
                                                   (dur % 3600) / 60,
                                                   dur % 60))

window.close()
