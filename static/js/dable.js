!(function (define) {
    define([], function () {
        return function (tableId) {
            var $export = {
                id: tableId,
                columns: [],
                rows: [],
                visibleRows: [],
                hiddenColumns: [],
                currentFilter: '',
                sortColumn: null,
                sortOrder: 'descending',
                minimumSearchLength: 1,
                columnData: [],
                pageNumber: 0,
                pageSize: 100000,
                pageSizes: [10, 25, 50, 100],
                pagerSize: 0,
                pagerIncludeFirstAndLast: false,
                async: false,
                asyncData: {},
                asyncStart: 0,
                asyncLength: 1000,
                style: 'none',
                evenRowColor: 'rgba(76, 148, 52, 0.1)',
                oddRowColor: '#fffff7'
            };

            $export.RowCount = function () {
                return $export.rows.length;
            }
            $export.VisibleRowCount = function () {
                return $export.visibleRows.length;
            }
            $export.NumberOfPages = function () {
                var n = $export.VisibleRowCount() / $export.pageSize;
                return Math.ceil(n);
            };
            $export.GetPageForRow = function (row) {
                return Math.ceil(row / $export.pageSize);
            }

            $export.asyncRequest = function (start, filter, sortColumn, ascending, asynchronous) {
                if (typeof asynchronous == 'undefined') {
                    asynchronous = false;
                }
                var dableRequest = new XMLHttpRequest();
                dableRequest.onreadystatechange = function () {
                    if (dableRequest.readyState == 4 && dableRequest.status == 200) {
                        var data = JSON.parse(dableRequest.responseText);
                        var actualData = JSON.parse(data.d);    //stupid json
                        var actualRows = actualData.rows;
                        //create empty rows for the rest of the set
                        actualRows.reverse();
                        for (var i = 0; i < start; ++i) {
                            actualRows.push([]);
                        }
                        actualRows.reverse();
                        for (var i = (start + $export.asyncLength); i < actualData.includedRowCount; ++i) {
                            actualRows.push([]);
                        }
                        //update
                        $export.SetDataAsRows(actualRows);
                        $export.RowCount = function () {
                            return actualData.rowCount;
                        };
                        $export.VisibleRowCount = function () {
                            return actualData.includedRowCount;
                        };
                        if (asynchronous != false && !!(asynchronous && asynchronous.call && asynchronous.apply)) {
                            asynchronous();
                        }
                    }
                }
                dableRequest.open('POST', $export.async, asynchronous != false);
                dableRequest.setRequestHeader('content-type', 'application/json');
                var requestObject = JSON.parse(JSON.stringify($export.asyncData));
                requestObject['start'] = start;
                $export.asyncStart = start;
                requestObject['count'] = $export.asyncLength;
                requestObject['filter'] = filter;
                requestObject['sortColumn'] = sortColumn == null ? -1 : sortColumn;
                requestObject['ascending'] = ascending;
                dableRequest.send(JSON.stringify(requestObject));
            }
            $export.searchFunc = function (event) {
                var searchBox = this;
                if (searchBox.id != $export.id + '_search') {
                    return false;
                }
                if (!searchBox.value || searchBox.value.length < $export.minimumSearchLength) {
                    $export.currentFilter = '';
                }
                else {
                    var searchText = searchBox.value;
                    $export.currentFilter = searchText;
                }
                if ($export.async) {
                    var ascending = true;
                    if ($export.sortOrder.length > 3 && $export.sortOrder.substr(0, 4).toLowerCase() == 'desc') {
                        ascending = false;
                    }
                    //search is wired up to be async so the user can keep typing, but it creates a race condition
                    //that is not conducive to fast typing, so I'll have to figure out a fix
                    $export.asyncRequest(0, $export.currentFilter, $export.sortColumn, ascending);
                    var body = document.getElementById($export.id + '_body');
                    $export.UpdateDisplayedRows(body);
                    $export.UpdateStyle(document.getElementById($export.id));
                }
                else {
                    var includedRows = [];
                    if ($export.currentFilter) {
                        for (var i = 0; i < $export.filters.length; ++i) {
                            for (var j = 0; j < $export.rows.length; ++j) {
                                if (ArrayContains(includedRows, $export.rows[j])) {
                                    continue;
                                }
                                for (var k = 0; k < $export.rows[j].length; ++k) {
                                    if ($export.filters[i]($export.currentFilter, $export.rows[j][k])) {
                                        includedRows.push($export.rows[j]);
                                        break;
                                    }
                                }
                            }
                        }
                    }
                    else {
                        includedRows = $export.rows;
                    }
                    $export.visibleRows = includedRows;
                    var body = document.getElementById($export.id + '_body');
                    $export.UpdateDisplayedRows(body);
                    $export.UpdateStyle(document.getElementById($export.id));
                }
            };
            $export.sortFunc = function (event) {
                var tag = this.tagName;
                //prevent sorting from some form elements
                if (tag != 'INPUT' && tag != 'BUTTON' && tag != 'SELECT' && tag != 'TEXTAREA') {
                    var columnCell = this;  //use this here, as the event.srcElement is probably a <span>
                    var sortSpan = columnCell.querySelector('.table-sort');
                    var columnTag = columnCell.getAttribute('data-tag');
                    var columnIndex = -1;

                    for (var i = 0; i < $export.columnData.length; ++i) {
                        if ($export.columnData[i].Tag.toLowerCase() == columnTag.toLowerCase()) {
                            columnIndex = i;
                            break;
                        }
                    }
                    if (columnIndex == -1) {
                        return false;
                    }
                    $export.sortColumn = columnIndex;
                    var ascend = false;
                    if ($export.sortOrder.length > 3 && $export.sortOrder.substr(0, 4).toLowerCase() == 'desc') {
                        ascend = true;  //switching from descending to ascending
                    }
                    if (ascend) {
                        $export.sortOrder = 'asc';
                        sortSpan.innerHTML = '^';
                    }
                    else {
                        $export.sortOrder = 'desc';
                        sortSpan.innerHTML = 'v';
                    }

                    if ($export.async) {
                        $export.asyncRequest($export.asyncStart, $export.currentFilter, columnIndex, ascend);
                    }
                    else if ($export.columnData[columnIndex].CustomSortFunc) {
                        $export.visibleRows = $export.columnData[columnIndex].CustomSortFunc(columnIndex, ascend, $export.visibleRows);
                    }
                    else {
                        $export.visibleRows = $export.baseSort(columnIndex, ascend, $export.visibleRows);
                    }

                    $export.UpdateDisplayedRows(document.getElementById($export.id + '_body'));
                    $export.UpdateStyle();
                }
            };

            $export.baseSort = function (columnIndex, ascending, currentRows) {
                var isInt = true;
                var newRows = currentRows.slice(0);
                for (var i = 0; i < currentRows.length; ++i) {
                    if (parseInt(currentRows[i][columnIndex]).toString().toLowerCase() == 'nan') {
                        isInt = false;
                        break;
                    }
                }

                if (isInt) {
                    newRows = newRows.sort(function (a, b) {
                        return parseInt(a[columnIndex]) - parseInt(b[columnIndex]);
                    });
                }
                else {
                    newRows = newRows.sort(function (a, b) {
                        if (a[columnIndex] > b[columnIndex]) {
                            return 1;
                        }
                        else if (a[columnIndex] < b[columnIndex]) {
                            return -1;
                        }
                        else {
                            return 0;
                        }
                    });
                }

                if (!ascending) {
                    newRows = newRows.reverse();
                }

                return newRows;
            };
            $export.filters = [
                //PHRASES FILTER
                function (searchText, value) {
                    searchText = searchText.toString().toLowerCase();
                    value = value.toString().toLowerCase();
                    var phrases = [];
                    var regex = /\s*".*?"\s*/g;
                    var match;
                    while (match = regex.exec(searchText)) {
                        var phrase = match[0].replace(/"/g, '').trim();
                        phrases.push(phrase);
                        searchText = searchText.replace(match[0], " ");
                    }

                    for (var i = 0; i < phrases.length; ++i) {
                        if (value.indexOf(phrases[i]) > -1) {
                            return true;
                        }
                    }
                    return false;
                },
                //WORDS FILTER, IGNORING PHRASES
                function (searchText, value) {
                    searchText = searchText.toString().toLowerCase();
                    value = value.toString().toLowerCase();
                    var regex = /\s*".*?"\s*/g;
                    var match;
                    while (match = regex.exec(searchText)) {
                        searchText = searchText.replace(match[0], ' ');
                    } //remove phrases
                    var splitText = searchText.split(' ');
                    for (var i = 0; i < splitText.length; ++i) {
                        if (!splitText[i]) {  //clear out empty strings
                            splitText.splice(i, 1);
                            --i;
                        }
                    }

                    for (var i = 0; i < splitText.length; ++i) {
                        if (value.indexOf(splitText[i]) > -1) {
                            return true;
                        }
                    }
                    return false;
                }
            ];

            $export.SetColumnNames = function (columnNames) {
                if (!columnNames) {
                    return false;
                }
                ;

                for (var i = 0; i < columnNames.length; ++i) {
                    if ($export.columnData.length <= i) {
                        $export.columnData.push({
                            Tag: columnNames[i],
                            FriendlyName: columnNames[i],
                            CustomSortFunc: null,
                            CustomRendering: null
                        });
                    }
                    else {
                        $export.columnData[i].Name = columnNames[i];
                    }
                }
            };
            $export.SetDataAsColumns = function (columns) {
                if (!columns) {
                    return false;
                }

                var tableRows = [];
                for (var i = 0; i < columns.length; ++i) {
                    while (tableRows.length < columns[i].length) {
                        tableRows.push([]);
                    }
                    for (var j = 0; j < columns[i].length; ++j) {
                        tableRows[j][i] = columns[i][j];
                    }
                }
                ;

                $export.columns = columns;
                $export.rows = tableRows;
            };
            $export.SetDataAsRows = function (rows) {
                if (!rows) {
                    return false;
                }

                var tableColumns = [];
                for (var i = 0; i < rows.length; ++i) {
                    while (tableColumns.length < rows[i].length) {
                        tableColumns.push([]);
                    }
                    for (var j = 0; j < rows[i].length; ++j) {
                        tableColumns[j][i] = rows[i][j];
                    }
                }

                $export.columns = tableColumns;
                $export.rows = rows;
                $export.visibleRows = rows;
            };

            $export.UpdateDisplayedRows = function (body) {
                if (!body) {
                    body = document.getElementById($export.id + '_body');
                    if (!body) {
                        return false;
                    }
                }
                var tempBody = body.cloneNode(false);
                while (tempBody.firstChild) {
                    tempBody.removeChild(tempBody.firstChild);
                }
                var displayedRows = [];
                var row = document.createElement('tr');
                var cell = document.createElement('td');
                //get the display start id
                var pageDisplay = ($export.pageNumber * $export.pageSize);
                if ($export.VisibleRowCount() <= pageDisplay) {    //if this is too big, go back to page 1
                    $export.pageNumber = 0;
                    pageDisplay = 0;
                }
                //get the display end id
                var length = pageDisplay + $export.pageSize;
                if (pageDisplay + $export.pageSize >= $export.VisibleRowCount()) { //if this is too big, only show remaining rows
                    length = $export.VisibleRowCount();
                }
                //loop through the visible rows and display this page
                var rows = [];
                for (var i = pageDisplay; i < length; ++i) {
                    var tempRow = row.cloneNode(false);
                    if (i % 2 == 0) {
                        tempRow.setAttribute('class', 'table-row-even');
                    }
                    else {
                        tempRow.setAttribute('class', 'table-row-odd');
                    }

                    for (var j = 0; j < $export.visibleRows[i].length; ++j) {
                        var tempCell = cell.cloneNode(false);
                        var text = $export.visibleRows[i][j];
                        if ($export.columnData[j].CustomRendering != null) {
                            text = $export.columnData[j].CustomRendering(text);
                        }
                        tempCell.innerHTML = text;
                        tempRow.appendChild(tempCell);
                    }
                    tempBody.appendChild(tempRow);
                }

                if (body.parentElement) {
                    body.parentElement.replaceChild(tempBody, body);
                }
                body = tempBody;

                var footer = document.getElementById($export.id + '_footer');
                $export.UpdateFooter(footer);
                return body;
            };
            $export.UpdateFooter = function (footer) {
                if (!footer) {
                    return false;
                }
                var start = ($export.pageNumber * $export.pageSize) + 1;
                var end = start + $export.pageSize - 1;
                if (end > $export.VisibleRowCount()) {
                    end = $export.VisibleRowCount();
                }

                var showing = footer.querySelector('#' + $export.id + '_showing');
                if (showing) {
                    showing.innerHTML = "Du siehst insgesamt " + ($export.VisibleRowCount()) + " Einträge";
                    if ($export.VisibleRowCount() != $export.RowCount()) {
                        showing.innerHTML += " (gefiltert, von insgesamt " + ($export.RowCount()) + " Einträgen)";
                    }
                }
                var right = footer.querySelector('#' + $export.id + '_page_prev').parentElement;
                footer.replaceChild($export.BuildPager(), right);

                return footer;
            };
            $export.UpdateStyle = function (tableDiv, style) {
                if (!tableDiv) {
                    tableDiv = document.getElementById($export.id);
                    if (!tableDiv) {
                        return false;
                    }
                }
                if (!style) {
                    style = $export.style;
                }
                $export.style = style;

                //initial style cleanup
                $export.RemoveStyles(tableDiv);
                //clear is a style option to completely avoid any styling so you can roll your own
                if (style.toLowerCase() != 'clear') {
                    //base styles for 'none', the other styles sometimes build on these, so we apply them beforehand
                    $export.ApplyBaseStyles(tableDiv);

                    if (style.toLowerCase() == 'none') {
                        return true;
                    }
                    else {
                        if (style.toLowerCase() == 'jqueryui') {
                            $export.ApplyJqueryUIStyles(tableDiv);
                        }
                        else if (style.toLowerCase() == 'bootstrap') {
                            $export.ApplyBootstrapStyles(tableDiv);
                        }
                    }
                }
            };

            $export.RemoveStyles = function (tableDiv) {
                tableDiv.removeAttribute('class');
                var children = tableDiv.children;
                for (var i = 0; i < children.length; ++i) {
                    children[i].removeAttribute('class');
                }
                var header = children[0];
                var headerChildren = header.children;
                for (var i = 0; i < headerChildren.length; ++i) {
                    headerChildren[i].removeAttribute('class');
                }

                var table = children[1];
                var thead = table.children[0];
                thead.removeAttribute('class');
                thead.children[0].removeAttribute('class');
                var theadCells = thead.children[0].children;
                for (var i = 0; i < theadCells.length; ++i) {
                    theadCells[i].removeAttribute('class');
                }
                var sorts = tableDiv.querySelectorAll('.table-sort');
                for (var i = 0; i < sorts.length; ++i) {
                    sorts[i].innerHTML = '^';
                    sorts[i].setAttribute('class', 'table-sort');
                    if (i == $export.sortColumn) {
                        if ($export.sortOrder.toLowerCase().substr(0, 4) == 'desc') {
                            sorts[i].innerHTML = 'v';
                        }
                    }
                }

                var tbody = table.children[1];
                tbody.removeAttribute('class');

                var footer = children[2];
                var footerChildren = footer.children;
                var leftChildren = footerChildren[0].children;
                for (var i = 0; i < leftChildren.length; ++i) {
                    leftChildren[i].removeAttribute('class');
                }
                var right = footer.querySelector('#' + $export.id + '_page_prev').parentElement;
                footer.replaceChild($export.BuildPager(), right);

                RemoveStyle(tableDiv);  //recursive function to remove style attributes
            }
            $export.ApplyBaseStyles = function (tableDiv) {
                var table = tableDiv.querySelector('table');
                table.setAttribute('style', 'width: 100%;');

                var oddRows = tableDiv.querySelectorAll('.table-row-odd');
                for (var i = 0; i < oddRows.length; ++i) {
                    oddRows[i].setAttribute('style', 'background-color: ' + $export.oddRowColor);
                }
                var evenRows = tableDiv.querySelectorAll('.table-row-even');
                for (var i = 0; i < evenRows.length; ++i) {
                    evenRows[i].setAttribute('style', 'background-color: ' + $export.evenRowColor);
                }
                var cells = tableDiv.querySelectorAll('td');
                for (var i = 0; i < cells.length; ++i) {
                    cells[i].setAttribute('style', 'padding: 5px;');
                }

                var headCells = tableDiv.querySelectorAll('th');
                for (var i = 0; i < headCells.length; ++i) {
                    headCells[i].setAttribute('style', 'padding: 5px;');
                    var headCellLeft = headCells[i].children[0];
                    headCellLeft.setAttribute('style', 'float: left');
                    if ($export.columnData[i].CustomSortFunc !== false) {
                        var headCellRight = headCells[i].children[1];
                        headCellRight.setAttribute('style', 'float: right');
                        var headCellClear = headCells[i].children[2];
                        headCellClear.setAttribute('style', 'clear: both;');

                        headCells[i].onmouseover = function () {
                            this.setAttribute('style', 'padding: 5px; cursor: pointer');
                        };
                        headCells[i].onmouseout = function () {
                            this.setAttribute('style', 'padding: 5px; cursor: default');
                        };
                    }
                    else {
                        var headCellClear = headCells[i].children[1];
                        headCellClear.setAttribute('style', 'clear: both;');
                    }
                }

                var header = tableDiv.querySelector('#' + $export.id + '_header');
                header.setAttribute('style', 'padding: 5px;');
                var headLeft = header.children[0];
                headLeft.setAttribute('style', 'float: left;');
                var headRight = header.children[1];
                headRight.setAttribute('style', 'float: right;');
                var headClear = header.children[2];
                headClear.setAttribute('style', 'clear: both;');

                var footer = tableDiv.querySelector('#' + $export.id + '_footer');
                footer.setAttribute('style', 'padding: 5px;');
                var footLeft = footer.children[0];
                footLeft.setAttribute('style', 'float: left;');
                var footClear = footer.children[2];
                footClear.setAttribute('style', 'clear: both;');
                var footRight = footer.children[1];
                footRight.setAttribute('style', 'float: right; list-style: none;');
                var footRightItems = footRight.querySelectorAll('li');
                for (var i = 0; i < footRightItems.length; ++i) {
                    footRightItems[i].setAttribute('style', 'display: inline; margin-right: 5px;');
                }
            }
            $export.ApplyJqueryUIStyles = function (tableDiv) {
                if (!tableDiv) {
                    return false;
                }
                var header = tableDiv.querySelector('#' + $export.id + '_header');
                var footer = tableDiv.querySelector('#' + $export.id + '_footer');
                var span = document.createElement('span');

                header.setAttribute('class', 'fg-toolbar ui-widget-header ui-corner-tl ui-corner-tr ui-helper-clearfix');

                var headCells = tableDiv.querySelectorAll('th');
                for (var i = 0; i < headCells.length; ++i) {
                    headCells[i].setAttribute('class', 'ui-state-default');
                    var sort = headCells[i].querySelector('.table-sort');
                    if (sort) {
                        if (sort.innerHTML == 'v') {
                            sort.setAttribute('class', 'table-sort ui-icon ui-icon-triangle-1-s');
                        }
                        else {
                            sort.setAttribute('class', 'table-sort ui-icon ui-icon-triangle-1-n');
                        }
                        sort.innerHTML = '';
                    }
                }

                var pagerItems = footer.querySelectorAll('li');
                for (var i = 0; i < pagerItems.length; ++i) {
                    RemoveStyle(pagerItems[i]);
                }
                footer.setAttribute('class', 'fg-toolbar ui-widget-header ui-corner-bl ui-corner-br ui-helper-clearfix');
                var pageClass = 'fg-button ui-button ui-state-default ui-corner-left table-page';

                var pageButtons = footer.querySelectorAll('.table-page');
                for (var i = 0; i < pageButtons.length; ++i) {
                    pageButtons[i].setAttribute('class', pageClass);
                }

                var pageLeft = footer.querySelector('#' + $export.id + '_page_prev');
                pageLeft.innerHTML = '';
                var pageLeftSpan = span.cloneNode(false);
                pageLeftSpan.setAttribute('class', 'ui-icon ui-icon-circle-arrow-w');
                pageLeft.appendChild(pageLeftSpan);
                if (pageLeft.getAttribute('disabled')) {
                    pageLeft.setAttribute('class', pageClass + ' ui-state-disabled');
                }
                var pageRight = footer.querySelector('#' + $export.id + '_page_next');
                pageRight.innerHTML = '';
                var pageRightSpan = span.cloneNode(false);
                pageRightSpan.setAttribute('class', 'ui-icon ui-icon-circle-arrow-e');
                pageRight.appendChild(pageRightSpan);
                if (pageRight.getAttribute('disabled')) {
                    pageRight.setAttribute('class', pageClass + ' ui-state-disabled');
                }

                if ($export.pagerIncludeFirstAndLast) {
                    var pageFirst = footer.querySelector('#' + $export.id + '_page_first');
                    var pageLast = footer.querySelector('#' + $export.id + '_page_last');
                    pageFirst.innerHTML = '';
                    var pageFirstSpan = span.cloneNode(false);
                    pageFirstSpan.setAttribute('class', 'ui-icon ui-icon-arrowthickstop-1-w');
                    pageFirst.appendChild(pageFirstSpan);
                    pageLast.innerHTML = '';
                    var pageLastSpan = span.cloneNode(false);
                    pageLastSpan.setAttribute('class', 'ui-icon ui-icon-arrowthickstop-1-e');
                    pageLast.appendChild(pageLastSpan);
                }
            };
            $export.ApplyBootstrapStyles = function (tableDiv) {
                if (!tableDiv) {
                    return false;
                }
                var div = document.createElement('div');
                var span = document.createElement('span');
                var header = tableDiv.querySelector('#' + $export.id + '_header');
                var footer = tableDiv.querySelector('#' + $export.id + '_footer');
                var table = tableDiv.querySelector('table');
                table.setAttribute('class', 'table table-bordered table-striped');
                table.setAttribute('style', 'width: 100%; margin-bottom: 0;');
                header.setAttribute('class', 'panel-heading');
                footer.setAttribute('class', 'panel-footer');
                tableDiv.setAttribute('class', 'panel panel-info');
                tableDiv.setAttribute('style', 'margin-bottom: 0;');

                var tableRows = table.querySelectorAll('.tbody tr');
                for (var i = 0; i < tableRows.length; ++i) {    //remove manual striping
                    tableRows[i].removeAttribute('style');
                }

                var headCells = table.querySelectorAll('th');
                for (var i = 0; i < headCells.length; ++i) {
                    var sort = headCells[i].querySelector('.table-sort');
                    if (sort) {
                        if (sort.innerHTML == 'v') {
                            sort.setAttribute('class', 'table-sort glyphicon glyphicon-chevron-down');
                        }
                        else {
                            sort.setAttribute('class', 'table-sort glyphicon glyphicon-chevron-up');
                        }
                        sort.innerHTML = '';
                    }
                }

                var pageClass = 'btn btn-default table-page';
                var pageLeft = footer.querySelector('#' + $export.id + '_page_prev');
                var pageRight = footer.querySelector('#' + $export.id + '_page_next');
                var pageParent = pageLeft.parentElement;

                var pagerItems = footer.querySelectorAll('li');
                for (var i = 0; i < pagerItems.length; ++i) {
                    RemoveStyle(pagerItems[i]);
                }

                pageParent.setAttribute('class', 'btn-group');

                pageLeft.innerHTML = '';
                var pageLeftSpan = span.cloneNode(false);
                pageLeftSpan.setAttribute('class', 'glyphicon glyphicon-arrow-left');
                pageLeft.appendChild(pageLeftSpan);

                pageRight.innerHTML = '';
                var pageRightSpan = span.cloneNode(false);
                pageRightSpan.setAttribute('class', 'glyphicon glyphicon-arrow-right');
                pageRight.appendChild(pageRightSpan);

                if ($export.pagerIncludeFirstAndLast) {
                    var pageFirst = footer.querySelector('#' + $export.id + '_page_first');
                    var pageLast = footer.querySelector('#' + $export.id + '_page_last');
                    pageFirst.innerHTML = '';
                    var pageFirstSpan = span.cloneNode(false);
                    pageFirstSpan.setAttribute('class', 'glyphicon glyphicon-fast-backward');
                    pageFirst.appendChild(pageFirstSpan);
                    pageLast.innerHTML = '';
                    var pageLastSpan = span.cloneNode(false);
                    pageLastSpan.setAttribute('class', 'glyphicon glyphicon-fast-forward');
                    pageLast.appendChild(pageLastSpan);
                }

                var pageButtons = footer.querySelectorAll('.table-page');
                for (var i = 0; i < pageButtons.length; ++i) {
                    pageButtons[i].setAttribute('class', pageClass);
                }
            };

            $export.CheckForTable = function () {//Check for existing table
                var tableDiv = document.getElementById($export.id);
                if (tableDiv) {
                    var table = tableDiv.querySelector("table");
                    if (table) {
                        var newTable = $export.GenerateTableFromHtml(table);	//Make it a Dable!
                        $export.BuildAll(newTable);
                        return true;
                    }
                }
                return false;
            }
            $export.GenerateTableFromHtml = function (tableNode) {
                if (!tableNode) {
                    return false;
                }
                var headers = tableNode.querySelectorAll("thead tr th");
                var colNames = [];
                for (var i = 0; i < headers.length; ++i) {	//add our column names
                    colNames.push(headers[i].innerHTML);
                }
                $export.SetColumnNames(colNames);

                var rowsHtml = tableNode.querySelectorAll("tbody tr");
                var allRows = [];
                for (var i = 0; i < rowsHtml.length; ++i) {
                    allRows.push([]);
                    var rowCells = rowsHtml[i].children;
                    for (var j = 0; j < rowCells.length; ++j) {
                        allRows[i].push(rowCells[j].innerHTML);
                    }
                }
                $export.SetDataAsRows(allRows);

                var parentDiv = tableNode.parentElement;
                parentDiv.innerHTML = '';

                return parentDiv.id;
            };

            $export.BuildAll = function (tableId) {
                if (!tableId) {
                    tableId = $export.id;
                }
                $export.id = tableId;
                var tableDiv = document.getElementById(tableId);

                if (!tableDiv) {
                    if (!$export.rows || $export.rows.length < 1) {
                        if ($export.CheckForTable()) {
                            return true;	//build table off of existing data
                        }
                    }
                    else {
                        return false;   //get the right element type
                    }
                }
                else if (tableDiv.nodeName.toLowerCase() != 'div') {
                    return false;
                }

                if ($export.async) {
                    $export.asyncRequest(0, '', -1, true);
                }

                tableDiv.innerHTML = '';

                var header = $export.BuildHeader(tableDiv);
                var table = $export.BuildTable(tableDiv);
                var footer = $export.BuildFooter(tableDiv);

                tableDiv.appendChild(header);
                tableDiv.appendChild(table);
                tableDiv.appendChild(footer);

                $export.UpdateStyle(tableDiv);
            };
            $export.BuildHeader = function (tableDiv) {
                if (!tableDiv) {
                    return false;
                }
                var div = document.createElement('div');
                var span = document.createElement('span');
                var select = document.createElement('select');
                var option = document.createElement('option');
                var input = document.createElement('input');

                var left = div.cloneNode(false);
                var show = span.cloneNode(false);
                show.innerHTML = 'Zeige ';
//				left.appendChild(show);
                var entryCount = select.cloneNode(false);
                for (var i = 0; i < $export.pageSizes.length; ++i) {
                    var tempOption = option.cloneNode(false);
                    tempOption.innerHTML = $export.pageSizes[i];
                    tempOption.setAttribute('value', $export.pageSizes[i]);
                    entryCount.appendChild(tempOption);
                }
                entryCount.onchange = function () {
                    var entCnt = this;
                    var value = entCnt.value;
                    $export.pageSize = parseInt(value);
                    $export.UpdateDisplayedRows(document.getElementById($export.id + '_body'));
                    $export.UpdateStyle(tableDiv);
                };
//				left.appendChild(entryCount);

                var right = div.cloneNode(false);
                var search = span.cloneNode(false);
                search.innerHTML = 'Hier Filtern: ';
                right.appendChild(search);
                var inputSearch = input.cloneNode(false);
                inputSearch.setAttribute('id', $export.id + '_search');
                inputSearch.onkeyup = $export.searchFunc;
                right.appendChild(inputSearch);

                var clear = div.cloneNode(false);

                var head = div.cloneNode(false);
                head.id = $export.id + '_header';
                head.appendChild(left);
                head.appendChild(right);
                head.appendChild(clear);

                return head;
            };
            $export.BuildTable = function (tableDiv) {
                if (!tableDiv) {
                    return false;
                }
                //all the elements we need to build a neat table
                var table = document.createElement('table');
                var head = document.createElement('thead');
                var headCell = document.createElement('th');
                var body = document.createElement('tbody');
                var row = document.createElement('tr');
                var span = document.createElement('span');
                //The thead section contains the column names
                var headRow = row.cloneNode(false);
                for (var i = 0; i < $export.columnData.length; ++i) {
                    var tempCell = headCell.cloneNode(false);
                    var nameSpan = span.cloneNode(false);
                    nameSpan.innerHTML = $export.columnData[i].FriendlyName + ' ';
                    tempCell.appendChild(nameSpan);

                    if ($export.columnData[i].CustomSortFunc !== false) {
                        var sortSpan = span.cloneNode(false);
                        sortSpan.setAttribute('class', 'table-sort');
                        sortSpan.innerHTML = 'v';
                        tempCell.appendChild(sortSpan);
                        tempCell.onclick = $export.sortFunc;
                    }

                    var clear = span.cloneNode(false);
                    tempCell.appendChild(clear);

                    tempCell.setAttribute('data-tag', $export.columnData[i].Tag);
                    headRow.appendChild(tempCell);
                }
                head.appendChild(headRow);
                table.appendChild(head);

                $export.visibleRows = $export.rows;
                body = $export.UpdateDisplayedRows(body);
                body.id = $export.id + '_body';
                table.appendChild(body);

                return table;
            };
            $export.BuildFooter = function (tableDiv) {
                if (!tableDiv) {
                    return false;
                }
                var div = document.createElement('div');
                var span = document.createElement('span');
                var button = document.createElement('button');

                var left = div.cloneNode(false);
                var showing = span.cloneNode(false);
                showing.id = $export.id + '_showing';
                left.appendChild(showing);

                var right = $export.BuildPager(footer);

                var clear = div.cloneNode(false);

                var footer = div.cloneNode(false);
                footer.id = $export.id + '_footer';
                footer.innerHTML = '';
                footer.appendChild(left);
                footer.appendChild(right);
                footer.appendChild(clear);
                return $export.UpdateFooter(footer);
            };
            $export.BuildPager = function () {
                var ul = document.createElement('ul');
                var li = document.createElement('li');
                var anchor = document.createElement('a');
                var right = ul.cloneNode(false);

                if ($export.pagerIncludeFirstAndLast) {
                    var pageFirst = li.cloneNode(false);
                    var pageFirstAnchor = anchor.cloneNode(false);
                    pageFirstAnchor.innerHTML = 'First';
                    pageFirst.setAttribute('class', 'table-page');
                    pageFirst.id = $export.id + '_page_first';
                    pageFirstAnchor.onclick = function () {
                        $export.pageNumber = 0;
                        if ($export.async &&
                            ($export.asyncStart > $export.pageNumber * $export.pageSize
                                || $export.pageNumber * $export.pageSize > $export.asyncStart + $export.asyncLength)) {
                            var ascending = true;
                            if ($export.sortOrder.length > 3 && $export.sortOrder.substr(0, 4).toLowerCase() == 'desc') {
                                ascending = false;
                            }
                            $export.asyncRequest(0, $export.currentFilter, $export.sortColumn, ascending);
                        }
                        $export.UpdateDisplayedRows(document.getElementById($export.id + '_body'));
                        $export.UpdateStyle();
                    };
                    if ($export.pageNumber <= 0) {
                        pageFirst.setAttribute('disabled', 'disabled');
                        pageFirstAnchor.onclick = function () {
                        };	//disable onclick
                    }
                    pageFirst.appendChild(pageFirstAnchor);
                    right.appendChild(pageFirst);
                }

                var pageLeft = li.cloneNode(false);
                var pageLeftAnchor = anchor.cloneNode(false);
                pageLeftAnchor.innerHTML = 'Vorherige Seite';
                pageLeft.setAttribute('class', 'table-page');
                pageLeft.id = $export.id + '_page_prev';
                pageLeftAnchor.onclick = function () {
                    $export.pageNumber -= 1;
                    if ($export.async &&
                        ($export.asyncStart > $export.pageNumber * $export.pageSize
                            || $export.pageNumber * $export.pageSize > $export.asyncStart + $export.asyncLength)) {
                        var newStart = $export.pageNumber * $export.pageSize;
                        var pages = 500 / $export.pageSize;
                        if ($export.pageNumber - pages > -1) {
                            newStart = ($export.pageNumber - pages) * $export.pageSize;
                        }
                        var ascending = true;
                        if ($export.sortOrder.length > 3 && $export.sortOrder.substr(0, 4).toLowerCase() == 'desc') {
                            ascending = false;
                        }
                        $export.asyncRequest(newStart, $export.currentFilter, $export.sortColumn, ascending);
                    }
                    $export.UpdateDisplayedRows(document.getElementById($export.id + '_body'));
                    $export.UpdateStyle();
                };
                if ($export.pageNumber <= 0) {
                    pageLeft.setAttribute('disabled', 'disabled');
                    pageLeftAnchor.onclick = function () {
                    };	//disable onclick
                }
                pageLeft.appendChild(pageLeftAnchor);
                right.appendChild(pageLeft);

                if ($export.pagerSize > 0) {
                    var start = $export.pageNumber - parseInt($export.pagerSize / 2);
                    var length = start + $export.pagerSize;
                    if ($export.pageNumber <= ($export.pagerSize / 2)) {
                        // display from beginning
                        length = $export.pagerSize;
                        start = 0;
                        if (length > $export.NumberOfPages()) {
                            length = $export.NumberOfPages();
                        }   //very small tables
                    }
                    else if (($export.NumberOfPages() - $export.pageNumber) <= ($export.pagerSize / 2)) {
                        //display the last five pages
                        length = $export.NumberOfPages();
                        start = $export.NumberOfPages() - $export.pagerSize;
                    }

                    for (var i = start; i < length; ++i) {
                        var liNode = li.cloneNode(false);
                        var liNodeAnchor = anchor.cloneNode(false);
                        liNodeAnchor.innerHTML = (i + 1).toString();
                        var page = i;
                        liNodeAnchor.onclick = function (j) {
                            return function () {
                                $export.pageNumber = j;
                                if ($export.async &&
                                    ($export.asyncStart > $export.pageNumber * $export.pageSize
                                        || $export.pageNumber * $export.pageSize >= $export.asyncStart + $export.asyncLength)) {
                                    var newStart = $export.pageNumber * $export.pageSize;
                                    var ascending = true;
                                    if ($export.sortOrder.length > 3 && $export.sortOrder.substr(0, 4).toLowerCase() == 'desc') {
                                        ascending = false;
                                    }
                                    $export.asyncRequest(newStart, $export.currentFilter, $export.sortColumn, ascending);
                                }
                                $export.UpdateDisplayedRows(document.getElementById($export.id + '_body'));
                                $export.UpdateStyle();
                            }
                        }(i);
                        liNode.setAttribute('class', 'table-page');
                        if (i == $export.pageNumber) {
                            liNode.setAttribute('disabled', 'disabled');
                            liNodeAnchor.onclick = function () {
                            };	//disable onclick
                        }
                        liNode.appendChild(liNodeAnchor);
                        right.appendChild(liNode);
                    }
                }

                var pageRight = li.cloneNode(false);
                var pageRightAnchor = anchor.cloneNode(false);
                pageRightAnchor.innerHTML = 'Nächste Steite';
                pageRight.setAttribute('class', 'table-page');
                pageRight.id = $export.id + '_page_next';
                pageRightAnchor.onclick = function () {
                    $export.pageNumber += 1;
                    if ($export.async &&
                        ($export.asyncStart > $export.pageNumber * $export.pageSize
                            || $export.pageNumber * $export.pageSize > $export.asyncStart + $export.asyncLength)) {
                        var newStart = $export.pageNumber * $export.pageSize;
                        var ascending = true;
                        if ($export.sortOrder.length > 3 && $export.sortOrder.substr(0, 4).toLowerCase() == 'desc') {
                            ascending = false;
                        }
                        $export.asyncRequest(newStart, $export.currentFilter, $export.sortColumn, ascending);
                    }
                    $export.UpdateDisplayedRows(document.getElementById($export.id + '_body'));
                    $export.UpdateStyle();
                };
                if ($export.NumberOfPages() - 1 == $export.pageNumber) {
                    pageRight.setAttribute('disabled', 'disabled');
                    pageRightAnchor.onclick = function () {
                    };	//disable onclick
                }
                pageRight.appendChild(pageRightAnchor);
                right.appendChild(pageRight);

                if ($export.pagerIncludeFirstAndLast) {
                    var pageLast = li.cloneNode(false);
                    var pageLastAnchor = anchor.cloneNode(false);
                    pageLastAnchor.innerHTML = 'Last';
                    pageLast.setAttribute('class', 'table-page');
                    pageLast.id = $export.id + '_page_last';
                    pageLastAnchor.onclick = function () {
                        $export.pageNumber = $export.NumberOfPages() - 1;   //page number is 0 based
                        if ($export.async &&
                            ($export.asyncStart > $export.pageNumber * $export.pageSize
                                || $export.pageNumber * $export.pageSize > $export.asyncStart + $export.asyncLength)) {
                            var newStart = 0;
                            var pages = (1000 / $export.pageSize) - 1;  //-1 for the page number and -1 to include current page
                            if ($export.pageNumber - pages > -1) {
                                newStart = ($export.pageNumber - pages) * $export.pageSize;
                            }
                            var ascending = true;
                            if ($export.sortOrder.length > 3 && $export.sortOrder.substr(0, 4).toLowerCase() == 'desc') {
                                ascending = false;
                            }
                            $export.asyncRequest(newStart, $export.currentFilter, $export.sortColumn, ascending);
                        }
                        $export.UpdateDisplayedRows(document.getElementById($export.id + '_body'));
                        $export.UpdateStyle();
                    };
                    if ($export.NumberOfPages() - 1 == $export.pageNumber) {
                        pageLast.setAttribute('disabled', 'disabled');
                        pageLastAnchor.onclick = function () {
                        };	//disable onclick
                    }
                    pageLast.appendChild(pageLastAnchor);
                    right.appendChild(pageLast);
                }

                return right;
            };

            //Utility functions
            function ArrayContains(array, object) {
                for (var i = 0; i < array.length; ++i) {
                    if (array[i] === object) {
                        return true;
                    }
                }
                return false;
            }

            function RemoveStyle(node) {
                node.removeAttribute('style');
                var childNodes = node.children;
                if (childNodes && childNodes.length > 0) {
                    for (var i = 0; i < childNodes.length; ++i) {
                        RemoveStyle(childNodes[i]);
                    }
                }
            }

            $export.CheckForTable();
            return $export;
        };
    });
}(typeof define === 'function' && define.amd ? define : function (deps, factory) {
        if (typeof module !== 'undefined' && module.exports) { //Node
            module.exports = factory();
        } else {
            window['Dable'] = factory();
        }
    }));
