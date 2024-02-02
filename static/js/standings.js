document.addEventListener('DOMContentLoaded', function () {
    // 获取日期切换按钮和当前日期元素
    const prevSeasonBtn = document.getElementById('prev-season');
    const nextSeasonBtn = document.getElementById('next-season');
    const currentSeasonSpan = document.getElementById('current-season');

    // 更新当前日期显示
    updateCurrentSeason();
    fetchDataFromBackend();

    // 监听前一天按钮点击事件
    prevSeasonBtn.addEventListener('click', function () {
        currentSeason.setFullYear(currentSeason.getFullYear() - 1);
        updateCurrentSeason();
        fetchDataFromBackend();
    });
    
    // 监听后一年按钮点击事件
    nextSeasonBtn.addEventListener('click', function () {
        currentSeason.setFullYear(currentSeason.getFullYear() + 1);
        updateCurrentSeason();
        fetchDataFromBackend();
    });
    
    // 更新当前日期显示
    function updateCurrentSeason() {
        const formattedSeason = formatSeason(currentSeason);
        currentSeasonSpan.textContent = formattedSeason;
    }

    // 格式化日期为 'YYYY'
    function formatSeason(Season) {
        const year = Season.getFullYear();
        return `${year}`;
    }

    // 从后端获取数据的函数
    function fetchDataFromBackend() {
        // 发送 HTTP 请求到后端，使用当前日期和 X-Script-Name 作为参数
        const apiUrl = `${applicationRoot}/api/NBA/Standings_season_data?season=${formatSeason(currentSeason)}`;

        // 使用 fetch 或其他 HTTP 请求库发送请求
        fetch(apiUrl)
            .then(response => response.json())
            .then(data => {
                // 处理从后端获取的数据，更新前端显示
                updateFrontendWithData(data);
            })
            .catch(error => {
                console.error('Error fetching data from backend:', error);
            });
    }

    function updateFrontendWithData(responseData) {
        const data = responseData.data; // 获取实际的团队数据数组
        const table = document.getElementById('standingboard-table');
        while (table.rows.length > 1) {
            table.deleteRow(1);
        }
    
        data.forEach(teamData => {
            const row = document.createElement('tr');
    
            // 假设数据结构是固定的（Team, Wins, WinPercentage, Losses, LossPercentage）
            const [team, wins, winPercentage, losses, lossPercentage] = teamData;
    
            // 创建表格单元格并设置其内容
            const teamCell = document.createElement('td');
            teamCell.textContent = team;
            row.appendChild(teamCell);
    
            const winsCell = document.createElement('td');
            winsCell.textContent = wins;
            row.appendChild(winsCell);
    
            const winPercentageCell = document.createElement('td');
            winPercentageCell.textContent = winPercentage;
            row.appendChild(winPercentageCell);
    
            const lossesCell = document.createElement('td');
            lossesCell.textContent = losses;
            row.appendChild(lossesCell);
    
            const lossPercentageCell = document.createElement('td');
            lossPercentageCell.textContent = lossPercentage;
            row.appendChild(lossPercentageCell);
    
            table.appendChild(row);
        });
        // 构建字符串
        var seasonString = currentSeason.getFullYear() + '-' + (currentSeason.getFullYear() + 1);

        // 将字符串插入到 HTML 中
        document.getElementById('current-season').innerHTML = seasonString;
    }

    // 获取表头中的所有可排序的列
    const sortableHeaders = document.querySelectorAll('.sortable-header');

    // 为每个可排序的列设置点击事件
    sortableHeaders.forEach(header => {
        const columnName = header.getAttribute('data-column');
        header.onclick = function () {
            sortTable(columnName);
        };
    });
});

function sortTable(columnName) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    var orderSort = ''
    table = document.getElementById("standingboard-table");
    sortableHeaders = document.querySelectorAll('.sortable-header[data-column]');

    sortableHeaders.forEach(function(header) {
        var column = header.getAttribute('data-column');
        var currentSort = header.getAttribute('data-sort');

        if (column === columnName) {
            if (currentSort === '' || currentSort === 'desc') {
                header.setAttribute('data-sort', 'asc');
                orderSort = 'asc';
            } else {
                header.setAttribute('data-sort', 'desc');
                orderSort = 'desc';
            }
        } else {
            header.setAttribute('data-sort', '');
        }
    });

    switching = true;
    while (switching) {
        switching = false;
        rows = table.rows;

        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("td")[getColumnIndex(columnName)].innerHTML;
            y = rows[i + 1].getElementsByTagName("td")[getColumnIndex(columnName)].innerHTML;
            if (columnName === 'wins' || columnName === 'losses'){
                x = parseFloat(x)
                y = parseFloat(y)
            }

            if (orderSort === "asc") {
                if (x > y) {
                    shouldSwitch = true;
                    break;
                }
            } else if (orderSort === "desc") {
                if (x < y) {
                    shouldSwitch = true;
                    break;
                }
            }
        }

        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            switchcount++;
        } else {
            if (switchcount === 0 && orderSort === "asc") {
                orderSort = "desc";
                switching = true;
            }
        }
    }
}

// 获取列索引
function getColumnIndex(columnName) {
    var headers = document.querySelectorAll(".sortable-header");
    for (var i = 0; i < headers.length; i++) {
        if (headers[i].getAttribute("data-column") === columnName) {
            return i;
        }
    }
    return -1;
}