import os
import json
from flask import app, request
from datetime import datetime

# Methods for the files doc
with open(os.path.join('properties','defaults.json')) as f:
    conf = json.load(f.read())['files.html']

def build_file_table(defaultPath:str,path:str=None,**kwargs):
    """
    build out the HTML table for files.html
    """
    data=[]
    td = lambda x: f'<td>{x}</td>'
    href = lambda path,alias: f'<a href="{os.path.join(request.base_url,path)}">{alias}</a>'
    row = f'<tr><td><a href="{os.path.dirname(request.base_url)}">Parent Directory</a></td>{td("")*3}</tr>'
    if path:
        defaultPath = os.path.join(defaultPath,path)
    content = os.listdir(defaultPath)
    # each iteration represents a row
    for obj in content:
        path=os.path.join(defaultPath,obj)
        # Name
        row+=td(href(obj,obj))
        # Modified Datetime
        row+=td(
            datetime.fromtimestamp(
                os.path.getmtime(path)
                ).strftime(
                    "%m/%d/%Y %I:%M:%S %p"
                    )
        )
        # Object Type
        is_dir = os.path.isdir(path)
        if is_dir:
            row+=td('Folder')
        else:
            row+=td('File')
        # Size
        size = int(os.path.getsize(path)/1000)
        if not is_dir:
            row+=td(str(size)+' KB')
        else:
            row+=td('-')
        row = '<tr>'+row+'</tr>'
        data.append(row)
        row=''
    return ''.join(data)

@app.route("/files2/")
@app.route("/files2/<path:path>")
def files2(path:str=''):
    os_path = os.path.join(conf['files.html']['defaultPath'],path)
    # # if the path string is empty, go to our mounts page
    # if not path:
    #     f=FilesPage()
    #     data = []
    #         for i in conf['files.html']['mounts']:
    #             f.td(f.href(i['path']))
    #             f.td(i['alias'])
                
    # if it's a folder, open up the contents on a new page
    if not os.path.isfile(os_path):
        data = build_file_table(conf['files.html']['defaultPath'],path)
        return f"""
        {banner()}
        <p style="text-align:center">
        {render_template('files.html',content=banner(),data=data)}
        </p>
        """
    else:
        attach=request.args.get('attach',default=1,type=bool)
        return send_file(os_path,as_attachment=attach)