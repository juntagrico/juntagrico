/*global define */
define([], function () {

    let markers = map_with_markers(
        JSON.parse(document.getElementById('depots').textContent),
        JSON.parse(document.getElementById('selected_depot').textContent)
    )
    $('#depot').on('change', function(e){
        open_marker(markers, $("option:selected", this)[0].text)
    })

});