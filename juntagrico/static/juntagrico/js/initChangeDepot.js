/*global define */
define([], function () {

    let [map, markers] = map_with_markers(
        JSON.parse(document.getElementById('depots').textContent),
        JSON.parse(document.getElementById('selected_depot').textContent)
    )

    init_depot_map(map, markers)
});