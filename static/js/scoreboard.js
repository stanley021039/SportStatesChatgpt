document.addEventListener('DOMContentLoaded', function () {
    // 获取日期切换按钮和当前日期元素
    const prevDateBtn = document.getElementById('prev-date');
    const nextDateBtn = document.getElementById('next-date');
    const currentDateSpan = document.getElementById('current-date');

    // 初始日期
    // let currentDate = new Date('2024-01-19');

    updateCurrentDate();
    fetchDataFromBackend();

    // 监听前一天按钮点击事件
    prevDateBtn.addEventListener('click', function () {
        currentDate.setDate(currentDate.getDate() - 1);
        updateCurrentDate();
        fetchDataFromBackend();
    });

    // 监听后一天按钮点击事件
    nextDateBtn.addEventListener('click', function () {
        currentDate.setDate(currentDate.getDate() + 1);
        updateCurrentDate();
        fetchDataFromBackend();
    });

    // 更新当前日期显示
    function updateCurrentDate() {
        const formattedDate = formatDate(currentDate);
        currentDateSpan.textContent = formattedDate;
    }

    // 格式化日期为 'YYYY-MM-DD'
    function formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    // 从后端获取数据的函数
    function fetchDataFromBackend() {
        const apiUrl = `${applicationRoot}/api/NBA/scoreboard_data?date=${formatDate(currentDate)}`;
    
        // 使用 fetch 或其他 HTTP 请求库发送请求
        fetch(apiUrl)
            .then(response => response.json())
            .then(data => {
                console.log(data)
                // 处理从后端获取的数据，更新前端显示
                updateFrontendWithData(data);
            })
            .catch(error => {
                console.error('Error fetching data from backend:', error);
            });
    }

    // 更新前端显示的函数
    function updateFrontendWithData(data) {
        // 假设表格的 ID 是 'scoreboard-table'
        const table = document.getElementById('scoreboard-table');
    
        // 清空表格内容
        table.innerHTML = '';
    
        // 添加表头
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
    
        // 假设列名存在于 data.column_names 中
        data.column_names.forEach(column => {
            const th = document.createElement('th');
            th.textContent = column;
            headerRow.appendChild(th);
        });
    
        thead.appendChild(headerRow);
        table.appendChild(thead);
    
        // 添加数据行
        const tbody = document.createElement('tbody');
        data.data.forEach(rowData => {
            const row = document.createElement('tr');
    
            rowData.forEach(cellData => {
                const td = document.createElement('td');
                td.textContent = cellData;
                row.appendChild(td);
            });
    
            tbody.appendChild(row);
        });
    
        table.appendChild(tbody);
    }

    var sendMessageBtn = document.getElementById("send-message");
    // 为每个可排序的列设置点击事件
    sendMessageBtn.addEventListener("click", function() {
        chatWithGPT(formatDate(currentDate))
    });
});
function sendMessage() {
    var messageInput = document.getElementById('message-input');
    var chatWindow = document.getElementById('chat-window');
    var responseDiv = document.getElementById('response');

    // Get user input
    var userMessage = messageInput.value;

    // Display user message in the chat window
    chatWindow.innerHTML += '<div><strong>You:</strong> ' + userMessage + '</div>';

    // Simulate processing and generate a response
    var responseMessage = simulateGPTResponse(userMessage);

    // Display the response in the chat window
    chatWindow.innerHTML += '<div><strong>ChatGPT:</strong> ' + responseMessage + '</div>';

    // Clear the input field
    messageInput.value = '';
}
function chatWithGPT(currentDate) {
    var userInputBlock = document.getElementById("message-input")
    var userInput = userInputBlock.value;
    var chatWindow = document.getElementById('chat-window');
    chatWindow.innerHTML += '<div><strong>You:</strong> ' + userInput + '</div>';
    // 修改文本的样式
    fetch(`${applicationRoot}/GPT?frontpage=scoreboard&date=${currentDate}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: userInput })
    })
    .then(response => response.json())
    .then(data => {
        // 在页面上显示后端返回的 JSON 数据
        chatWindow.innerHTML += '<div><strong>ChatGPT:</strong> ' + data.response + '</div>';
        userInputBlock.value = '';
    })
    .catch(error => {
        console.error('Fetch Error:', error);
    });
}