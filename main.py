import json
import yaml
import os
import cv2
from datetime import datetime
from flask import Flask, url_for, render_template, request, send_file, Response, escape, abort

app = Flask(__name__)
# app.add_url_rule('/favicon.ico',
                #  redirect_to=url_for('static', filename='favicon.ico'))
# get configuration
with open(r'properties\defaults.yaml') as f:
    conf = yaml.safe_load(f)

def gen():
    video = cv2.VideoCapture(2)
    face_cascade = cv2.CascadeClassifier()
    # Load the pretrained model
    face_cascade.load(cv2.samples.findFile("properties/haarcascade_frontalface_alt.xml"))
    while True:
        success, image = video.read()
        frame_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        frame_gray = cv2.equalizeHist(frame_gray)

        faces = face_cascade.detectMultiScale(frame_gray)

        for (x, y, w, h) in faces:
            center = (x + w//2, y + h//2)
            cv2.putText(image, "X: " + str(center[0]) + " Y: " + str(center[1]), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
            image = cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

            faceROI = frame_gray[y:y+h, x:x+w]
        ret, jpeg = cv2.imencode('.jpg', image)

        frame = jpeg.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

class FilesPage:
    def __init__(self) -> None:
        self.td = lambda x: f'<td>{x}</td>'
        self.href = lambda path,alias: f'<a href="{os.path.join(request.base_url,path)}">{alias}</a>'
        self.row = f'<tr><td><a href="{os.path.dirname(request.base_url)}">Parent Directory</a></td>{self.td("")*3}</tr>'

def build_file_table(root:str,path:str=None,**kwargs):
    """
    build out the HTML table for files.html
    """
    data=[]
    td = lambda x: f'<td>{x}</td>'
    href = lambda path,alias: f'<a href="{os.path.join(request.base_url,path)}">{alias}</a>'
    row = f'<tr><td><a href="{os.path.dirname(request.base_url)}">Parent Directory</a></td>{td("")*3}</tr>'
    
    if path:
        root = os.path.join(root,path)
    # Read the contents of the directory. Return 403 if we cannot read the folder.
    try:
        content = os.listdir(root)
    except PermissionError as e:
        return abort(403)
    # if there's no content, return row containing link to parent dir
    if not content:
        return row
    # each iteration represents a row
    for obj in content:

        path=os.path.join(root,obj)
        # Name
        row+=td(href(obj.replace('#','%23'),obj))
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

def banner():
    return f"""
    <h3 style="text-align:center">
    <a href={url_for('home')}>Home</a> |
     <a href={url_for('videos')}>Videos</a> |
      <a href={url_for('files')}>Files</a> |
      <a href={url_for('cctv')}>CCTV</a> |
      <a href={url_for('tree')}>Tree</a>
    </h3>
    """

@app.route("/")
def home():
    return f"""
    {banner()}
    <p style="text-align:center">
    Welcome!
    </p>
    """

@app.route("/videos")
def videos():
    return f"""
    {banner()}
    <p style="text-align:center">
    <br>
    <iframe width="1120" height="630" src="https://www.youtube.com/embed/videoseries?list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
    </p>
    """

@app.route("/files/")
@app.route("/files/<path:path>")
def files(path:str=''):
    # if the path string is empty, go to our mounts page
    if not path:
        f=FilesPage()
        data=''
        for i in conf['files.html']['mounts']:
            data+='<tr>'+f.td(f.href(i['path'],i['alias']))+'</tr>'
        return f"""
        {banner()}
        <p style="text-align:center">
        {render_template('files.html',content=banner(),data=data)}
        </p>
        """
                
    # 
    if path:
        # os_path = os.path.join(conf['files.html']['defaultPath'],path)
        # separate path by drive letter and endpoint
        parts = path.split('/')
        drive = parts[0]+':\\'
        if len(parts)>1:
            path = '\\'.join(parts[1:])
        else:
            path=''
        os_path = os.path.join(drive,path)
        # if it's a folder, open up the contents on a new page
        if os.path.isdir(os_path):
            # data = build_file_table(conf['files.html']['defaultPath'],path)
            data = build_file_table(drive,path)
            return f"""
            {banner()}
            <p style="text-align:center">
            {render_template('files.html',content=banner(),data=data)}
            </p>
            """
        # if a path to a file is selected
        else:
            # optionally view the file in browser, if capable. download the file by default
            attach=request.args.get('attach',default=True,type=lambda x: x.lower()=='true')
            return send_file(os_path,as_attachment=attach)        

@app.route("/cctv")
def cctv():
    # return Response(gen(),
    #                 mimetype='multipart/x-mixed-replace; boundary=frame')
    return f"""
    {banner()}
    <br>
    """

@app.route("/tree")
def tree():
    return f"""
    {render_template('tree.html',content=banner())}
    """

if __name__ == '__main__':
    app.run(host="192.168.0.36", port=80)
    # app.run(host="0.0.0.0", port=80)
