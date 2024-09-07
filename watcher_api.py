import json
import os

from flask import Flask, render_template, send_file, send_from_directory, abort, request
import flask_resize

from peewee import fn

from playhouse.shortcuts import model_to_dict

from db.models import Event, Media, Detection
from db import get_db, close_db

# from json import dumps

app = Flask(__name__)
app.config['RESIZE_URL'] = os.path.dirname(__file__) + '/media/'
app.config['RESIZE_ROOT'] = os.path.dirname(__file__) + '/media'

resize = flask_resize.Resize(app)

# to access media directory from current dir
static_directory_path = "./static/"

@app.before_request
def before_request():
    get_db()

@app.teardown_request
def teardown_request(exception):
    close_db()

@app.route("/get-dates")
def api_dates():
    earliest_date = Event.select(fn.MIN(Event.date)).scalar()
    latest_date = Event.select(fn.MAX(Event.date)).scalar()

    dates = [earliest_date]

    if earliest_date != latest_date:
        dates.append(latest_date)

    # dates.append("2024-06-26")

    dump = json.dumps(dates, indent=4, sort_keys=True, default=str)

    return f'{dump}'


@app.route("/get-events/<date>")
def api_events(date):
    events = []

    query = (Event
             .select(Event.id,
                     Event.type,
                     Event.date,
                     Event.time,
                     fn.CONCAT("[",
                                  fn.GROUP_CONCAT(
                            fn.JSON_OBJECT('id', Media.id, 'type', Media.type, 'file', Media.file)
                        ), "]").alias('media'))
             .where(Event.date == date)
             .join(Media, on=(Event.id == Media.relation))
             .order_by(Event.time.asc())
             .group_by(Event.id))

    for event in query:
        item = model_to_dict(event)
        item['media'] = json.loads(event.media)

        events.append(item)

    dump = json.dumps(events, indent=4, sort_keys=True, default=str)

    return f'{dump}'


@app.route("/get-image/<int:media_id>")
def api_image(media_id):
    query = Media.select(Media.file).where(Media.id == media_id)

    if not query.exists():
        abort(404)

    media = query.get()

    if media.file.lower().endswith(('.png', '.jpg', '.jpeg')):
        file_path = os.path.abspath(media.file)

        if os.path.exists(file_path):
            isFull = request.args.get('mode') == 'full'

            if isFull is False:
                # check is resized images dir exists
                resized_images_path = app.config['RESIZE_ROOT'] + '/resized-images'
                if os.path.exists(os.path.abspath(resized_images_path)) is False:
                    abort(500, description=f"no dir {os.path.abspath(resized_images_path)}")

                thumbPath = os.path.abspath(resize(file_path, '640x480'))

                if os.path.exists(thumbPath):
                    return send_file(thumbPath)
                else:
                    abort(404)
            else:
                return send_file(file_path)
        else:
            abort(404)
    else:
        abort(400)


@app.route("/get-detections/<int:event_id>")
def api_detections(event_id):
    #TODO: make media resolution dynamic?
    MEDIA_WIDTH = 3072
    MEDIA_HEIGHT = 2048

    detections = []

    query = (Detection.select(Detection.id, Detection.type, Detection.confidence,
                             Detection.x1, Detection.x2, Detection.y1, Detection.y2, Detection.mode)
             .where(Detection.relation == event_id))#, Detection.mode == 'detailed'))

    if not query.exists():
        abort(404)

    for detection in query:
        width = round((detection.x2 - detection.x1) / MEDIA_WIDTH * 100, 3)
        height = round((detection.y2 - detection.y1) / MEDIA_HEIGHT * 100, 3)

        left = round(detection.x1 / MEDIA_WIDTH * 100, 3)
        top = round(detection.y1 / MEDIA_HEIGHT * 100, 3)

        item = {"id": detection.id, "type": detection.type, "confidence": detection.confidence,
                "width": width, "height": height, "left": left, "top": top, "mode": detection.mode}

        detections.append(item)

    dump = json.dumps(detections, indent=4, sort_keys=True, default=str)

    return f'{dump}'


@app.route("/watcher", strict_slashes=False)
def web_index():
    return render_template('index.html')


@app.route("/watcher/<date>")
def web_events(date):
    return render_template('viewEvents.html', date=date)


@app.route("/static/<file>")
def web_static(file):
    return send_from_directory(static_directory_path, file)

if __name__ == "__main__":
    app.run(port=6670, debug=True)
