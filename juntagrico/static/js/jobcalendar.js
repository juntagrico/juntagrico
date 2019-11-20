// debounce function calls a function delayed
function debounce(fn, delay) {
    var timer = null;
    return function () {
        var context = this, args = arguments;
        clearTimeout(timer);
        timer = setTimeout(function () {
            fn.apply(context, args);
        }, delay);
    };
}

document.addEventListener('DOMContentLoaded', function() {
    // the date format
    var dateFormat = {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    }

    // factory for day lists views
    function list_days(days) {
        return {
            type: 'list',
            buttonText: days +' Tage',
            duration: { days: days },
            listDayFormat: dateFormat,
        }
    }

    // adds tooltips to events
    function add_tooltip(el, event, placement='left', with_title=false) {
        // generate text for tooltip
        var text = ""
        if( with_title ) {
            text += "<div class='tooltip-title'>"+ event.title +"</div>"
        }
        var ep = event.extendedProps
        text += "<pre>"+ ep.summary +"</pre>"
        + "<div class=\'tooltip-list-location\'>Ort: "+ ep.location +"</div>"
        + "<div class=\'tooltip-list-area\'>Bereich: "+ ep.area +"</div>"

        // setup tooltip
        el.data('placement', placement)
        el.data('html', true)
        el.attr('title', text)
    }

    ////////////////////////
    // The Calendar Object
    var calendarEl = document.getElementById('jobs_calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        plugins: [ 'bootstrap', 'dayGrid', 'list' ],
        eventSources: [{
            id: 'original',
            url: json_job_url
        }],
        eventColor: '#66cc66',
        locale: 'de',
        header: {
            left: 'title',
            center: 'list7,dayGridMonth',
            right: 'today prev,next'
        },
        footer: {
            center: 'list7,list30,list90',
        },
        views: {  // create custom views
            list7: list_days(7),
            list30: list_days(30),
            list90: list_days(90),
        },
        defaultView: 'list7',
        themeSystem: 'bootstrap',
        height: 'auto',  // show full height, no scroll bar
        eventRender: function(info) {
            // filter events when searching
            if( !filter_job(info.event) ) {
                return false
            }

            var ep = info.event.extendedProps
            if( info.view.type.startsWith('list') ) {  // if is a list view
                // add more info to the title
                var title_el = $(info.el).find('td.fc-list-item-title')
                title_el.prepend('<span class="area">'+ ep.area +'</span>')
                var info_button = $('<span class="info fas fa-info-circle" onclick="return false">')
                add_tooltip(info_button, info.event)
                title_el.prepend(info_button)
                title_el.append('<span class="location">'+ ep.location +'</span>')
                // replace marker
                var marker_el = $(info.el).find('td.fc-list-item-marker')
                marker_el.find('.fc-event-dot').remove()
                marker_el.addClass('p'+ Math.round(4*ep.occupied_places/ep.slots)*25)
                marker_el.append('<span class="occupied_places">'+ ep.occupied_places +'</span>/<span class="slots">'+ ep.slots +'</span>')

            } else if( info.view.type == 'dayGridMonth' ) {  // if is calendar view
                add_tooltip($(info.el), info.event, 'bottom', true)
            }
        },
        eventPositioned: function(info) {
            // enable tooltip after event has been positioned to get correct location
            $('#jobs_calendar span.info').tooltip()
            $('#jobs_calendar a.fc-day-grid-event').tooltip()
        },
        viewSkeletonRender: function(info) {
            // show more list options in footer, if is a list view
            $('.fc-footer-toolbar').toggle(info.view.type.startsWith('list'))
        }
    });
    calendar.render();

    ////////////////////////
    // Search function

    // the search field
    var search_field = $('#job_search input')

    // event source for calendar, that contains the events found on the server
    var deep_search_event_source = {
        id: 'deep_search',
        url: json_job_url,
        extraParams: function() {
            // add content of search field
            return {'search': search_field.val()}
        }
    }

    // setup debounced refetch of search results
    var refetch_debounced = debounce(function() {
        var event_source = calendar.getEventSourceById('deep_search')
        if( event_source ) {
            event_source.refetch()
        }
    }, 1500 )

    // run search
    var deep_search_active = false
    search_field.on('keyup', function() {
        // rerender (events get filtered on render)
        calendar.render()

        // activate deep search if search field is not empty
        if( $(this).val() != '' ) {
            if( !deep_search_active ) {
                deep_search_active = true
                // add event source for search
                calendar.addEventSource(deep_search_event_source)
            }
            // load more search results from added source but not too fast
            refetch_debounced()
        } else if( deep_search_active )  {
            // disable deep search if field becomes empty
            deep_search_active = false
            var deep_search = calendar.getEventSourceById('deep_search')
            if( deep_search ) {
                deep_search.remove()
            }
        }
    })

    // apply search filter
    function filter_job(event) {
        // if same event was found by deep search, don't show original
        if( calendar.getEventById(event.id+'s') ) {
            return false
        }
        // search by content of search field
        var search_for = new RegExp(search_field.val(), "i")  // make case insensitive
        return event.title.search(search_for) != -1
            || calendar.formatDate(event.start, dateFormat).search(search_for) != -1
            || calendar.formatDate(event.end, dateFormat).search(search_for) != -1
            || event.extendedProps.area.search(search_for) != -1
            || event.extendedProps.location.search(search_for) != -1
            || event.extendedProps.summary.search(search_for) != -1
            || event.extendedProps.search_result.search(search_for) != -1
    }
});