let selectedFrameIndex = 0;

let events = [];
let images = [];

function getDatesBetween(startDate, endDate) {
    const dateArray = [];
    let currentDate = new Date(startDate);
    endDate = new Date(endDate);

    while (currentDate < endDate) {
        dateArray.push(new Date(currentDate).toISOString().split('T')[0]);
        currentDate.setDate(currentDate.getDate() + 1);
    }

    return dateArray;
}

function getDatesMenuItem(date) {
    return "<li date='" + date + "'>" + date + "</li>";
}

function loadDates() {
    $.getJSON("/get-dates", function(data) {
        var items = []

        items.push(getDatesMenuItem(data[0]));

        if (data.length > 1) {
            var datesBetween = getDatesBetween(data[0], data[1]);

            $.each(datesBetween, function(key, val) {
                items.push(getDatesMenuItem(val));
            });

           items.push(getDatesMenuItem(data[1]));
        }

        $('#top-panel').empty().append("<ul>" + items.join("") + "</ul>");

        $('#top-panel > ul > li').on('click', function() {
            window.location.href = "/watcher/" + $(this).attr('date');
        });

    }).fail(function() {
        console.log("Error fetching data.");
        $('#top-panel').text("Failed to load data.");
    });
}

function getFramesMenuItem(event) {
    let time = event.time;

    return "<div event='" + event.id + "'>" + time + "</div>";
}

function loadEvents(date) {
    $.getJSON("/get-events/" + date, function(data) {
        events = data;


        var items = []

        $.each(data, function(key, val) {
            items.push(getFramesMenuItem(val));
        });

        $('#framesList').empty().append(items.join(""));

        loadFrame(0);

        $('#framesList > div').on('click', function() {
            let id = parseInt($(this).attr("event"));
            index = events.map(function(x) {return x.id; }).indexOf(id);
            loadFrame(index);
        });

    }).fail(function() {
        console.log("Error fetching data.");
        $('#framesList').text("Failed to load data.");
    });
}

function setSelected(index) {
    $('#framesList > div').removeClass('selectedFrameItem');
    $('#framesList > div').eq(index).addClass('selectedFrameItem');
}

function loadFrame(index) {
    selectedFrameIndex = index;

    setSelected(index);

    if(selectedFrameIndex == -1){
        selectedFrameIndex = 0;
        return;
    }

    if(selectedFrameIndex >= events.length){
        selectedFrameIndex = events.length;
        return;
    }

    document.getElementById('frame_img').setAttribute('src', '/get-image/' + events[index].media[0].id);

    loadDetections(events[index].id);

    $('#status .date').html('<b>' + (selectedFrameIndex + 1) + '/' + events.length + '</b> ' + events[index].time);
    window.location.hash = (selectedFrameIndex + 1);

    // preload images

    for (var i = 0; i < 11; i++) {
        let frameIndex = selectedFrameIndex - 4 + i;

        if(selectedFrameIndex !== frameIndex && frameIndex >= 0 && frameIndex < events.length){
            images[i] = new Image();
            images[i].src = '/get-image/' + events[frameIndex].media[0].id;
        }

    }

}

function keyPress(e) {
    e = e || window.event;

    if (e.keyCode == '37') {
       // left arrow
       loadFrame(--selectedFrameIndex);
    }
    else if (e.keyCode == '39') {
       // right arrow
       loadFrame(++selectedFrameIndex);
    }
}

function setKeyboard() {
    document.onkeydown = keyPress;
}

function openFullImage(img) {
    var imageUrl = img.src + "?mode=full";
    window.open(imageUrl, '_blank');
}

function loadDetections(eventId) {
    $.getJSON("/get-detections/" + eventId, function(data) {
        $('#frame .detection_frame').remove();

        console.log(data);

        $.each(data, function(key, val) {
            let width = val.width + "%";
            let height = val.height + "%";

            let left = val.left + "%";
            let top = val.top + "%";

            let item = $("<div class='detection_frame'></div>")
                            .css("width", width)
                            .css("height", height)
                            .css("left", left)
                            .css("top", top);

            if (val.mode) {
                item.addClass('mode_' + val.mode);
            }

            item.on("mouseenter", function() {
                $('#status .info').html(val.type + ' ' + val.confidence + '% (' + val.mode + ')');
            });

            item.on("mouseout", function() {
                $('#status .info').html('');
            });

            $('#frame').append(item);
        });

    }).fail(function() {
        console.log("Error fetching data.");
        $('#frame .detection_frame').remove();
    });
}

let hash = parseInt(window.location.hash.replace('#', ''));

if(hash > 0 && hash < events.length){
    selectedFrameIndex = hash - 1;
    loadFrame(selectedFrameIndex);
}