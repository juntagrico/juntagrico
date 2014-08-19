/*global define*/
define([], function () {
    var dable = new Dable("jobs");
    dable.columnData[0].CustomRendering = function (cellValue) {
        return cellValue.split("||")[0];
    }
    dable.columnData[0].CustomSortFunc = function (columnIndex, ascending, currentRows) {
        currentRows.sort(function (a, b) {
            var a = a[0].split("||")[1];
            var b = b[0].split("||")[1];
            return ascending ? a - b : b - a;
        });
        return currentRows;
    }
    dable.UpdateDisplayedRows();        // Update the table
    dable.UpdateStyle();                // Reapply our styles
});