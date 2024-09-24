function populateTable(itemTableInfo) {
    var tbody = document.querySelector('#itemTableInfo tbody');
    tbody.innerHTML = ''; 

    itemTableInfo.forEach(function(row) {
        var tr = document.createElement('tr');
        tr.innerHTML = tr.innerHTML = `
                                        <td class = "item-cell">
                                            <img class="item-table-icons" src="static/images/items/${row.Item}.png" alt="${row.Item} Icon">
                                            <span class="item-text">${row.Item}</span>
                                        </td>
                                        <td>${row.Games_Played}</td>
                                        <td>${(row.Winrate * 100).toFixed(2)}%</td>
                                    `;
        tbody.appendChild(tr);
    });
}


populateTable(itemTableInfo);


function sortTable(criteria) {
    var sorteditemTableInfo = itemTableInfo.slice(); 

    if (criteria === 'winrate') {
        sorteditemTableInfo.sort(function(a, b) {
            return b.Winrate - a.Winrate;
        });
    } else if (criteria === 'games') {
        sorteditemTableInfo.sort(function(a, b) {
            return b.Games_Played - a.Games_Played;
        });
    }

    populateTable(sorteditemTableInfo);
}